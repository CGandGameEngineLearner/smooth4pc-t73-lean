#!/usr/bin/env python3
"""Apply exact functional/height hashes to prove v3 collar core clearance."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import sys
from collections import defaultdict
from itertools import pairwise
from pathlib import Path

from gmpy2 import mpq
from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_core_push_clearance import segment_intersects

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v3_receipt.json"
MATRIX = ROOT / "audit/t73_x_m1_outer_collar_v3_core_candidate_matrix.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v3_core_clearance.json"
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
FUNCTIONAL_PAIRS = {(1, 1), (1, 2), (1, 4), (2, 5), (4, 5), (5, 5)}
HEIGHT_PAIRS = {(2, 3), (2, 4), (3, 4)}
DIRECT_PAIRS = {(0, 0), (0, 1)}


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
    return value[1] - SLOPE * value[0] + FUNCTIONAL_Z * value[2]


def exact_bounds(segment):
    return tuple(min(segment[0][axis], segment[1][axis]) for axis in range(3)), tuple(
        max(segment[0][axis], segment[1][axis]) for axis in range(3)
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


def load(receipt):
    groups = defaultdict(list)
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            vertices = [point(value) for value in record["final_core_vertices"]]
            for segment_type, (first, second) in enumerate(pairwise(vertices)):
                groups[segment_type].append(
                    {
                        "interface": record["interface_index"],
                        "neighbor_id": record["neighbor_id"],
                        "type": segment_type,
                        "vertices": (first, second),
                    }
                )
    return groups


def permitted(first, second):
    shared = set(first["vertices"]) & set(second["vertices"])
    if not shared:
        return False
    if first["interface"] == second["interface"]:
        return abs(first["type"] - second["type"]) == 1
    return (
        first["type"] == second["type"] == 0
        and first["neighbor_id"] == second["neighbor_id"]
        and first["vertices"][0] == second["vertices"][0]
    )


def equal_invariant_candidates(first_group, second_group, key, symmetric):
    buckets = defaultdict(list)
    for index, record in enumerate(second_group):
        buckets[key(record)].append(index)
    for first_index, first in enumerate(first_group):
        for second_index in buckets.get(key(first), ()):
            if symmetric and second_index >= first_index:
                continue
            yield first, second_group[second_index]


def direct_candidates(first_group, second_group, symmetric):
    bounds = [exact_bounds(record["vertices"]) for record in second_group]
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        ((index, float_bounds(value), None) for index, value in enumerate(bounds)),
        properties=properties,
    )
    for first_index, first in enumerate(first_group):
        first_bounds = exact_bounds(first["vertices"])
        for second_index in tree.intersection(float_bounds(first_bounds)):
            if symmetric and second_index >= first_index:
                continue
            if overlap(first_bounds, bounds[second_index]):
                yield first, second_group[second_index]


def check_pair(pair, groups, broad_count):
    first_type, second_type = pair
    first_group, second_group = groups[first_type], groups[second_type]
    symmetric = first_type == second_type
    if pair in FUNCTIONAL_PAIRS:
        key = lambda record: functional(record["vertices"][0])
        candidates = equal_invariant_candidates(
            first_group, second_group, key, symmetric
        )
        invariant = "constant exact routing functional"
    elif pair in HEIGHT_PAIRS:
        key = lambda record: record["vertices"][0][2]
        candidates = equal_invariant_candidates(
            first_group, second_group, key, symmetric
        )
        invariant = "constant exact routing height"
    elif pair in DIRECT_PAIRS:
        candidates = direct_candidates(first_group, second_group, symmetric)
        invariant = "outward-rounded 3D AABB then GMP"
    else:
        raise AssertionError(f"unclassified v3 core type pair: {pair}")
    hash_candidates = incidences = exact = 0
    for first, second in candidates:
        hash_candidates += 1
        if permitted(first, second):
            incidences += 1
            continue
        exact += 1
        if segment_intersects(first["vertices"], second["vertices"]):
            raise AssertionError(
                f"v3 collar core collision: {first['interface']}/{first_type} vs {second['interface']}/{second_type}"
            )
    return {
        "pair": f"{TYPE_NAMES[first_type]}/{TYPE_NAMES[second_type]}",
        "broad_aabb_candidates": broad_count,
        "exact_reduction_invariant": invariant,
        "equal_invariant_or_direct_candidates": hash_candidates,
        "permitted_incidences": incidences,
        "exact_segment_checks": exact,
        "intersections": 0,
        "status": "PASS",
    }


def build():
    collars = json.loads(COLLARS.read_text())
    matrix = json.loads(MATRIX.read_text())
    if matrix["outer_collars_v3_receipt_sha256"] != collars["sha256"]:
        raise AssertionError("v3 core matrix is stale")
    groups = load(collars)
    matrix_counts = matrix["expanded_3d_aabb_candidate_matrix"]
    results = []
    classified = FUNCTIONAL_PAIRS | HEIGHT_PAIRS | DIRECT_PAIRS
    for pair in sorted(classified):
        name = f"{TYPE_NAMES[pair[0]]}/{TYPE_NAMES[pair[1]]}"
        results.append(check_pair(pair, groups, matrix_counts[name]))
    if {result["pair"] for result in results} != set(matrix_counts):
        raise AssertionError(
            "v3 core clearance does not cover the complete candidate matrix"
        )
    result = {
        "schema": "t73_x_m1_outer_collar_v3_core_clearance/v1",
        "outer_collars_v3_receipt_sha256": collars["sha256"],
        "v3_core_candidate_matrix_sha256": matrix["sha256"],
        "core_segment_count": sum(len(group) for group in groups.values()),
        "semantic_type_pair_count": len(results),
        "type_pair_results": results,
        "broad_aabb_candidate_count": sum(
            item["broad_aabb_candidates"] for item in results
        ),
        "reduced_candidate_count": sum(
            item["equal_invariant_or_direct_candidates"] for item in results
        ),
        "permitted_incidence_count": sum(
            item["permitted_incidences"] for item in results
        ),
        "exact_segment_check_count": sum(
            item["exact_segment_checks"] for item in results
        ),
        "intersection_count": 0,
        "global_core_clearance": True,
        "verdict": "PASS_X_M1_OUTER_COLLAR_V3_CORE_CLEARANCE",
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
        raise AssertionError("v3 collar core clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "broad": result["broad_aabb_candidate_count"],
                "reduced": result["reduced_candidate_count"],
                "exact": result["exact_segment_check_count"],
                "intersections": result["intersection_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
