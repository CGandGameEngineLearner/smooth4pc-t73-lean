#!/usr/bin/env python3
"""Verify the saved exact Rust repaired stub-cross clearance receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_repaired_stub_cross_clearance.json"
RUST = ROOT / "rust/t73_exact_cross_clearance/src/main.rs"
REPAIRED = ROOT / "audit/t73_x_m1_repaired_global_r3_middle_transition_cores_receipt.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def verify():
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("repaired stub-clearance payload SHA mismatch")
    repaired = json.loads(REPAIRED.read_text())
    if data["repaired_middle_transition_cores_receipt_sha256"] != repaired["sha256"]:
        raise AssertionError("repaired stub-clearance transition binding changed")
    if data["rust_source_sha256"] != hashlib.sha256(RUST.read_bytes()).hexdigest().upper():
        raise AssertionError("repaired stub-clearance Rust source changed")
    result = data["rust_result"]
    if result["verdict"] != "PASS_EXACT_STUB_CROSS_SYSTEM_CORE_CLEARANCE":
        raise AssertionError("saved Rust result is not PASS")
    if result["stub_band_columns"]["extra_intersections"] != 0:
        raise AssertionError("saved stub/band extras are nonzero")
    escapes = result["stub_transition_escape_germs"]
    if (escapes["escape_germs"], escapes["expected_endpoint_incidences"], escapes["extra_intersections"]) != (3026, 3026, 0):
        raise AssertionError("saved escape-germ clearance changed")
    lifts = result["stub_transition_lifts"]
    if lifts["modular_pairs"] != 32021132 or lifts["modular_survivors"] != 0:
        raise AssertionError("saved skew-lift modular clearance changed")
    return {
        "verdict": "PASS_X_M1_REPAIRED_STUB_CROSS_CLEARANCE",
        "old_collision_repaired": data["old_collision_repaired"],
        "escape_germs": escapes["escape_germs"],
        "escape_extra_intersections": 0,
        "skew_modular_pairs": lifts["modular_pairs"],
        "skew_modular_survivors": 0,
        "remaining_cross_system_checks": data["remaining_cross_system_checks"],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
