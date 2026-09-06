#!/usr/bin/env python3
"""Save/check independent verification of the comprehensive V7 trace."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_v2_receipt.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_v2_verification.json"
BUILDER = ROOT / "scripts/build_t73_x_m1_outer_collar_v7_isotopy_trace_v2.py"
VERIFIER = ROOT / "scripts/verify_t73_x_m1_outer_collar_v7_isotopy_trace_v2.py"


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


def load_verifier():
    spec = importlib.util.spec_from_file_location("v7_trace_v2_verifier", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_result(result):
    expected = {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_COMPREHENSIVE_ISOTOPY_TRACE_V2_LOCAL",
        "cache_sha_checked": True,
        "traces_reconstructed": 3026,
        "complete_core_trace_triangles": 60520,
        "complete_push_trace_triangles": 60520,
        "r4_triangle_rank_checks": 121040,
        "phase_boundary_core_push_matches": 6052,
        "classification": "CANDIDATE_UNVERIFIED",
        "spacetime_global_embeddedness": "OPEN",
        "ambient_support": "OPEN",
    }
    if result != expected:
        raise AssertionError(f"V7 comprehensive trace result changed: {result}")


def build_full():
    data = json.loads(DATA.read_text())
    result = load_verifier().verify_full()
    check_result(result)
    receipt = {
        "schema": "t73_x_m1_outer_collar_v7_isotopy_trace_v2_verification/v1",
        "construction_receipt_sha256": data["sha256"],
        "cache_sha256": data["cache_sha256"],
        "builder_path": BUILDER.relative_to(ROOT).as_posix(),
        "builder_sha256": file_sha(BUILDER),
        "verifier_path": VERIFIER.relative_to(ROOT).as_posix(),
        "verifier_sha256": file_sha(VERIFIER),
        "full_result": result,
        "verdict": result["verdict"],
    }
    receipt["sha256"] = canonical_sha(receipt)
    return receipt


def check_files(receipt):
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in receipt.items() if key != "sha256"}
    if (
        receipt.get("sha256") != canonical_sha(payload)
        or receipt.get("construction_receipt_sha256") != data["sha256"]
        or receipt.get("cache_sha256") != data["cache_sha256"]
        or receipt.get("builder_sha256") != file_sha(BUILDER)
        or receipt.get("verifier_sha256") != file_sha(VERIFIER)
    ):
        raise AssertionError("V7 comprehensive trace verification binding changed")
    check_result(receipt["full_result"])
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check-files", action="store_true")
    args = parser.parse_args()
    receipt = build_full() if args.write else json.loads(OUTPUT.read_text())
    if args.write:
        OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    check_files(receipt)
    print(f"T73_X_M1_V7_TRACE_V2={receipt['verdict']}")
    print(f"SHA256={receipt['sha256']}")


if __name__ == "__main__":
    main()
