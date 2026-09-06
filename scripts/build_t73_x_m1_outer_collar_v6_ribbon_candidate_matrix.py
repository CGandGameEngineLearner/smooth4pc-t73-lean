#!/usr/bin/env python3
"""Build the V6 ribbon matrix after complete one-skeleton clearance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v4_ribbon_candidate_matrix import (
    build as build_versioned,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v6_receipt.json"
ONE_SKELETON = ROOT / "audit/t73_x_m1_outer_collar_v6_one_skeleton_clearance.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v6_ribbon_candidate_matrix.json"


def build():
    return build_versioned(COLLARS, ONE_SKELETON, "v6")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("v6 ribbon candidate matrix is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "rectangles": result.get("rectangle_count"),
                "local_stars": result.get("local_star_count"),
                "broad": result.get("expanded_3d_aabb_rectangle_pair_count"),
                "nonincident": result.get("nonincident_candidate_count"),
                "type_pairs": result.get("nonempty_nonincident_type_pair_count"),
                "clearance": result.get("clearance_status"),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
