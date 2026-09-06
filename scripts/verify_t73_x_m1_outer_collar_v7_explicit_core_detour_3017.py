#!/usr/bin/env python3
"""Independently replay the explicit interface-3017 core detour."""

from __future__ import annotations

import gzip
import hashlib
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
from build_t73_x_m1_outer_collar_v7_reverse_dynamic_core_candidate_matrix import (
    COLLARS,
    FUNCTIONALS,
    LOCAL,
    functional_box,
    load_static,
)
from build_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import resolve
from verify_t73_candidate_t_band0_surface import triangles_intersect
from verify_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import rank_two

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_outer_collar_v7_explicit_core_detour_3017.json"
MATRIX = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_dynamic_core_candidate_matrix.json"
)
OBSTRUCTION = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_dynamic_core_obstruction.json"
)
STATIC_CORE = ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_static_core_clearance.json"
INTERFACE = 3017
EXPECTED_CHANGED_VERTICES = (
    1,
    2,
    3,
    4,
    5,
    1,
    2,
    3,
    4,
    5,
    5,
    4,
    3,
    2,
    1,
    5,
    4,
    3,
    2,
    1,
)


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


def load_local_record(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            if record["interface_index"] == INTERFACE:
                return record
    raise AssertionError("interface 3017 is absent")


def spatial_segment(triangle):
    points = {vertex[:3] for vertex in triangle}
    if len(points) != 2:
        raise AssertionError("vertical triangle does not recover one segment")
    return tuple(points)


def obstacles(interface, sources, finals):
    values = []
    for source_interface, half, triangle in sources:
        if half == 0 and source_interface < interface:
            values.append(("source", source_interface, 0, spatial_segment(triangle)))
    for final_interface, semantic_type, half, triangle in finals:
        if half == 0 and final_interface > interface:
            values.append(
                ("final", final_interface, semantic_type, spatial_segment(triangle))
            )
    return values


def vertical_triangles(segment):
    vertices = (
        (*segment[0], Fraction(0)),
        (*segment[1], Fraction(0)),
        (*segment[0], Fraction(1)),
        (*segment[1], Fraction(1)),
    )
    return (
        (vertices[0], vertices[1], vertices[3]),
        (vertices[0], vertices[3], vertices[2]),
    )


def expected_cells(size, mode):
    if mode == "CANONICAL_FORWARD":
        return [
            cell
            for local in range(size - 1)
            for cell in (
                [local, local + 1, size + local + 1],
                [local, size + local + 1, size + local],
            )
        ]
    if mode == "TIME_REVERSE_OF_CANONICAL_BACKWARD":
        return [
            cell
            for local in range(size - 1)
            for cell in (
                [size + local, size + local + 1, local + 1],
                [size + local, local + 1, local],
            )
        ]
    raise AssertionError("unknown saved triangulation mode")


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    local = json.loads(LOCAL.read_text())
    collars = json.loads(COLLARS.read_text())
    matrix = json.loads(MATRIX.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    static_core = json.loads(STATIC_CORE.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["local_trace_receipt_sha256"] != local["sha256"]
        or data["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or data["reverse_dynamic_core_candidate_matrix_sha256"] != matrix["sha256"]
        or data["reverse_dynamic_core_obstruction_sha256"] != obstruction["sha256"]
        or data["reverse_static_core_clearance_sha256"] != static_core["sha256"]
    ):
        raise AssertionError("explicit detour bindings changed")
    record = load_local_record(local)
    initial = [point(value) for value in record["initial_core_subdivision"]]
    final = [point(value) for value in record["final_core_route"]]
    states = [[point(vertex) for vertex in state] for state in data["states"]]
    if len(states) != 22 or states[0] != initial or states[-1] != final:
        raise AssertionError("explicit detour endpoint states changed")
    if any(state[0] != initial[0] for state in states):
        raise AssertionError("explicit detour does not fix the germ vertex")
    for transition, vertex in enumerate(EXPECTED_CHANGED_VERTICES):
        changed = [
            index
            for index, (first, second) in enumerate(
                zip(states[transition], states[transition + 1])
            )
            if first != second
        ]
        if changed != [vertex]:
            raise AssertionError("zipper/hub transition changes the wrong vertex")
    if [
        index for index, (a, b) in enumerate(zip(states[20], states[21])) if a != b
    ] != [
        1,
        2,
        3,
        4,
        5,
    ]:
        raise AssertionError("linear tail does not change the five moving vertices")
    sources, finals = load_static(collars)
    obstacle_segments = obstacles(INTERFACE, sources, finals)
    static_triangles = [
        (kind, obstacle_interface, semantic_type, half, triangle)
        for kind, obstacle_interface, semantic_type, segment in obstacle_segments
        for half, triangle in enumerate(vertical_triangles(segment))
    ]
    properties = rtree_index.Property()
    properties.dimension = len(FUNCTIONALS)
    tree = rtree_index.Index(
        (
            (index, functional_box(value[4]), None)
            for index, value in enumerate(static_triangles)
        ),
        properties=properties,
    )
    permitted_pairs = {
        (value["final_interface"], value["source_interface"])
        for value in static_core["permitted_opposite_germ_incidences"]
    }
    state_checks = self_checks = rank_checks = boundary_checks = static_checks = 0
    permitted = 0
    for state in states:
        segments = list(pairwise(state))
        for first in range(5):
            for second in range(first + 2, 5):
                state_checks += 1
                if segment_intersects(segments[first], segments[second]):
                    raise AssertionError("saved detour state self-intersects")
    if len(data["transitions"]) != 21:
        raise AssertionError("saved detour transition count changed")
    for transition, saved in enumerate(data["transitions"]):
        mode = saved["triangulation_mode"]
        vertices = [(*value, Fraction(0)) for value in states[transition]] + [
            (*value, Fraction(1)) for value in states[transition + 1]
        ]
        cells = expected_cells(6, mode)
        if (
            saved["start_state"] != transition
            or saved["end_state"] != transition + 1
            or saved["trace_triangles"] != cells
            or saved["spacetime_vertices"]
            != [[str(coordinate) for coordinate in vertex] for vertex in vertices]
        ):
            raise AssertionError("saved transition simplices changed")
        triangles = [tuple(vertices[index] for index in cell) for cell in cells]
        bottom = {value[:3] for value in vertices if value[3] == 0}
        top = {value[:3] for value in vertices if value[3] == 1}
        if bottom != set(states[transition]) or top != set(states[transition + 1]):
            raise AssertionError("saved transition boundary changed")
        boundary_checks += 2
        for triangle in triangles:
            if not rank_two(triangle, (0, 1, 2)):
                raise AssertionError("saved detour has a degenerate trace triangle")
            rank_checks += 1
        for first_edge in range(5):
            for second_edge in range(first_edge + 2, 5):
                for first_triangle in triangles[2 * first_edge : 2 * first_edge + 2]:
                    for second_triangle in triangles[
                        2 * second_edge : 2 * second_edge + 2
                    ]:
                        self_checks += 1
                        if triangles_intersect(first_triangle, second_triangle):
                            raise AssertionError("saved detour trace self-intersects")
        for moving in triangles:
            for obstacle_index in tree.intersection(functional_box(moving)):
                kind, obstacle_interface, _semantic_type, _half, obstacle = (
                    static_triangles[obstacle_index]
                )
                pair = (
                    (INTERFACE, obstacle_interface)
                    if kind == "source"
                    else (obstacle_interface, INTERFACE)
                )
                shared = set(moving) & set(obstacle)
                if pair in permitted_pairs and len(shared) >= 2:
                    permitted += 1
                    continue
                static_checks += 1
                if triangles_intersect(moving, obstacle):
                    raise AssertionError("saved detour meets a static core")
    if (
        state_checks,
        self_checks,
        rank_checks,
        boundary_checks,
        static_checks,
        permitted,
    ) != (
        132,
        504,
        210,
        42,
        332,
        0,
    ):
        raise AssertionError("independent detour totals changed")
    if (
        data["configuration_dimension"] != 15
        or data["fixed_vertex_indices"] != [0]
        or data["moving_vertex_indices"] != [1, 2, 3, 4, 5]
        or data["forbidden_intersection_count"] != 0
        or not data["exact_core_detour_clearance"]
        or data["push_and_ribbon_status"] != "OPEN"
    ):
        raise AssertionError("explicit detour scope changed")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_EXPLICIT_CORE_DETOUR_3017_INDEPENDENT",
        "states_replayed": len(states),
        "transitions_replayed": len(data["transitions"]),
        "trace_triangles_replayed": rank_checks,
        "state_self_segment_checks": state_checks,
        "transition_self_triangle_checks": self_checks,
        "transition_boundary_checks": boundary_checks,
        "static_core_exact_triangle_checks": static_checks,
        "forbidden_intersections": 0,
        "fixed_vertices": [0],
        "moving_vertices": [1, 2, 3, 4, 5],
        "push_and_ribbon_status": "OPEN",
        "classification": "RATIONAL_CORE_CANDIDATE_UNVERIFIED_FOR_FRAMING",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
