#!/usr/bin/env python3
"""Build the fixed-germ volume-aware ribbon movie for interface 3017."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
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
from build_t73_x_m1_outer_collar_v7_normal_field_static_clearance_3017 import (
    COLLARS,
    FUNCTIONALS,
    functional_box,
    load_static,
)
from build_t73_x_m1_outer_collar_v7_ribbon_volume_3017 import (
    CANONICAL_PRISM,
    REVERSED_PRISM,
    rank_three,
    ribbon_cells,
    tetrahedral_faces,
)
from build_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import resolve
from t73_exact_simplex import tetrahedra_intersect
from verify_t73_candidate_t_band0_surface import triangles_intersect
from verify_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import rank_two

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "geometry/t73_x_m1_outer_collar_v7_explicit_core_detour_3017.json"
LOCAL = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
BOUNDARY = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_retained_germ_boundary_obstruction_3017.json"
)
PRIOR_MOVIE = ROOT / "geometry/t73_x_m1_outer_collar_v7_relative_framed_movie_3017.json"
OUTPUT = ROOT / "geometry/t73_x_m1_outer_collar_v7_relative_ribbon_volume_3017.json"
NORMAL_INDICES = (0, 16, 2, 2, 2, 2, 11, 0, 0, 0, 2, 9, 9, 9, 12, 12, 0, 0, 0, 0, 0, 0)
MODE_CODES = tuple("CCCCCRRCCCCCCCRRCCCCC")
REPAIR_TRANSITION = 15
REPAIR_VERTEX = 5
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


def load_local_record(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            if record["interface_index"] == 3017:
                return record
    raise AssertionError("interface 3017 local trace is absent")


def trace_cells(mode, complement=False):
    canonical = (mode == "CANONICAL_FORWARD") != complement
    return [
        list(cell)
        for edge in range(5)
        for cell in (
            ((edge, edge + 1, 7 + edge), (edge, 7 + edge, 6 + edge))
            if canonical
            else ((6 + edge, 7 + edge, edge + 1), (6 + edge, edge + 1, edge))
        )
    ]


def build():
    core = json.loads(CORE.read_text())
    local = json.loads(LOCAL.read_text())
    boundary = json.loads(BOUNDARY.read_text())
    prior = json.loads(PRIOR_MOVIE.read_text())
    collars = json.loads(COLLARS.read_text())
    if (
        boundary["explicit_core_detour_sha256"] != core["sha256"]
        or prior["retained_germ_boundary_obstruction_sha256"] != boundary["sha256"]
        or prior["ribbon_volume_status"] != "OPEN_REBUILD_WITH_NEW_CORE_MODES"
    ):
        raise AssertionError("relative ribbon-volume inputs are stale")
    record = load_local_record(local)
    initial_core = [point(value) for value in record["initial_core_subdivision"]]
    initial_push = [
        point(value) for value in record["phase_one_push_initial_subdivision"]
    ]
    source_normal = subtract(initial_push[0], initial_core[0])
    directions = [
        direction
        for direction in itertools.product((-1, 0, 1), repeat=3)
        if direction != (0, 0, 0)
    ]
    candidates = [source_normal] + [
        tuple(Fraction(value, 500) for value in direction) for direction in directions
    ]
    normals = [candidates[index] for index in NORMAL_INDICES]
    modes = [
        "CANONICAL_FORWARD" if code == "C" else "TIME_REVERSE_OF_CANONICAL_BACKWARD"
        for code in MODE_CODES
    ]
    original_core = [[point(vertex) for vertex in state] for state in core["states"]]
    original_push = [
        [
            add(vertex, source_normal if vertex_index == 0 else normals[state_index])
            for vertex_index, vertex in enumerate(state)
        ]
        for state_index, state in enumerate(original_core)
    ]
    states = [(original_core[0], original_push[0], {"kind": "original", "index": 0})]
    specs = []
    for transition, mode in enumerate(modes):
        if transition == REPAIR_TRANSITION:
            midpoint_core = [
                tuple((a + b) / 2 for a, b in zip(first, second))
                for first, second in zip(
                    original_core[transition], original_core[transition + 1]
                )
            ]
            midpoint_push = [
                tuple((a + b) / 2 for a, b in zip(first, second))
                for first, second in zip(
                    original_push[transition], original_push[transition + 1]
                )
            ]
            midpoint_core[REPAIR_VERTEX] = add(
                midpoint_core[REPAIR_VERTEX], PERTURBATION
            )
            midpoint_push[REPAIR_VERTEX] = add(
                midpoint_push[REPAIR_VERTEX], PERTURBATION
            )
            states.append(
                (
                    midpoint_core,
                    midpoint_push,
                    {
                        "kind": "repair_midpoint",
                        "original_transition": transition,
                        "changed_vertex": REPAIR_VERTEX,
                        "perturbation": [str(value) for value in PERTURBATION],
                    },
                )
            )
            specs.append((transition, "a", mode))
        states.append(
            (
                original_core[transition + 1],
                original_push[transition + 1],
                {"kind": "original", "index": transition + 1},
            )
        )
        specs.append(
            (
                transition,
                "b" if transition == REPAIR_TRANSITION else "full",
                mode,
            )
        )
    if len(states) != 23 or len(specs) != 22:
        raise AssertionError("relative ribbon-volume state inventory changed")
    fixed_edge = {point(value) for value in boundary["fixed_framing_edge"]}
    static = load_static(collars)
    properties = rtree_index.Property()
    properties.dimension = len(FUNCTIONALS)
    static_tree = rtree_index.Index(
        ((index, functional_box(value[5]), None) for index, value in enumerate(static)),
        properties=properties,
    )
    ribbon_state_cells = ribbon_cells()
    counts = Counter()
    star_counts = Counter()
    state_records = []
    for state_index, (core_state, push_state, provenance) in enumerate(states):
        if {core_state[0], push_state[0]} != fixed_edge:
            raise AssertionError("relative ribbon volume loses fixed germ edge")
        vertices = core_state + push_state
        triangles = [
            tuple(vertices[index] for index in cell) for cell in ribbon_state_cells
        ]
        core_segments = list(pairwise(core_state))
        push_segments = list(pairwise(push_state))
        for edge in range(5):
            counts["transverse"] += 1
            if cross(
                subtract(core_segments[edge][1], core_segments[edge][0]),
                subtract(push_state[edge], core_state[edge]),
            ) == (0, 0, 0):
                raise AssertionError("relative ribbon state framing tangent")
            for push_segment in push_segments:
                counts["state_core_push"] += 1
                if segment_intersects(core_segments[edge], push_segment):
                    raise AssertionError("relative ribbon state core meets push")
        for triangle in triangles:
            counts["state_rank"] += 1
            if not rank_two(
                tuple((*vertex, Fraction(0)) for vertex in triangle), (0, 1, 2)
            ):
                raise AssertionError("relative ribbon state triangle degenerates")
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
                raise AssertionError("relative ribbon state folds")
        state_records.append(
            {
                "state_index": state_index,
                "global_time": str(Fraction(state_index, 22)),
                "provenance": provenance,
                "core_vertices": [
                    [str(coordinate) for coordinate in vertex] for vertex in core_state
                ],
                "push_vertices": [
                    [str(coordinate) for coordinate in vertex] for vertex in push_state
                ],
                "ribbon_triangles": [list(cell) for cell in ribbon_state_cells],
            }
        )
    transition_records = []
    for transition, (original, subtransition, mode) in enumerate(specs):
        start_core, start_push, _ = states[transition]
        end_core, end_push, _ = states[transition + 1]
        start_time = Fraction(transition, 22)
        end_time = Fraction(transition + 1, 22)
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
        for triangle in core_triangles + push_triangles:
            counts["trace_rank"] += 1
            if not rank_two(triangle, (0, 1, 2)):
                raise AssertionError("relative ribbon trace triangle degenerates")
        for first in core_triangles:
            for second in push_triangles:
                counts["core_push"] += 1
                if triangles_intersect(first, second):
                    raise AssertionError("relative ribbon core/push traces intersect")
        for strand, moving_triangles in (
            ("core", core_triangles),
            ("push", push_triangles),
        ):
            for moving in moving_triangles:
                for static_index in static_tree.intersection(functional_box(moving)):
                    counts[f"{strand}_static"] += 1
                    if triangles_intersect(moving, static[static_index][5]):
                        raise AssertionError(
                            "relative ribbon trace meets static one-skeleton"
                        )
        template = (
            REVERSED_PRISM
            if mode == "TIME_REVERSE_OF_CANONICAL_BACKWARD"
            else CANONICAL_PRISM
        )
        tetrahedra = []
        for triangle in ribbon_state_cells:
            local = list(triangle) + [12 + index for index in triangle]
            tetrahedra.extend([local[index] for index in cell] for cell in template)
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
            counts["tetra_nonincident"] += 1
            if tetrahedra_intersect(geometric[first], geometric[second]):
                raise AssertionError("relative ribbon volume self-intersects")
        faces = tetrahedral_faces(tetrahedra)
        boundary_faces = sum(value == 1 for value in faces.values())
        internal_faces = sum(value == 2 for value in faces.values())
        if boundary_faces != 44 or internal_faces != 38:
            raise AssertionError("relative ribbon volume face incidence changed")
        counts["boundary"] += boundary_faces
        counts["internal"] += internal_faces
        transition_records.append(
            {
                "transition_index": transition,
                "original_transition": original,
                "subtransition": subtransition,
                "mode": mode,
                "global_time_interval": [str(start_time), str(end_time)],
                "spacetime_vertices": [
                    [str(coordinate) for coordinate in vertex] for vertex in vertices
                ],
                "core_trace_triangles": core_trace_cells,
                "push_trace_triangles": push_trace_cells,
                "tetrahedra": tetrahedra,
            }
        )
    expected = {
        "transverse": 115,
        "state_core_push": 575,
        "state_rank": 230,
        "trace_rank": 440,
        "core_push": 2200,
        "tetra_rank": 660,
        "tetra_nonincident": 5896,
        "boundary": 968,
        "internal": 836,
    }
    for key, value in expected.items():
        if counts[key] != value:
            raise AssertionError(
                f"relative ribbon volume count changed: {key}={counts[key]}"
            )
    result = {
        "schema": "t73_x_m1_outer_collar_v7_relative_ribbon_volume/v1",
        "explicit_core_detour_sha256": core["sha256"],
        "retained_germ_boundary_obstruction_sha256": boundary["sha256"],
        "prior_relative_framed_movie_sha256": prior["sha256"],
        "interface_index": 3017,
        "normal_path_candidate_indices": list(NORMAL_INDICES),
        "core_mode_codes": list(MODE_CODES),
        "fixed_germ_normal": [str(value) for value in source_normal],
        "repair_original_transition": REPAIR_TRANSITION,
        "repair_changed_vertex": REPAIR_VERTEX,
        "repair_perturbation": [str(value) for value in PERTURBATION],
        "state_count": len(state_records),
        "states": state_records,
        "transition_count": len(transition_records),
        "transitions": transition_records,
        "fixed_germ_boundary_all_states": True,
        "framing_transversality_check_count": counts["transverse"],
        "state_core_push_segment_check_count": counts["state_core_push"],
        "state_ribbon_triangle_count": counts["state_rank"],
        "state_local_star_relation_counts": dict(sorted(star_counts.items())),
        "state_local_star_count": sum(star_counts.values()),
        "trace_triangle_rank_check_count": counts["trace_rank"],
        "core_push_trace_triangle_check_count": counts["core_push"],
        "moving_core_static_triangle_check_count": counts["core_static"],
        "moving_push_static_triangle_check_count": counts["push_static"],
        "r4_tetrahedron_count": counts["tetra_rank"],
        "r4_nonincident_tetrahedron_check_count": counts["tetra_nonincident"],
        "boundary_triangle_count": counts["boundary"],
        "internal_face_pair_count": counts["internal"],
        "global_time_coverage": ["0", "1"],
        "forbidden_intersection_count": 0,
        "internal_ribbon_volume_self_clearance": True,
        "scheduled_static_one_skeleton_clearance": True,
        "external_ribbon_volume_clearance_status": "OPEN",
        "classification": "RATIONAL_RELATIVE_RIBBON_VOLUME_CANDIDATE",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_RELATIVE_RIBBON_VOLUME_3017_SELF_CLEAR",
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
        raise AssertionError("relative ribbon volume 3017 is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "states": result["state_count"],
                "transitions": result["transition_count"],
                "tetrahedra": result["r4_tetrahedron_count"],
                "nonincident": result["r4_nonincident_tetrahedron_check_count"],
                "core_static": result["moving_core_static_triangle_check_count"],
                "push_static": result["moving_push_static_triangle_check_count"],
                "germ_fixed": result["fixed_germ_boundary_all_states"],
                "external": result["external_ribbon_volume_clearance_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
