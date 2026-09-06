#!/usr/bin/env python3
"""Independently verify the affine-versus-atlas coverage gap."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_affine_core_atlas_coverage_gap.json"
AFFINE = ROOT / "geometry/t73_affine_s3_core_realization.json"
ATLAS = ROOT / "geometry/t73_complete_framed_dotted_atlas.json"
POST_X = ROOT / "geometry/t73_post_x_framed_cycle_assembly.json"
POST_X_RECEIPT = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"


def canonical_sha256(value: dict) -> str:
    unsigned = {key: item for key, item in value.items() if key != "sha256"}
    encoded = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def verify() -> dict:
    data = json.loads(DATA.read_text())
    affine = json.loads(AFFINE.read_text())
    atlas = json.loads(ATLAS.read_text())
    post_x = json.loads(POST_X.read_text())
    post_x_receipt = json.loads(POST_X_RECEIPT.read_text())
    if data["sha256"] != canonical_sha256(data):
        raise AssertionError("affine atlas coverage payload SHA mismatch")
    bindings = {
        "affine_core_realization_sha256": affine["sha256"],
        "complete_framed_dotted_atlas_sha256": atlas["sha256"],
        "post_x_framed_cycle_assembly_sha256": post_x["sha256"],
        "post_x_replacement_cells_receipt_sha256": post_x_receipt["sha256"],
    }
    if any(data[key] != value for key, value in bindings.items()):
        raise AssertionError("affine atlas coverage source binding changed")

    roles = Counter(
        role["kind"]
        for component in affine["framed_core_components"]
        for role in component["segment_roles"]
    )
    expected_roles = {
        "actual_central_connector": 7092,
        "affine_corridor": 14232,
        "dotted_passage": 1785,
    }
    if dict(sorted(roles.items())) != expected_roles:
        raise AssertionError("affine core role inventory changed")
    if (sum(roles.values()) != affine["framed_core_segment_count"]
            or affine["framed_core_segment_count"] != 23109):
        raise AssertionError("affine core segment total changed")

    blocks = [
        (component["component"], block)
        for component in post_x["components"]
        for block in component["blocks"]
        if block["kind"] == "post_x_framed_replacement_path"
    ]
    by_component = Counter()
    for name, block in blocks:
        if block["core_segment_count"] != 40 or block["push_segment_count"] != 40:
            raise AssertionError("post-x replacement cell size changed")
        by_component[name] += 40
    if len(blocks) != 1513 or sum(by_component.values()) != 60520:
        raise AssertionError("post-x replacement inventory changed")
    if dict(sorted(by_component.items())) != {
        "m_2": 10760,
        "m_3": 49600,
        "r_xy": 80,
        "r_zx": 80,
    }:
        raise AssertionError("post-x component inventory changed")
    if roles.get("post_x_framed_replacement_path", 0) != 0:
        raise AssertionError("expected affine omission no longer exists")
    if atlas["framed_core_segment_count"] != 80007 or atlas["framed_push_segment_count"] != 84383:
        raise AssertionError("complete atlas totals changed")
    if data["homology_model_actual_t73_status"] != "REFUTED_BY_ATLAS_COVERAGE_GAP":
        raise AssertionError("coverage gap scope was overstated")

    return {
        "verdict": "PASS_AFFINE_CORE_ATLAS_COVERAGE_GAP",
        "complete_atlas_core_segments": 80007,
        "affine_skeleton_core_segments": 23109,
        "omitted_post_x_replacement_core_segments": 60520,
        "omitted_post_x_replacement_push_segments": 60520,
        "affine_post_x_replacement_roles": 0,
        "actual_t73_affine_input": False,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
