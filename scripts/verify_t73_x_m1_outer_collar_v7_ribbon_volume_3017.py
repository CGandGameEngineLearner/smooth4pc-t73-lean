#!/usr/bin/env python3
"""Independently replay the local interface-3017 ribbon world-volume."""

from __future__ import annotations

import itertools
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from verify_t73_candidate_t_band0_surface import triangles_intersect
from verify_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import rank_two
from verify_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    canonical_sha,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_outer_collar_v7_ribbon_volume_3017.json"
CORE = ROOT / "geometry/t73_x_m1_outer_collar_v7_explicit_core_detour_3017.json"
NORMAL = ROOT / "geometry/t73_x_m1_outer_collar_v7_normal_field_3017.json"
STATIC = ROOT / "audit/t73_x_m1_outer_collar_v7_normal_field_static_clearance_3017.json"
CANONICAL = ((0, 1, 2, 5), (0, 1, 4, 5), (0, 3, 4, 5))
REVERSED = ((3, 4, 5, 2), (3, 4, 1, 2), (3, 0, 1, 2))


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def state_cells():
    return [
        cell
        for edge in range(5)
        for cell in (
            (edge, edge + 1, 6 + edge + 1),
            (edge, 6 + edge + 1, 6 + edge),
        )
    ]


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
        determinant([[vectors[row][axis] for axis in columns] for row in range(3)])
        for columns in itertools.combinations(range(4), 3)
    )


def faces(tetrahedra):
    result = Counter()
    for tetrahedron in tetrahedra:
        for omitted in range(4):
            result[
                tuple(sorted(tetrahedron[:omitted] + tetrahedron[omitted + 1 :]))
            ] += 1
    return result


def expected_tetrahedra(mode):
    template = REVERSED if mode == "TIME_REVERSE_OF_CANONICAL_BACKWARD" else CANONICAL
    tetrahedra = []
    for triangle in state_cells():
        local = list(triangle) + [12 + index for index in triangle]
        tetrahedra.extend([local[index] for index in cell] for cell in template)
    return tetrahedra


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    core = json.loads(CORE.read_text())
    normal = json.loads(NORMAL.read_text())
    static = json.loads(STATIC.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["explicit_core_detour_sha256"] != core["sha256"]
        or data["normal_field_sha256"] != normal["sha256"]
        or data["normal_field_static_clearance_sha256"] != static["sha256"]
    ):
        raise AssertionError("ribbon-volume bindings changed")
    core_states = [[point(vertex) for vertex in state] for state in core["states"]]
    push_states = [
        [point(vertex) for vertex in state] for state in normal["push_states"]
    ]
    cells = state_cells()
    state_rank = state_nonincident = 0
    for core_state, push_state in zip(core_states, push_states):
        vertices = core_state + push_state
        triangles = [tuple(vertices[index] for index in cell) for cell in cells]
        for triangle in triangles:
            state_rank += 1
            lifted = tuple((*vertex, Fraction(0)) for vertex in triangle)
            if not rank_two(lifted, (0, 1, 2)):
                raise AssertionError("independent ribbon-state triangle degenerates")
        for first in range(5):
            for second in range(first + 2, 5):
                for a in triangles[2 * first : 2 * first + 2]:
                    for b in triangles[2 * second : 2 * second + 2]:
                        state_nonincident += 1
                        if triangles_intersect(
                            tuple((*vertex, Fraction(0)) for vertex in a),
                            tuple((*vertex, Fraction(0)) for vertex in b),
                        ):
                            raise AssertionError(
                                "independent ribbon state self-intersects"
                            )
    tetra_rank = boundary_count = endpoint_count = internal_count = 0
    for transition, saved in enumerate(data["transition_volumes"]):
        start = core_states[transition] + push_states[transition]
        end = core_states[transition + 1] + push_states[transition + 1]
        vertices = [(*value, Fraction(0)) for value in start] + [
            (*value, Fraction(1)) for value in end
        ]
        expected_vertices = [
            [str(coordinate) for coordinate in vertex] for vertex in vertices
        ]
        mode = core["transitions"][transition]["triangulation_mode"]
        tetrahedra = expected_tetrahedra(mode)
        if (
            saved["transition_index"] != transition
            or saved["triangulation_mode"] != mode
            or saved["spacetime_vertices"] != expected_vertices
            or saved["tetrahedra"] != tetrahedra
        ):
            raise AssertionError("saved ribbon transition changed")
        for tetrahedron in tetrahedra:
            tetra_rank += 1
            if not rank_three(vertices, tetrahedron):
                raise AssertionError("independent ribbon tetrahedron degenerates")
        incidence = faces(tetrahedra)
        boundary = {face for face, count in incidence.items() if count == 1}
        internal = sum(count == 2 for count in incidence.values())
        if (
            any(count not in (1, 2) for count in incidence.values())
            or len(boundary) != 44
            or internal != 38
        ):
            raise AssertionError("independent ribbon face incidence changed")
        endpoint_vertices = ({0, 6, 12, 18}, {5, 11, 17, 23})
        endpoint_faces = [
            face
            for face in boundary
            if any(set(face) <= allowed for allowed in endpoint_vertices)
        ]
        if len(endpoint_faces) != 4:
            raise AssertionError("independent endpoint boundary changed")
        boundary_count += len(boundary)
        endpoint_count += len(endpoint_faces)
        internal_count += internal
    if (
        state_rank,
        state_nonincident,
        tetra_rank,
        boundary_count,
        endpoint_count,
        internal_count,
    ) != (220, 528, 630, 924, 84, 798):
        raise AssertionError("independent ribbon-volume totals changed")
    if (
        not data["local_simplicial_volume_complete"]
        or data["r4_volume_self_clearance_status"] != "OPEN"
        or data["static_ribbon_volume_clearance_status"] != "OPEN"
    ):
        raise AssertionError("ribbon-volume scope changed")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_RIBBON_VOLUME_3017_LOCAL_INDEPENDENT",
        "states_replayed": 22,
        "state_ribbon_triangles": state_rank,
        "state_nonincident_triangle_checks": state_nonincident,
        "transitions_replayed": 21,
        "r4_tetrahedra": tetra_rank,
        "boundary_triangles": boundary_count,
        "endpoint_boundary_triangles": endpoint_count,
        "internal_face_pairs": internal_count,
        "r4_volume_self_clearance": "OPEN",
        "static_ribbon_volume_clearance": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
