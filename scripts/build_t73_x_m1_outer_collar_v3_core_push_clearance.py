#!/usr/bin/env python3
"""Exact directed core-versus-push clearance for waypoint collars v3."""

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
MATRIX = ROOT / "audit/t73_x_m1_outer_collar_v3_core_push_candidate_matrix.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v3_core_push_clearance.json"
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
CORE_F_TYPES = {1, 2, 4, 5}
PUSH_F_TYPES = {1, 2, 4}
HEIGHT_TYPES = {2, 3, 4}
DIRECT_PAIRS = {(0, 0), (0, 1), (1, 0)}
END_INTERVAL_PAIRS = {(2, 5), (4, 5), (5, 5)}


class CorePushCollision(Exception):
    def __init__(self, data):
        super().__init__(str(data))
        self.data = data


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


def intersection_witness(first, second):
    a, b = first
    c, d = second
    u = tuple(b[axis] - a[axis] for axis in range(3))
    v = tuple(d[axis] - c[axis] for axis in range(3))
    w = tuple(c[axis] - a[axis] for axis in range(3))
    for first_axis, second_axis in ((0, 1), (0, 2), (1, 2)):
        denominator = u[first_axis] * (-v[second_axis]) - u[second_axis] * (
            -v[first_axis]
        )
        if not denominator:
            continue
        first_parameter = (
            w[first_axis] * (-v[second_axis]) - w[second_axis] * (-v[first_axis])
        ) / denominator
        second_parameter = (
            u[first_axis] * w[second_axis] - u[second_axis] * w[first_axis]
        ) / denominator
        if (
            0 <= first_parameter <= 1
            and 0 <= second_parameter <= 1
            and all(
                a[axis] + first_parameter * u[axis]
                == c[axis] + second_parameter * v[axis]
                for axis in range(3)
            )
        ):
            return {
                "point": [
                    str(a[axis] + first_parameter * u[axis]) for axis in range(3)
                ],
                "core_parameter": str(first_parameter),
                "push_parameter": str(second_parameter),
            }
        return None
    return None


def load(receipt):
    core = defaultdict(list)
    push = defaultdict(list)
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            for kind, groups in (
                ("final_core_vertices", core),
                ("final_push_vertices", push),
            ):
                vertices = [point(value) for value in record[kind]]
                for segment_type, segment in enumerate(pairwise(vertices)):
                    groups[segment_type].append(
                        {
                            "interface": record["interface_index"],
                            "neighbor_kind": record["neighbor_kind"],
                            "type": segment_type,
                            "vertices": segment,
                        }
                    )
    return core, push


def invariant_candidates(first_group, second_group, key):
    buckets = defaultdict(list)
    for record in second_group:
        buckets[key(record)].append(record)
    for first in first_group:
        yield from ((first, second) for second in buckets.get(key(first), ()))


def direct_candidates(first_group, second_group):
    bounds = [exact_bounds(record["vertices"]) for record in second_group]
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        ((index, float_bounds(value), None) for index, value in enumerate(bounds)),
        properties=properties,
    )
    for first in first_group:
        first_bounds = exact_bounds(first["vertices"])
        for second_index in tree.intersection(float_bounds(first_bounds)):
            if overlap(first_bounds, bounds[second_index]):
                yield first, second_group[second_index]


def check_pair(pair, core, push, broad):
    core_type, push_type = pair
    if core_type in CORE_F_TYPES and push_type in PUSH_F_TYPES:
        candidates = invariant_candidates(
            core[core_type],
            push[push_type],
            lambda record: functional(record["vertices"][0]),
        )
        invariant = "equal exact core/push routing functional"
    elif core_type in HEIGHT_TYPES and push_type in HEIGHT_TYPES:
        candidates = invariant_candidates(
            core[core_type], push[push_type], lambda record: record["vertices"][0][2]
        )
        invariant = "equal exact core/push routing height"
    elif pair in DIRECT_PAIRS:
        candidates = direct_candidates(core[core_type], push[push_type])
        invariant = "outward-rounded 3D AABB then GMP"
    else:
        raise AssertionError(f"unclassified standard core/push pair {pair}")
    reduced = exact = 0
    for first, second in candidates:
        reduced += 1
        exact += 1
        if segment_intersects(first["vertices"], second["vertices"]):
            witness = intersection_witness(first["vertices"], second["vertices"])
            if witness is None:
                raise AssertionError(
                    "v3 core/push collision lacks a unique exact witness"
                )
            raise CorePushCollision(
                {
                    "pair": f"core:{TYPE_NAMES[core_type]}/push:{TYPE_NAMES[push_type]}",
                    "core_interface": first["interface"],
                    "push_interface": second["interface"],
                    "core_segment": [
                        [str(value) for value in vertex] for vertex in first["vertices"]
                    ],
                    "push_segment": [
                        [str(value) for value in vertex]
                        for vertex in second["vertices"]
                    ],
                    "witness": witness,
                    "reduction_invariant": invariant,
                    "reduced_candidates_before_collision": reduced,
                    "exact_checks_before_collision": exact,
                }
            )
    return {
        "pair": f"core:{TYPE_NAMES[core_type]}/push:{TYPE_NAMES[push_type]}",
        "broad_aabb_candidates": broad,
        "exact_reduction_invariant": invariant,
        "reduced_candidates": reduced,
        "exact_segment_checks": exact,
        "intersections": 0,
        "status": "PASS",
    }


def interval_distance(value, interval):
    low, high, _ = interval
    return mpq(0) if low <= value <= high else min(abs(value - low), abs(value - high))


def minimum_point_interval_margin(points, intervals):
    lows = [interval[0] for interval in intervals]
    distances = []
    for value in points:
        position = bisect.bisect_left(lows, value)
        nearby = range(max(0, position - 2), min(len(intervals), position + 2))
        distances.append(
            min(interval_distance(value, intervals[index]) for index in nearby)
        )
    return min(distances)


def check_push_end_intervals(core, push, matrix_counts):
    push_end = push[5]
    johnson = [
        record
        for record in push_end
        if record["neighbor_kind"] == "actual_johnson_central_connector"
    ]
    dual = [
        record
        for record in push_end
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
    interval_gap = min(right[0] - left[1] for left, right in pairwise(intervals))
    if interval_gap <= 0:
        raise AssertionError("Johnson push end-lift F intervals overlap")
    margins = {}
    for core_type in (2, 4, 5):
        points = [functional(record["vertices"][0]) for record in core[core_type]]
        margin = minimum_point_interval_margin(points, intervals)
        if margin <= 0:
            raise AssertionError(
                f"core type {core_type} enters a Johnson push end-lift F interval"
            )
        margins[core_type] = margin
    direct_checks = 0
    for core_type in (2, 4, 5):
        for first in core[core_type]:
            for second in dual:
                direct_checks += 1
                if segment_intersects(first["vertices"], second["vertices"]):
                    raise AssertionError(
                        f"dual push end-lift meets core: {first['interface']}/{core_type} vs {second['interface']}"
                    )
    return {
        "pair_family": "core types 2/4/5 versus push end_skew_lift",
        "broad_aabb_candidates": sum(
            matrix_counts[f"core:{TYPE_NAMES[core_type]}/push:end_skew_lift"]
            for core_type in (2, 4, 5)
        ),
        "johnson_push_end_lift_count": len(johnson),
        "dual_push_end_lift_count": len(dual),
        "johnson_exact_minimum_inter_interval_gap": str(interval_gap),
        "core_type_exact_minimum_interval_margins": {
            TYPE_NAMES[key]: str(value) for key, value in margins.items()
        },
        "dual_direct_gmp_checks": direct_checks,
        "intersections": 0,
        "status": "PASS",
    }


def build():
    collars = json.loads(COLLARS.read_text())
    matrix = json.loads(MATRIX.read_text())
    if matrix["outer_collars_v3_receipt_sha256"] != collars["sha256"]:
        raise AssertionError("v3 core/push matrix is stale")
    core, push = load(collars)
    matrix_counts = matrix["expanded_3d_aabb_candidate_matrix"]
    matrix_pairs = {
        (
            TYPE_NAMES.index(name.split("/")[0].removeprefix("core:")),
            TYPE_NAMES.index(name.split("/")[1].removeprefix("push:")),
        )
        for name in matrix_counts
    }
    standard_pairs = matrix_pairs - END_INTERVAL_PAIRS
    standard = []
    try:
        for pair in sorted(standard_pairs):
            name = f"core:{TYPE_NAMES[pair[0]]}/push:{TYPE_NAMES[pair[1]]}"
            standard.append(check_pair(pair, core, push, matrix_counts[name]))
    except CorePushCollision as collision:
        result = {
            "schema": "t73_x_m1_outer_collar_v3_core_push_clearance/v1",
            "outer_collars_v3_receipt_sha256": collars["sha256"],
            "v3_core_push_candidate_matrix_sha256": matrix["sha256"],
            "core_segment_count": sum(len(group) for group in core.values()),
            "push_segment_count": sum(len(group) for group in push.values()),
            "completed_type_pair_results_before_collision": standard,
            "collision": collision.data,
            "global_core_push_clearance": False,
            "classification": "CANDIDATE_REFUTED",
            "verdict": "REFUTED_X_M1_OUTER_COLLAR_V3_CORE_PUSH_CLEARANCE",
        }
        result["sha256"] = canonical_sha(result)
        return result
    end_result = check_push_end_intervals(core, push, matrix_counts)
    result = {
        "schema": "t73_x_m1_outer_collar_v3_core_push_clearance/v1",
        "outer_collars_v3_receipt_sha256": collars["sha256"],
        "v3_core_push_candidate_matrix_sha256": matrix["sha256"],
        "core_segment_count": sum(len(group) for group in core.values()),
        "push_segment_count": sum(len(group) for group in push.values()),
        "standard_directed_type_pair_results": standard,
        "push_end_lift_interval_result": end_result,
        "covered_directed_type_pair_count": len(standard) + len(END_INTERVAL_PAIRS),
        "broad_aabb_candidate_count": matrix["expanded_3d_aabb_candidate_count"],
        "exact_segment_check_count": sum(
            item["exact_segment_checks"] for item in standard
        )
        + end_result["dual_direct_gmp_checks"],
        "intersection_count": 0,
        "global_core_push_clearance": True,
        "verdict": "PASS_X_M1_OUTER_COLLAR_V3_CORE_PUSH_CLEARANCE",
    }
    if (
        result["covered_directed_type_pair_count"]
        != matrix["directed_nonempty_type_pair_count"]
    ):
        raise AssertionError(
            "v3 core/push clearance does not cover all directed type pairs"
        )
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
        raise AssertionError("v3 core/push clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "type_pairs": result.get("covered_directed_type_pair_count"),
                "broad": result.get("broad_aabb_candidate_count"),
                "exact": result.get("exact_segment_check_count"),
                "intersections": result.get("intersection_count"),
                "collision": result.get("collision"),
            },
            sort_keys=True,
        )
    )
    if result["verdict"].startswith("REFUTED"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
