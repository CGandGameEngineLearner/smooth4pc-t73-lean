#!/usr/bin/env python3
"""Build the midpoint-refined globally timed ribbon volume for interface 3017."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations, pairwise
from pathlib import Path

from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_core_push_clearance import segment_intersects
from build_t73_x_m1_outer_collar_v2_ribbon_self_clearance import star_relation
from build_t73_x_m1_outer_collar_v7_normal_field_3017 import complementary_cells
from build_t73_x_m1_outer_collar_v7_normal_field_static_clearance_3017 import (
    FUNCTIONALS,
    functional_box,
    load_static,
)
from build_t73_x_m1_outer_collar_v7_ribbon_volume_3017 import (
    CANONICAL_PRISM,
    REVERSED_PRISM,
    map_trace_cells,
    rank_three,
    ribbon_cells,
    tetrahedral_faces,
)
from t73_exact_simplex import tetrahedra_intersect
from verify_t73_candidate_t_band0_surface import triangles_intersect
from verify_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import rank_two

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "geometry/t73_x_m1_outer_collar_v7_explicit_core_detour_3017.json"
NORMAL = ROOT / "geometry/t73_x_m1_outer_collar_v7_normal_field_3017.json"
STATIC = ROOT / "audit/t73_x_m1_outer_collar_v7_normal_field_static_clearance_3017.json"
V1 = ROOT / "geometry/t73_x_m1_outer_collar_v7_ribbon_volume_3017.json"
OBSTRUCTION = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_ribbon_volume_obstruction_3017.json"
)
OUTPUT = ROOT / "geometry/t73_x_m1_outer_collar_v7_ribbon_volume_v2_3017.json"
REPAIRS = {7: 3, 8: 4, 11: 4, 12: 3}
PERTURBATION = (Fraction(-1, 1_000_000),) * 3


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


def core_cells(mode):
    cells = []
    for edge in range(5):
        if mode == "CANONICAL_FORWARD":
            cells.extend(
                ([edge, edge + 1, 6 + edge + 1], [edge, 6 + edge + 1, 6 + edge])
            )
        elif mode == "TIME_REVERSE_OF_CANONICAL_BACKWARD":
            cells.extend(
                ([6 + edge, 6 + edge + 1, edge + 1], [6 + edge, edge + 1, edge])
            )
        else:
            raise AssertionError("unknown core transition mode")
    return cells


def interpolate(first, second):
    return [
        tuple((a + b) / 2 for a, b in zip(left, right))
        for left, right in zip(first, second)
    ]


def expanded_movie(core_states, push_states, core, normal):
    states = [(core_states[0], push_states[0], {"kind": "original", "index": 0})]
    transitions = []
    for index, core_record in enumerate(core["transitions"]):
        mode = core_record["triangulation_mode"]
        if index in REPAIRS:
            midpoint_core = interpolate(core_states[index], core_states[index + 1])
            vertex = REPAIRS[index]
            midpoint_core[vertex] = add(midpoint_core[vertex], PERTURBATION)
            first_normal = point(normal["normal_path"][index])
            second_normal = point(normal["normal_path"][index + 1])
            midpoint_normal = tuple(
                (a + b) / 2 for a, b in zip(first_normal, second_normal)
            )
            midpoint_push = [add(value, midpoint_normal) for value in midpoint_core]
            states.append(
                (
                    midpoint_core,
                    midpoint_push,
                    {
                        "kind": "repair_midpoint",
                        "original_transition": index,
                        "changed_vertex": vertex,
                        "perturbation": [str(value) for value in PERTURBATION],
                    },
                )
            )
            transitions.append(
                {"original_transition": index, "subtransition": "a", "mode": mode}
            )
        states.append(
            (
                core_states[index + 1],
                push_states[index + 1],
                {"kind": "original", "index": index + 1},
            )
        )
        transitions.append(
            {
                "original_transition": index,
                "subtransition": "b" if index in REPAIRS else "full",
                "mode": mode,
            }
        )
    if len(states) != 26 or len(transitions) != 25:
        raise AssertionError("v2 expanded movie inventory changed")
    return states, transitions


def build():
    core = json.loads(CORE.read_text())
    normal = json.loads(NORMAL.read_text())
    static = json.loads(STATIC.read_text())
    v1 = json.loads(V1.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    if (
        normal["explicit_core_detour_sha256"] != core["sha256"]
        or static["normal_field_sha256"] != normal["sha256"]
        or v1["normal_field_static_clearance_sha256"] != static["sha256"]
        or obstruction["ribbon_volume_sha256"] != v1["sha256"]
        or obstruction["ribbon_volume_status"] != "CANDIDATE_REFUTED"
    ):
        raise AssertionError("ribbon-volume v2 inputs are stale or inconsistent")
    original_core = [[point(vertex) for vertex in state] for state in core["states"]]
    original_push = [
        [point(vertex) for vertex in state] for state in normal["push_states"]
    ]
    states, transition_specs = expanded_movie(
        original_core, original_push, core, normal
    )
    static_triangles = load_static(
        json.loads(
            (
                ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
            ).read_text()
        )
    )
    properties = rtree_index.Property()
    properties.dimension = len(FUNCTIONALS)
    static_tree = rtree_index.Index(
        (
            (index, functional_box(value[5]), None)
            for index, value in enumerate(static_triangles)
        ),
        properties=properties,
    )
    state_cells = ribbon_cells()
    counts = Counter()
    star_counts = Counter()
    state_records = []
    for state_index, (core_state, push_state, provenance) in enumerate(states):
        vertices = core_state + push_state
        triangles = [tuple(vertices[index] for index in cell) for cell in state_cells]
        core_segments = list(pairwise(core_state))
        push_segments = list(pairwise(push_state))
        normals = [subtract(push_state[index], core_state[index]) for index in range(6)]
        for edge in range(5):
            tangent = subtract(core_segments[edge][1], core_segments[edge][0])
            counts["state_transverse"] += 1
            if cross(tangent, normals[edge]) == (0, 0, 0) or cross(
                tangent, normals[edge + 1]
            ) == (0, 0, 0):
                raise AssertionError("v2 repair state framing is tangent")
            for push_segment in push_segments:
                counts["state_core_push"] += 1
                if segment_intersects(core_segments[edge], push_segment):
                    raise AssertionError("v2 repair state core meets push")
        for triangle in triangles:
            counts["state_rank"] += 1
            if not rank_two(
                tuple((*vertex, Fraction(0)) for vertex in triangle), (0, 1, 2)
            ):
                raise AssertionError("v2 repair state ribbon degenerates")
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
            relation = star_relation(rectangles[edge], rectangles[edge + 1], shared)
            star_counts[relation] += 1
            if relation == "COPLANAR_SAME_SIDE_OVERLAP":
                raise AssertionError("v2 repair state ribbon folds")
        for first in range(5):
            for second in range(first + 2, 5):
                for a in triangles[2 * first : 2 * first + 2]:
                    for b in triangles[2 * second : 2 * second + 2]:
                        counts["state_nonincident"] += 1
                        if triangles_intersect(
                            tuple((*vertex, Fraction(0)) for vertex in a),
                            tuple((*vertex, Fraction(0)) for vertex in b),
                        ):
                            raise AssertionError(
                                "v2 repair state ribbon self-intersects"
                            )
        state_records.append(
            {
                "state_index": state_index,
                "global_time": str(Fraction(state_index, 25)),
                "provenance": provenance,
                "core_vertices": [
                    [str(coordinate) for coordinate in vertex] for vertex in core_state
                ],
                "push_vertices": [
                    [str(coordinate) for coordinate in vertex] for vertex in push_state
                ],
                "ribbon_triangles": [list(cell) for cell in state_cells],
            }
        )
    transition_records = []
    for transition, spec in enumerate(transition_specs):
        start_core, start_push, _ = states[transition]
        end_core, end_push, _ = states[transition + 1]
        start_time = Fraction(transition, 25)
        end_time = Fraction(transition + 1, 25)
        vertices = [(*value, start_time) for value in start_core + start_push] + [
            (*value, end_time) for value in end_core + end_push
        ]
        mode = spec["mode"]
        core_trace_cells = core_cells(mode)
        push_trace_cells = complementary_cells(mode)
        core_trace_vertices = [*range(6), *range(12, 18)]
        push_trace_vertices = [*range(6, 12), *range(18, 24)]
        core_triangles = [
            tuple(vertices[core_trace_vertices[index]] for index in cell)
            for cell in core_trace_cells
        ]
        push_triangles = [
            tuple(vertices[push_trace_vertices[index]] for index in cell)
            for cell in push_trace_cells
        ]
        for triangle in core_triangles + push_triangles:
            counts["trace_rank"] += 1
            if not rank_two(triangle, (0, 1, 2)):
                raise AssertionError("v2 core/push trace triangle degenerates")
        for first in core_triangles:
            for second in push_triangles:
                counts["trace_core_push"] += 1
                if triangles_intersect(first, second):
                    raise AssertionError("v2 core/push traces intersect")
        for moving_strand, moving_triangles in (
            ("core", core_triangles),
            ("push", push_triangles),
        ):
            for moving in moving_triangles:
                for static_index in static_tree.intersection(functional_box(moving)):
                    counts[f"{moving_strand}_static"] += 1
                    if triangles_intersect(moving, static_triangles[static_index][5]):
                        raise AssertionError(
                            "v2 moving trace meets static one-skeleton"
                        )
        prism_template = (
            REVERSED_PRISM
            if mode == "TIME_REVERSE_OF_CANONICAL_BACKWARD"
            else CANONICAL_PRISM
        )
        tetrahedra = []
        for triangle in state_cells:
            local = list(triangle) + [12 + index for index in triangle]
            tetrahedra.extend(
                [local[index] for index in cell] for cell in prism_template
            )
        geometric_tetrahedra = [
            tuple(vertices[index] for index in tetrahedron)
            for tetrahedron in tetrahedra
        ]
        for tetrahedron in tetrahedra:
            counts["tetra_rank"] += 1
            if not rank_three(vertices, tetrahedron):
                raise AssertionError("v2 ribbon tetrahedron degenerates")
        for first, second in combinations(range(30), 2):
            if set(tetrahedra[first]) & set(tetrahedra[second]):
                continue
            counts["tetra_nonincident"] += 1
            if tetrahedra_intersect(
                geometric_tetrahedra[first], geometric_tetrahedra[second]
            ):
                raise AssertionError(
                    f"v2 ribbon volume self-intersects at transition {transition}"
                )
        faces = tetrahedral_faces(tetrahedra)
        boundary = {face for face, multiplicity in faces.items() if multiplicity == 1}
        start_boundary = {tuple(sorted(cell)) for cell in state_cells}
        end_boundary = {
            tuple(sorted(12 + index for index in cell)) for cell in state_cells
        }
        core_boundary = map_trace_cells(core_trace_cells, 0)
        push_boundary = map_trace_cells(push_trace_cells, 6)
        declared = start_boundary | end_boundary | core_boundary | push_boundary
        endpoint_boundary = boundary - declared
        internal_faces = sum(multiplicity == 2 for multiplicity in faces.values())
        if (
            not declared <= boundary
            or len(boundary) != 44
            or len(endpoint_boundary) != 4
            or internal_faces != 38
        ):
            raise AssertionError("v2 ribbon volume face incidence changed")
        counts["boundary"] += len(boundary)
        counts["endpoint_boundary"] += len(endpoint_boundary)
        counts["internal_faces"] += internal_faces
        transition_records.append(
            {
                "transition_index": transition,
                **spec,
                "global_time_interval": [str(start_time), str(end_time)],
                "spacetime_vertices": [
                    [str(coordinate) for coordinate in vertex] for vertex in vertices
                ],
                "core_trace_triangles": core_trace_cells,
                "push_trace_triangles": push_trace_cells,
                "tetrahedra": tetrahedra,
                "boundary_triangle_count": len(boundary),
                "internal_face_pair_count": internal_faces,
            }
        )
    expected = {
        "state_transverse": 130,
        "state_core_push": 650,
        "state_rank": 260,
        "state_nonincident": 624,
        "trace_rank": 500,
        "trace_core_push": 2500,
        "tetra_rank": 750,
        "tetra_nonincident": 6700,
        "boundary": 1100,
        "endpoint_boundary": 100,
        "internal_faces": 950,
    }
    for key, value in expected.items():
        if counts[key] != value:
            raise AssertionError(f"v2 count changed: {key}={counts[key]}")
    result = {
        "schema": "t73_x_m1_outer_collar_v7_ribbon_volume/v2",
        "explicit_core_detour_sha256": core["sha256"],
        "normal_field_sha256": normal["sha256"],
        "normal_field_static_clearance_sha256": static["sha256"],
        "refuted_v1_ribbon_volume_sha256": v1["sha256"],
        "v1_obstruction_sha256": obstruction["sha256"],
        "interface_index": 3017,
        "repair_original_transitions": sorted(REPAIRS),
        "repair_changed_vertices": {str(key): value for key, value in REPAIRS.items()},
        "repair_perturbation": [str(value) for value in PERTURBATION],
        "state_count": len(state_records),
        "states": state_records,
        "transition_count": len(transition_records),
        "transitions": transition_records,
        "state_ribbon_triangle_count": counts["state_rank"],
        "state_local_star_relation_counts": dict(sorted(star_counts.items())),
        "state_local_star_count": sum(star_counts.values()),
        "state_nonincident_triangle_check_count": counts["state_nonincident"],
        "core_push_trace_triangle_check_count": counts["trace_core_push"],
        "moving_core_static_exact_triangle_check_count": counts["core_static"],
        "moving_push_static_exact_triangle_check_count": counts["push_static"],
        "r4_tetrahedron_count": counts["tetra_rank"],
        "r4_tetrahedron_rank_check_count": counts["tetra_rank"],
        "r4_nonincident_tetrahedron_check_count": counts["tetra_nonincident"],
        "boundary_triangle_count": counts["boundary"],
        "endpoint_boundary_triangle_count": counts["endpoint_boundary"],
        "internal_face_pair_count": counts["internal_faces"],
        "global_time_coverage": ["0", "1"],
        "internal_ribbon_volume_self_clearance": True,
        "static_one_skeleton_clearance": True,
        "static_ribbon_volume_clearance_status": "OPEN",
        "classification": "RATIONAL_RIBBON_VOLUME_CANDIDATE",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_RIBBON_VOLUME_V2_3017_SELF_CLEAR",
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
        raise AssertionError("ribbon volume v2 3017 is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "states": result["state_count"],
                "transitions": result["transition_count"],
                "tetrahedra": result["r4_tetrahedron_count"],
                "nonincident": result["r4_nonincident_tetrahedron_check_count"],
                "core_static": result["moving_core_static_exact_triangle_check_count"],
                "push_static": result["moving_push_static_exact_triangle_check_count"],
                "static_ribbon": result["static_ribbon_volume_clearance_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
