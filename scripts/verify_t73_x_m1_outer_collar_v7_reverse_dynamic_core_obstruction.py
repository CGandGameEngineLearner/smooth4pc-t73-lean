#!/usr/bin/env python3
"""Independently validate the reverse dynamic core intersection segment."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v7_reverse_dynamic_core_candidate_matrix import (
    COLLARS,
    LOCAL,
    load_active,
    load_static,
)
from verify_t73_candidate_t_band0_surface import point_in_triangle
from verify_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    canonical_sha,
    intersects,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_dynamic_core_obstruction.json"
MATRIX = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_dynamic_core_candidate_matrix.json"
)
REVERSE_VOLUME = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_framed_isotopy_volume_receipt.json"
)
FORWARD_OBSTRUCTION = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_midpoint_obstruction.json"
)


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    local = json.loads(LOCAL.read_text())
    collars = json.loads(COLLARS.read_text())
    matrix = json.loads(MATRIX.read_text())
    volume = json.loads(REVERSE_VOLUME.read_text())
    forward = json.loads(FORWARD_OBSTRUCTION.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["reverse_dynamic_core_candidate_matrix_sha256"] != matrix["sha256"]
        or data["reverse_framed_volume_receipt_sha256"] != volume["sha256"]
        or data["forward_schedule_obstruction_sha256"] != forward["sha256"]
        or matrix["local_trace_receipt_sha256"] != local["sha256"]
        or matrix["outer_collars_v7_receipt_sha256"] != collars["sha256"]
    ):
        raise AssertionError("reverse dynamic obstruction bindings changed")
    active = load_active(local)
    sources, _finals = load_static(collars)
    active_triangle = next(
        triangle
        for interface, _type, local_index, triangle in active
        if interface == 2 and local_index == 0
    )
    source_triangle = next(
        triangle
        for interface, half, triangle in sources
        if interface == 0 and half == 1
    )
    endpoints = [
        tuple(Fraction(coordinate) for coordinate in value)
        for value in data["intersection_segment_endpoints"]
    ]
    if len(endpoints) != 2 or endpoints[0] == endpoints[1]:
        raise AssertionError("saved reverse intersection segment is degenerate")
    midpoint = tuple((a + b) / 2 for a, b in zip(*endpoints))
    for value in (*endpoints, midpoint):
        if not point_in_triangle(value, active_triangle) or not point_in_triangle(
            value, source_triangle
        ):
            raise AssertionError("saved reverse intersection segment leaves a triangle")
    times = {value[3] for value in endpoints}
    expected_time = Fraction(250000, 30205031068581)
    if times != {expected_time} or data["local_phase_one_time"] != str(expected_time):
        raise AssertionError("reverse intersection time changed")

    def source_segment(interface):
        spatial = {
            vertex[:3]
            for source_interface, _half, triangle in sources
            if source_interface == interface
            for vertex in triangle
        }
        if len(spatial) != 2:
            raise AssertionError("source vertical triangles do not recover one segment")
        return tuple(spatial)

    if intersects(source_segment(2), source_segment(0)):
        raise AssertionError("initial source segments are not independently separated")
    if (
        forward["active_interface"] != 2
        or forward["obstacle_interface"] != 0
        or forward["linear_spatial_interpolation_status"] != "REFUTED"
        or data["forward_order_0_before_2_status"] != "REFUTED_BY_FINAL_COLLISION"
        or data["reverse_order_2_before_0_status"] != "REFUTED_BY_SOURCE_COLLISION"
        or data["sequential_reordering_only_status"] != "REFUTED_FOR_INTERFACE_PAIR_0_2"
    ):
        raise AssertionError("two-order obstruction logic changed")
    return {
        "verdict": "REFUTED_X_M1_OUTER_COLLAR_V7_REVERSE_DYNAMIC_CORE_CLEARANCE_INDEPENDENT",
        "active_interface": 2,
        "source_interface": 0,
        "intersection_dimension": 1,
        "intersection_segment_endpoints_checked": 2,
        "intersection_midpoint_checked": True,
        "local_phase_one_time": str(expected_time),
        "static_source_segments_disjoint": True,
        "forward_order": "REFUTED",
        "reverse_order": "REFUTED",
        "sequential_reordering_only": "REFUTED",
        "required_repair": data["required_repair"],
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
