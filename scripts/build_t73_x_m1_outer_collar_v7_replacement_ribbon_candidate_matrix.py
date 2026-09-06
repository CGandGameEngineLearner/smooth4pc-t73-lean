#!/usr/bin/env python3
"""Build V7 collar versus complete replacement ribbon candidate matrix."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np
from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v2_ribbon_self_clearance import star_relation

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
COLLAR_CLEARANCE = ROOT / "audit/t73_x_m1_outer_collar_v7_ribbon_clearance.json"
REPLACEMENTS = (
    ROOT / "audit/t73_x_m1_complete_global_r3_framed_replacement_cycles_receipt.json"
)
REPLACEMENT_VERIFY = (
    ROOT
    / "audit/t73_x_m1_complete_global_r3_framed_replacement_cycles_verification.json"
)
OUTPUT = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_replacement_ribbon_candidate_matrix.json"
)
COLLAR_TYPES = (
    "retained_source_germ",
    "start_skew_lift",
    "first_exterior_ray",
    "staggered_height_bridge",
    "staggered_last_exterior_ray",
    "end_skew_lift",
)
SYSTEMS = ("stub", "band", "transition", "middle")


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def exact_bounds(vertices):
    return tuple(min(vertex[axis] for vertex in vertices) for axis in range(3)), tuple(
        max(vertex[axis] for vertex in vertices) for axis in range(3)
    )


def float_bounds(bounds):
    return tuple(
        math.nextafter(float(value), -math.inf) for value in bounds[0]
    ) + tuple(math.nextafter(float(value), math.inf) for value in bounds[1])


def functional_bounds(vertices):
    values = [vertex[1] - 1_000_033 * vertex[0] + 2 * vertex[2] for vertex in vertices]
    return (
        math.nextafter(float(min(values)), -math.inf),
        math.nextafter(float(max(values)), math.inf),
    )


def replacement_system(piece):
    if "stub" in piece or "complement" in piece:
        return "stub"
    if "band_lane" in piece:
        return "band"
    if "transition" in piece:
        return "transition"
    if "middle" in piece:
        return "middle"
    raise AssertionError(f"unknown replacement piece {piece}")


def load_replacements(receipt):
    rectangles = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            core = [point(value) for value in record["core_vertices"]]
            push = [point(value) for value in record["push_vertices"]]
            piece_by_segment = {}
            for piece in record["piece_ranges"]:
                low, high = piece["segment_range"]
                for segment in range(low, high):
                    piece_by_segment[segment] = piece["piece"]
            for segment in range(len(core) - 1):
                rectangles.append(
                    {
                        "band": record["band_index"],
                        "segment": segment,
                        "piece": piece_by_segment[segment],
                        "system": replacement_system(piece_by_segment[segment]),
                        "inner_edge": (core[segment], push[segment]),
                        "target_edge": (core[segment + 1], push[segment + 1]),
                        "quad": (
                            core[segment],
                            core[segment + 1],
                            push[segment + 1],
                            push[segment],
                        ),
                        "f_bounds": functional_bounds(
                            (
                                core[segment],
                                core[segment + 1],
                                push[segment + 1],
                                push[segment],
                            )
                        ),
                        "triangles": (
                            (core[segment], core[segment + 1], push[segment + 1]),
                            (core[segment], push[segment + 1], push[segment]),
                        ),
                    }
                )
    return rectangles


def load_collars(receipt):
    rectangles = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            core = [point(value) for value in record["final_core_vertices"]]
            push = [point(value) for value in record["final_push_vertices"]]
            for segment in range(len(core) - 1):
                rectangles.append(
                    {
                        "interface": record["interface_index"],
                        "band": record["band_index"],
                        "side": record["side"],
                        "type": segment,
                        "inner_edge": (core[segment], push[segment]),
                        "target_edge": (core[segment + 1], push[segment + 1]),
                        "quad": (
                            core[segment],
                            core[segment + 1],
                            push[segment + 1],
                            push[segment],
                        ),
                        "f_bounds": functional_bounds(
                            (
                                core[segment],
                                core[segment + 1],
                                push[segment + 1],
                                push[segment],
                            )
                        ),
                        "triangles": (
                            (core[segment], core[segment + 1], push[segment + 1]),
                            (core[segment], push[segment + 1], push[segment]),
                        ),
                    }
                )
    return rectangles


def intended_target_adjacency(collar, replacement):
    if collar["type"] != 5 or collar["band"] != replacement["band"]:
        return False
    if collar["side"] == "before":
        return (
            replacement["piece"] == "source_stub_before"
            and replacement["segment"] == 0
            and collar["target_edge"] == replacement["inner_edge"]
        )
    return (
        replacement["piece"] == "source_stub_after"
        and collar["target_edge"] == replacement["target_edge"]
    )


def build():
    collars_receipt = json.loads(COLLARS.read_text())
    collar_clearance = json.loads(COLLAR_CLEARANCE.read_text())
    replacements_receipt = json.loads(REPLACEMENTS.read_text())
    replacement_verify = json.loads(REPLACEMENT_VERIFY.read_text())
    if (
        collar_clearance["outer_collars_v7_receipt_sha256"] != collars_receipt["sha256"]
        or not collar_clearance["global_ribbon_clearance"]
    ):
        raise AssertionError("V7 internal ribbon clearance is stale or failed")
    if (
        replacement_verify["construction_receipt_sha256"]
        != replacements_receipt["sha256"]
        or not replacement_verify["full_result"]["globally_embedded_complete_framing"]
    ):
        raise AssertionError("replacement framing verification is stale or failed")
    collars = load_collars(collars_receipt)
    replacements = load_replacements(replacements_receipt)
    if (len(collars), len(replacements)) != (18_156, 92_284):
        raise AssertionError("collar/replacement rectangle inventory changed")
    replacement_bounds = [exact_bounds(item["quad"]) for item in replacements]
    replacement_f_low = np.asarray([item["f_bounds"][0] for item in replacements])
    replacement_f_high = np.asarray([item["f_bounds"][1] for item in replacements])
    replacement_system_codes = np.asarray(
        [SYSTEMS.index(item["system"]) for item in replacements]
    )
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        (
            (index, float_bounds(value), None)
            for index, value in enumerate(replacement_bounds)
        ),
        properties=properties,
    )
    matrix = Counter()
    functional_matrix = Counter()
    target_star_relations = Counter()
    broad = intended = 0
    for collar in collars:
        candidates = np.fromiter(
            tree.intersection(float_bounds(exact_bounds(collar["quad"]))),
            dtype=np.int64,
        )
        f_low, f_high = collar["f_bounds"]
        f_mask = (replacement_f_high[candidates] >= f_low) & (
            replacement_f_low[candidates] <= f_high
        )
        for system_code, system in enumerate(SYSTEMS):
            functional_matrix[(collar["type"], system)] += int(
                np.count_nonzero(
                    f_mask & (replacement_system_codes[candidates] == system_code)
                )
            )
        for replacement_index in candidates:
            replacement_index = int(replacement_index)
            broad += 1
            replacement = replacements[replacement_index]
            if intended_target_adjacency(collar, replacement):
                edge = tuple(set(collar["quad"]) & set(replacement["quad"]))
                relation = star_relation(collar, replacement, edge)
                if relation == "COPLANAR_SAME_SIDE_OVERLAP":
                    raise AssertionError("collar/replacement target ribbon star folds")
                target_star_relations[relation] += 1
                intended += 1
                continue
            matrix[(collar["type"], replacement["system"])] += 1
    if intended != 3026:
        raise AssertionError(f"target framing-edge adjacency count changed: {intended}")
    functional_matrix[(5, "stub")] -= intended
    functional_matrix = Counter(
        {key: value for key, value in functional_matrix.items() if value}
    )
    result = {
        "schema": "t73_x_m1_outer_collar_v7_replacement_ribbon_candidate_matrix/v1",
        "outer_collars_v7_receipt_sha256": collars_receipt["sha256"],
        "outer_collars_v7_ribbon_clearance_sha256": collar_clearance["sha256"],
        "complete_replacement_framing_receipt_sha256": replacements_receipt["sha256"],
        "complete_replacement_framing_verification_sha256": replacement_verify[
            "sha256"
        ],
        "collar_rectangle_count": len(collars),
        "replacement_rectangle_count": len(replacements),
        "expanded_3d_aabb_pair_count": broad,
        "intended_target_framing_edge_adjacency_count": intended,
        "target_framing_edge_star_relation_counts": dict(
            sorted(target_star_relations.items())
        ),
        "nonincident_candidate_matrix": {
            f"collar:{COLLAR_TYPES[collar_type]}/replacement:{system}": count
            for (collar_type, system), count in sorted(matrix.items())
        },
        "nonincident_candidate_count": sum(matrix.values()),
        "nonempty_type_pair_count": len(matrix),
        "aabb_and_functional_interval_candidate_matrix": {
            f"collar:{COLLAR_TYPES[collar_type]}/replacement:{system}": count
            for (collar_type, system), count in sorted(functional_matrix.items())
        },
        "aabb_and_functional_interval_candidate_count": sum(functional_matrix.values()),
        "clearance_status": "OPEN_APPLY_EXACT_FUNCTIONAL_INTERVAL_BOUNDS_AND_TRIANGLE_CHECKS",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_REPLACEMENT_RIBBON_CANDIDATE_MATRIX_ONLY",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("V7 collar/replacement ribbon matrix is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "collars": result["collar_rectangle_count"],
                "replacements": result["replacement_rectangle_count"],
                "broad": result["expanded_3d_aabb_pair_count"],
                "adjacencies": result["intended_target_framing_edge_adjacency_count"],
                "nonincident": result["nonincident_candidate_count"],
                "type_pairs": result["nonempty_type_pair_count"],
                "clearance": result["clearance_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
