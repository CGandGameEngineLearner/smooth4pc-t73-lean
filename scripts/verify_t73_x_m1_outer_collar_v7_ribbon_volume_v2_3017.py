#!/usr/bin/env python3
"""Independently replay the midpoint-refined interface-3017 ribbon volume."""

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
from verify_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    canonical_sha,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_outer_collar_v7_ribbon_volume_v2_3017.json"
CORE = ROOT / "geometry/t73_x_m1_outer_collar_v7_explicit_core_detour_3017.json"
NORMAL = ROOT / "geometry/t73_x_m1_outer_collar_v7_normal_field_3017.json"
STATIC = ROOT / "audit/t73_x_m1_outer_collar_v7_normal_field_static_clearance_3017.json"
V1 = ROOT / "geometry/t73_x_m1_outer_collar_v7_ribbon_volume_3017.json"
OBSTRUCTION = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_ribbon_volume_obstruction_3017.json"
)
REPAIRS = {7: 3, 8: 4, 11: 4, 12: 3}
PERTURBATION = (Fraction(-1, 1_000_000),) * 3
CANONICAL = ((0, 1, 2, 5), (0, 1, 4, 5), (0, 3, 4, 5))
REVERSED = ((3, 4, 5, 2), (3, 4, 1, 2), (3, 0, 1, 2))


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def add(first, second):
    return tuple(a + b for a, b in zip(first, second))


def state_cells():
    return [
        cell
        for edge in range(5)
        for cell in (
            (edge, edge + 1, 7 + edge),
            (edge, 7 + edge, 6 + edge),
        )
    ]


def trace_cells(mode, complement=False):
    cells = []
    canonical = mode == "CANONICAL_FORWARD"
    use_canonical = canonical != complement
    for edge in range(5):
        if use_canonical:
            cells.extend(([edge, edge + 1, 7 + edge], [edge, 7 + edge, 6 + edge]))
        else:
            cells.extend(([6 + edge, 7 + edge, edge + 1], [6 + edge, edge + 1, edge]))
    return cells


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


def face_counts(tetrahedra):
    counts = Counter()
    for tetrahedron in tetrahedra:
        for omitted in range(4):
            counts[
                tuple(sorted(tetrahedron[:omitted] + tetrahedron[omitted + 1 :]))
            ] += 1
    return counts


def expected_states(core, normal):
    core_states = [[point(vertex) for vertex in state] for state in core["states"]]
    push_states = [
        [point(vertex) for vertex in state] for state in normal["push_states"]
    ]
    states = [(core_states[0], push_states[0], "original")]
    specs = []
    for transition, core_record in enumerate(core["transitions"]):
        mode = core_record["triangulation_mode"]
        if transition in REPAIRS:
            midpoint_core = [
                tuple((a + b) / 2 for a, b in zip(first, second))
                for first, second in zip(
                    core_states[transition], core_states[transition + 1]
                )
            ]
            vertex = REPAIRS[transition]
            midpoint_core[vertex] = add(midpoint_core[vertex], PERTURBATION)
            first_normal = point(normal["normal_path"][transition])
            second_normal = point(normal["normal_path"][transition + 1])
            midpoint_normal = tuple(
                (a + b) / 2 for a, b in zip(first_normal, second_normal)
            )
            midpoint_push = [add(value, midpoint_normal) for value in midpoint_core]
            states.append((midpoint_core, midpoint_push, "repair_midpoint"))
            specs.append((transition, "a", mode))
        states.append(
            (core_states[transition + 1], push_states[transition + 1], "original")
        )
        specs.append((transition, "b" if transition in REPAIRS else "full", mode))
    return states, specs


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    core = json.loads(CORE.read_text())
    normal = json.loads(NORMAL.read_text())
    static = json.loads(STATIC.read_text())
    v1 = json.loads(V1.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["explicit_core_detour_sha256"] != core["sha256"]
        or data["normal_field_sha256"] != normal["sha256"]
        or data["normal_field_static_clearance_sha256"] != static["sha256"]
        or data["refuted_v1_ribbon_volume_sha256"] != v1["sha256"]
        or data["v1_obstruction_sha256"] != obstruction["sha256"]
    ):
        raise AssertionError("ribbon-volume v2 bindings changed")
    states, specs = expected_states(core, normal)
    if len(data["states"]) != 26 or len(data["transitions"]) != 25:
        raise AssertionError("ribbon-volume v2 inventory changed")
    for index, (core_state, push_state, kind) in enumerate(states):
        saved = data["states"][index]
        if (
            saved["state_index"] != index
            or saved["global_time"] != str(Fraction(index, 25))
            or saved["provenance"]["kind"] != kind
            or saved["core_vertices"]
            != [[str(coordinate) for coordinate in vertex] for vertex in core_state]
            or saved["push_vertices"]
            != [[str(coordinate) for coordinate in vertex] for vertex in push_state]
        ):
            raise AssertionError("ribbon-volume v2 state changed")
    static_triangles = load_static(json.loads(COLLARS.read_text()))
    properties = rtree_index.Property()
    properties.dimension = len(FUNCTIONALS)
    tree = rtree_index.Index(
        (
            (index, functional_box(value[5]), None)
            for index, value in enumerate(static_triangles)
        ),
        properties=properties,
    )
    counts = Counter()
    for transition, (original, subtransition, mode) in enumerate(specs):
        saved = data["transitions"][transition]
        start_core, start_push, _ = states[transition]
        end_core, end_push, _ = states[transition + 1]
        start_time = Fraction(transition, 25)
        end_time = Fraction(transition + 1, 25)
        vertices = [(*value, start_time) for value in start_core + start_push] + [
            (*value, end_time) for value in end_core + end_push
        ]
        core_trace_cells = trace_cells(mode)
        push_trace_cells = trace_cells(mode, complement=True)
        core_map = [*range(6), *range(12, 18)]
        push_map = [*range(6, 12), *range(18, 24)]
        core_triangles = [
            tuple(vertices[core_map[index]] for index in cell)
            for cell in core_trace_cells
        ]
        push_triangles = [
            tuple(vertices[push_map[index]] for index in cell)
            for cell in push_trace_cells
        ]
        if (
            saved["original_transition"] != original
            or saved["subtransition"] != subtransition
            or saved["mode"] != mode
            or saved["global_time_interval"] != [str(start_time), str(end_time)]
            or saved["spacetime_vertices"]
            != [[str(coordinate) for coordinate in vertex] for vertex in vertices]
            or saved["core_trace_triangles"] != core_trace_cells
            or saved["push_trace_triangles"] != push_trace_cells
        ):
            raise AssertionError("ribbon-volume v2 trace changed")
        for first in core_triangles:
            for second in push_triangles:
                counts["core_push"] += 1
                if triangles_intersect(first, second):
                    raise AssertionError("independent v2 core/push trace collision")
        for strand, triangles in (("core", core_triangles), ("push", push_triangles)):
            for moving in triangles:
                for static_index in tree.intersection(functional_box(moving)):
                    counts[f"{strand}_static"] += 1
                    if triangles_intersect(moving, static_triangles[static_index][5]):
                        raise AssertionError("independent v2 static collision")
        template = (
            REVERSED if mode == "TIME_REVERSE_OF_CANONICAL_BACKWARD" else CANONICAL
        )
        tetrahedra = []
        for triangle in state_cells():
            local = list(triangle) + [12 + index for index in triangle]
            tetrahedra.extend([local[index] for index in cell] for cell in template)
        if saved["tetrahedra"] != tetrahedra:
            raise AssertionError("ribbon-volume v2 tetrahedra changed")
        geometric = [
            tuple(vertices[index] for index in tetrahedron)
            for tetrahedron in tetrahedra
        ]
        for tetrahedron in tetrahedra:
            counts["rank"] += 1
            if not rank_three(vertices, tetrahedron):
                raise AssertionError("independent v2 tetrahedron degenerates")
        for first, second in combinations(range(30), 2):
            if set(tetrahedra[first]) & set(tetrahedra[second]):
                continue
            counts["nonincident"] += 1
            if tetrahedra_intersect(geometric[first], geometric[second]):
                raise AssertionError("independent v2 tetrahedron self-intersection")
        incidence = face_counts(tetrahedra)
        boundary = sum(value == 1 for value in incidence.values())
        internal = sum(value == 2 for value in incidence.values())
        if boundary != 44 or internal != 38:
            raise AssertionError("independent v2 face incidence changed")
        counts["boundary"] += boundary
        counts["internal"] += internal
    expected = {
        "core_push": 2500,
        "core_static": 774,
        "push_static": 982,
        "rank": 750,
        "nonincident": 6700,
        "boundary": 1100,
        "internal": 950,
    }
    if counts != Counter(expected):
        raise AssertionError(f"independent v2 totals changed: {counts}")
    if (
        not data["internal_ribbon_volume_self_clearance"]
        or not data["static_one_skeleton_clearance"]
        or data["static_ribbon_volume_clearance_status"] != "OPEN"
    ):
        raise AssertionError("ribbon-volume v2 scope changed")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_RIBBON_VOLUME_V2_3017_SELF_CLEAR_INDEPENDENT",
        "states_reconstructed": 26,
        "transitions_reconstructed": 25,
        "repair_midpoints_reconstructed": 4,
        "core_push_trace_checks": counts["core_push"],
        "moving_core_static_checks": counts["core_static"],
        "moving_push_static_checks": counts["push_static"],
        "r4_tetrahedra": counts["rank"],
        "r4_nonincident_tetrahedron_checks": counts["nonincident"],
        "boundary_triangles": counts["boundary"],
        "internal_face_pairs": counts["internal"],
        "internal_ribbon_volume_self_clearance": True,
        "static_one_skeleton_clearance": True,
        "static_ribbon_volume_clearance": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
