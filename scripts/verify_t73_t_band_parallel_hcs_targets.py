#!/usr/bin/env python3
"""Verify all six t-band targets are framed parallel copies of h_CS."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
INTERVALS = ROOT / "geometry/t73_t_band_attachment_intervals.json"
EXPECTED_LANES = [-25, -15, -5, 5, 15, 25]


def point(values):
    return tuple(Fraction(value) for value in values)


def verify() -> dict:
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    intervals = json.loads(INTERVALS.read_text(encoding="utf-8"))
    hcs = ar_link["components"]["h_CS"]
    center = point(hcs["section_point"])
    framing = point(hcs["framing_annulus"]["offset"])
    lane_coefficients = []
    for interval in intervals["intervals"]:
        target = point(interval["target_center"][:3])
        coefficients = []
        for axis in range(3):
            difference = target[axis] - center[axis]
            if framing[axis]:
                coefficients.append(difference / framing[axis])
            elif difference:
                raise AssertionError("t-band target leaves the h_CS framing line")
        if not coefficients or len(set(coefficients)) != 1:
            raise AssertionError("t-band target is not one framed parallel h_CS copy")
        lane_coefficients.append(int(coefficients[0]))
        target_start, target_end = (point(value) for value in interval["target_interval"])
        if target_start[:3] != target or target_end[:3] != target:
            raise AssertionError("t-band target interval leaves its framed h_CS copy")
    if lane_coefficients != EXPECTED_LANES:
        raise AssertionError("h_CS parallel-lane order changed")
    return {
        "verdict": "PASS_ACTUAL_HCS_PARALLEL_TARGET_BINDING",
        "lane_coefficients": lane_coefficients,
        "targets": 6,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
