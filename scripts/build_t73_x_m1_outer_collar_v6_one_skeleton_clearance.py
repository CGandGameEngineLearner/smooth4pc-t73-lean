#!/usr/bin/env python3
"""Aggregate fresh V6 core, push and directed mutual exact clearances."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v4_core_clearance import build as build_core
from build_t73_x_m1_outer_collar_v4_core_push_clearance import (
    build as build_mutual,
)
from build_t73_x_m1_outer_collar_v4_push_clearance import build as build_push

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v6_receipt.json"
MATRICES = ROOT / "audit/t73_x_m1_outer_collar_v6_one_skeleton_candidate_matrices.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v6_one_skeleton_clearance.json"


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def build():
    collars = json.loads(COLLARS.read_text())
    matrices = json.loads(MATRICES.read_text())
    core = build_core(COLLARS, MATRICES, "v6")
    push = build_push(COLLARS, MATRICES, "v6")
    mutual = build_mutual(COLLARS, MATRICES, "v6")
    if (
        not core["global_core_clearance"]
        or not push["global_push_clearance"]
        or not mutual["global_core_push_clearance"]
    ):
        raise AssertionError("a V6 one-skeleton layer failed")
    result = {
        "schema": "t73_x_m1_outer_collar_v6_one_skeleton_clearance/v1",
        "outer_collars_v6_receipt_sha256": collars["sha256"],
        "v6_candidate_matrices_sha256": matrices["sha256"],
        "core_clearance": core,
        "push_clearance": push,
        "directed_core_push_clearance": mutual,
        "core_exact_segment_checks": core["exact_segment_check_count"],
        "push_exact_segment_checks": push["exact_segment_check_count"],
        "mutual_exact_segment_checks": mutual["exact_segment_check_count"],
        "intersection_count": core["intersection_count"]
        + push["intersection_count"]
        + mutual["intersection_count"],
        "globally_embedded_one_skeleton": True,
        "global_core_push_clearance": True,
        "ribbon_clearance_status": "OPEN_REBUILD_V6_RIBBON_MATRIX",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V6_ONE_SKELETON_CLEARANCE",
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
        raise AssertionError("v6 one-skeleton clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "core_exact": result["core_exact_segment_checks"],
                "push_exact": result["push_exact_segment_checks"],
                "mutual_exact": result["mutual_exact_segment_checks"],
                "intersections": result["intersection_count"],
                "ribbon": result["ribbon_clearance_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
