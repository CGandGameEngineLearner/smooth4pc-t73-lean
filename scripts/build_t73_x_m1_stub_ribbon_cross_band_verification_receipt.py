#!/usr/bin/env python3
"""Persist a full verification of global x-m1 stub ribbon clearance."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit/t73_x_m1_stub_ribbon_cross_band_clearance.json"
STUBS = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
OUTPUT = ROOT / "audit/t73_x_m1_stub_ribbon_cross_band_verification.json"
VERIFIER = ROOT / "scripts/verify_t73_x_m1_stub_ribbon_cross_band_clearance.py"
BUILDER = ROOT / "scripts/build_t73_x_m1_stub_ribbon_cross_band_clearance.py"


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_verifier():
    spec = importlib.util.spec_from_file_location("stub_ribbon_cross_verifier", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_result(result, artifact):
    expected = {
        "verdict": "PASS_X_M1_STUB_RIBBON_CROSS_BAND_CLEARANCE",
        "segments": 10582,
        "ribbons": 10582,
        "parallel_exact_candidates": 791,
        "minimum_clearance_in_ribbon_widths": "100000",
        "sha256": artifact["sha256"],
    }
    if any(result.get(key) != value for key, value in expected.items()):
        raise AssertionError("stub ribbon verification result changed")
    if result.get("nonparallel_exact_candidates", 0) <= 0:
        raise AssertionError("full nonparallel exact audit was not recorded")


def build_full():
    artifact = json.loads(ARTIFACT.read_text())
    stubs = json.loads(STUBS.read_text())
    result = load_verifier().verify(ARTIFACT)
    check_result(result, artifact)
    receipt = {
        "schema": "t73_x_m1_stub_ribbon_cross_band_verification/v1",
        "artifact_path": ARTIFACT.relative_to(ROOT).as_posix(),
        "artifact_content_sha256": file_sha(ARTIFACT),
        "artifact_payload_sha256": artifact["sha256"],
        "stub_paths_receipt_sha256": stubs["sha256"],
        "stub_cache_sha256": stubs["cache_sha256"],
        "verifier_path": VERIFIER.relative_to(ROOT).as_posix(),
        "verifier_sha256": file_sha(VERIFIER),
        "geometry_builder_path": BUILDER.relative_to(ROOT).as_posix(),
        "geometry_builder_sha256": file_sha(BUILDER),
        "result": result,
        "status": "PASS_FULL_EXACT_AND_ERROR_BOUNDED_VERIFICATION",
    }
    receipt["sha256"] = canonical_sha(receipt)
    return receipt


def check_files(receipt):
    payload = {key: value for key, value in receipt.items() if key != "sha256"}
    if receipt.get("sha256") != canonical_sha(payload):
        raise AssertionError("stub ribbon verification receipt hash is stale")
    artifact = json.loads(ARTIFACT.read_text())
    stubs = json.loads(STUBS.read_text())
    checks = {
        "artifact_path": ARTIFACT.relative_to(ROOT).as_posix(),
        "artifact_content_sha256": file_sha(ARTIFACT),
        "artifact_payload_sha256": artifact["sha256"],
        "stub_paths_receipt_sha256": stubs["sha256"],
        "stub_cache_sha256": stubs["cache_sha256"],
        "verifier_path": VERIFIER.relative_to(ROOT).as_posix(),
        "verifier_sha256": file_sha(VERIFIER),
        "geometry_builder_path": BUILDER.relative_to(ROOT).as_posix(),
        "geometry_builder_sha256": file_sha(BUILDER),
        "status": "PASS_FULL_EXACT_AND_ERROR_BOUNDED_VERIFICATION",
    }
    if any(receipt.get(key) != value for key, value in checks.items()):
        raise AssertionError("stub ribbon verification file binding changed")
    check_result(receipt.get("result", {}), artifact)
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check-files", action="store_true")
    args = parser.parse_args()
    if args.write:
        receipt = build_full()
        OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        receipt = json.loads(OUTPUT.read_text())
    check_files(receipt)
    print(f"T73_X_M1_STUB_RIBBON_GLOBAL={receipt['result']['verdict']}")
    print(f"SHA256={receipt['sha256']}")


if __name__ == "__main__":
    main()
