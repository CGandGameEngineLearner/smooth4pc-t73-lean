#!/usr/bin/env python3
"""Independently replay the fixed-germ relative ribbon volume 3017."""

from __future__ import annotations

import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v7_normal_field_static_clearance_3017 import (
    COLLARS,
    FUNCTIONALS,
    functional_box,
    load_static,
)
from t73_exact_simplex import tetrahedra_intersect
from verify_t73_candidate_t_band0_surface import triangles_intersect
from verify_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import rank_two
from verify_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    canonical_sha,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_outer_collar_v7_relative_ribbon_volume_3017.json"
BOUNDARY = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_retained_germ_boundary_obstruction_3017.json"
)


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def determinant(matrix):
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def rank_three(vertices, tetrahedron):
    origin = vertices[tetrahedron[0]]
    vectors = [
        tuple(vertices[tetrahedron[row]][axis] - origin[axis] for axis in range(4))
        for row in (1, 2, 3)
    ]
    return any(
        determinant([[vectors[row][axis] for axis in axes] for row in range(3)])
        for axes in combinations(range(4), 3)
    )


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    boundary = json.loads(BOUNDARY.read_text())
    collars = json.loads(COLLARS.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["retained_germ_boundary_obstruction_sha256"] != boundary["sha256"]
    ):
        raise AssertionError("relative ribbon-volume bindings changed")
    fixed_edge = {point(vertex) for vertex in boundary["fixed_framing_edge"]}
    states = data["states"]
    if len(states) != 23:
        raise AssertionError("relative ribbon-volume state count changed")
    for index, state in enumerate(states):
        core = [point(vertex) for vertex in state["core_vertices"]]
        push = [point(vertex) for vertex in state["push_vertices"]]
        if (
            state["global_time"] != str(Fraction(index, 22))
            or {
                core[0],
                push[0],
            }
            != fixed_edge
        ):
            raise AssertionError("relative ribbon-volume state boundary changed")
    repair = [
        state for state in states if state["provenance"]["kind"] == "repair_midpoint"
    ]
    if (
        len(repair) != 1
        or repair[0]["provenance"]["original_transition"] != 15
        or repair[0]["provenance"]["changed_vertex"] != 5
    ):
        raise AssertionError("relative ribbon-volume repair state changed")
    static = load_static(collars)
    properties = rtree_index.Property()
    properties.dimension = len(FUNCTIONALS)
    tree = rtree_index.Index(
        ((index, functional_box(value[5]), None) for index, value in enumerate(static)),
        properties=properties,
    )
    counts = Counter()
    if len(data["transitions"]) != 22:
        raise AssertionError("relative ribbon-volume transition count changed")
    for transition, record in enumerate(data["transitions"]):
        start, end = (Fraction(value) for value in record["global_time_interval"])
        if start != Fraction(transition, 22) or end != Fraction(transition + 1, 22):
            raise AssertionError("relative ribbon-volume time intervals changed")
        vertices = [point(value) for value in record["spacetime_vertices"]]
        core_map = [*range(6), *range(12, 18)]
        push_map = [*range(6, 12), *range(18, 24)]
        core_triangles = [
            tuple(vertices[core_map[index]] for index in cell)
            for cell in record["core_trace_triangles"]
        ]
        push_triangles = [
            tuple(vertices[push_map[index]] for index in cell)
            for cell in record["push_trace_triangles"]
        ]
        for triangle in core_triangles + push_triangles:
            counts["trace_rank"] += 1
            if not rank_two(triangle, (0, 1, 2)):
                raise AssertionError("relative ribbon trace triangle degenerates")
        for first in core_triangles:
            for second in push_triangles:
                counts["core_push"] += 1
                if triangles_intersect(first, second):
                    raise AssertionError("relative ribbon core/push collision")
        for strand, triangles in (("core", core_triangles), ("push", push_triangles)):
            for moving in triangles:
                for static_index in tree.intersection(functional_box(moving)):
                    counts[f"{strand}_static"] += 1
                    if triangles_intersect(moving, static[static_index][5]):
                        raise AssertionError("relative ribbon static collision")
        tetrahedra = record["tetrahedra"]
        geometric = [
            tuple(vertices[index] for index in tetrahedron)
            for tetrahedron in tetrahedra
        ]
        for tetrahedron in tetrahedra:
            counts["tetra_rank"] += 1
            if not rank_three(vertices, tetrahedron):
                raise AssertionError("relative ribbon tetrahedron degenerates")
        for first, second in combinations(range(30), 2):
            if set(tetrahedra[first]) & set(tetrahedra[second]):
                continue
            counts["nonincident"] += 1
            if tetrahedra_intersect(geometric[first], geometric[second]):
                raise AssertionError("relative ribbon tetrahedra self-intersect")
    expected = {
        "trace_rank": 440,
        "core_push": 2200,
        "core_static": 718,
        "push_static": 550,
        "tetra_rank": 660,
        "nonincident": 5896,
    }
    if counts != Counter(expected):
        raise AssertionError(f"independent relative volume totals changed: {counts}")
    if (
        not data["fixed_germ_boundary_all_states"]
        or data["forbidden_intersection_count"] != 0
        or not data["internal_ribbon_volume_self_clearance"]
        or not data["scheduled_static_one_skeleton_clearance"]
        or data["external_ribbon_volume_clearance_status"] != "OPEN"
    ):
        raise AssertionError("relative ribbon-volume scope changed")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_RELATIVE_RIBBON_VOLUME_3017_SELF_CLEAR_INDEPENDENT",
        "states_replayed": 23,
        "transitions_replayed": 22,
        "repair_midpoints_replayed": 1,
        "fixed_germ_boundary_all_states": True,
        "trace_triangle_rank_checks": counts["trace_rank"],
        "core_push_trace_checks": counts["core_push"],
        "moving_core_static_checks": counts["core_static"],
        "moving_push_static_checks": counts["push_static"],
        "r4_tetrahedra": counts["tetra_rank"],
        "r4_nonincident_tetrahedron_checks": counts["nonincident"],
        "forbidden_intersections": 0,
        "external_ribbon_volume_clearance": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
