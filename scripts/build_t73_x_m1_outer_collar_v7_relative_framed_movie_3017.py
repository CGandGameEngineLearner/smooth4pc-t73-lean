#!/usr/bin/env python3
"""Build the fixed-germ relative framed core/push movie for interface 3017."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import sys
from collections import Counter
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
from build_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import resolve
from verify_t73_candidate_t_band0_surface import triangles_intersect
from verify_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import rank_two

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "geometry/t73_x_m1_outer_collar_v7_explicit_core_detour_3017.json"
LOCAL = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
BOUNDARY_OBSTRUCTION = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_retained_germ_boundary_obstruction_3017.json"
)
OUTPUT = ROOT / "geometry/t73_x_m1_outer_collar_v7_relative_framed_movie_3017.json"
NORMAL_INDICES = (0, 16, 2, 2, 2, 2, 11, 0, 0, 0, 0, 2, 2, 3, 19, 0, 0, 0, 0, 0, 0, 0)
MODE_CODES = tuple("CCCCCRRCCCRCRCRCCCCCC")


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


def cells(mode, complement=False):
    canonical = (mode == "CANONICAL_FORWARD") != complement
    return [
        list(cell)
        for edge in range(5)
        for cell in (
            (
                (edge, edge + 1, 7 + edge),
                (edge, 7 + edge, 6 + edge),
            )
            if canonical
            else (
                (6 + edge, 7 + edge, edge + 1),
                (6 + edge, edge + 1, edge),
            )
        )
    ]


def trace(first, second, trace_cells):
    vertices = [(*value, Fraction(0)) for value in first] + [
        (*value, Fraction(1)) for value in second
    ]
    return vertices, [tuple(vertices[index] for index in cell) for cell in trace_cells]


def build():
    core = json.loads(CORE.read_text())
    local = json.loads(LOCAL.read_text())
    boundary = json.loads(BOUNDARY_OBSTRUCTION.read_text())
    collars = json.loads(COLLARS.read_text())
    if (
        boundary["normal_field_sha256"]
        != json.loads(
            (
                ROOT / "geometry/t73_x_m1_outer_collar_v7_normal_field_3017.json"
            ).read_text()
        )["sha256"]
        or boundary["explicit_core_detour_sha256"] != core["sha256"]
        or boundary["literal_retained_framing_boundary_status"] != "REFUTED"
    ):
        raise AssertionError("relative framed movie inputs are stale")
    record = load_local_record(local)
    initial_core = [point(value) for value in record["initial_core_subdivision"]]
    initial_push = [
        point(value) for value in record["phase_one_push_initial_subdivision"]
    ]
    final_push = [
        point(value) for value in record["phase_one_push_final_constant_normal_route"]
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
    core_states = [[point(vertex) for vertex in state] for state in core["states"]]
    push_states = [
        [
            add(vertex, source_normal if vertex_index == 0 else normals[state_index])
            for vertex_index, vertex in enumerate(core_state)
        ]
        for state_index, core_state in enumerate(core_states)
    ]
    if push_states[0] != initial_push or push_states[-1] != final_push:
        raise AssertionError("relative framed movie endpoint push paths changed")
    fixed_edge = {point(value) for value in boundary["fixed_framing_edge"]}
    if any(
        {core_state[0], push_state[0]} != fixed_edge
        for core_state, push_state in zip(core_states, push_states)
    ):
        raise AssertionError("relative framed movie does not fix the germ framing edge")
    static = load_static(collars)
    properties = rtree_index.Property()
    properties.dimension = len(FUNCTIONALS)
    static_tree = rtree_index.Index(
        ((index, functional_box(value[5]), None) for index, value in enumerate(static)),
        properties=properties,
    )
    counts = Counter()
    for state_index, (core_state, push_state) in enumerate(
        zip(core_states, push_states)
    ):
        core_segments = list(pairwise(core_state))
        push_segments = list(pairwise(push_state))
        state_normal = normals[state_index]
        for edge in range(5):
            tangent = subtract(core_segments[edge][1], core_segments[edge][0])
            counts["transverse"] += 1
            if cross(tangent, source_normal if edge == 0 else state_normal) == (
                0,
                0,
                0,
            ):
                raise AssertionError("relative normal is tangent")
            for push_segment in push_segments:
                counts["state_core_push"] += 1
                if segment_intersects(core_segments[edge], push_segment):
                    raise AssertionError("relative framed state core meets push")
        for first in range(5):
            for second in range(first + 2, 5):
                counts["state_push_self"] += 1
                if segment_intersects(push_segments[first], push_segments[second]):
                    raise AssertionError("relative push state self-intersects")
    transitions = []
    for transition, mode in enumerate(modes):
        core_cells = cells(mode)
        push_cells = cells(mode, complement=True)
        core_vertices, core_triangles = trace(
            core_states[transition], core_states[transition + 1], core_cells
        )
        push_vertices, push_triangles = trace(
            push_states[transition], push_states[transition + 1], push_cells
        )
        for triangle in core_triangles + push_triangles:
            counts["rank"] += 1
            if not rank_two(triangle, (0, 1, 2)):
                raise AssertionError("relative trace triangle degenerates")
        for first_edge in range(5):
            for second_edge in range(first_edge + 2, 5):
                for triangle_a in core_triangles[2 * first_edge : 2 * first_edge + 2]:
                    for triangle_b in core_triangles[
                        2 * second_edge : 2 * second_edge + 2
                    ]:
                        counts["core_self"] += 1
                        if triangles_intersect(triangle_a, triangle_b):
                            raise AssertionError("relative core trace self-intersects")
                for triangle_a in push_triangles[2 * first_edge : 2 * first_edge + 2]:
                    for triangle_b in push_triangles[
                        2 * second_edge : 2 * second_edge + 2
                    ]:
                        counts["push_self"] += 1
                        if triangles_intersect(triangle_a, triangle_b):
                            raise AssertionError("relative push trace self-intersects")
        for first in core_triangles:
            for second in push_triangles:
                counts["core_push"] += 1
                if triangles_intersect(first, second):
                    raise AssertionError("relative core/push traces intersect")
        for strand, moving_triangles in (
            ("core", core_triangles),
            ("push", push_triangles),
        ):
            for moving in moving_triangles:
                for static_index in static_tree.intersection(functional_box(moving)):
                    counts[f"{strand}_static"] += 1
                    if triangles_intersect(moving, static[static_index][5]):
                        raise AssertionError(
                            "relative moving trace meets static one-skeleton"
                        )
        transitions.append(
            {
                "transition_index": transition,
                "mode": mode,
                "start_normal_index": NORMAL_INDICES[transition],
                "end_normal_index": NORMAL_INDICES[transition + 1],
                "core_spacetime_vertices": [
                    [str(coordinate) for coordinate in vertex]
                    for vertex in core_vertices
                ],
                "push_spacetime_vertices": [
                    [str(coordinate) for coordinate in vertex]
                    for vertex in push_vertices
                ],
                "core_trace_triangles": core_cells,
                "push_trace_triangles": push_cells,
            }
        )
    expected = {
        "transverse": 110,
        "state_core_push": 550,
        "state_push_self": 132,
        "rank": 420,
        "core_self": 504,
        "push_self": 504,
        "core_push": 2100,
        "core_static": 776,
        "push_static": 784,
    }
    for key, value in expected.items():
        if counts[key] != value:
            raise AssertionError(
                f"relative framed movie count changed: {key}={counts[key]}"
            )
    result = {
        "schema": "t73_x_m1_outer_collar_v7_relative_framed_movie/v1",
        "explicit_core_detour_sha256": core["sha256"],
        "retained_germ_boundary_obstruction_sha256": boundary["sha256"],
        "outer_collars_v7_receipt_sha256": collars["sha256"],
        "interface_index": 3017,
        "candidate_normal_scale": "1/500",
        "normal_path_candidate_indices": list(NORMAL_INDICES),
        "normal_path": [[str(value) for value in normal] for normal in normals],
        "core_mode_codes": list(MODE_CODES),
        "fixed_germ_normal": [str(value) for value in source_normal],
        "fixed_germ_framing_edge": [
            [str(coordinate) for coordinate in vertex] for vertex in sorted(fixed_edge)
        ],
        "state_count": len(core_states),
        "core_states": [
            [[str(coordinate) for coordinate in vertex] for vertex in state]
            for state in core_states
        ],
        "push_states": [
            [[str(coordinate) for coordinate in vertex] for vertex in state]
            for state in push_states
        ],
        "transition_count": len(transitions),
        "transitions": transitions,
        "framing_transversality_check_count": counts["transverse"],
        "state_core_push_segment_check_count": counts["state_core_push"],
        "push_state_self_segment_check_count": counts["state_push_self"],
        "trace_triangle_rank_check_count": counts["rank"],
        "core_trace_self_triangle_check_count": counts["core_self"],
        "push_trace_self_triangle_check_count": counts["push_self"],
        "core_push_trace_triangle_check_count": counts["core_push"],
        "moving_core_static_triangle_check_count": counts["core_static"],
        "moving_push_static_triangle_check_count": counts["push_static"],
        "fixed_germ_boundary_all_states": True,
        "forbidden_intersection_count": 0,
        "relative_framed_one_skeleton_clearance": True,
        "ribbon_volume_status": "OPEN_REBUILD_WITH_NEW_CORE_MODES",
        "classification": "RATIONAL_RELATIVE_FRAMED_MOVIE_CANDIDATE",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_RELATIVE_FRAMED_MOVIE_3017",
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
        raise AssertionError("relative framed movie 3017 is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "states": result["state_count"],
                "transitions": result["transition_count"],
                "core_static": result["moving_core_static_triangle_check_count"],
                "push_static": result["moving_push_static_triangle_check_count"],
                "germ_fixed": result["fixed_germ_boundary_all_states"],
                "forbidden": result["forbidden_intersection_count"],
                "volume": result["ribbon_volume_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
