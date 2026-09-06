#!/usr/bin/env python3
"""Rebuild all v4 core, push and directed mutual AABB type matrices."""

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
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v4_receipt.json"
LOCAL_VERIFY = (
    ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v4_verification.json"
)
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v4_one_skeleton_candidate_matrices.json"
SLOPE = 1_000_033
FUNCTIONAL_Z = 2
TYPE_NAMES = (
    "retained_source_germ",
    "start_skew_lift",
    "first_exterior_ray",
    "staggered_height_bridge",
    "staggered_last_exterior_ray",
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


def matrix(first_segments, second_segments, symmetric):
    bounds = [exact_bounds(segment[2]) for segment in second_segments]
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        ((index, float_bounds(value), None) for index, value in enumerate(bounds)),
        properties=properties,
    )
    counts = Counter()
    for first_index, (_, first_type, segment) in enumerate(first_segments):
        for second_index in tree.intersection(float_bounds(exact_bounds(segment))):
            if symmetric and second_index >= first_index:
                continue
            pair = (first_type, second_segments[second_index][1])
            counts[tuple(sorted(pair)) if symmetric else pair] += 1
    return counts


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


def encode_matrix(counts, directed):
    return {
        (
            f"core:{TYPE_NAMES[first]}/push:{TYPE_NAMES[second]}"
            if directed
            else f"{TYPE_NAMES[first]}/{TYPE_NAMES[second]}"
        ): count
        for (first, second), count in sorted(counts.items())
    }


def build(collars_path=COLLARS, local_verify_path=LOCAL_VERIFY, version="v4"):
    collars = json.loads(collars_path.read_text())
    local = json.loads(local_verify_path.read_text())
    if local["construction_receipt_sha256"] != collars["sha256"]:
        raise AssertionError("v4 local verification is stale")
    core = []
    push = []
    with gzip.open(resolve(collars["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            for key, output in (
                ("final_core_vertices", core),
                ("final_push_vertices", push),
            ):
                vertices = [point(value) for value in record[key]]
                output.extend(
                    (record["interface_index"], segment_type, segment)
                    for segment_type, segment in enumerate(pairwise(vertices))
                )
    if (len(core), len(push)) != (18_156, 18_156):
        raise AssertionError("v4 one-skeleton inventory changed")
    core_matrix = matrix(core, core, True)
    push_matrix = matrix(push, push, True)
    mutual_matrix = matrix(core, push, False)
    result = {
        "schema": f"t73_x_m1_outer_collar_{version}_one_skeleton_candidate_matrices/v1",
        f"outer_collars_{version}_receipt_sha256": collars["sha256"],
        f"outer_collars_{version}_local_verification_sha256": local["sha256"],
        "core_segment_count": len(core),
        "push_segment_count": len(push),
        "segment_type_names": list(TYPE_NAMES),
        "core_matrix": encode_matrix(core_matrix, False),
        "push_matrix": encode_matrix(push_matrix, False),
        "directed_core_push_matrix": encode_matrix(mutual_matrix, True),
        "core_candidate_count": sum(core_matrix.values()),
        "push_candidate_count": sum(push_matrix.values()),
        "directed_core_push_candidate_count": sum(mutual_matrix.values()),
        "core_nonempty_type_pair_count": len(core_matrix),
        "push_nonempty_type_pair_count": len(push_matrix),
        "directed_core_push_nonempty_type_pair_count": len(mutual_matrix),
        "core_constant_functional_types": [
            TYPE_NAMES[index] for index in constant_types(core, functional)
        ],
        "push_constant_functional_types": [
            TYPE_NAMES[index] for index in constant_types(push, functional)
        ],
        "core_constant_height_types": [
            TYPE_NAMES[index] for index in constant_types(core, lambda value: value[2])
        ],
        "push_constant_height_types": [
            TYPE_NAMES[index] for index in constant_types(push, lambda value: value[2])
        ],
        "end_exterior_height_offset": collars["end_exterior_height_offset"],
        "clearance_status": f"OPEN_APPLY_{version.upper()}_EXACT_HASH_INTERVAL_AND_GMP_REDUCTIONS",
        "verdict": f"PASS_X_M1_OUTER_COLLAR_{version.upper()}_ONE_SKELETON_CANDIDATE_MATRICES_ONLY",
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
        raise AssertionError("v4 one-skeleton matrices are stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "core": result["core_candidate_count"],
                "push": result["push_candidate_count"],
                "mutual": result["directed_core_push_candidate_count"],
                "type_pairs": [
                    result["core_nonempty_type_pair_count"],
                    result["push_nonempty_type_pair_count"],
                    result["directed_core_push_nonempty_type_pair_count"],
                ],
                "clearance": result["clearance_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
