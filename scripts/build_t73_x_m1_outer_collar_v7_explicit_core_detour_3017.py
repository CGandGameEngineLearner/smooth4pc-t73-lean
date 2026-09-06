#!/usr/bin/env python3
"""Build the exact 18-state core detour for interface 3017."""

from __future__ import annotations

import argparse
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
MATRIX = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_dynamic_core_candidate_matrix.json"
)
OBSTRUCTION = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_dynamic_core_obstruction.json"
)
STATIC_CORE = ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_static_core_clearance.json"
OUTPUT = ROOT / "geometry/t73_x_m1_outer_collar_v7_explicit_core_detour_3017.json"
INTERFACE = 3017
GOAL_PARAMETER = Fraction(3, 4)
ZIPPER_VECTOR = (Fraction(0), Fraction(10000), Fraction(0))
ZIPPER_ORDER = (1, 2, 3, 4, 5)
HUB_X_STEP = Fraction(-100000)
HUB_Y = Fraction(100000000000)
HUB_Z_STEP = Fraction(100000)


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


def encode_state(state):
    return [[str(coordinate) for coordinate in vertex] for vertex in state]


def load_local_record(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            if record["interface_index"] == INTERFACE:
                return record
    raise AssertionError("interface 3017 is absent from local trace cache")


def spatial_segment(triangle):
    points = {vertex[:3] for vertex in triangle}
    if len(points) != 2:
        raise AssertionError("vertical triangle does not recover one segment")
    return tuple(points)


def obstacle_segments(interface, sources, finals):
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


def trace_cells(size, mode):
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
    raise AssertionError(f"unknown trace triangulation mode: {mode}")


def transition_triangles(first, second, mode):
    vertices = [(*value, Fraction(0)) for value in first] + [
        (*value, Fraction(1)) for value in second
    ]
    cells = trace_cells(len(first), mode)
    return vertices, cells, [tuple(vertices[index] for index in cell) for cell in cells]


def zipper(base):
    states = [base]
    for vertex in ZIPPER_ORDER:
        current = list(states[-1])
        value = current[vertex]
        current[vertex] = tuple(value[axis] + ZIPPER_VECTOR[axis] for axis in range(3))
        states.append(current)
    return states


def move_to(base, target):
    states = [base]
    for vertex in ZIPPER_ORDER:
        current = list(states[-1])
        current[vertex] = target[vertex]
        states.append(current)
    return states


def append_transitions(states, sequence, mode, modes):
    if states[-1] != sequence[0]:
        raise AssertionError("detour sequence endpoints do not concatenate")
    for state in sequence[1:]:
        states.append(state)
        modes.append(mode)


def build_states(initial, final):
    linear_goal = [
        tuple(
            (1 - GOAL_PARAMETER) * first[axis] + GOAL_PARAMETER * second[axis]
            for axis in range(3)
        )
        for first, second in zip(initial, final)
    ]
    hub = [initial[0]] + [
        (HUB_X_STEP * index, HUB_Y, HUB_Z_STEP * index) for index in range(1, 6)
    ]
    initial_zipper = zipper(initial)
    goal_zipper = zipper(linear_goal)
    left_hub = move_to(initial_zipper[-1], hub)
    right_hub = move_to(goal_zipper[-1], hub)
    states = [initial]
    modes = []
    append_transitions(states, initial_zipper, "CANONICAL_FORWARD", modes)
    append_transitions(states, left_hub, "CANONICAL_FORWARD", modes)
    append_transitions(
        states,
        list(reversed(right_hub)),
        "TIME_REVERSE_OF_CANONICAL_BACKWARD",
        modes,
    )
    append_transitions(states, list(reversed(goal_zipper)), "CANONICAL_FORWARD", modes)
    append_transitions(states, [linear_goal, final], "CANONICAL_FORWARD", modes)
    if (
        len(states) != 22
        or len(modes) != 21
        or states[0] != initial
        or states[-1] != final
    ):
        raise AssertionError("explicit core detour state inventory changed")
    return states, modes, linear_goal, hub


def build():
    local = json.loads(LOCAL.read_text())
    collars = json.loads(COLLARS.read_text())
    matrix = json.loads(MATRIX.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    static_core = json.loads(STATIC_CORE.read_text())
    if (
        matrix["local_trace_receipt_sha256"] != local["sha256"]
        or matrix["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or obstruction["reverse_dynamic_core_candidate_matrix_sha256"]
        != matrix["sha256"]
        or not static_core["reverse_mixed_static_core_clearance"]
    ):
        raise AssertionError("explicit detour inputs are stale or failed")
    record = load_local_record(local)
    initial = [point(value) for value in record["initial_core_subdivision"]]
    final = [point(value) for value in record["final_core_route"]]
    if initial[0] != final[0]:
        raise AssertionError("explicit detour germ endpoint is not fixed")
    states, modes, linear_goal, hub = build_states(initial, final)
    sources, finals = load_static(collars)
    obstacles = obstacle_segments(INTERFACE, sources, finals)
    permitted_pairs = {
        (value["final_interface"], value["source_interface"])
        for value in static_core["permitted_opposite_germ_incidences"]
    }
    static_triangles = [
        (kind, obstacle_interface, semantic_type, half, triangle)
        for kind, obstacle_interface, semantic_type, segment in obstacles
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
    state_self_checks = transition_self_checks = rank_checks = 0
    boundary_checks = static_checks = permitted = 0
    transition_records = []
    for state in states:
        segments = list(pairwise(state))
        for first in range(len(segments)):
            for second in range(first + 2, len(segments)):
                state_self_checks += 1
                if segment_intersects(segments[first], segments[second]):
                    raise AssertionError(
                        "explicit detour state has a core self-intersection"
                    )
    for transition, ((first, second), mode) in enumerate(zip(pairwise(states), modes)):
        vertices, cells, triangles = transition_triangles(first, second, mode)
        bottom = {value[:3] for value in vertices if value[3] == 0}
        top = {value[:3] for value in vertices if value[3] == 1}
        if bottom != set(first) or top != set(second):
            raise AssertionError("explicit detour transition boundary changed")
        boundary_checks += 2
        for triangle in triangles:
            if not rank_two(triangle, (0, 1, 2)):
                raise AssertionError("explicit detour trace triangle is degenerate")
            rank_checks += 1
        for first_edge in range(5):
            for second_edge in range(first_edge + 2, 5):
                for first_triangle in triangles[2 * first_edge : 2 * first_edge + 2]:
                    for second_triangle in triangles[
                        2 * second_edge : 2 * second_edge + 2
                    ]:
                        transition_self_checks += 1
                        if triangles_intersect(first_triangle, second_triangle):
                            raise AssertionError(
                                "explicit detour transition has a core self-intersection"
                            )
        for moving_triangle in triangles:
            for obstacle_index in tree.intersection(functional_box(moving_triangle)):
                kind, obstacle_interface, _semantic_type, _half, obstacle = (
                    static_triangles[obstacle_index]
                )
                pair = (
                    (INTERFACE, obstacle_interface)
                    if kind == "source"
                    else (obstacle_interface, INTERFACE)
                )
                shared = set(moving_triangle) & set(obstacle)
                if pair in permitted_pairs and len(shared) >= 2:
                    permitted += 1
                    continue
                static_checks += 1
                if triangles_intersect(moving_triangle, obstacle):
                    raise AssertionError(
                        "explicit detour transition intersects a static core"
                    )
        transition_records.append(
            {
                "transition_index": transition,
                "start_state": transition,
                "end_state": transition + 1,
                "triangulation_mode": mode,
                "spacetime_vertices": [
                    [str(coordinate) for coordinate in vertex] for vertex in vertices
                ],
                "trace_triangles": cells,
            }
        )
    expected = (132, 504, 210, 42, 332, 0)
    actual = (
        state_self_checks,
        transition_self_checks,
        rank_checks,
        boundary_checks,
        static_checks,
        permitted,
    )
    if actual != expected:
        raise AssertionError(f"explicit detour verification totals changed: {actual}")
    result = {
        "schema": "t73_x_m1_outer_collar_v7_explicit_core_detour/v1",
        "local_trace_receipt_sha256": local["sha256"],
        "outer_collars_v7_receipt_sha256": collars["sha256"],
        "reverse_dynamic_core_candidate_matrix_sha256": matrix["sha256"],
        "reverse_dynamic_core_obstruction_sha256": obstruction["sha256"],
        "reverse_static_core_clearance_sha256": static_core["sha256"],
        "interface_index": INTERFACE,
        "construction": "DETERMINISTIC_DOUBLE_ZIPPER_VIA_EXTERIOR_HUB",
        "configuration_dimension": 15,
        "fixed_vertex_indices": [0],
        "moving_vertex_indices": list(ZIPPER_ORDER),
        "goal_linear_parameter": str(GOAL_PARAMETER),
        "zipper_order": list(ZIPPER_ORDER),
        "zipper_vector": [str(value) for value in ZIPPER_VECTOR],
        "hub": encode_state(hub),
        "linear_goal_state": encode_state(linear_goal),
        "state_count": len(states),
        "states": [encode_state(state) for state in states],
        "transition_count": len(transition_records),
        "canonical_transition_count": modes.count("CANONICAL_FORWARD"),
        "time_reversed_transition_count": modes.count(
            "TIME_REVERSE_OF_CANONICAL_BACKWARD"
        ),
        "transitions": transition_records,
        "trace_triangle_count": rank_checks,
        "trace_triangle_rank_check_count": rank_checks,
        "state_self_segment_check_count": state_self_checks,
        "transition_self_triangle_check_count": transition_self_checks,
        "transition_boundary_check_count": boundary_checks,
        "static_core_exact_triangle_check_count": static_checks,
        "permitted_vertical_germ_count": permitted,
        "forbidden_intersection_count": 0,
        "exact_core_detour_clearance": True,
        "push_and_ribbon_status": "OPEN",
        "classification": "RATIONAL_CORE_CANDIDATE_UNVERIFIED_FOR_FRAMING",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_EXPLICIT_CORE_DETOUR_3017",
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
        raise AssertionError("explicit core detour 3017 is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "states": result["state_count"],
                "transitions": result["transition_count"],
                "triangles": result["trace_triangle_count"],
                "self_checks": result["transition_self_triangle_check_count"],
                "static_checks": result["static_core_exact_triangle_check_count"],
                "forbidden": result["forbidden_intersection_count"],
                "framing": result["push_and_ribbon_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
