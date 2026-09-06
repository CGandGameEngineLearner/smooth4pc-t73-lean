#!/usr/bin/env python3
"""Build the directed v3 collar core-versus-push candidate matrix."""

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
CORE = ROOT / "audit/t73_x_m1_outer_collar_v3_core_clearance.json"
PUSH = ROOT / "audit/t73_x_m1_outer_collar_v3_push_clearance.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v3_core_push_candidate_matrix.json"
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
    core_clearance = json.loads(CORE.read_text())
    push_clearance = json.loads(PUSH.read_text())
    if (
        core_clearance["outer_collars_v3_receipt_sha256"] != collars["sha256"]
        or push_clearance["outer_collars_v3_receipt_sha256"] != collars["sha256"]
    ):
        raise AssertionError("v3 core/push clearance sources are stale")
    core_segments = []
    push_segments = []
    with gzip.open(resolve(collars["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            core = [point(value) for value in record["final_core_vertices"]]
            push = [point(value) for value in record["final_push_vertices"]]
            for segment_type, segment in enumerate(pairwise(core)):
                core_segments.append((record["interface_index"], segment_type, segment))
            for segment_type, segment in enumerate(pairwise(push)):
                push_segments.append((record["interface_index"], segment_type, segment))
    push_bounds = [exact_bounds(segment[2]) for segment in push_segments]
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        ((index, float_bounds(value), None) for index, value in enumerate(push_bounds)),
        properties=properties,
    )
    matrix = Counter()
    for _, core_type, segment in core_segments:
        for push_index in tree.intersection(float_bounds(exact_bounds(segment))):
            matrix[(core_type, push_segments[push_index][1])] += 1

    def constant_types(segments, invariant):
        return [
            segment_type
            for segment_type in range(6)
            if all(
                invariant(first) == invariant(second)
                for _, kind, (first, second) in segments
                if kind == segment_type
            )
        ]

    result = {
        "schema": "t73_x_m1_outer_collar_v3_core_push_candidate_matrix/v1",
        "outer_collars_v3_receipt_sha256": collars["sha256"],
        "v3_core_clearance_sha256": core_clearance["sha256"],
        "v3_push_clearance_sha256": push_clearance["sha256"],
        "core_segment_count": len(core_segments),
        "push_segment_count": len(push_segments),
        "segment_type_names": list(TYPE_NAMES),
        "directed_nonempty_type_pair_count": len(matrix),
        "expanded_3d_aabb_candidate_matrix": {
            f"core:{TYPE_NAMES[core_type]}/push:{TYPE_NAMES[push_type]}": count
            for (core_type, push_type), count in sorted(matrix.items())
        },
        "expanded_3d_aabb_candidate_count": sum(matrix.values()),
        "core_constant_functional_types": [
            TYPE_NAMES[index] for index in constant_types(core_segments, functional)
        ],
        "push_constant_functional_types": [
            TYPE_NAMES[index] for index in constant_types(push_segments, functional)
        ],
        "core_constant_height_types": [
            TYPE_NAMES[index]
            for index in constant_types(core_segments, lambda value: value[2])
        ],
        "push_constant_height_types": [
            TYPE_NAMES[index]
            for index in constant_types(push_segments, lambda value: value[2])
        ],
        "routing_functional": [str(-SLOPE), "1", str(FUNCTIONAL_Z)],
        "clearance_status": "OPEN_APPLY_DIRECTED_EXACT_HASH_INTERVAL_AND_GMP_REDUCTIONS",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V3_CORE_PUSH_CANDIDATE_MATRIX_ONLY",
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
        raise AssertionError("v3 core/push candidate matrix is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "type_pairs": result["directed_nonempty_type_pair_count"],
                "candidates": result["expanded_3d_aabb_candidate_count"],
                "clearance": result["clearance_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
