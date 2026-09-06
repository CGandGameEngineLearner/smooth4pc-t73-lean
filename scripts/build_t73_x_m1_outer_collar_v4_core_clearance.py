#!/usr/bin/env python3
"""Exact global v4 core clearance using F, interface and GMP reductions."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_core_push_clearance import segment_intersects
from build_t73_x_m1_outer_collar_v3_core_clearance import (
    direct_candidates,
    functional,
    load,
    permitted,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v4_receipt.json"
MATRICES = ROOT / "audit/t73_x_m1_outer_collar_v4_one_skeleton_candidate_matrices.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v4_core_clearance.json"
TYPE_NAMES = (
    "retained_source_germ",
    "start_skew_lift",
    "first_exterior_ray",
    "staggered_height_bridge",
    "staggered_last_exterior_ray",
    "end_skew_lift",
)
FUNCTIONAL_PAIRS = {(1, 1), (1, 2), (1, 4), (2, 5), (4, 5), (5, 5)}
INTERFACE_PAIRS = {(2, 3), (2, 4), (3, 4)}
DIRECT_PAIRS = {(0, 0), (0, 1)}


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def bucket_candidates(first_group, second_group, key, symmetric):
    buckets = {}
    for record in second_group:
        buckets.setdefault(key(record), []).append(record)
    for first_index, first in enumerate(first_group):
        for second in buckets.get(key(first), ()):
            if symmetric and second is first:
                continue
            if symmetric and second["interface"] >= first["interface"]:
                continue
            yield first, second


def check_pair(pair, groups, broad):
    first_type, second_type = pair
    if pair in FUNCTIONAL_PAIRS:
        candidates = bucket_candidates(
            groups[first_type],
            groups[second_type],
            lambda record: functional(record["vertices"][0]),
            first_type == second_type,
        )
        invariant = "constant exact routing functional"
    elif pair in INTERFACE_PAIRS:
        candidates = bucket_candidates(
            groups[first_type],
            groups[second_type],
            lambda record: record["interface"],
            False,
        )
        invariant = "same-interface staggered corner"
    elif pair in DIRECT_PAIRS:
        candidates = direct_candidates(
            groups[first_type], groups[second_type], first_type == second_type
        )
        invariant = "outward-rounded 3D AABB then GMP"
    else:
        raise AssertionError(f"unclassified v4 core pair {pair}")
    reduced = incidences = exact = 0
    for first, second in candidates:
        reduced += 1
        if permitted(first, second):
            incidences += 1
            continue
        exact += 1
        if segment_intersects(first["vertices"], second["vertices"]):
            raise AssertionError(
                f"v4 core collision: {first['interface']}/{first_type} vs {second['interface']}/{second_type}"
            )
    return {
        "pair": f"{TYPE_NAMES[first_type]}/{TYPE_NAMES[second_type]}",
        "broad_aabb_candidates": broad,
        "exact_reduction_invariant": invariant,
        "reduced_candidates": reduced,
        "permitted_incidences": incidences,
        "exact_segment_checks": exact,
        "intersections": 0,
        "status": "PASS",
    }


def build():
    collars = json.loads(COLLARS.read_text())
    matrices = json.loads(MATRICES.read_text())
    if matrices["outer_collars_v4_receipt_sha256"] != collars["sha256"]:
        raise AssertionError("v4 matrices are stale")
    groups = load(collars)
    counts = matrices["core_matrix"]
    pairs = FUNCTIONAL_PAIRS | INTERFACE_PAIRS | DIRECT_PAIRS
    results = []
    for pair in sorted(pairs):
        name = f"{TYPE_NAMES[pair[0]]}/{TYPE_NAMES[pair[1]]}"
        results.append(check_pair(pair, groups, counts[name]))
    if {result["pair"] for result in results} != set(counts):
        raise AssertionError("v4 core proof does not consume the complete matrix")
    result = {
        "schema": "t73_x_m1_outer_collar_v4_core_clearance/v1",
        "outer_collars_v4_receipt_sha256": collars["sha256"],
        "v4_one_skeleton_matrices_sha256": matrices["sha256"],
        "core_segment_count": sum(len(group) for group in groups.values()),
        "type_pair_results": results,
        "covered_type_pair_count": len(results),
        "broad_aabb_candidate_count": sum(
            item["broad_aabb_candidates"] for item in results
        ),
        "reduced_candidate_count": sum(item["reduced_candidates"] for item in results),
        "permitted_incidence_count": sum(
            item["permitted_incidences"] for item in results
        ),
        "exact_segment_check_count": sum(
            item["exact_segment_checks"] for item in results
        ),
        "intersection_count": 0,
        "global_core_clearance": True,
        "verdict": "PASS_X_M1_OUTER_COLLAR_V4_CORE_CLEARANCE",
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
        raise AssertionError("v4 core clearance is stale")
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
