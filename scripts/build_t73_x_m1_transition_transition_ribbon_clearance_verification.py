#!/usr/bin/env python3
"""Persist/check the full GMP transition/transition ribbon verification."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUSH = ROOT / "audit/t73_x_m1_negative_transition_push_paths_v3_receipt.json"
BROAD = ROOT / "audit/t73_x_m1_transition_ribbon_transition_candidates.json"
PARTITION = ROOT / "audit/t73_x_m1_transition_ribbon_exact_candidate_partition.json"
OUTPUT = ROOT / "audit/t73_x_m1_transition_transition_ribbon_clearance_verification.json"
PROBE = ROOT / "scripts/probe_t73_x_m1_transition_ribbon_global_clearance.py"
PARTITION_BUILDER = ROOT / "scripts/build_t73_x_m1_transition_ribbon_exact_candidate_partition.py"
VERIFIER = ROOT / "scripts/verify_t73_x_m1_transition_transition_ribbon_clearance_gmp.py"


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def load_verifier():
    spec = importlib.util.spec_from_file_location("transition_transition_gmp", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expected_result(result):
    expected = {
        "verdict": "PASS_TRANSITION_TRANSITION_RIBBON_EXACT_CLEARANCE",
        "constant_rectangle_checks": 5_865_390,
        "variable_triangle_checks": 88,
        "intersections": 0,
    }
    if result != expected:
        raise AssertionError(f"transition/transition result changed: {result}")


def file_bindings():
    push = json.loads(PUSH.read_text())
    broad = json.loads(BROAD.read_text())
    partition = json.loads(PARTITION.read_text())
    return {
        "transition_push_receipt_sha256": push["sha256"],
        "transition_push_cache_sha256": push["cache_sha256"],
        "broad_candidate_audit_content_sha256": file_sha(BROAD),
        "broad_candidate_stream_sha256": file_sha(resolve(broad["candidate_path"])),
        "exact_candidate_partition_sha256": partition["sha256"],
        "constant_candidate_stream_sha256": file_sha(resolve(partition["constant_candidate_path"])),
        "variable_candidate_stream_sha256": file_sha(resolve(partition["variable_candidate_path"])),
        "broad_phase_builder_sha256": file_sha(PROBE),
        "partition_builder_sha256": file_sha(PARTITION_BUILDER),
        "gmp_verifier_sha256": file_sha(VERIFIER),
    }


def build_full():
    result = load_verifier().verify()
    expected_result(result)
    receipt = {
        "schema": "t73_x_m1_transition_transition_ribbon_clearance_verification/v1",
        **file_bindings(),
        "broad_phase_builder_path": PROBE.relative_to(ROOT).as_posix(),
        "partition_builder_path": PARTITION_BUILDER.relative_to(ROOT).as_posix(),
        "gmp_verifier_path": VERIFIER.relative_to(ROOT).as_posix(),
        "full_result": result,
        "status": "PASS_FULL_GMP_EXACT_VERIFICATION",
        "verdict": result["verdict"],
    }
    receipt["sha256"] = canonical_sha(receipt)
    return receipt


def check_files(receipt):
    payload = {key: value for key, value in receipt.items() if key != "sha256"}
    if receipt.get("sha256") != canonical_sha(payload):
        raise AssertionError("transition/transition verification receipt hash changed")
    for key, value in file_bindings().items():
        if receipt.get(key) != value:
            raise AssertionError(f"transition/transition binding changed: {key}")
    expected_result(receipt["full_result"])
    if receipt["status"] != "PASS_FULL_GMP_EXACT_VERIFICATION":
        raise AssertionError("transition/transition full status changed")
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
    print(f"T73_X_M1_TRANSITION_TRANSITION_RIBBONS={receipt['verdict']}")
    print(f"SHA256={receipt['sha256']}")


if __name__ == "__main__":
    main()
