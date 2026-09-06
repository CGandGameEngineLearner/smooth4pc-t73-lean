#!/usr/bin/env python3
"""Exact directed mutual core/push clearance for staggered collars v4."""

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
from build_t73_x_m1_outer_collar_v3_core_push_clearance import (
    check_push_end_intervals,
    direct_candidates,
    functional,
    load,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v4_receipt.json"
MATRICES = ROOT / "audit/t73_x_m1_outer_collar_v4_one_skeleton_candidate_matrices.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v4_core_push_clearance.json"
TYPE_NAMES = (
    "retained_source_germ",
    "start_skew_lift",
    "first_exterior_ray",
    "staggered_height_bridge",
    "staggered_last_exterior_ray",
    "end_skew_lift",
)
CORE_F_TYPES = {1, 2, 4, 5}
PUSH_F_TYPES = {1, 2, 4}
STAGGER_TYPES = {2, 3, 4}
DIRECT_PAIRS = {(0, 0), (0, 1), (1, 0)}
END_PAIRS = {(2, 5), (4, 5), (5, 5)}


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def bucket_candidates(first_group, second_group, key):
    buckets = {}
    for record in second_group:
        buckets.setdefault(key(record), []).append(record)
    for first in first_group:
        yield from ((first, second) for second in buckets.get(key(first), ()))


def check_pair(pair, core, push, broad):
    core_type, push_type = pair
    if core_type in CORE_F_TYPES and push_type in PUSH_F_TYPES:
        candidates = bucket_candidates(
            core[core_type],
            push[push_type],
            lambda record: functional(record["vertices"][0]),
        )
        invariant = "equal exact directed core/push functional"
    elif core_type in STAGGER_TYPES and push_type in STAGGER_TYPES:
        candidates = bucket_candidates(
            core[core_type], push[push_type], lambda record: record["interface"]
        )
        invariant = "same-interface staggered directed corner"
    elif pair in DIRECT_PAIRS:
        candidates = direct_candidates(core[core_type], push[push_type])
        invariant = "outward-rounded 3D AABB then GMP"
    else:
        raise AssertionError(f"unclassified v4 directed pair {pair}")
    reduced = exact = 0
    for first, second in candidates:
        reduced += 1
        exact += 1
        if segment_intersects(first["vertices"], second["vertices"]):
            raise AssertionError(
                f"v4 core/push collision: core {first['interface']}/{core_type}, push {second['interface']}/{push_type}"
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


def build():
    collars = json.loads(COLLARS.read_text())
    matrices = json.loads(MATRICES.read_text())
    if matrices["outer_collars_v4_receipt_sha256"] != collars["sha256"]:
        raise AssertionError("v4 matrices are stale")
    core, push = load(collars)
    counts = matrices["directed_core_push_matrix"]
    matrix_pairs = {
        (
            TYPE_NAMES.index(name.split("/")[0].removeprefix("core:")),
            TYPE_NAMES.index(name.split("/")[1].removeprefix("push:")),
        )
        for name in counts
    }
    standard_pairs = matrix_pairs - END_PAIRS
    standard = []
    for pair in sorted(standard_pairs):
        name = f"core:{TYPE_NAMES[pair[0]]}/push:{TYPE_NAMES[pair[1]]}"
        standard.append(check_pair(pair, core, push, counts[name]))
    aliases = {
        "core:first_exterior_ray/push:end_skew_lift": counts[
            "core:first_exterior_ray/push:end_skew_lift"
        ],
        "core:last_exterior_ray/push:end_skew_lift": counts[
            "core:staggered_last_exterior_ray/push:end_skew_lift"
        ],
        "core:end_skew_lift/push:end_skew_lift": counts[
            "core:end_skew_lift/push:end_skew_lift"
        ],
    }
    end_result = check_push_end_intervals(core, push, aliases)
    covered = {result["pair"] for result in standard} | {
        "core:first_exterior_ray/push:end_skew_lift",
        "core:staggered_last_exterior_ray/push:end_skew_lift",
        "core:end_skew_lift/push:end_skew_lift",
    }
    if covered != set(counts):
        raise AssertionError("v4 directed proof does not consume the complete matrix")
    result = {
        "schema": "t73_x_m1_outer_collar_v4_core_push_clearance/v1",
        "outer_collars_v4_receipt_sha256": collars["sha256"],
        "v4_one_skeleton_matrices_sha256": matrices["sha256"],
        "core_segment_count": sum(len(group) for group in core.values()),
        "push_segment_count": sum(len(group) for group in push.values()),
        "standard_directed_type_pair_results": standard,
        "push_end_lift_interval_result": end_result,
        "covered_directed_type_pair_count": len(covered),
        "broad_aabb_candidate_count": sum(counts.values()),
        "exact_segment_check_count": sum(
            item["exact_segment_checks"] for item in standard
        )
        + end_result["dual_direct_gmp_checks"],
        "intersection_count": 0,
        "global_core_push_clearance": True,
        "former_v3_collision_pair_covered_by_same_interface_gmp": True,
        "verdict": "PASS_X_M1_OUTER_COLLAR_V4_CORE_PUSH_CLEARANCE",
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
        raise AssertionError("v4 core/push clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "type_pairs": result["covered_directed_type_pair_count"],
                "broad": result["broad_aabb_candidate_count"],
                "exact": result["exact_segment_check_count"],
                "intersections": result["intersection_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
