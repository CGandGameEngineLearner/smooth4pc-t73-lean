#!/usr/bin/env python3
"""Apply the directed exact semantic engine to V5 mutual clearance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v4_core_push_clearance import (
    build as build_versioned,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v5_receipt.json"
MATRICES = ROOT / "audit/t73_x_m1_outer_collar_v5_one_skeleton_candidate_matrices.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v5_core_push_clearance.json"


def build():
    return build_versioned(COLLARS, MATRICES, "v5")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("v5 core/push clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "type_pairs": result["covered_directed_type_pair_count"],
                "broad": result["broad_aabb_candidate_count"],
                "exact": result["exact_segment_check_count"],
                "intersections": result["intersection_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
