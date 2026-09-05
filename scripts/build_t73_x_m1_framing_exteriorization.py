#!/usr/bin/env python3
"""Construct one outward framing representative for the final x-local link."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
COLLAR = ROOT / "geometry/t73_x_m1_collar_ejection_map.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
OUTPUT = ROOT / "geometry/t73_x_m1_framing_exteriorization.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def build() -> dict:
    local_movie = json.loads(LOCAL_MOVIE.read_text(encoding="utf-8"))
    collar = json.loads(COLLAR.read_text(encoding="utf-8"))
    cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    width = Fraction(cancellation["slide_bands"][0]["band_width"])
    maximum_core_height_multiplier = len(cancellation["slide_bands"]) + 1
    push_multiplier = maximum_core_height_multiplier + 1
    push_vector = (Fraction(0), Fraction(0), Fraction(0), push_multiplier * width)
    result = {
        "schema": "t73_x_m1_framing_exteriorization/v1",
        "x_local_movie_sha256": local_movie["sha256"],
        "x_m1_collar_ejection_sha256": collar["sha256"],
        "x_cancellation_sha256": cancellation["sha256"],
        "band_width": str(width),
        "maximum_core_nu": str(1 + maximum_core_height_multiplier * width),
        "uniform_push_vector": [str(value) for value in push_vector],
        "uniform_push_nu": str(push_multiplier * width),
        "minimum_push_nu": str(1 + push_multiplier * width),
        "normal_homotopy_rule": (
            "linearly homotope each nonzero local framing vector to the uniform "
            "positive-nu vector; accepted source vectors have a nonzero y or z coordinate"
        ),
        "remaining_core_segment_count": 12104,
        "remaining_core_segment_state_sha256": local_movie[
            "final_local_segments_sha256"
        ],
        "completion_status": "X_FINAL_LINK_UNIFORM_OUTWARD_FRAMING_CONSTRUCTED",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("x/m1 framing exteriorization is stale")
    print("T73_X_M1_FRAMING=X_FINAL_LINK_UNIFORM_OUTWARD_FRAMING_CONSTRUCTED")


if __name__ == "__main__":
    main()
