#!/usr/bin/env python3
"""Save/check independent local verification of outer collars v4."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v4_receipt.json"
OUTPUT = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v4_verification.json"
BUILDER = ROOT / "scripts/build_t73_x_m1_framed_outer_interface_collars_v4.py"
VERIFIER = ROOT / "scripts/verify_t73_x_m1_framed_outer_interface_collars_v4.py"


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
    spec = importlib.util.spec_from_file_location("outer_collar_v4_verifier", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_result(result):
    expected = {
        "verdict": "PASS_X_M1_FRAMED_OUTER_INTERFACE_COLLARS_V4_FULL_LOCAL_CANDIDATE",
        "cache_sha_checked": True,
        "collars_reconstructed": 3026,
        "changed_end_exterior_vertices": 3026,
        "core_push_segments_each": 18156,
        "ribbon_triangles_reconstructed": 36312,
        "normal_transversality_checks": 18156,
        "end_exterior_height_offset": "1/2",
        "former_v3_collision_exact_rechecks": 1,
        "classification": "CANDIDATE_UNVERIFIED",
        "global_clearance": "OPEN",
        "ambient_support": "OPEN",
    }
    if result != expected:
        raise AssertionError(f"v4 outer collar result changed: {result}")


def build_full():
    data = json.loads(DATA.read_text())
    result = load_verifier().verify_full()
    check_result(result)
    receipt = {
        "schema": "t73_x_m1_framed_outer_interface_collars_v4_verification/v1",
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
        raise AssertionError("v4 outer collar verification binding changed")
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
    print(f"T73_X_M1_OUTER_COLLARS_V4={receipt['verdict']}")
    print(f"SHA256={receipt['sha256']}")


if __name__ == "__main__":
    main()
