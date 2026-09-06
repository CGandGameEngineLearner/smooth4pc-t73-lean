#!/usr/bin/env python3
"""Bind the saved full GMP collar core/push clearance run for daily checks."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_outer_collar_core_push_clearance.json"
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_receipt.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_core_push_clearance_verification.json"
VERIFIER = ROOT / "scripts/build_t73_x_m1_outer_collar_core_push_clearance.py"


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


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
        "core/core": (2_235_099, 4),
        "push/push": (2_231_193, 4),
        "core/push": (4_469_079, 0),
    }
    if (
        result["verdict"] != "PASS_X_M1_OUTER_COLLAR_CORE_PUSH_CLEARANCE"
        or result["failing_pairs"]
    ):
        raise AssertionError("saved collar core/push full result failed")
    for pair, (checks, incidences) in expected.items():
        value = result["pair_results"][pair]
        if (
            value["exact_segment_checks"] != checks
            or value["permitted_incidences"] != incidences
            or value["intersections"]
        ):
            raise AssertionError(f"saved collar core/push result changed: {pair}")


def build_from_saved():
    result = json.loads(DATA.read_text())
    collars = json.loads(COLLARS.read_text())
    check_result(result)
    receipt = {
        "schema": "t73_x_m1_outer_collar_core_push_clearance_verification/v1",
        "clearance_artifact_content_sha256": file_sha(DATA),
        "clearance_artifact_payload_sha256": result["sha256"],
        "outer_collar_receipt_sha256": collars["sha256"],
        "outer_collar_cache_sha256": collars["cache_sha256"],
        "full_verifier_path": VERIFIER.relative_to(ROOT).as_posix(),
        "full_verifier_sha256": file_sha(VERIFIER),
        "full_result": result,
        "status": "PASS_SAVED_FULL_GMP_RUN",
        "verdict": result["verdict"],
    }
    receipt["sha256"] = canonical_sha(receipt)
    return receipt


def check_files(receipt):
    expected = build_from_saved()
    if receipt != expected:
        raise AssertionError("collar core/push saved verification binding changed")
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
    print(f"T73_X_M1_OUTER_COLLAR_CORE_PUSH={receipt['verdict']}")
    print(f"SHA256={receipt['sha256']}")


if __name__ == "__main__":
    main()
