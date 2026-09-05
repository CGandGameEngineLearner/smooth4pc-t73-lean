#!/usr/bin/env python3
"""Persist one complete overlap-transition verification run."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from verify_t73_x_m1_ejection_overlap_transitions import RECEIPT, verify_full
ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts/verify_t73_x_m1_ejection_overlap_transitions.py"
OUTPUT = ROOT / "audit/t73_x_m1_ejection_overlap_transitions_verification.json"
def file_sha(path): return hashlib.sha256(path.read_bytes()).hexdigest().upper()
def canonical_sha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()
if __name__ == "__main__":
    construction = json.loads(RECEIPT.read_text(encoding="utf-8")); result = verify_full(check_cache_sha=True)
    if result["verdict"] != "PASS_X_M1_FRAMED_OVERLAP_TRANSITIONS_FULL": raise AssertionError("full overlap verification failed")
    receipt = {"schema": "t73_x_m1_ejection_overlap_transitions_verification/v1", "construction_receipt_sha256": construction["sha256"], "verifier_path": str(VERIFIER.relative_to(ROOT)).replace("\\", "/"), "verifier_sha256": file_sha(VERIFIER), "full_verifier_result": result, "verdict": result["verdict"]}
    receipt["sha256"] = canonical_sha(receipt); OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"); print(json.dumps(result, sort_keys=True))
