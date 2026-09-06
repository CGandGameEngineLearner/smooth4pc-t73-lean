#!/usr/bin/env python3
"""Bind the saved full V7/retained ribbon cross-clearance run."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_outer_collar_v7_retained_ribbon_clearance.json"
MATRIX = ROOT / "audit/t73_x_m1_outer_collar_v7_retained_ribbon_candidate_matrix.json"
OUTPUT = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_retained_ribbon_clearance_verification.json"
)
VERIFIER = ROOT / "scripts/build_t73_x_m1_outer_collar_v7_retained_ribbon_clearance.py"


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def check_result(result):
    expected = {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_RETAINED_RIBBON_CLEARANCE",
        "collar_rectangle_count": 18156,
        "retained_rectangle_count": 4630,
        "aabb_and_float_outward_f_candidates": 825896,
        "source_framing_adjacencies": 3018,
        "exact_functional_interval_rejects": 0,
        "exact_bounds_rejects": 0,
        "exact_skew_axis_rejects": 825896,
        "exact_triangle_pair_checks": 0,
        "intersection_count": 0,
        "global_retained_cross_clearance": True,
    }
    if any(result.get(key) != value for key, value in expected.items()):
        raise AssertionError(f"saved V7/retained result changed: {result}")


def build_from_saved():
    result = json.loads(DATA.read_text())
    matrix = json.loads(MATRIX.read_text())
    check_result(result)
    if result["candidate_matrix_sha256"] != matrix["sha256"]:
        raise AssertionError("saved V7/retained result is stale relative to matrix")
    receipt = {
        "schema": "t73_x_m1_outer_collar_v7_retained_ribbon_clearance_verification/v1",
        "clearance_artifact_content_sha256": file_sha(DATA),
        "clearance_artifact_payload_sha256": result["sha256"],
        "candidate_matrix_sha256": matrix["sha256"],
        "full_verifier_path": VERIFIER.relative_to(ROOT).as_posix(),
        "full_verifier_sha256": file_sha(VERIFIER),
        "full_result": result,
        "status": "PASS_SAVED_FULL_EXACT_RUN",
        "verdict": result["verdict"],
    }
    receipt["sha256"] = canonical_sha(receipt)
    return receipt


def check_files(receipt):
    if receipt != build_from_saved():
        raise AssertionError("V7/retained verification binding changed")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check-files", action="store_true")
    args = parser.parse_args()
    receipt = build_from_saved() if args.write else json.loads(OUTPUT.read_text())
    if args.write:
        OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    check_files(receipt)
    print(f"T73_X_M1_V7_RETAINED_RIBBONS={receipt['verdict']}")
    print(f"SHA256={receipt['sha256']}")


if __name__ == "__main__":
    main()
