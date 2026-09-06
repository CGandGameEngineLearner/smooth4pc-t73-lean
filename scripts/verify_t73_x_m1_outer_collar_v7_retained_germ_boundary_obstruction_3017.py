#!/usr/bin/env python3
"""Independently verify the retained-germ framing boundary mismatch."""

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
DATA = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_retained_germ_boundary_obstruction_3017.json"
)
NORMAL = ROOT / "geometry/t73_x_m1_outer_collar_v7_normal_field_3017.json"
CORE = ROOT / "geometry/t73_x_m1_outer_collar_v7_explicit_core_detour_3017.json"


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    normal = json.loads(NORMAL.read_text())
    core = json.loads(CORE.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["normal_field_sha256"] != normal["sha256"]
        or data["explicit_core_detour_sha256"] != core["sha256"]
    ):
        raise AssertionError("retained-germ boundary obstruction bindings changed")
    fixed_edge = {point(vertex) for vertex in data["fixed_framing_edge"]}
    outer_edge = {point(vertex) for vertex in data["retained_outer_shared_edge"]}
    bridge = {point(vertex) for vertex in data["collar_germ_bridge_rectangle"]}
    if (
        len(fixed_edge) != 2
        or len(outer_edge) != 2
        or not (fixed_edge | outer_edge) <= bridge
    ):
        raise AssertionError("collar germ bridge boundary changed")
    core_states = [[point(vertex) for vertex in state] for state in core["states"]]
    push_states = [
        [point(vertex) for vertex in state] for state in normal["push_states"]
    ]
    matching = [
        index
        for index, (core_state, push_state) in enumerate(zip(core_states, push_states))
        if {core_state[0], push_state[0]} == fixed_edge
    ]
    mismatching = [index for index in range(22) if index not in matching]
    if (
        matching != data["matching_state_indices"]
        or mismatching != data["mismatching_state_indices"]
        or len({state[0] for state in core_states}) != 1
        or len({state[0] for state in push_states}) == 1
    ):
        raise AssertionError("independent retained-germ mismatch replay changed")
    if (
        data["literal_retained_framing_boundary_status"] != "REFUTED"
        or data["normal_field_internal_status"] != "RETAINED"
    ):
        raise AssertionError("retained-germ obstruction scope changed")
    return {
        "verdict": "REFUTED_X_M1_OUTER_COLLAR_V7_RETAINED_GERM_BOUNDARY_3017_INDEPENDENT",
        "retained_rectangle_index": data["retained_rectangle_index"],
        "matching_states": len(matching),
        "mismatching_states": len(mismatching),
        "mismatching_state_indices": mismatching,
        "fixed_core_germ_vertex": True,
        "fixed_push_germ_vertex": False,
        "normal_field_internal": "RETAINED",
        "literal_retained_framing_boundary": "REFUTED",
        "required_repair": data["required_repair"],
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
