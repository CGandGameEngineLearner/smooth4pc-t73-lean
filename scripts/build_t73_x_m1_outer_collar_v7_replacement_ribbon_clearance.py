#!/usr/bin/env python3
"""Exact V7 collar/replacement ruled-ribbon cross-clearance."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from gmpy2 import mpq
from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v2_ribbon_self_clearance import (
    triangle_intersection_witness,
)
from verify_t73_x_m1_transition_transition_ribbon_clearance_gmp import (
    cross3,
    subtract,
    triangles_intersect,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
REPLACEMENTS = (
    ROOT / "audit/t73_x_m1_complete_global_r3_framed_replacement_cycles_receipt.json"
)
MATRIX = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_replacement_ribbon_candidate_matrix.json"
)
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v7_replacement_ribbon_clearance.json"
SYSTEMS = ("stub", "band", "transition", "middle")
TYPE_NAMES = (
    "retained_source_germ",
    "start_skew_lift",
    "first_exterior_ray",
    "staggered_height_bridge",
    "staggered_last_exterior_ray",
    "end_skew_lift",
)
ZERO = (mpq(0), mpq(0), mpq(0))


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
    return tuple(mpq(coordinate) for coordinate in value)


def functional(value):
    return value[1] - 1_000_033 * value[0] + 2 * value[2]


def dot(first, second):
    return sum(a * b for a, b in zip(first, second))


def exact_bounds(vertices):
    return tuple(min(vertex[axis] for vertex in vertices) for axis in range(3)), tuple(
        max(vertex[axis] for vertex in vertices) for axis in range(3)
    )


def float_bounds(bounds):
    return tuple(
        math.nextafter(float(value), -math.inf) for value in bounds[0]
    ) + tuple(math.nextafter(float(value), math.inf) for value in bounds[1])


def overlap(first, second):
    return all(
        first[0][axis] <= second[1][axis] and second[0][axis] <= first[1][axis]
        for axis in range(3)
    )


def record_rectangle(core, push, segment, metadata):
    quad = (core[segment], core[segment + 1], push[segment + 1], push[segment])
    f_values = [functional(vertex) for vertex in quad]
    return {
        **metadata,
        "quad": quad,
        "inner_edge": (core[segment], push[segment]),
        "target_edge": (core[segment + 1], push[segment + 1]),
        "bounds": exact_bounds(quad),
        "f_low": min(f_values),
        "f_high": max(f_values),
        "f_float_low": math.nextafter(float(min(f_values)), -math.inf),
        "f_float_high": math.nextafter(float(max(f_values)), math.inf),
        "triangles": (
            (core[segment], core[segment + 1], push[segment + 1]),
            (core[segment], push[segment + 1], push[segment]),
        ),
    }


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
    output = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            core = [point(value) for value in record["core_vertices"]]
            push = [point(value) for value in record["push_vertices"]]
            pieces = {}
            for piece in record["piece_ranges"]:
                for segment in range(*piece["segment_range"]):
                    pieces[segment] = piece["piece"]
            for segment in range(len(core) - 1):
                output.append(
                    record_rectangle(
                        core,
                        push,
                        segment,
                        {
                            "band": record["band_index"],
                            "segment": segment,
                            "piece": pieces[segment],
                            "system": replacement_system(pieces[segment]),
                        },
                    )
                )
    return output


def load_collars(receipt):
    output = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            core = [point(value) for value in record["final_core_vertices"]]
            push = [point(value) for value in record["final_push_vertices"]]
            for segment in (1, 5):
                output.append(
                    record_rectangle(
                        core,
                        push,
                        segment,
                        {
                            "interface": record["interface_index"],
                            "band": record["band_index"],
                            "side": record["side"],
                            "type": segment,
                        },
                    )
                )
    return output


def intended_adjacency(collar, replacement):
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


def skew_axis_separates(first, second):
    axis = cross3(
        subtract(first["quad"][1], first["quad"][0]),
        subtract(second["quad"][1], second["quad"][0]),
    )
    if axis == ZERO:
        return False
    first_values = [dot(axis, vertex) for vertex in first["quad"]]
    second_values = [dot(axis, vertex) for vertex in second["quad"]]
    return max(first_values) < min(second_values) or max(second_values) < min(
        first_values
    )


def build():
    collars_receipt = json.loads(COLLARS.read_text())
    replacements_receipt = json.loads(REPLACEMENTS.read_text())
    matrix = json.loads(MATRIX.read_text())
    if (
        matrix["outer_collars_v7_receipt_sha256"] != collars_receipt["sha256"]
        or matrix["complete_replacement_framing_receipt_sha256"]
        != replacements_receipt["sha256"]
    ):
        raise AssertionError("collar/replacement matrix is stale")
    collars = load_collars(collars_receipt)
    replacements = load_replacements(replacements_receipt)
    replacement_bounds = [record["bounds"] for record in replacements]
    replacement_low = np.asarray([record["f_float_low"] for record in replacements])
    replacement_high = np.asarray([record["f_float_high"] for record in replacements])
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        (
            (index, float_bounds(value), None)
            for index, value in enumerate(replacement_bounds)
        ),
        properties=properties,
    )
    stats = Counter()
    by_pair = Counter()
    for collar_index, collar in enumerate(collars):
        candidates = np.fromiter(
            tree.intersection(float_bounds(collar["bounds"])), dtype=np.int64
        )
        mask = (replacement_high[candidates] >= collar["f_float_low"]) & (
            replacement_low[candidates] <= collar["f_float_high"]
        )
        for replacement_index in candidates[mask]:
            replacement = replacements[int(replacement_index)]
            if intended_adjacency(collar, replacement):
                stats["adjacency"] += 1
                continue
            pair = f"collar:{TYPE_NAMES[collar['type']]}/replacement:{replacement['system']}"
            by_pair[pair] += 1
            stats["float_f_candidates"] += 1
            if (
                collar["f_high"] < replacement["f_low"]
                or replacement["f_high"] < collar["f_low"]
            ):
                stats["exact_f_reject"] += 1
                continue
            if not overlap(collar["bounds"], replacement["bounds"]):
                stats["exact_bounds_reject"] += 1
                continue
            if skew_axis_separates(collar, replacement):
                stats["skew_axis_reject"] += 1
                continue
            for first_local, first_triangle in enumerate(collar["triangles"]):
                for second_local, second_triangle in enumerate(
                    replacement["triangles"]
                ):
                    stats["triangle_checks"] += 1
                    if triangles_intersect(first_triangle, second_triangle):
                        witness = triangle_intersection_witness(
                            first_triangle, second_triangle
                        )
                        result = {
                            "schema": "t73_x_m1_outer_collar_v7_replacement_ribbon_clearance/v1",
                            "outer_collars_v7_receipt_sha256": collars_receipt[
                                "sha256"
                            ],
                            "candidate_matrix_sha256": matrix["sha256"],
                            "collision": {
                                "collar": [
                                    collar["interface"],
                                    collar["type"],
                                    first_local,
                                ],
                                "replacement": [
                                    replacement["band"],
                                    replacement["segment"],
                                    replacement["piece"],
                                    second_local,
                                ],
                                "witness": witness,
                                "checks_before_collision": dict(stats),
                            },
                            "global_replacement_cross_clearance": False,
                            "classification": "CANDIDATE_REFUTED",
                            "verdict": "REFUTED_X_M1_OUTER_COLLAR_V7_REPLACEMENT_RIBBON_CLEARANCE",
                        }
                        result["sha256"] = canonical_sha(result)
                        return result
    result = {
        "schema": "t73_x_m1_outer_collar_v7_replacement_ribbon_clearance/v1",
        "outer_collars_v7_receipt_sha256": collars_receipt["sha256"],
        "candidate_matrix_sha256": matrix["sha256"],
        "collar_rectangle_count_checked": len(collars),
        "replacement_rectangle_count": len(replacements),
        "candidate_type_counts": dict(sorted(by_pair.items())),
        "aabb_and_float_outward_f_candidates": stats["float_f_candidates"],
        "intended_target_adjacencies": stats["adjacency"],
        "exact_functional_interval_rejects": stats["exact_f_reject"],
        "exact_bounds_rejects": stats["exact_bounds_reject"],
        "exact_skew_axis_rejects": stats["skew_axis_reject"],
        "exact_triangle_pair_checks": stats["triangle_checks"],
        "intersection_count": 0,
        "global_replacement_cross_clearance": True,
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_REPLACEMENT_RIBBON_CLEARANCE",
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
        raise AssertionError("V7 replacement cross-clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "collision": result.get("collision"),
                "f_candidates": result.get("aabb_and_float_outward_f_candidates"),
                "skew_rejects": result.get("exact_skew_axis_rejects"),
                "triangle_checks": result.get("exact_triangle_pair_checks"),
                "intersections": result.get("intersection_count"),
            },
            sort_keys=True,
        )
    )
    if result["verdict"].startswith("REFUTED"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
