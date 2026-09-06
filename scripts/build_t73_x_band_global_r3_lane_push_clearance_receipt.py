#!/usr/bin/env python3
"""Persist the full global x-band lane push/ribbon clearance replay."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from verify_t73_x_band_global_r3_lane_push_clearance import LANES, verify


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts/verify_t73_x_band_global_r3_lane_push_clearance.py"
OUTPUT = ROOT / "audit/t73_x_band_global_r3_lane_push_clearance.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def main():
    construction = json.loads(LANES.read_text())
    result = verify()
    receipt = {
        "schema": "t73_x_band_global_r3_lane_push_clearance/v1",
        "lane_push_paths_receipt_sha256": construction["sha256"],
        "lane_push_cache_sha256": construction["cache_sha256"],
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
