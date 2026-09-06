#!/usr/bin/env python3
"""Run and persist the full connector/stub transition clearance replay."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from verify_t73_post_x_connector_stub_framing_transition_global_clearance import verify


ROOT = Path(__file__).resolve().parents[1]
CONSTRUCTION = ROOT / "audit/t73_post_x_connector_stub_framing_transitions_receipt.json"
LOCAL_VERIFICATION = ROOT / "audit/t73_post_x_connector_stub_framing_transitions_verification.json"
VERIFIER = ROOT / "scripts/verify_t73_post_x_connector_stub_framing_transition_global_clearance.py"
OUTPUT = ROOT / "audit/t73_post_x_connector_stub_framing_transition_global_clearance.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def main():
    construction = json.loads(CONSTRUCTION.read_text())
    local_verification = json.loads(LOCAL_VERIFICATION.read_text())
    result = verify()
    receipt = {
        "schema": "t73_post_x_connector_stub_framing_transition_global_clearance/v1",
        "construction_receipt_sha256": construction["sha256"],
        "local_verification_sha256": local_verification["sha256"],
        "transition_cache_sha256": construction["cache_sha256"],
        "verifier_path": str(VERIFIER.relative_to(ROOT)).replace("\\", "/"),
        "verifier_sha256": hashlib.sha256(VERIFIER.read_bytes()).hexdigest().upper(),
        "full_result": result,
        "verdict": result["verdict"],
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
