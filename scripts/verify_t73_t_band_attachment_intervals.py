#!/usr/bin/env python3
"""Independently verify the six candidate intervals against actual AR edges."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERVALS = ROOT / "geometry/t73_t_band_attachment_intervals.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def lies_on_segment(value, start, end) -> bool:
    direction = tuple(end[i] - start[i] for i in range(len(start)))
    delta = tuple(value[i] - start[i] for i in range(len(start)))
    axis = next((i for i, coordinate in enumerate(direction) if coordinate), None)
    if axis is None:
        return value == start
    parameter = delta[axis] / direction[axis]
    return 0 <= parameter <= 1 and all(delta[i] == parameter * direction[i] for i in range(len(start)))


def verify() -> dict:
    data = json.loads(INTERVALS.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    if data["completion_status"] != "VERIFIED_LOCATORS_WITH_CANDIDATE_INTERVALS":
        raise AssertionError("t-band interval status changed")
    for interval in data["intervals"]:
        core = [point(value) for value in ar_link["components"][interval["component"]]["core_polyline_T3xI"]]
        index = interval["source_core_vertex_index"]
        before, after = (point(value) for value in interval["source_interval"])
        center = core[index]
        if not lies_on_segment(before, center, core[index - 1]):
            raise AssertionError("source interval start left its actual core edge")
        if not lies_on_segment(after, center, core[index + 1]):
            raise AssertionError("source interval end left its actual core edge")
        if not lies_on_segment(center, before, after):
            raise AssertionError("source attachment is not one straight actual core interval")
        target_start, target_end = (point(value) for value in interval["target_interval"])
        target_center = point(interval["target_center"])
        if target_start[:3] != target_center[:3] or target_end[:3] != target_center[:3]:
            raise AssertionError("target interval left its parallel h_CS line")
        if not lies_on_segment(target_center, target_start, target_end):
            raise AssertionError("target center is not inside its attachment interval")
    return {"verdict": "PASS_T_INTERVAL_ACTUAL_EDGE_BINDING_CANDIDATE_WIDTH", "intervals": 6}


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
