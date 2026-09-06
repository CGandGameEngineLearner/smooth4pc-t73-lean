#!/usr/bin/env python3
"""Save/check the full v3 transition-push verification receipt."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_negative_transition_push_paths_v3_receipt.json"
OUTPUT = ROOT / "audit/t73_x_m1_negative_transition_push_paths_v3_verification.json"
VERIFIER = ROOT / "scripts/verify_t73_x_m1_negative_transition_push_paths_v3.py"
BUILDER = ROOT / "scripts/build_t73_x_m1_negative_transition_push_paths_v3.py"


def sha_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def load_verifier():
    spec = importlib.util.spec_from_file_location("transition_push_verifier", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_full():
    data = json.loads(DATA.read_text())
    result = load_verifier().verify_full()
    receipt = {
        "schema": "t73_x_m1_negative_transition_push_paths_v3_verification/v1",
        "construction_receipt_sha256": data["sha256"],
        "cache_sha256": data["cache_sha256"],
        "builder_path": BUILDER.relative_to(ROOT).as_posix(),
        "builder_sha256": sha_file(BUILDER),
        "verifier_path": VERIFIER.relative_to(ROOT).as_posix(),
        "verifier_sha256": sha_file(VERIFIER),
        "full_result": result,
        "verdict": result["verdict"],
    }
    receipt["sha256"] = canonical_sha(receipt)
    return receipt


def check_files(receipt):
    payload = {key: value for key, value in receipt.items() if key != "sha256"}
    data = json.loads(DATA.read_text())
    if receipt.get("sha256") != canonical_sha(payload):
        raise AssertionError("transition push verification hash changed")
    expected = {
        "construction_receipt_sha256": data["sha256"],
        "cache_sha256": data["cache_sha256"],
        "builder_sha256": sha_file(BUILDER),
        "verifier_sha256": sha_file(VERIFIER),
        "verdict": "PASS_X_M1_NEGATIVE_TRANSITION_PUSH_PATHS_V3_FULL_LOCAL",
    }
    if any(receipt.get(key) != value for key, value in expected.items()):
        raise AssertionError("transition push verification binding changed")
    result = receipt["full_result"]
    if (result["transitions"], result["endpoint_push_port_matches"], result["global_clearance"]) != (3026, 6052, "OPEN"):
        raise AssertionError("transition push verification totals changed")
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
    print(f"T73_X_M1_TRANSITION_PUSH_V3={receipt['verdict']}")
    print(f"SHA256={receipt['sha256']}")


if __name__ == "__main__":
    main()
