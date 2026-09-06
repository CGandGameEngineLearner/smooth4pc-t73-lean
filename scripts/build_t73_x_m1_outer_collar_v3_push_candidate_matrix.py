#!/usr/bin/env python3
"""Classify v3 collar-push broad candidates by six semantic segment types."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
from collections import Counter
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

from rtree import index as rtree_index

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v3_receipt.json"
CORE_CLEARANCE = ROOT / "audit/t73_x_m1_outer_collar_v3_core_clearance.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v3_push_candidate_matrix.json"
SLOPE = 1_000_033
FUNCTIONAL_Z = 2
TYPE_NAMES = (
    "retained_source_germ",
    "start_skew_lift",
    "first_exterior_ray",
    "height_bridge",
    "last_exterior_ray",
    "end_skew_lift_with_normal_change",
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
    return tuple(Fraction(coordinate) for coordinate in value)


def functional(value):
    return value[1] - SLOPE * value[0] + FUNCTIONAL_Z * value[2]


def exact_bounds(segment):
    return tuple(min(segment[0][axis], segment[1][axis]) for axis in range(3)), tuple(
        max(segment[0][axis], segment[1][axis]) for axis in range(3)
    )


def float_bounds(bounds):
    return tuple(
        math.nextafter(float(value), -math.inf) for value in bounds[0]
    ) + tuple(math.nextafter(float(value), math.inf) for value in bounds[1])


def build():
    collars = json.loads(COLLARS.read_text())
    core = json.loads(CORE_CLEARANCE.read_text())
    if (
        core["outer_collars_v3_receipt_sha256"] != collars["sha256"]
        or not core["global_core_clearance"]
    ):
        raise AssertionError("v3 core clearance is stale or failed")
    segments = []
    endpoint_values = {
        "germ_source_normal": [],
        "target_high_source_normal": [],
        "target_target_normal": [],
    }
    with gzip.open(resolve(collars["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            vertices = [point(value) for value in record["final_push_vertices"]]
            for segment_type, segment in enumerate(pairwise(vertices)):
                segments.append((record["interface_index"], segment_type, segment))
            endpoint_values["germ_source_normal"].append(functional(vertices[1]))
            endpoint_values["target_high_source_normal"].append(functional(vertices[5]))
            endpoint_values["target_target_normal"].append(functional(vertices[6]))
    if len(segments) != 18_156:
        raise AssertionError("v3 push segment inventory changed")
    all_endpoint_values = [
        value for group in endpoint_values.values() for value in group
    ]
    if len(all_endpoint_values) != len(set(all_endpoint_values)):
        raise AssertionError(
            "v3 push routing endpoint functional values are not globally injective"
        )
    bounds = [exact_bounds(segment[2]) for segment in segments]
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        ((index, float_bounds(value), None) for index, value in enumerate(bounds)),
        properties=properties,
    )
    matrix = Counter()
    for first_index, (_, first_type, segment) in enumerate(segments):
        for second_index in tree.intersection(float_bounds(bounds[first_index])):
            if second_index >= first_index:
                continue
            second_type = segments[second_index][1]
            matrix[tuple(sorted((first_type, second_type)))] += 1
    constant_functional_types = []
    constant_height_types = []
    for segment_type in range(6):
        group = [segment for _, kind, segment in segments if kind == segment_type]
        if all(functional(first) == functional(second) for first, second in group):
            constant_functional_types.append(segment_type)
        if all(first[2] == second[2] for first, second in group):
            constant_height_types.append(segment_type)
    result = {
        "schema": "t73_x_m1_outer_collar_v3_push_candidate_matrix/v1",
        "outer_collars_v3_receipt_sha256": collars["sha256"],
        "v3_core_clearance_sha256": core["sha256"],
        "segment_count": len(segments),
        "segment_type_names": list(TYPE_NAMES),
        "segment_count_per_type": 3026,
        "expanded_3d_aabb_candidate_matrix": {
            f"{TYPE_NAMES[first]}/{TYPE_NAMES[second]}": count
            for (first, second), count in sorted(matrix.items())
        },
        "expanded_3d_aabb_candidate_count": sum(matrix.values()),
        "constant_functional_segment_types": [
            TYPE_NAMES[index] for index in constant_functional_types
        ],
        "constant_height_segment_types": [
            TYPE_NAMES[index] for index in constant_height_types
        ],
        "routing_functional": [str(-SLOPE), "1", str(FUNCTIONAL_Z)],
        "push_functional_endpoint_group_counts": {
            name: len(values) for name, values in endpoint_values.items()
        },
        "push_functional_endpoint_union_count": len(all_endpoint_values),
        "push_functional_endpoint_union_distinct_count": len(set(all_endpoint_values)),
        "clearance_status": "OPEN_APPLY_EXACT_HASH_AND_END_LIFT_COPLANARITY_REDUCTIONS",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V3_PUSH_CANDIDATE_MATRIX_ONLY",
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
        raise AssertionError("v3 push candidate matrix is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "segments": result["segment_count"],
                "candidates": result["expanded_3d_aabb_candidate_count"],
                "constant_f_types": result["constant_functional_segment_types"],
                "clearance": result["clearance_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
