#!/usr/bin/env python3
"""Prove v3 collar push clearance with exact hashes and end-lift intervals."""

from __future__ import annotations

import argparse
import bisect
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
MATRIX = ROOT / "audit/t73_x_m1_outer_collar_v3_push_candidate_matrix.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v3_push_clearance.json"
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
FUNCTIONAL_PAIRS = {(1, 1), (1, 2), (1, 4)}
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
            vertices = [point(value) for value in record["final_push_vertices"]]
            for segment_type, segment in enumerate(pairwise(vertices)):
                groups[segment_type].append(
                    {
                        "interface": record["interface_index"],
                        "neighbor_kind": record["neighbor_kind"],
                        "neighbor_id": record["neighbor_id"],
                        "type": segment_type,
                        "vertices": segment,
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


def invariant_candidates(first_group, second_group, key, symmetric):
    buckets = defaultdict(list)
    for index, record in enumerate(second_group):
        buckets[key(record)].append(index)
    for first_index, first in enumerate(first_group):
        for second_index in buckets.get(key(first), ()):
            if symmetric and second_index >= first_index:
                continue
            yield first, second_group[second_index]


def direct_aabb_candidates(first_group, second_group, symmetric):
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


def check_standard_pair(pair, groups, broad_count):
    first_type, second_type = pair
    symmetric = first_type == second_type
    if pair in FUNCTIONAL_PAIRS:
        candidates = invariant_candidates(
            groups[first_type],
            groups[second_type],
            lambda record: functional(record["vertices"][0]),
            symmetric,
        )
        invariant = "constant exact push routing functional"
    elif pair in HEIGHT_PAIRS:
        candidates = invariant_candidates(
            groups[first_type],
            groups[second_type],
            lambda record: record["vertices"][0][2],
            symmetric,
        )
        invariant = "constant exact push routing height"
    else:
        candidates = direct_aabb_candidates(
            groups[first_type], groups[second_type], symmetric
        )
        invariant = "outward-rounded 3D AABB then GMP"
    reduced = incidences = exact = 0
    for first, second in candidates:
        reduced += 1
        if permitted(first, second):
            incidences += 1
            continue
        exact += 1
        if segment_intersects(first["vertices"], second["vertices"]):
            raise AssertionError(
                f"v3 push collision: {first['interface']}/{first_type} vs {second['interface']}/{second_type}"
            )
    return {
        "pair": f"{TYPE_NAMES[first_type]}/{TYPE_NAMES[second_type]}",
        "broad_aabb_candidates": broad_count,
        "exact_reduction_invariant": invariant,
        "reduced_candidates": reduced,
        "permitted_incidences": incidences,
        "exact_segment_checks": exact,
        "intersections": 0,
        "status": "PASS",
    }


def interval_distance(value, interval):
    low, high, _ = interval
    return mpq(0) if low <= value <= high else min(abs(value - low), abs(value - high))


def nearest_interval_distances(values, intervals, exclude_same_interface=False):
    lows = [interval[0] for interval in intervals]
    distances = []
    for value, interface in values:
        position = bisect.bisect_left(lows, value)
        candidates = range(max(0, position - 2), min(len(intervals), position + 2))
        valid = [
            interval_distance(value, intervals[index])
            for index in candidates
            if not (exclude_same_interface and intervals[index][2] == interface)
        ]
        distances.append(min(valid))
    return min(distances)


def check_end_lifts(groups, matrix_counts):
    end_group = groups[5]
    johnson = [
        record
        for record in end_group
        if record["neighbor_kind"] == "actual_johnson_central_connector"
    ]
    dual = [
        record
        for record in end_group
        if record["neighbor_kind"] != "actual_johnson_central_connector"
    ]
    intervals = sorted(
        (
            min(functional(record["vertices"][0]), functional(record["vertices"][1])),
            max(functional(record["vertices"][0]), functional(record["vertices"][1])),
            record["interface"],
        )
        for record in johnson
    )
    widths = {high - low for low, high, _ in intervals}
    if len(widths) != 1:
        raise AssertionError("Johnson end-lift push F widths changed")
    width = next(iter(widths))
    interval_gap = min(right[0] - left[1] for left, right in pairwise(intervals))
    if interval_gap <= 0:
        raise AssertionError("Johnson end-lift push F intervals overlap")
    type2_values = [
        (functional(record["vertices"][0]), record["interface"]) for record in groups[2]
    ]
    type4_values = [
        (functional(record["vertices"][0]), record["interface"]) for record in groups[4]
    ]
    type2_margin = nearest_interval_distances(type2_values, intervals)
    type4_margin = nearest_interval_distances(type4_values, intervals, True)
    if min(type2_margin, type4_margin) <= 0:
        raise AssertionError(
            "constant push ray enters a nonincident Johnson end-lift F interval"
        )

    direct_specs = (
        (2, groups[2], dual, False),
        (4, groups[4], dual, False),
        (5, johnson, dual, False),
        (5, dual, dual, True),
    )
    direct_checks = incidences = 0
    for first_type, first_group, second_group, symmetric in direct_specs:
        for first_index, first in enumerate(first_group):
            for second_index, second in enumerate(second_group):
                if symmetric and second_index >= first_index:
                    continue
                if permitted(first, second):
                    incidences += 1
                    continue
                direct_checks += 1
                if segment_intersects(first["vertices"], second["vertices"]):
                    raise AssertionError(
                        f"dual end-lift push collision: {first['interface']} vs {second['interface']}"
                    )
    return {
        "pair_family": "end_skew_lift_with_normal_change",
        "broad_aabb_candidates": matrix_counts[
            "first_exterior_ray/end_skew_lift_with_normal_change"
        ]
        + matrix_counts["last_exterior_ray/end_skew_lift_with_normal_change"]
        + matrix_counts[
            "end_skew_lift_with_normal_change/end_skew_lift_with_normal_change"
        ],
        "johnson_end_lift_count": len(johnson),
        "dual_end_lift_count": len(dual),
        "johnson_exact_functional_interval_width": str(width),
        "johnson_exact_minimum_inter_interval_gap": str(interval_gap),
        "type2_exact_minimum_interval_margin": str(type2_margin),
        "type4_nonincident_exact_minimum_interval_margin": str(type4_margin),
        "dual_direct_gmp_checks": direct_checks,
        "permitted_incidences": incidences + len(johnson),
        "intersections": 0,
        "status": "PASS",
    }


def build():
    collars = json.loads(COLLARS.read_text())
    matrix = json.loads(MATRIX.read_text())
    if matrix["outer_collars_v3_receipt_sha256"] != collars["sha256"]:
        raise AssertionError("v3 push matrix is stale")
    groups = load(collars)
    matrix_counts = matrix["expanded_3d_aabb_candidate_matrix"]
    standard_pairs = FUNCTIONAL_PAIRS | HEIGHT_PAIRS | DIRECT_PAIRS
    standard = []
    for pair in sorted(standard_pairs):
        name = f"{TYPE_NAMES[pair[0]]}/{TYPE_NAMES[pair[1]]}"
        standard.append(check_standard_pair(pair, groups, matrix_counts[name]))
    end_lifts = check_end_lifts(groups, matrix_counts)
    covered = {result["pair"] for result in standard} | {
        "first_exterior_ray/end_skew_lift_with_normal_change",
        "last_exterior_ray/end_skew_lift_with_normal_change",
        "end_skew_lift_with_normal_change/end_skew_lift_with_normal_change",
    }
    if covered != set(matrix_counts):
        raise AssertionError("v3 push clearance does not cover the complete matrix")
    result = {
        "schema": "t73_x_m1_outer_collar_v3_push_clearance/v1",
        "outer_collars_v3_receipt_sha256": collars["sha256"],
        "v3_push_candidate_matrix_sha256": matrix["sha256"],
        "push_segment_count": sum(len(group) for group in groups.values()),
        "standard_type_pair_results": standard,
        "end_lift_result": end_lifts,
        "covered_type_pair_count": len(covered),
        "broad_aabb_candidate_count": matrix["expanded_3d_aabb_candidate_count"],
        "exact_segment_check_count": sum(
            item["exact_segment_checks"] for item in standard
        )
        + end_lifts["dual_direct_gmp_checks"],
        "permitted_incidence_count": sum(
            item["permitted_incidences"] for item in standard
        )
        + end_lifts["permitted_incidences"],
        "intersection_count": 0,
        "global_push_clearance": True,
        "verdict": "PASS_X_M1_OUTER_COLLAR_V3_PUSH_CLEARANCE",
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
        raise AssertionError("v3 collar push clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "broad": result["broad_aabb_candidate_count"],
                "exact": result["exact_segment_check_count"],
                "incidences": result["permitted_incidence_count"],
                "intersections": result["intersection_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
