#!/usr/bin/env python3
"""Persist/check the complete GMP stub/band ribbon clearance."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "audit/t73_x_m1_stub_band_ribbon_exact_candidates.json"
OUTPUT = ROOT / "audit/t73_x_m1_stub_band_ribbon_clearance_verification.json"
BUILDER = ROOT / "scripts/build_t73_x_m1_stub_band_ribbon_exact_candidates.py"
VERIFIER = ROOT / "scripts/verify_t73_x_m1_stub_band_ribbon_clearance_gmp.py"


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


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


def load_verifier():
    spec = importlib.util.spec_from_file_location("stub_band_gmp", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bindings():
    candidates = json.loads(CANDIDATES.read_text())
    return {
        "candidate_receipt_sha256": candidates["sha256"],
        "candidate_stream_sha256": file_sha(resolve(candidates["candidate_path"])),
        "candidate_builder_sha256": file_sha(BUILDER),
        "gmp_verifier_sha256": file_sha(VERIFIER),
    }


def check_result(result):
    expected = {
        "verdict": "PASS_STUB_BAND_RIBBON_EXACT_CLEARANCE",
        "exact_rectangle_checks": 2_656_225,
        "shared_vertex_triangle_incidences": 18_156,
        "adjacent_rectangle_triangle_incidences": 1_517,
        "intersections": 0,
    }
    if result != expected:
        raise AssertionError(f"stub/band exact result changed: {result}")


def build_full():
    result = load_verifier().verify()
    check_result(result)
    receipt = {
        "schema": "t73_x_m1_stub_band_ribbon_clearance_verification/v1",
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
        raise AssertionError("stub/band verification receipt hash changed")
    if any(receipt.get(key) != value for key, value in bindings().items()):
        raise AssertionError("stub/band verification binding changed")
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
    print(f"T73_X_M1_STUB_BAND_RIBBONS={receipt['verdict']}")
    print(f"SHA256={receipt['sha256']}")


if __name__ == "__main__":
    main()
