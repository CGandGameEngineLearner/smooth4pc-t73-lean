#!/usr/bin/env python3
"""Independently verify boundary-compatible t-band framing extensions."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTENSIONS = ROOT / "geometry/t73_t_band_framing_extensions.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def verify() -> dict:
    data = json.loads(EXTENSIONS.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    if data["completion_status"] != "CANDIDATE_INTERIOR_EXTENSIONS_BOUNDARY_VERIFIED":
        raise AssertionError("t-band framing extension status changed")
    if len(data["extensions"]) != 6:
        raise AssertionError("expected six t-band framing extensions")
    target = point([*ar_link["components"]["h_CS"]["framing_annulus"]["offset"], "0"])
    for extension in data["extensions"]:
        component = ar_link["components"][extension["component"]]
        width = Fraction(component["full_framing_annulus"]["width"])
        direction = point([*component["full_framing_annulus"]["product_direction"], "0"])
        source = tuple(width * value for value in direction)
        normals = [point(value) for value in extension["normal_field"]]
        centerline = [point(value) for value in extension["centerline"]]
        push_off = [point(value) for value in extension["push_off_centerline"]]
        if normals[0] != source or normals[-1] != target:
            raise AssertionError("framing extension boundary normal changed")
        if any(not any(normal) for normal in normals):
            raise AssertionError("framing extension has a zero normal")
        if len(centerline) != len(normals) or len(push_off) != len(normals):
            raise AssertionError("framing extension lengths disagree")
        for center, normal, pushed in zip(centerline, normals, push_off):
            if tuple(center[i] + normal[i] for i in range(4)) != pushed:
                raise AssertionError("framing push-off is not center plus normal")
    return {"verdict": "PASS_CANDIDATE_T_FRAMING_BOUNDARY_ONLY", "extensions": 6}


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
