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


def build(collars_path=COLLARS, matrices_path=MATRICES, version="v6"):
    collars = json.loads(collars_path.read_text())
    matrices = json.loads(matrices_path.read_text())
    core = build_core(collars_path, matrices_path, version)
    push = build_push(collars_path, matrices_path, version)
    mutual = build_mutual(collars_path, matrices_path, version)
    if (
        not core["global_core_clearance"]
        or not push["global_push_clearance"]
        or not mutual["global_core_push_clearance"]
    ):
        raise AssertionError("a V6 one-skeleton layer failed")
    result = {
        "schema": f"t73_x_m1_outer_collar_{version}_one_skeleton_clearance/v1",
        f"outer_collars_{version}_receipt_sha256": collars["sha256"],
        f"{version}_candidate_matrices_sha256": matrices["sha256"],
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
        "ribbon_clearance_status": f"OPEN_REBUILD_{version.upper()}_RIBBON_MATRIX",
        "verdict": f"PASS_X_M1_OUTER_COLLAR_{version.upper()}_ONE_SKELETON_CLEARANCE",
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
