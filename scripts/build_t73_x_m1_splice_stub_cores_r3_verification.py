#!/usr/bin/env python3
"""Persist the first full replay of all splice-stub core R3 maps."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from verify_t73_x_m1_splice_stub_cores_r3 import DATA, verify_full


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts/verify_t73_x_m1_splice_stub_cores_r3.py"
OUTPUT = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_verification.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def main():
    receipt = json.loads(DATA.read_text())
    result = verify_full(check_cache_sha=True)
    verification = {
        "schema": "t73_x_m1_splice_stub_cores_r3_verification/v1",
        "construction_receipt_sha256": receipt["sha256"],
        "cache_sha256": receipt["cache_sha256"],
        "verifier_path": str(VERIFIER.relative_to(ROOT)).replace("\\", "/"),
        "verifier_sha256": hashlib.sha256(VERIFIER.read_bytes()).hexdigest().upper(),
        "full_result": result,
        "verdict": result["verdict"],
    }
    verification["sha256"] = canonical_sha256(verification)
    OUTPUT.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n")
    print(json.dumps(verification, sort_keys=True))


if __name__ == "__main__":
    main()
