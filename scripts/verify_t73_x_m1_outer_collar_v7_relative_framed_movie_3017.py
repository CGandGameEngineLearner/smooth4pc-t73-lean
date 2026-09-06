#!/usr/bin/env python3
"""Independently replay the fixed-germ relative framed movie 3017."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_core_push_clearance import segment_intersects
from build_t73_x_m1_outer_collar_v7_normal_field_static_clearance_3017 import (
    COLLARS,
    FUNCTIONALS,
    functional_box,
    load_static,
)
from verify_t73_candidate_t_band0_surface import triangles_intersect
from verify_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import rank_two
from verify_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    canonical_sha,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_outer_collar_v7_relative_framed_movie_3017.json"
BOUNDARY = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_retained_germ_boundary_obstruction_3017.json"
)


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    boundary = json.loads(BOUNDARY.read_text())
    collars = json.loads(COLLARS.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["retained_germ_boundary_obstruction_sha256"] != boundary["sha256"]
        or data["outer_collars_v7_receipt_sha256"] != collars["sha256"]
    ):
        raise AssertionError("relative framed movie bindings changed")
    core_states = [[point(vertex) for vertex in state] for state in data["core_states"]]
    push_states = [[point(vertex) for vertex in state] for state in data["push_states"]]
    fixed_edge = {point(vertex) for vertex in data["fixed_germ_framing_edge"]}
    if any(
        {core_state[0], push_state[0]} != fixed_edge
        for core_state, push_state in zip(core_states, push_states)
    ):
        raise AssertionError("independent germ framing edge is not fixed")
    state_core_push = push_state_self = 0
    for core_state, push_state in zip(core_states, push_states):
        core_segments = list(pairwise(core_state))
        push_segments = list(pairwise(push_state))
        for first in core_segments:
            for second in push_segments:
                state_core_push += 1
                if segment_intersects(first, second):
                    raise AssertionError("independent relative state collision")
        for first in range(5):
            for second in range(first + 2, 5):
                push_state_self += 1
                if segment_intersects(push_segments[first], push_segments[second]):
                    raise AssertionError("independent relative push self collision")
    static = load_static(collars)
    properties = rtree_index.Property()
    properties.dimension = len(FUNCTIONALS)
    tree = rtree_index.Index(
        ((index, functional_box(value[5]), None) for index, value in enumerate(static)),
        properties=properties,
    )
    rank = core_self = push_self = core_push = core_static = push_static = 0
    for transition, record in enumerate(data["transitions"]):
        core_vertices = [point(value) for value in record["core_spacetime_vertices"]]
        push_vertices = [point(value) for value in record["push_spacetime_vertices"]]
        core_triangles = [
            tuple(core_vertices[index] for index in cell)
            for cell in record["core_trace_triangles"]
        ]
        push_triangles = [
            tuple(push_vertices[index] for index in cell)
            for cell in record["push_trace_triangles"]
        ]
        if (
            {value[:3] for value in core_vertices if value[3] == 0}
            != set(core_states[transition])
            or {value[:3] for value in core_vertices if value[3] == 1}
            != set(core_states[transition + 1])
            or {value[:3] for value in push_vertices if value[3] == 0}
            != set(push_states[transition])
            or {value[:3] for value in push_vertices if value[3] == 1}
            != set(push_states[transition + 1])
        ):
            raise AssertionError("relative trace boundary changed")
        for triangle in core_triangles + push_triangles:
            rank += 1
            if not rank_two(triangle, (0, 1, 2)):
                raise AssertionError("relative trace triangle degenerates")
        for first_edge in range(5):
            for second_edge in range(first_edge + 2, 5):
                for a in core_triangles[2 * first_edge : 2 * first_edge + 2]:
                    for b in core_triangles[2 * second_edge : 2 * second_edge + 2]:
                        core_self += 1
                        if triangles_intersect(a, b):
                            raise AssertionError("relative core trace self-intersects")
                for a in push_triangles[2 * first_edge : 2 * first_edge + 2]:
                    for b in push_triangles[2 * second_edge : 2 * second_edge + 2]:
                        push_self += 1
                        if triangles_intersect(a, b):
                            raise AssertionError("relative push trace self-intersects")
        for a in core_triangles:
            for b in push_triangles:
                core_push += 1
                if triangles_intersect(a, b):
                    raise AssertionError("relative core/push traces intersect")
        for strand, triangles in (("core", core_triangles), ("push", push_triangles)):
            for moving in triangles:
                for static_index in tree.intersection(functional_box(moving)):
                    if strand == "core":
                        core_static += 1
                    else:
                        push_static += 1
                    if triangles_intersect(moving, static[static_index][5]):
                        raise AssertionError("relative trace meets static one-skeleton")
    actual = (
        state_core_push,
        push_state_self,
        rank,
        core_self,
        push_self,
        core_push,
        core_static,
        push_static,
    )
    if actual != (550, 132, 420, 504, 504, 2100, 776, 784):
        raise AssertionError(f"independent relative framed totals changed: {actual}")
    if (
        not data["fixed_germ_boundary_all_states"]
        or data["forbidden_intersection_count"] != 0
        or not data["relative_framed_one_skeleton_clearance"]
        or data["ribbon_volume_status"] != "OPEN_REBUILD_WITH_NEW_CORE_MODES"
    ):
        raise AssertionError("relative framed movie scope changed")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_RELATIVE_FRAMED_MOVIE_3017_INDEPENDENT",
        "states_replayed": 22,
        "transitions_replayed": 21,
        "fixed_germ_boundary_all_states": True,
        "trace_triangle_rank_checks": rank,
        "core_trace_self_checks": core_self,
        "push_trace_self_checks": push_self,
        "core_push_trace_checks": core_push,
        "moving_core_static_checks": core_static,
        "moving_push_static_checks": push_static,
        "forbidden_intersections": 0,
        "ribbon_volume": "OPEN_REBUILD_WITH_NEW_CORE_MODES",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
