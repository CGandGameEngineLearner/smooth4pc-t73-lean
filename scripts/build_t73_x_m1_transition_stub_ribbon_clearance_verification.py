#!/usr/bin/env python3
"""Persist/check full GMP transition/stub ribbon clearance."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUSH = ROOT / "audit/t73_x_m1_negative_transition_push_paths_v3_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
BROAD = ROOT / "audit/t73_x_m1_transition_ribbon_stub_candidates.json"
CANDIDATES = ROOT / "audit/t73_x_m1_transition_stub_ribbon_exact_candidates.json"
OUTPUT = ROOT / "audit/t73_x_m1_transition_stub_ribbon_clearance_verification.json"
VERIFIER = ROOT / "scripts/verify_t73_x_m1_transition_stub_ribbon_clearance_gmp.py"
BUILDER = ROOT / "scripts/build_t73_x_m1_transition_stub_ribbon_exact_candidates.py"


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def sha_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def load_verifier():
    spec = importlib.util.spec_from_file_location("transition_stub_gmp", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bindings():
    push, stubs, broad, candidates = (json.loads(path.read_text()) for path in (PUSH, STUBS, BROAD, CANDIDATES))
    return {
        "transition_push_receipt_sha256": push["sha256"],
        "stub_push_receipt_sha256": stubs["sha256"],
        "broad_audit_content_sha256": sha_file(BROAD),
        "broad_candidate_stream_sha256": sha_file(resolve(broad["candidate_path"])),
        "exact_candidate_partition_sha256": candidates["sha256"],
        "exact_candidate_stream_sha256": sha_file(resolve(candidates["candidate_path"])),
        "candidate_builder_sha256": sha_file(BUILDER),
        "gmp_verifier_sha256": sha_file(VERIFIER),
    }


def check_result(result):
    expected = {"verdict": "PASS_TRANSITION_STUB_RIBBON_EXACT_CLEARANCE", "exact_rectangle_checks": 2_287_656, "permitted_port_triangle_pairs": 2, "intersections": 0}
    if result != expected:
        raise AssertionError(f"transition/stub result changed: {result}")


def build_full():
    result = load_verifier().verify()
    check_result(result)
    receipt = {
        "schema": "t73_x_m1_transition_stub_ribbon_clearance_verification/v1",
        **bindings(),
        "candidate_builder_path": BUILDER.relative_to(ROOT).as_posix(),
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
        raise AssertionError("transition/stub verification receipt hash changed")
    if any(receipt.get(key) != value for key, value in bindings().items()):
        raise AssertionError("transition/stub verification file binding changed")
    check_result(receipt["full_result"])
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
    print(f"T73_X_M1_TRANSITION_STUB_RIBBONS={receipt['verdict']}")
    print(f"SHA256={receipt['sha256']}")


if __name__ == "__main__":
    main()
