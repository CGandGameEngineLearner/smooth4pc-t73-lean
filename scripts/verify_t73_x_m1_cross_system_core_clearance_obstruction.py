#!/usr/bin/env python3
"""Verify the persisted Rust exact cross-system collision obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_cross_system_core_clearance_obstruction.json"
SOURCE = ROOT / "rust/t73_exact_cross_clearance/src/main.rs"
LOCK = ROOT / "rust/t73_exact_cross_clearance/Cargo.lock"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def verify():
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("cross-system obstruction payload SHA mismatch")
    if data["rust_source_sha256"] != hashlib.sha256(SOURCE.read_bytes()).hexdigest().upper():
        raise AssertionError("cross-system obstruction Rust source changed")
    if data["rust_lock_sha256"] != hashlib.sha256(LOCK.read_bytes()).hexdigest().upper():
        raise AssertionError("cross-system obstruction Cargo lock changed")
    rust = data["rust_result"]
    if rust["stub_segments"] != 10582:
        raise AssertionError("Rust stub inventory changed")
    band = rust["stub_band_columns"]
    if (band["columns"], band["exact_line_candidates"], band["expected_endpoint_incidences"], band["extra_intersections"]) != (6052, 9750, 6052, 0):
        raise AssertionError("Rust stub/band clearance result changed")
    transition = rust["stub_transition_lifts"]
    if transition["modular_pairs"] != 32021132 or transition["extra_intersections_at_least"] != 1:
        raise AssertionError("Rust stub/transition obstruction totals changed")
    expected = {
        "transition": 0,
        "transition_band": 0,
        "transition_side": "first",
        "stub_band": 1,
        "stub_piece": "target_complement_first",
        "stub_segment": 1,
    }
    if transition["first_extra_intersection"] != expected:
        raise AssertionError("first exact cross-system collision changed")
    if data["complete_replacement_core_embedding_status"] != "OPEN_REPAIR_TRANSITION_SHELL_ESCAPE_GERMS":
        raise AssertionError("collision obstruction was overstated as an embedding")
    return {
        "verdict": "PASS_EXACT_CROSS_SYSTEM_COLLISION_OBSTRUCTION",
        "stub_band_extra_intersections": 0,
        "stub_transition_extra_intersections_at_least": 1,
        "first_collision": expected,
        "complete_replacement_core_embedding": False,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
