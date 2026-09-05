#!/usr/bin/env python3
"""Record the missing local/global overlap transitions after x/m1 ejection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUBS = ROOT / "audit/t73_x_m1_ejected_splice_stubs_receipt.json"
MIDDLES = ROOT / "audit/t73_x_m1_ejected_middle_complements_receipt.json"
LANES = ROOT / "audit/t73_x_m1_ejected_band_lanes_receipt.json"
OUTPUT = ROOT / "audit/t73_x_m1_ejection_overlap_transition_gap.json"


def canonical_sha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def build():
    stubs = json.loads(STUBS.read_text(encoding="utf-8")); middles = json.loads(MIDDLES.read_text(encoding="utf-8")); lanes = json.loads(LANES.read_text(encoding="utf-8"))
    result = {
        "schema": "t73_x_m1_ejection_overlap_transition_gap/v1",
        "ejected_splice_stubs_receipt_sha256": stubs["sha256"],
        "ejected_middle_complements_receipt_sha256": middles["sha256"],
        "ejected_band_lanes_receipt_sha256": lanes["sha256"],
        "band_count": 1513,
        "interfaces_per_band": 2,
        "core_overlap_transition_count": 3026,
        "push_overlap_transition_count": 3026,
        "local_side_chart": "x_m1_cubical_product_target",
        "middle_side_chart": "mapping_torus_global_annulus_target",
        "extended_chart_transition_present": False,
        "complete_core_image_gluing": False,
        "complete_push_image_gluing": False,
        "completion_status": "X_M1_LOCAL_GLOBAL_EJECTION_OVERLAP_TRANSITIONS_OPEN",
        "required_repair": "construct disjoint framed mapping-cylinder germs at both ends of every parallel complement and verify compatibility with both ambient maps",
    }
    result["sha256"] = canonical_sha(result); return result


if __name__ == "__main__":
    result = build(); OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"); print(json.dumps(result, sort_keys=True))
