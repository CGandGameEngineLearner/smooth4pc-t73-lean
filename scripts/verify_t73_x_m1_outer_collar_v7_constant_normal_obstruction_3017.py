#!/usr/bin/env python3
"""Independently replay all constant-normal push masks at transition 6."""

from __future__ import annotations

import gzip
import json
import sys
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_core_push_clearance import segment_intersects
from build_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import resolve
from verify_t73_candidate_t_band0_surface import triangles_intersect
from verify_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    canonical_sha,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_outer_collar_v7_constant_normal_obstruction_3017.json"
CORE = ROOT / "geometry/t73_x_m1_outer_collar_v7_explicit_core_detour_3017.json"
LOCAL = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def add(first, second):
    return tuple(a + b for a, b in zip(first, second))


def mask_cells(mask):
    cells = []
    for edge in range(5):
        if mask & (1 << edge):
            cells.extend(
                ([6 + edge, 6 + edge + 1, edge + 1], [6 + edge, edge + 1, edge])
            )
        else:
            cells.extend(
                ([edge, edge + 1, 6 + edge + 1], [edge, 6 + edge + 1, 6 + edge])
            )
    return cells


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    core = json.loads(CORE.read_text())
    local = json.loads(LOCAL.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["explicit_core_detour_sha256"] != core["sha256"]
        or data["local_trace_receipt_sha256"] != local["sha256"]
    ):
        raise AssertionError("constant-normal obstruction bindings changed")
    with gzip.open(resolve(local["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        record = next(
            json.loads(line)
            for line in source
            if json.loads(line)["interface_index"] == 3017
        )
    initial_core = [point(value) for value in record["initial_core_subdivision"]]
    initial_push = [
        point(value) for value in record["phase_one_push_initial_subdivision"]
    ]
    normal = tuple(initial_push[0][axis] - initial_core[0][axis] for axis in range(3))
    states = [[point(vertex) for vertex in state] for state in core["states"]]
    push_states = [[add(vertex, normal) for vertex in state] for state in states]
    state_checks = push_self_checks = 0
    for core_state, push_state in zip(states, push_states):
        core_segments = list(pairwise(core_state))
        push_segments = list(pairwise(push_state))
        for first in core_segments:
            for second in push_segments:
                state_checks += 1
                if segment_intersects(first, second):
                    raise AssertionError("independent constant-normal state collision")
        for first in range(5):
            for second in range(first + 2, 5):
                push_self_checks += 1
                if segment_intersects(push_segments[first], push_segments[second]):
                    raise AssertionError("independent push-state self collision")
    transition = core["transitions"][6]
    core_vertices = [point(value) for value in transition["spacetime_vertices"]]
    core_triangles = [
        tuple(core_vertices[index] for index in cell)
        for cell in transition["trace_triangles"]
    ]
    push_vertices = [(*add(vertex[:3], normal), vertex[3]) for vertex in core_vertices]
    invalid = []
    first_collisions = []
    checks = 0
    for mask in range(32):
        push_triangles = [
            tuple(push_vertices[index] for index in cell) for cell in mask_cells(mask)
        ]
        collision = None
        for core_index, first in enumerate(core_triangles):
            for push_index, second in enumerate(push_triangles):
                checks += 1
                if triangles_intersect(first, second):
                    collision = {
                        "push_diagonal_mask": mask,
                        "core_triangle": core_index,
                        "push_triangle": push_index,
                    }
                    break
            if collision:
                break
        if collision:
            invalid.append(mask)
            first_collisions.append(collision)
    if (
        state_checks != 550
        or push_self_checks != 132
        or invalid != list(range(32))
        or first_collisions != data["first_collision_by_mask"]
        or checks != data["exact_triangle_checks_until_first_collision"]
        or data["synchronous_constant_normal_trace_status"]
        != "REFUTED_ALL_32_DIAGONAL_MASKS"
    ):
        raise AssertionError("independent constant-normal replay changed")
    return {
        "verdict": "REFUTED_X_M1_OUTER_COLLAR_V7_CONSTANT_NORMAL_FRAMING_3017_INDEPENDENT",
        "states_replayed": len(states),
        "state_core_push_segment_checks": state_checks,
        "push_state_self_segment_checks": push_self_checks,
        "push_diagonal_masks_replayed": 32,
        "invalid_push_diagonal_masks": len(invalid),
        "canonical_collision": data["canonical_collision"],
        "required_repair": data["required_repair"],
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
