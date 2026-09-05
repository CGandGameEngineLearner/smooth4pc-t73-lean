#!/usr/bin/env python3
"""Run full m1 tubular clearance once and write a hash-bound receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from verify_t73_m1_parallel_annulus_tubular_clearance import verify

ROOT = Path(__file__).resolve().parents[1]
FRAME = ROOT / "geometry/t73_m1_parallel_annulus_tubular_frame.json"
VERIFIER = ROOT / "scripts/verify_t73_m1_parallel_annulus_tubular_clearance.py"
OUTPUT = ROOT / "audit/t73_m1_parallel_annulus_tubular_clearance_receipt.json"


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def build():
    frame = json.loads(FRAME.read_text(encoding="utf-8")); result = verify()
    if result["verdict"] != "PASS_M1_PARALLEL_ANNULUS_NONINCIDENT_TETRAHEDRON_CLEARANCE":
        raise AssertionError("full m1 tubular clearance did not pass")
    receipt = {
        "schema": "t73_m1_parallel_annulus_tubular_clearance_receipt/v1",
        "tubular_frame_sha256": frame["sha256"],
        "verifier_path": str(VERIFIER.relative_to(ROOT)).replace("\\", "/"),
        "verifier_sha256": file_sha(VERIFIER),
        "full_verifier_result": result,
        "verdict": result["verdict"],
        "completion_status": "M1_PARALLEL_ANNULUS_EMBEDDED_TUBULAR_NEIGHBORHOOD_VERIFIED",
    }
    receipt["sha256"] = canonical_sha(receipt); return receipt


if __name__ == "__main__":
    receipt = build(); OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"); print(json.dumps(receipt["full_verifier_result"], sort_keys=True))
