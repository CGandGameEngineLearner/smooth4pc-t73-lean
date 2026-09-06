#!/usr/bin/env python3
"""Apply exact ruled-rectangle clearance to V7 collars."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v5_ribbon_clearance import (
    build as build_versioned,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
MATRIX = ROOT / "audit/t73_x_m1_outer_collar_v7_ribbon_candidate_matrix.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v7_ribbon_clearance.json"


def build():
    return build_versioned(COLLARS, MATRIX, "v7")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("v7 ribbon clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "collision": result.get("collision"),
                "type_pairs": result.get("covered_nonincident_type_pair_count"),
                "broad": result.get("broad_aabb_nonincident_candidate_count"),
                "f_overlaps": result.get("global_functional_interval_overlap_count"),
                "exact_triangles": result.get("exact_triangle_pair_check_count"),
                "intersections": result.get("intersection_count"),
            },
            sort_keys=True,
        )
    )
    if result["verdict"].startswith("REFUTED"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
