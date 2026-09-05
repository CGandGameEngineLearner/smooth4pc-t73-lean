#!/usr/bin/env python3
"""Save the missing geometric primitives needed to construct kappa_AR."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "geometry/t73_ar_source_coordinate_atlas.json"
OUTPUT = ROOT / "geometry/t73_actual_ar_kirby_construction_request.json"


def canonical_sha(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def build():
    atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
    missing = atlas["missing_transitions_in_order"]
    if any(item["status"] != "OPEN" for item in missing):
        raise AssertionError("AR atlas transition status unexpectedly changed")
    result = {
        "schema": "t73_actual_ar_kirby_construction_request/v1",
        "atlas_sha256": atlas["sha256"],
        "source_bindings": atlas["source_bindings"],
        "required_chart_transitions": missing[:3],
        "required_band_geometry": {
            "t_band_count": 6,
            "x_band_count": 1513,
            "per_band": [
                "two_oriented_boundary_edges",
                "attachment_parameters_on_source_and_target_cores",
                "embedded_parallel_replacement_arc",
                "framing_normal_trivialization",
                "spliced_cyclic_successor",
            ],
        },
        "required_post_cancellation_components": [
            "m_2", "m_3", "r_xy", "r_yz", "r_zx", "dotted_y", "dotted_z"
        ],
        "required_final_data": [
            "five_closed_rational_core_polylines",
            "five_closed_rational_framing_push_offs",
            "two_dotted_circle_closed_polylines",
            "one_generic_oriented_projection",
            "cut_and_surgery_quotient_pairings",
        ],
        "completion_status": "OPEN",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("AR Kirby construction request is stale")
    print("T73_AR_KIRBY_CONSTRUCTION_REQUEST=OPEN")
    print(f"SHA256={result['sha256']}")


if __name__ == "__main__":
    main()
