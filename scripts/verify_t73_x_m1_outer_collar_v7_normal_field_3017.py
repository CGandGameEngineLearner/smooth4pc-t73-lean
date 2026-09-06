#!/usr/bin/env python3
"""Independently replay the interface-3017 normal-field path."""

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
from verify_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import rank_two
from verify_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    canonical_sha,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_outer_collar_v7_normal_field_3017.json"
CORE = ROOT / "geometry/t73_x_m1_outer_collar_v7_explicit_core_detour_3017.json"
LOCAL = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
OBSTRUCTION = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_constant_normal_obstruction_3017.json"
)


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def add(first, second):
    return tuple(a + b for a, b in zip(first, second))


def subtract(first, second):
    return tuple(a - b for a, b in zip(first, second))


def cross(first, second):
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def load_local_record(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            if record["interface_index"] == 3017:
                return record
    raise AssertionError("interface 3017 local trace is absent")


def expected_normals(source):
    scale = Fraction(1, 500)
    negative = -scale
    return [
        *([source] * 6),
        (Fraction(0), scale, Fraction(0)),
        *([(negative, negative, negative)] * 7),
        *([(negative, negative, scale)] * 2),
        (negative, negative, Fraction(0)),
        (scale, negative, scale),
        *([source] * 4),
    ]


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    core = json.loads(CORE.read_text())
    local = json.loads(LOCAL.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["explicit_core_detour_sha256"] != core["sha256"]
        or data["constant_normal_obstruction_sha256"] != obstruction["sha256"]
        or obstruction["local_trace_receipt_sha256"] != local["sha256"]
    ):
        raise AssertionError("normal-field bindings changed")
    record = load_local_record(local)
    initial_core = [point(value) for value in record["initial_core_subdivision"]]
    initial_push = [
        point(value) for value in record["phase_one_push_initial_subdivision"]
    ]
    source_normal = subtract(initial_push[0], initial_core[0])
    normals = expected_normals(source_normal)
    if data["normal_path"] != [[str(value) for value in normal] for normal in normals]:
        raise AssertionError("saved normal path changed")
    core_states = [[point(vertex) for vertex in state] for state in core["states"]]
    push_states = [[point(vertex) for vertex in state] for state in data["push_states"]]
    if any(
        push_states[state][vertex] != add(core_states[state][vertex], normals[state])
        for state in range(22)
        for vertex in range(6)
    ):
        raise AssertionError("saved push states are not the claimed normal translates")
    transversality = state_checks = push_state_self = 0
    for core_state, push_state, normal in zip(core_states, push_states, normals):
        core_segments = list(pairwise(core_state))
        push_segments = list(pairwise(push_state))
        for first in range(5):
            transversality += 1
            if cross(subtract(*reversed(core_segments[first])), normal) == (0, 0, 0):
                raise AssertionError("independent normal is tangent to a core segment")
            for second in range(5):
                state_checks += 1
                if segment_intersects(core_segments[first], push_segments[second]):
                    raise AssertionError("independent normal-field state collision")
        for first in range(5):
            for second in range(first + 2, 5):
                push_state_self += 1
                if segment_intersects(push_segments[first], push_segments[second]):
                    raise AssertionError("independent push-state self collision")
    push_rank = push_self = core_push = 0
    if len(data["push_transitions"]) != 21:
        raise AssertionError("normal-field transition count changed")
    for index, (core_transition, push_transition) in enumerate(
        zip(core["transitions"], data["push_transitions"])
    ):
        core_vertices = [
            point(value) for value in core_transition["spacetime_vertices"]
        ]
        push_vertices = [
            (
                *add(
                    vertex[:3],
                    normals[index] if vertex[3] == 0 else normals[index + 1],
                ),
                vertex[3],
            )
            for vertex in core_vertices
        ]
        cells = core_transition["trace_triangles"]
        if push_transition["trace_triangles"] != cells or push_transition[
            "push_spacetime_vertices"
        ] != [[str(coordinate) for coordinate in vertex] for vertex in push_vertices]:
            raise AssertionError("saved push transition changed")
        core_triangles = [
            tuple(core_vertices[vertex] for vertex in cell) for cell in cells
        ]
        push_triangles = [
            tuple(push_vertices[vertex] for vertex in cell) for cell in cells
        ]
        for triangle in push_triangles:
            push_rank += 1
            if not rank_two(triangle, (0, 1, 2)):
                raise AssertionError("independent push trace triangle degenerates")
        for first_edge in range(5):
            for second_edge in range(first_edge + 2, 5):
                for first in push_triangles[2 * first_edge : 2 * first_edge + 2]:
                    for second in push_triangles[2 * second_edge : 2 * second_edge + 2]:
                        push_self += 1
                        if triangles_intersect(first, second):
                            raise AssertionError(
                                "independent push trace self collision"
                            )
        for first in core_triangles:
            for second in push_triangles:
                core_push += 1
                if triangles_intersect(first, second):
                    raise AssertionError("independent core/push trace collision")
    actual = (
        transversality,
        state_checks,
        push_state_self,
        push_rank,
        push_self,
        core_push,
    )
    if actual != (110, 550, 132, 210, 504, 2100):
        raise AssertionError("independent normal-field totals changed")
    if (
        data["forbidden_internal_intersection_count"] != 0
        or not data["internal_framed_one_skeleton_clearance"]
        or data["static_one_skeleton_clearance_status"] != "OPEN"
        or data["ribbon_world_volume_status"] != "OPEN"
    ):
        raise AssertionError("normal-field scope changed")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_NORMAL_FIELD_3017_INTERNAL_INDEPENDENT",
        "states_replayed": 22,
        "transitions_replayed": 21,
        "framing_transversality_checks": transversality,
        "state_core_push_segment_checks": state_checks,
        "push_state_self_segment_checks": push_state_self,
        "push_trace_triangles": push_rank,
        "push_trace_self_triangle_checks": push_self,
        "core_push_trace_triangle_checks": core_push,
        "forbidden_internal_intersections": 0,
        "static_one_skeleton_clearance": "OPEN",
        "ribbon_world_volume": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
