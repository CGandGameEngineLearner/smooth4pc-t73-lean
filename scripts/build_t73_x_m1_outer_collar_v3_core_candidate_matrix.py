#!/usr/bin/env python3
"""Classify v3 collar-core broad candidates by six semantic segment types."""

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
LOCAL_VERIFY = (
    ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v3_verification.json"
)
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v3_core_candidate_matrix.json"
SLOPE = 1_000_033
FUNCTIONAL_Z = 2
TYPE_NAMES = (
    "retained_source_germ",
    "start_skew_lift",
    "first_exterior_ray",
    "height_bridge",
    "last_exterior_ray",
    "end_skew_lift",
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
    local = json.loads(LOCAL_VERIFY.read_text())
    if local["construction_receipt_sha256"] != collars["sha256"]:
        raise AssertionError("v3 local verification is stale")
    segments = []
    with gzip.open(resolve(collars["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            vertices = [point(value) for value in record["final_core_vertices"]]
            for segment_type, segment in enumerate(pairwise(vertices)):
                segments.append((record["interface_index"], segment_type, segment))
    if len(segments) != 18_156:
        raise AssertionError("v3 core segment inventory changed")
    bounds = [exact_bounds(record[2]) for record in segments]
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
    expected = {
        (0, 0): 4,
        (0, 1): 9_074,
        (1, 1): 2_281_620,
        (1, 2): 3_440_548,
        (1, 4): 12_097,
        (2, 3): 3_026,
        (2, 4): 3_026,
        (2, 5): 4_567_750,
        (3, 4): 3_026,
        (4, 5): 3_934_557,
        (5, 5): 232,
    }
    if dict(matrix) != expected:
        raise AssertionError(f"v3 core candidate matrix changed: {dict(matrix)}")
    constant_functional_types = []
    constant_height_types = []
    for segment_type in range(6):
        group = [segment for _, kind, segment in segments if kind == segment_type]
        if all(functional(first) == functional(second) for first, second in group):
            constant_functional_types.append(segment_type)
        if all(first[2] == second[2] for first, second in group):
            constant_height_types.append(segment_type)
    result = {
        "schema": "t73_x_m1_outer_collar_v3_core_candidate_matrix/v1",
        "outer_collars_v3_receipt_sha256": collars["sha256"],
        "outer_collars_v3_local_verification_sha256": local["sha256"],
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
        "heavy_pair_reduction_plan": {
            "functional_hash": [
                "start_skew_lift/start_skew_lift",
                "start_skew_lift/first_exterior_ray",
                "start_skew_lift/last_exterior_ray",
                "first_exterior_ray/end_skew_lift",
                "last_exterior_ray/end_skew_lift",
                "end_skew_lift/end_skew_lift",
            ],
            "height_hash": [
                "first_exterior_ray/height_bridge",
                "first_exterior_ray/last_exterior_ray",
                "height_bridge/last_exterior_ray",
            ],
            "direct_gmp": [
                "retained_source_germ/retained_source_germ",
                "retained_source_germ/start_skew_lift",
            ],
        },
        "clearance_status": "OPEN_APPLY_EXACT_HASH_REDUCTIONS_AND_GMP_SURVIVORS",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V3_CORE_CANDIDATE_MATRIX_ONLY",
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
        raise AssertionError("v3 core candidate matrix is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "segments": result["segment_count"],
                "candidates": result["expanded_3d_aabb_candidate_count"],
                "clearance": result["clearance_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
