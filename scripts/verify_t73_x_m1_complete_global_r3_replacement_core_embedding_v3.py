#!/usr/bin/env python3
"""Verify complete coverage of all ten v3 core subsystem pairs."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_core_embedding_v3.json"
ASSEMBLY = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_cores_v3_receipt.json"
STUB_TRANSFER = ROOT / "audit/t73_x_m1_stub_r3_embeddedness_transfer.json"
BAND = ROOT / "audit/t73_x_band_global_r3_port_strip_clearance.json"
TRANSITIONS = ROOT / "audit/t73_x_m1_negative_global_r3_middle_transition_cores_v3_receipt.json"
MIDDLES = ROOT / "audit/t73_x_m1_middle_paths_r3_verification.json"
STUB_CROSS = ROOT / "audit/t73_x_m1_repaired_stub_cross_clearance.json"
TRANSITION_BAND = ROOT / "audit/t73_x_m1_negative_transition_band_clearance.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def verify():
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("v3 core-embedding payload SHA mismatch")
    sources = {
        "complete_v3_assembly_receipt_sha256": json.loads(ASSEMBLY.read_text())["sha256"],
        "stub_r3_embeddedness_transfer_sha256": json.loads(STUB_TRANSFER.read_text())["sha256"],
        "band_strip_clearance_sha256": json.loads(BAND.read_text())["sha256"],
        "negative_v3_transition_receipt_sha256": json.loads(TRANSITIONS.read_text())["sha256"],
        "middle_full_verification_sha256": json.loads(MIDDLES.read_text())["sha256"],
        "repaired_stub_cross_clearance_sha256": json.loads(STUB_CROSS.read_text())["sha256"],
        "negative_transition_band_clearance_sha256": json.loads(TRANSITION_BAND.read_text())["sha256"],
    }
    if any(data[key] != value for key, value in sources.items()):
        raise AssertionError("v3 core-embedding source binding changed")
    expected_pairs = {
        "stub/stub", "band/band", "transition/transition", "middle/middle",
        "stub/band", "stub/transition", "stub/middle", "band/transition",
        "band/middle", "transition/middle",
    }
    records = data["subsystem_pair_clearance"]
    if len(records) != 10 or {record["pair"] for record in records} != expected_pairs:
        raise AssertionError("v3 core-embedding pair coverage is incomplete")
    if any(record["status"] != "PASS" or not record["evidence"] for record in records):
        raise AssertionError("v3 core-embedding pair has no positive evidence")
    extrema = {
        name: tuple(Fraction(value) for value in interval)
        for name, interval in data["exact_x_extrema"].items()
    }
    if not extrema["stub_x"][1] < extrema["middle_x"][0]:
        raise AssertionError("stub/middle exact x intervals overlap")
    if not extrema["band_x"][1] < extrema["middle_x"][0]:
        raise AssertionError("band/middle exact x intervals overlap")
    stub_transfer = json.loads(STUB_TRANSFER.read_text())
    if not stub_transfer["stub_r3_pairwise_embeddedness"]:
        raise AssertionError("stub/stub transfer evidence is false")
    band = json.loads(BAND.read_text())["full_result"]
    if not band["globally_embedded_port_fixed_band_strips"]:
        raise AssertionError("band/band clearance evidence is false")
    stub_cross = json.loads(STUB_CROSS.read_text())["rust_result"]
    if (
        stub_cross["stub_band_columns"]["extra_intersections"] != 0
        or stub_cross["stub_transition_escape_germs"]["extra_intersections"] != 0
        or stub_cross["stub_transition_lifts"]["modular_survivors"] != 0
    ):
        raise AssertionError("stub cross-system evidence is false")
    transition_band = json.loads(TRANSITION_BAND.read_text())
    if transition_band["outward_rounded_xy_box_candidate_count"] != 0:
        raise AssertionError("transition/band conservative boxes overlap")
    if Fraction(transition_band["maximum_transition_non_shell_z"]) >= Fraction(
        transition_band["minimum_band_horizontal_z"]
    ):
        raise AssertionError("transition/band z intervals overlap")
    assembly = json.loads(ASSEMBLY.read_text())
    if (
        data["core_segment_count"] != assembly["core_segment_count"]
        or data["core_segment_count"] != 92284
        or data["replacement_path_count"] != assembly["record_count"]
        or data["replacement_path_count"] != 1513
    ):
        raise AssertionError("v3 core-embedding aggregate counts changed")
    if data["transition_middle_endpoint_matches"] != 3026:
        raise AssertionError("transition/middle endpoint evidence changed")
    if not data["complete_replacement_core_embedding"]:
        raise AssertionError("v3 complete replacement core embedding is false")
    if data["complete_push_paths_status"] != "OPEN":
        raise AssertionError("core embedding was overstated as complete framing")
    return {
        "verdict": "PASS_X_M1_COMPLETE_GLOBAL_R3_REPLACEMENT_CORE_EMBEDDING_V3",
        "replacement_paths": data["replacement_path_count"],
        "core_segments": data["core_segment_count"],
        "subsystem_pairs_verified": len(records),
        "complete_replacement_core_embedding": True,
        "complete_push_paths": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
