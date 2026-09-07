#!/usr/bin/env python3
"""Independently verify the replacement-volume barycentric witness."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_t73_x_m1_outer_collar_v7_replacement_ribbon_candidate_matrix as replacement_module
from verify_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    canonical_sha,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_relative_volume_replacement_obstruction_3017.json"
)
VOLUME = ROOT / "geometry/t73_x_m1_outer_collar_v7_relative_ribbon_volume_3017.json"
PRISM = ((0, 1, 2, 5), (0, 1, 4, 5), (0, 3, 4, 5))


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    volume = json.loads(VOLUME.read_text())
    receipt = json.loads(replacement_module.REPLACEMENTS.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["relative_ribbon_volume_sha256"] != volume["sha256"]
        or data["replacement_framing_receipt_sha256"] != receipt["sha256"]
    ):
        raise AssertionError("replacement obstruction bindings changed")
    rectangles = replacement_module.load_replacements(receipt)
    rectangle = rectangles[data["replacement_rectangle_index"]]
    transition = volume["transitions"][data["transition_index"]]
    start, end = (Fraction(value) for value in transition["global_time_interval"])
    vertices = [point(value) for value in transition["spacetime_vertices"]]
    normalized = [
        (*value[:3], (value[3] - start) / (end - start)) for value in vertices
    ]
    moving = [
        normalized[index]
        for index in transition["tetrahedra"][data["moving_tetrahedron_index"]]
    ]
    local = data["static_tetrahedron_index"]
    triangle = rectangle["triangles"][local // 3]
    static_vertices = [(*value, Fraction(0)) for value in triangle] + [
        (*value, Fraction(1)) for value in triangle
    ]
    static = [static_vertices[index] for index in PRISM[local % 3]]
    first_weights = [
        Fraction(value) for value in data["moving_barycentric_coordinates"]
    ]
    second_weights = [
        Fraction(value) for value in data["static_barycentric_coordinates"]
    ]
    if (
        set(moving) & set(static)
        or sum(first_weights) != 1
        or sum(second_weights) != 1
        or any(value < 0 for value in first_weights + second_weights)
    ):
        raise AssertionError("replacement obstruction barycentric data are invalid")
    first_point = tuple(
        sum(moving[index][axis] * first_weights[index] for index in range(4))
        for axis in range(4)
    )
    second_point = tuple(
        sum(static[index][axis] * second_weights[index] for index in range(4))
        for axis in range(4)
    )
    if first_point != second_point or first_point != point(data["intersection_point"]):
        raise AssertionError("replacement intersection point replay failed")
    if (
        rectangle["band"] != 1102
        or rectangle["segment"] != 4
        or rectangle["piece"] != "negative_band_lane"
        or data["replacement_external_volume_status"] != "CANDIDATE_REFUTED"
    ):
        raise AssertionError("replacement obstruction provenance changed")
    return {
        "verdict": "REFUTED_X_M1_OUTER_COLLAR_V7_RELATIVE_VOLUME_REPLACEMENT_3017_INDEPENDENT",
        "transition_index": data["transition_index"],
        "moving_tetrahedron_index": data["moving_tetrahedron_index"],
        "replacement_rectangle_index": data["replacement_rectangle_index"],
        "replacement_band": rectangle["band"],
        "replacement_segment": rectangle["segment"],
        "shared_vertices": 0,
        "moving_barycentric_sum": "1",
        "static_barycentric_sum": "1",
        "intersection_point_replayed": True,
        "retained_external_volume": "PROBE_PASS_592_EXACT_CANDIDATES_NOT_RECEIPTED",
        "replacement_external_volume": "CANDIDATE_REFUTED",
        "required_repair": data["required_repair"],
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
