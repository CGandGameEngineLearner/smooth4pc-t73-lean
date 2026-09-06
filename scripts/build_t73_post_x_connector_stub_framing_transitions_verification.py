#!/usr/bin/env python3
"""Persist full verification of all connector/stub framing transitions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from verify_t73_post_x_connector_stub_framing_transitions import DATA, verify


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts/verify_t73_post_x_connector_stub_framing_transitions.py"
OUTPUT = ROOT / "audit/t73_post_x_connector_stub_framing_transitions_verification.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def main():
    receipt = json.loads(DATA.read_text())
    result = verify(check_cache_sha=True)
    record = {
        "schema": "t73_post_x_connector_stub_framing_transitions_verification/v1",
        "construction_receipt_sha256": receipt["sha256"],
        "cache_sha256": receipt["cache_sha256"],
        "verifier_path": str(VERIFIER.relative_to(ROOT)).replace("\\", "/"),
        "verifier_sha256": hashlib.sha256(VERIFIER.read_bytes()).hexdigest().upper(),
        "full_result": result,
        "verdict": result["verdict"],
    }
    record["sha256"] = canonical_sha256(record)
    OUTPUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    main()
