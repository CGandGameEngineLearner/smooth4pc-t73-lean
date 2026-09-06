#!/usr/bin/env python3
"""Build V7 collar versus retained Johnson/dual/passage ribbon candidates."""

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
COLLAR_REPLACEMENT = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_replacement_ribbon_clearance.json"
)
GAP = ROOT / "audit/t73_x_m1_complete_framed_outer_interface_gap.json"
CYCLES = ROOT / "geometry/t73_post_x_framed_cycle_assembly.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
PASSAGES = ROOT / "audit/t73_yz_framed_passage_mapping_cylinders_receipt.json"
PASSAGES_VERIFY = (
    ROOT / "audit/t73_yz_framed_passage_mapping_cylinders_verification.json"
)
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v7_retained_ribbon_candidate_matrix.json"
COLLAR_TYPES = (
    "retained_source_germ",
    "start_skew_lift",
    "first_exterior_ray",
    "staggered_height_bridge",
    "staggered_last_exterior_ray",
    "end_skew_lift",
)
RETAINED_TYPES = (
    "central_connector",
    "johnson_handle_arc",
    "bottom_closure",
    "dual_passage",
)


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
    return tuple(Fraction(coordinate) for coordinate in value[:3])


def add(first, second):
    return tuple(a + b for a, b in zip(first, second))


def functional_bounds(vertices):
    values = [vertex[1] - 1_000_033 * vertex[0] + 2 * vertex[2] for vertex in vertices]
    return min(values), max(values)


def exact_bounds(vertices):
    return tuple(min(vertex[axis] for vertex in vertices) for axis in range(3)), tuple(
        max(vertex[axis] for vertex in vertices) for axis in range(3)
    )


def float_bounds(bounds):
    return tuple(
        math.nextafter(float(value), -math.inf) for value in bounds[0]
    ) + tuple(math.nextafter(float(value), math.inf) for value in bounds[1])


def segment_key(first, second):
    return tuple(sorted((first, second)))


def rectangle(core, push, segment, metadata):
    quad = (core[segment], core[segment + 1], push[segment + 1], push[segment])
    f_low, f_high = functional_bounds(quad)
    return {
        **metadata,
        "inner_edge": (core[segment], push[segment]),
        "target_edge": (core[segment + 1], push[segment + 1]),
        "quad": quad,
        "bounds": exact_bounds(quad),
        "f_low": f_low,
        "f_high": f_high,
        "f_bounds": (
            math.nextafter(float(f_low), -math.inf),
            math.nextafter(float(f_high), math.inf),
        ),
        "triangles": (
            (core[segment], core[segment + 1], push[segment + 1]),
            (core[segment], push[segment + 1], push[segment]),
        ),
    }


def load_collars(receipt):
    output = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            core = [point(value) for value in record["final_core_vertices"]]
            push = [point(value) for value in record["final_push_vertices"]]
            for segment in range(len(core) - 1):
                output.append(
                    rectangle(
                        core,
                        push,
                        segment,
                        {
                            "interface": record["interface_index"],
                            "neighbor_id": record["neighbor_id"],
                            "type": segment,
                        },
                    )
                )
    return output


def load_retained(gap, cycles, spine, ar_link, passages_receipt):
    removed = {
        segment_key(point(item["source_inner_core"]), point(item["source_core_port"]))
        for item in gap["interfaces"]
    }
    width = Fraction(ar_link["framing"]["spine_ribbon_transport"]["width"])
    connector_normal = (width, width, width)
    output = []
    removed_count = 0
    used_connectors = {
        block["connector_id"]
        for component in cycles["components"]
        for block in component["blocks"]
        if block["kind"] == "actual_johnson_central_connector"
    }
    for connector in spine["central_connectors"]:
        if connector["connector_id"] not in used_connectors:
            continue
        core = [point(value) for value in connector["polyline"]]
        push = [add(value, connector_normal) for value in core]
        for segment in range(len(core) - 1):
            if segment_key(core[segment], core[segment + 1]) in removed:
                removed_count += 1
                continue
            output.append(
                rectangle(
                    core,
                    push,
                    segment,
                    {
                        "kind": "central_connector",
                        "owner_id": connector["connector_id"],
                        "segment": segment,
                    },
                )
            )
    chart_to_kind = {
        "johnson_fiber_handle": "johnson_handle_arc",
        "bottom_cut_ball": "bottom_closure",
        "fiber_dual_cell": "dual_passage",
    }
    with gzip.open(
        resolve(passages_receipt["cache_path"]), "rt", encoding="utf-8"
    ) as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            if record["source_chart"] == "x_m1_ejected_atlas":
                continue
            kind = chart_to_kind[record["source_chart"]]
            core = [point(value) for value in record["source_core_vertices"]]
            push = [point(value) for value in record["source_push_vertices"]]
            for segment in range(len(core) - 1):
                if segment_key(core[segment], core[segment + 1]) in removed:
                    removed_count += 1
                    continue
                output.append(
                    rectangle(
                        core,
                        push,
                        segment,
                        {
                            "kind": kind,
                            "owner_id": record["passage_id"],
                            "segment": segment,
                        },
                    )
                )
    return output, removed_count


def build():
    collars_receipt = json.loads(COLLARS.read_text())
    collar_replacement = json.loads(COLLAR_REPLACEMENT.read_text())
    gap = json.loads(GAP.read_text())
    cycles = json.loads(CYCLES.read_text())
    spine = json.loads(SPINE.read_text())
    ar_link = json.loads(AR_LINK.read_text())
    passages_receipt = json.loads(PASSAGES.read_text())
    passages_verify = json.loads(PASSAGES_VERIFY.read_text())
    if (
        collar_replacement["outer_collars_v7_receipt_sha256"]
        != collars_receipt["sha256"]
        or not collar_replacement["global_replacement_cross_clearance"]
    ):
        raise AssertionError("V7 replacement-side clearance is stale or failed")
    if passages_verify["construction_receipt_sha256"] != passages_receipt["sha256"]:
        raise AssertionError("passage source-boundary verification is stale")
    collars = load_collars(collars_receipt)
    retained, removed = load_retained(gap, cycles, spine, ar_link, passages_receipt)
    if removed != 3026 or len(retained) != 4630:
        raise AssertionError(
            f"retained inventory changed: removed={removed}, retained={len(retained)}"
        )
    kind_counts = Counter(item["kind"] for item in retained)
    expected_kinds = {
        "central_connector": 4074,
        "johnson_handle_arc": 524,
        "bottom_closure": 24,
        "dual_passage": 8,
    }
    if dict(kind_counts) != expected_kinds:
        raise AssertionError(f"retained kind inventory changed: {dict(kind_counts)}")
    retained_low = np.asarray([item["f_bounds"][0] for item in retained])
    retained_high = np.asarray([item["f_bounds"][1] for item in retained])
    retained_kind_codes = np.asarray(
        [RETAINED_TYPES.index(item["kind"]) for item in retained]
    )
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        (
            (index, float_bounds(item["bounds"]), None)
            for index, item in enumerate(retained)
        ),
        properties=properties,
    )
    matrix = Counter()
    f_matrix = Counter()
    broad = source_adjacencies = 0
    source_star_relations = Counter()
    for collar in collars:
        candidates = np.fromiter(
            tree.intersection(float_bounds(collar["bounds"])), dtype=np.int64
        )
        broad += len(candidates)
        f_low, f_high = collar["f_bounds"]
        f_mask = (retained_high[candidates] >= f_low) & (
            retained_low[candidates] <= f_high
        )
        for code, kind in enumerate(RETAINED_TYPES):
            f_matrix[(collar["type"], kind)] += int(
                np.count_nonzero(f_mask & (retained_kind_codes[candidates] == code))
            )
        for retained_index in candidates:
            retained_rectangle = retained[int(retained_index)]
            shared = tuple(set(collar["quad"]) & set(retained_rectangle["quad"]))
            if (
                collar["type"] == 0
                and collar["neighbor_id"] == retained_rectangle["owner_id"]
                and len(shared) == 2
            ):
                relation = star_relation(collar, retained_rectangle, shared)
                if relation == "COPLANAR_SAME_SIDE_OVERLAP":
                    raise AssertionError("V7 source-germ/retained ribbon star folds")
                source_star_relations[relation] += 1
                source_adjacencies += 1
                continue
            matrix[(collar["type"], retained_rectangle["kind"])] += 1
    if source_adjacencies != 3018:
        raise AssertionError(
            f"V7 source framing adjacency count changed: {source_adjacencies}"
        )
    f_matrix[(0, "central_connector")] -= 3018
    f_matrix = Counter({key: value for key, value in f_matrix.items() if value})
    result = {
        "schema": "t73_x_m1_outer_collar_v7_retained_ribbon_candidate_matrix/v1",
        "outer_collars_v7_receipt_sha256": collars_receipt["sha256"],
        "v7_replacement_cross_clearance_sha256": collar_replacement["sha256"],
        "outer_interface_gap_sha256": gap["sha256"],
        "post_x_framed_cycle_assembly_sha256": cycles["sha256"],
        "johnson_spine_sha256": spine["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "passage_mapping_cylinders_verification_sha256": passages_verify["sha256"],
        "original_nonreplacement_segment_count": 7656,
        "removed_terminal_segment_count": removed,
        "retained_rectangle_count": len(retained),
        "retained_kind_counts": dict(sorted(kind_counts.items())),
        "collar_rectangle_count": len(collars),
        "expanded_3d_aabb_pair_count": broad,
        "source_framing_edge_adjacency_count": source_adjacencies,
        "source_framing_edge_star_relation_counts": dict(
            sorted(source_star_relations.items())
        ),
        "nonincident_candidate_matrix": {
            f"collar:{COLLAR_TYPES[collar_type]}/retained:{kind}": count
            for (collar_type, kind), count in sorted(matrix.items())
        },
        "nonincident_candidate_count": sum(matrix.values()),
        "aabb_and_functional_interval_candidate_matrix": {
            f"collar:{COLLAR_TYPES[collar_type]}/retained:{kind}": count
            for (collar_type, kind), count in sorted(f_matrix.items())
        },
        "aabb_and_functional_interval_candidate_count": sum(f_matrix.values()),
        "clearance_status": "OPEN_APPLY_EXACT_BOUNDS_SKEW_AND_TRIANGLE_CHECKS",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_RETAINED_RIBBON_CANDIDATE_MATRIX_ONLY",
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
        raise AssertionError("V7 retained ribbon matrix is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "retained": result["retained_rectangle_count"],
                "removed": result["removed_terminal_segment_count"],
                "broad": result["expanded_3d_aabb_pair_count"],
                "adjacencies": result["source_framing_edge_adjacency_count"],
                "nonincident": result["nonincident_candidate_count"],
                "f_candidates": result["aabb_and_functional_interval_candidate_count"],
                "clearance": result["clearance_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
