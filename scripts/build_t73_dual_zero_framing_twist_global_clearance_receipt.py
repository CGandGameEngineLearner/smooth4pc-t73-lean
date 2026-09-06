#!/usr/bin/env python3
"""Run the full twist-patch clearance verifier and save its receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from verify_t73_dual_zero_framing_twist_global_clearance import verify


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_dual_zero_framing_twist_ribbons.json"
VERIFIER = ROOT / "scripts/verify_t73_dual_zero_framing_twist_global_clearance.py"
OUTPUT = ROOT / "audit/t73_dual_zero_framing_twist_global_clearance.json"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def canonical_sha256(value: dict) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def main() -> None:
    data = json.loads(DATA.read_text())
    result = verify()
    receipt = {
        "schema": "t73_dual_zero_framing_twist_global_clearance/v1",
        "twist_ribbon_payload_sha256": data["sha256"],
        "verifier_path": str(VERIFIER.relative_to(ROOT)).replace("\\", "/"),
        "verifier_sha256": file_sha256(VERIFIER),
        "full_result": result,
        "verdict": result["verdict"],
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
