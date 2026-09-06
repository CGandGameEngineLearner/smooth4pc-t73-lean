#!/usr/bin/env python3
"""Independently verify the explicit ribbon-volume intersection witness."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from verify_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    canonical_sha,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_outer_collar_v7_ribbon_volume_obstruction_3017.json"
VOLUME = ROOT / "geometry/t73_x_m1_outer_collar_v7_ribbon_volume_3017.json"


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    volume = json.loads(VOLUME.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["ribbon_volume_sha256"] != volume["sha256"]
    ):
        raise AssertionError("ribbon-volume obstruction bindings changed")
    record = volume["transition_volumes"][data["transition_index"]]
    vertices = [point(value) for value in record["spacetime_vertices"]]
    first_ids, second_ids = (
        record["tetrahedra"][index] for index in data["tetrahedron_indices"]
    )
    if set(first_ids) & set(second_ids) or data["shared_vertex_count"] != 0:
        raise AssertionError("obstruction tetrahedra are not nonincident")
    first = [vertices[index] for index in first_ids]
    second = [vertices[index] for index in second_ids]
    first_weights = [Fraction(value) for value in data["first_barycentric_coordinates"]]
    second_weights = [
        Fraction(value) for value in data["second_barycentric_coordinates"]
    ]
    if (
        len(first_weights) != 4
        or len(second_weights) != 4
        or sum(first_weights) != 1
        or sum(second_weights) != 1
        or any(value < 0 for value in first_weights + second_weights)
    ):
        raise AssertionError("saved barycentric coordinates are infeasible")
    first_point = tuple(
        sum(first[index][axis] * first_weights[index] for index in range(4))
        for axis in range(4)
    )
    second_point = tuple(
        sum(second[index][axis] * second_weights[index] for index in range(4))
        for axis in range(4)
    )
    saved_point = point(data["intersection_point"])
    if first_point != second_point or first_point != saved_point:
        raise AssertionError("independent intersection point replay failed")
    if (
        data["normal_field_status"] != "RETAINED"
        or data["framed_one_skeleton_status"] != "RETAINED"
        or data["ribbon_volume_status"] != "CANDIDATE_REFUTED"
    ):
        raise AssertionError("ribbon-volume obstruction scope changed")
    return {
        "verdict": "REFUTED_X_M1_OUTER_COLLAR_V7_RIBBON_VOLUME_3017_INDEPENDENT",
        "transition_index": data["transition_index"],
        "tetrahedron_indices": data["tetrahedron_indices"],
        "shared_vertices": 0,
        "first_barycentric_sum": "1",
        "second_barycentric_sum": "1",
        "intersection_point_replayed": True,
        "normal_field": "RETAINED",
        "framed_one_skeleton": "RETAINED",
        "ribbon_volume": "CANDIDATE_REFUTED",
        "required_repair": data["required_repair"],
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
