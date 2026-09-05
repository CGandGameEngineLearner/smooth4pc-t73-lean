#!/usr/bin/env python3
"""Run full ambient-ejection clearance and write its hash-bound receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from verify_t73_m1_parallel_annulus_ambient_ejection_clearance import verify

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_m1_parallel_annulus_ambient_ejection.json"
VERIFIER = ROOT / "scripts/verify_t73_m1_parallel_annulus_ambient_ejection_clearance.py"
OUTPUT = ROOT / "audit/t73_m1_parallel_annulus_ambient_ejection_receipt.json"


def file_sha(path): return hashlib.sha256(path.read_bytes()).hexdigest().upper()
def canonical_sha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def build():
    data = json.loads(DATA.read_text(encoding="utf-8")); result = verify()
    if result["verdict"] != "PASS_M1_PARALLEL_ANNULUS_AMBIENT_EJECTION_SUPPORT_CLEARANCE": raise AssertionError("ambient ejection clearance failed")
    receipt = {"schema": "t73_m1_parallel_annulus_ambient_ejection_receipt/v1", "ambient_ejection_sha256": data["sha256"], "verifier_path": str(VERIFIER.relative_to(ROOT)).replace("\\", "/"), "verifier_sha256": file_sha(VERIFIER), "full_verifier_result": result, "verdict": result["verdict"], "completion_status": "M1_PARALLEL_ANNULUS_COMPACTLY_SUPPORTED_AMBIENT_HOMEOMORPHISM_VERIFIED"}
    receipt["sha256"] = canonical_sha(receipt); return receipt


if __name__ == "__main__":
    receipt = build(); OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"); print(json.dumps(receipt["full_verifier_result"], sort_keys=True))
