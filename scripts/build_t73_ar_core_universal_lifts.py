#!/usr/bin/env python3
"""Lift wrapped T73 AR core polylines continuously to the T3 universal cover."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
OUTPUT = ROOT / "geometry/t73_ar_core_universal_lifts.json"
PERIOD = Fraction(4)


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def nearest_translate(value: Fraction, previous: Fraction) -> tuple[Fraction, int]:
    approximate = (previous - value) / PERIOD
    center = approximate.numerator // approximate.denominator
    candidates = [(abs(value + PERIOD * shift - previous), shift) for shift in range(center - 1, center + 3)]
    minimum = min(distance for distance, _ in candidates)
    minimizers = [shift for distance, shift in candidates if distance == minimum]
    if len(minimizers) != 1:
        raise AssertionError("universal-cover lift has a half-period ambiguity")
    shift = minimizers[0]
    return value + PERIOD * shift, shift


def lift_polyline(raw_points: list[list[str]]) -> dict[str, Any]:
    wrapped = [tuple(Fraction(value) for value in point) for point in raw_points]
    lifted = [wrapped[0]]
    offsets = [(0, 0, 0)]
    for raw in wrapped[1:]:
        previous = lifted[-1]
        spatial = [nearest_translate(raw[axis], previous[axis]) for axis in range(3)]
        lifted.append(tuple(value for value, _ in spatial) + (raw[3],))
        offsets.append(tuple(shift for _, shift in spatial))
    deck_displacement = tuple((lifted[-1][axis] - lifted[0][axis]) / PERIOD for axis in range(3))
    if any(value.denominator != 1 for value in deck_displacement):
        raise AssertionError("lift endpoint difference is not a deck translation")
    return {
        "wrapped_vertices": raw_points,
        "lifted_vertices": [[str(value) for value in point] for point in lifted],
        "deck_offsets": [list(offset) for offset in offsets],
        "closing_deck_translation": [int(value) for value in deck_displacement],
    }


def build() -> dict[str, Any]:
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    components = {
        name: lift_polyline(ar_link["components"][name]["core_polyline_T3xI"])
        for name in ("m_1", "m_2", "m_3")
    }
    expected_translations = {
        "m_1": [-1, 0, 1],
        "m_2": [269, 40, 0],
        "m_3": [1240, 189, 31],
    }
    if any(
        components[name]["closing_deck_translation"] != expected
        for name, expected in expected_translations.items()
    ):
        raise AssertionError("AR core deck translations do not equal the columns of A-I")
    result = {
        "schema": "t73_ar_core_universal_lifts/v1",
        "ar_link_sha256": ar_link["sha256"],
        "period": "4",
        "components": components,
        "deck_translation_matrix": [[-1, 269, 1240], [0, 40, 189], [1, 0, 31]],
        "deck_translation_identity": "columns equal A-I",
        "completion_status": "VERIFIED_CONTINUOUS_LIFTS",
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
        raise AssertionError("AR core universal lifts are stale")
    print("T73_AR_CORE_UNIVERSAL_LIFTS=VERIFIED_CONTINUOUS_LIFTS")


if __name__ == "__main__":
    main()
