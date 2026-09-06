#!/usr/bin/env python3
"""Build the local framed-ribbon world-volume for interface 3017."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v2_ribbon_self_clearance import star_relation
from verify_t73_candidate_t_band0_surface import triangles_intersect
from verify_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import rank_two

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "geometry/t73_x_m1_outer_collar_v7_explicit_core_detour_3017.json"
NORMAL = ROOT / "geometry/t73_x_m1_outer_collar_v7_normal_field_3017.json"
STATIC = ROOT / "audit/t73_x_m1_outer_collar_v7_normal_field_static_clearance_3017.json"
OUTPUT = ROOT / "geometry/t73_x_m1_outer_collar_v7_ribbon_volume_3017.json"
CANONICAL_PRISM = ((0, 1, 2, 5), (0, 1, 4, 5), (0, 3, 4, 5))
REVERSED_PRISM = ((3, 4, 5, 2), (3, 4, 1, 2), (3, 0, 1, 2))


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def ribbon_cells():
    cells = []
    for edge in range(5):
        cells.extend(
            (
                (edge, edge + 1, 6 + edge + 1),
                (edge, 6 + edge + 1, 6 + edge),
            )
        )
    return cells


def determinant3(matrix):
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def rank_three(vertices, tetrahedron):
    origin = vertices[tetrahedron[0]]
    directions = [
        tuple(vertices[tetrahedron[row]][axis] - origin[axis] for axis in range(4))
        for row in (1, 2, 3)
    ]
    return any(
        determinant3([[directions[row][axis] for axis in columns] for row in range(3)])
        for columns in itertools.combinations(range(4), 3)
    )


def tetrahedral_faces(tetrahedra):
    faces = Counter()
    for tetrahedron in tetrahedra:
        for omitted in range(4):
            face = tuple(sorted(tetrahedron[:omitted] + tetrahedron[omitted + 1 :]))
            faces[face] += 1
    return faces


def map_trace_cells(cells, offset):
    return {
        tuple(
            sorted(
                index + offset if index < 6 else index - 6 + offset + 12
                for index in cell
            )
        )
        for cell in cells
    }


def build():
    core = json.loads(CORE.read_text())
    normal = json.loads(NORMAL.read_text())
    static = json.loads(STATIC.read_text())
    normal_payload = {key: value for key, value in normal.items() if key != "sha256"}
    static_payload = {key: value for key, value in static.items() if key != "sha256"}
    if (
        normal["sha256"] != canonical_sha(normal_payload)
        or static["sha256"] != canonical_sha(static_payload)
        or normal["explicit_core_detour_sha256"] != core["sha256"]
        or static["normal_field_sha256"] != normal["sha256"]
        or not static["global_framed_one_skeleton_clearance"]
    ):
        raise AssertionError("ribbon-volume inputs are stale or failed")
    core_states = [[point(vertex) for vertex in state] for state in core["states"]]
    push_states = [
        [point(vertex) for vertex in state] for state in normal["push_states"]
    ]
    state_cells = ribbon_cells()
    counts = Counter()
    star_counts = Counter()
    for core_state, push_state in zip(core_states, push_states):
        vertices = core_state + push_state
        triangles = [tuple(vertices[index] for index in cell) for cell in state_cells]
        for triangle in triangles:
            counts["state_rank"] += 1
            lifted = tuple((*vertex, Fraction(0)) for vertex in triangle)
            if not rank_two(lifted, (0, 1, 2)):
                raise AssertionError("ribbon-state triangle degenerates")
        rectangles = []
        for edge in range(5):
            quad = (
                core_state[edge],
                core_state[edge + 1],
                push_state[edge + 1],
                push_state[edge],
            )
            rectangles.append(
                {
                    "quad": quad,
                    "triangles": (triangles[2 * edge], triangles[2 * edge + 1]),
                }
            )
        for edge in range(4):
            shared = tuple(
                set(rectangles[edge]["quad"]) & set(rectangles[edge + 1]["quad"])
            )
            if len(shared) != 2:
                raise AssertionError("successive ribbon rectangles lack a framing edge")
            relation = star_relation(rectangles[edge], rectangles[edge + 1], shared)
            star_counts[relation] += 1
            if relation == "COPLANAR_SAME_SIDE_OVERLAP":
                raise AssertionError("ribbon-state local star folds")
        for first in range(5):
            for second in range(first + 2, 5):
                for first_triangle in triangles[2 * first : 2 * first + 2]:
                    for second_triangle in triangles[2 * second : 2 * second + 2]:
                        counts["state_nonincident"] += 1
                        lifted_first = tuple(
                            (*vertex, Fraction(0)) for vertex in first_triangle
                        )
                        lifted_second = tuple(
                            (*vertex, Fraction(0)) for vertex in second_triangle
                        )
                        if triangles_intersect(lifted_first, lifted_second):
                            raise AssertionError("ribbon state self-intersects")
    transition_records = []
    for transition, (core_record, push_record) in enumerate(
        zip(core["transitions"], normal["push_transitions"])
    ):
        start_vertices = core_states[transition] + push_states[transition]
        end_vertices = core_states[transition + 1] + push_states[transition + 1]
        vertices = [(*value, Fraction(0)) for value in start_vertices] + [
            (*value, Fraction(1)) for value in end_vertices
        ]
        prism_template = (
            REVERSED_PRISM
            if core_record["triangulation_mode"] == "TIME_REVERSE_OF_CANONICAL_BACKWARD"
            else CANONICAL_PRISM
        )
        tetrahedra = []
        for triangle in state_cells:
            local = [triangle[0], triangle[1], triangle[2]] + [
                12 + triangle[0],
                12 + triangle[1],
                12 + triangle[2],
            ]
            tetrahedra.extend(
                [local[index] for index in cell] for cell in prism_template
            )
        for tetrahedron in tetrahedra:
            counts["tetra_rank"] += 1
            if not rank_three(vertices, tetrahedron):
                raise AssertionError("ribbon world-volume tetrahedron degenerates")
        faces = tetrahedral_faces(tetrahedra)
        boundary = {face for face, multiplicity in faces.items() if multiplicity == 1}
        if any(multiplicity not in (1, 2) for multiplicity in faces.values()):
            raise AssertionError("ribbon world-volume face multiplicity changed")
        start_boundary = {tuple(sorted(cell)) for cell in state_cells}
        end_boundary = {
            tuple(sorted(12 + index for index in cell)) for cell in state_cells
        }
        core_boundary = map_trace_cells(core_record["trace_triangles"], 0)
        push_boundary = map_trace_cells(push_record["trace_triangles"], 6)
        declared = start_boundary | end_boundary | core_boundary | push_boundary
        if not declared <= boundary:
            raise AssertionError(
                "ribbon volume does not induce core/push trace boundary: "
                f"transition={transition} mode={core_record['triangulation_mode']} "
                f"missing={sorted(declared - boundary)}"
            )
        endpoint_boundary = boundary - declared
        endpoint_vertices = ({0, 6, 12, 18}, {5, 11, 17, 23})
        if (
            len(boundary) != 44
            or len(endpoint_boundary) != 4
            or any(
                not any(set(face) <= allowed for allowed in endpoint_vertices)
                for face in endpoint_boundary
            )
        ):
            raise AssertionError("ribbon volume endpoint boundary changed")
        internal_faces = sum(multiplicity == 2 for multiplicity in faces.values())
        if internal_faces != 38:
            raise AssertionError("ribbon volume internal face count changed")
        counts["boundary"] += len(boundary)
        counts["endpoint_boundary"] += len(endpoint_boundary)
        counts["internal_faces"] += internal_faces
        transition_records.append(
            {
                "transition_index": transition,
                "triangulation_mode": core_record["triangulation_mode"],
                "spacetime_vertices": [
                    [str(coordinate) for coordinate in vertex] for vertex in vertices
                ],
                "tetrahedra": tetrahedra,
                "boundary_triangle_count": len(boundary),
                "internal_face_pair_count": internal_faces,
            }
        )
    expected = (220, 528, 630, 924, 84, 798)
    actual = (
        counts["state_rank"],
        counts["state_nonincident"],
        counts["tetra_rank"],
        counts["boundary"],
        counts["endpoint_boundary"],
        counts["internal_faces"],
    )
    if actual != expected or sum(star_counts.values()) != 88:
        raise AssertionError(f"ribbon-volume totals changed: {actual}")
    result = {
        "schema": "t73_x_m1_outer_collar_v7_ribbon_volume/v1",
        "explicit_core_detour_sha256": core["sha256"],
        "normal_field_sha256": normal["sha256"],
        "normal_field_static_clearance_sha256": static["sha256"],
        "interface_index": 3017,
        "state_count": len(core_states),
        "state_ribbon_triangle_count": counts["state_rank"],
        "state_ribbon_triangle_rank_check_count": counts["state_rank"],
        "state_local_star_relation_counts": dict(sorted(star_counts.items())),
        "state_local_star_count": sum(star_counts.values()),
        "state_nonincident_triangle_check_count": counts["state_nonincident"],
        "transition_count": len(transition_records),
        "canonical_prism_template": [list(value) for value in CANONICAL_PRISM],
        "time_reversed_prism_template": [list(value) for value in REVERSED_PRISM],
        "transition_volumes": transition_records,
        "r4_tetrahedron_count": counts["tetra_rank"],
        "r4_tetrahedron_rank_check_count": counts["tetra_rank"],
        "boundary_triangle_count": counts["boundary"],
        "endpoint_boundary_triangle_count": counts["endpoint_boundary"],
        "internal_face_pair_count": counts["internal_faces"],
        "local_simplicial_volume_complete": True,
        "r4_volume_self_clearance_status": "OPEN",
        "static_ribbon_volume_clearance_status": "OPEN",
        "classification": "RATIONAL_RIBBON_VOLUME_CANDIDATE",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_RIBBON_VOLUME_3017_LOCAL",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("ribbon volume 3017 is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "states": result["state_count"],
                "state_triangles": result["state_ribbon_triangle_count"],
                "transitions": result["transition_count"],
                "tetrahedra": result["r4_tetrahedron_count"],
                "boundary": result["boundary_triangle_count"],
                "self_clearance": result["r4_volume_self_clearance_status"],
                "static_clearance": result["static_ribbon_volume_clearance_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
