#!/usr/bin/env python3
"""Build all V5 one-skeleton matrices with the shared exact R-tree engine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v4_one_skeleton_candidate_matrices import (
    build as build_versioned,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v5_receipt.json"
LOCAL_VERIFY = (
    ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v5_verification.json"
)
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v5_one_skeleton_candidate_matrices.json"


def build():
    return build_versioned(COLLARS, LOCAL_VERIFY, "v5")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("v5 one-skeleton matrices are stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "core": result["core_candidate_count"],
                "push": result["push_candidate_count"],
                "mutual": result["directed_core_push_candidate_count"],
                "type_pairs": [
                    result["core_nonempty_type_pair_count"],
                    result["push_nonempty_type_pair_count"],
                    result["directed_core_push_nonempty_type_pair_count"],
                ],
                "clearance": result["clearance_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
