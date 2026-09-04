#!/usr/bin/env python3
"""Verify hemisphere movies against detector identities.

D(v A0) = D(v) and D(v A1) = 0 are required on actual sources.  The checker
does not flip actual_w2_lasagna_map from false to true.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPHERES = ROOT / "geometry" / "t73_actual_sphere_system.json"
OUTPUT = ROOT / "geometry" / "t73_actual_hemisphere_movies.json"
LEAN = ROOT / "Smooth4PC" / "LocalStabilization.lean"


def build(write: bool = False) -> dict[str, Any]:
    if not SPHERES.exists():
        raise AssertionError("geometry/t73_actual_sphere_system.json is missing")
    spheres = json.loads(SPHERES.read_text(encoding="utf-8"))
    if spheres.get("actual_w2_lasagna_map"):
        raise AssertionError("sphere system flipped actual_w2_lasagna_map without hemisphere movies")
    if not LEAN.is_file():
        raise AssertionError("LocalStabilization.lean is missing")
    movies = []
    for sphere in spheres["spheres"]:
        movies.append(
            {
                "sphere": sphere["name"],
                "A0_identity_on_detector": None,
                "A1_kills_detector": None,
                "status": "OPEN",
                "reason": "no actual ∂W2 hemisphere movie has been triangulated",
            }
        )
    result = {
        "schema": "t73_actual_hemisphere_movies/v1",
        "sphere_system_sha256": spheres["sha256"],
        "movies": movies,
        "detector_identities": {
            "D(v A0) = D(v)": "OPEN",
            "D(v A1) = 0": "OPEN",
        },
        "actual_w2_lasagna_map": False,
        "status": "OPEN",
    }
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.check or args.write:
        print("T73_HEMISPHERE_MOVIES=WRITTEN" if args.write else "T73_HEMISPHERE_MOVIES=CHECKED")
        print(f"STATUS={result['status']}")
        print(f"ACTUAL_W2_LASAGNA_MAP={result['actual_w2_lasagna_map']}")
        return
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
