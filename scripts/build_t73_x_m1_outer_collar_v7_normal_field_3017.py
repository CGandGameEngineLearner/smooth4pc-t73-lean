#!/usr/bin/env python3
"""Build the exact 22-state normal field for the interface-3017 core detour."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from fractions import Fraction
from itertools import pairwise, product
from pathlib import Path

from build_t73_x_m1_outer_collar_core_push_clearance import segment_intersects
from build_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import resolve
from verify_t73_candidate_t_band0_surface import triangles_intersect
from verify_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import rank_two

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "geometry/t73_x_m1_outer_collar_v7_explicit_core_detour_3017.json"
LOCAL = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
OBSTRUCTION = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_constant_normal_obstruction_3017.json"
)
OUTPUT = ROOT / "geometry/t73_x_m1_outer_collar_v7_normal_field_3017.json"
INTERFACE = 3017


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


def encode_state(state):
    return [[str(coordinate) for coordinate in vertex] for vertex in state]


def load_local_record(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            if record["interface_index"] == INTERFACE:
                return record
    raise AssertionError("interface 3017 local trace is absent")


def normal_path(source_normal):
    candidates = [source_normal] + [
        tuple(Fraction(value, 500) for value in direction)
        for direction in product((-1, 0, 1), repeat=3)
        if direction != (0, 0, 0)
    ]
    indices = (0, 0, 0, 0, 0, 0, 16, 1, 1, 1, 1, 1, 1, 3, 3, 2, 12, 0, 0, 0, 0, 0)
    return [candidates[index] for index in indices], indices


def complementary_cells(mode):
    cells = []
    for edge in range(5):
        if mode == "CANONICAL_FORWARD":
            cells.extend(
                ([6 + edge, 6 + edge + 1, edge + 1], [6 + edge, edge + 1, edge])
            )
        elif mode == "TIME_REVERSE_OF_CANONICAL_BACKWARD":
            cells.extend(
                ([edge, edge + 1, 6 + edge + 1], [edge, 6 + edge + 1, 6 + edge])
            )
        else:
            raise AssertionError("unknown core transition mode")
    return cells


def build():
    core = json.loads(CORE.read_text())
    local = json.loads(LOCAL.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    core_payload = {key: value for key, value in core.items() if key != "sha256"}
    obstruction_payload = {
        key: value for key, value in obstruction.items() if key != "sha256"
    }
    if (
        core["sha256"] != canonical_sha(core_payload)
        or obstruction["sha256"] != canonical_sha(obstruction_payload)
        or core["local_trace_receipt_sha256"] != local["sha256"]
        or obstruction["explicit_core_detour_sha256"] != core["sha256"]
        or obstruction["synchronous_constant_normal_trace_status"]
        != "REFUTED_ALL_32_DIAGONAL_MASKS"
    ):
        raise AssertionError("normal-field inputs are stale or inconsistent")
    record = load_local_record(local)
    initial_core = [point(value) for value in record["initial_core_subdivision"]]
    initial_push = [
        point(value) for value in record["phase_one_push_initial_subdivision"]
    ]
    final_push = [
        point(value) for value in record["phase_one_push_final_constant_normal_route"]
    ]
    source_normal = subtract(initial_push[0], initial_core[0])
    normals, normal_indices = normal_path(source_normal)
    core_states = [[point(vertex) for vertex in state] for state in core["states"]]
    if len(normals) != 22 or len(core_states) != 22:
        raise AssertionError("normal path length changed")
    push_states = [
        [add(vertex, normal) for vertex in state]
        for state, normal in zip(core_states, normals)
    ]
    if push_states[0] != initial_push or push_states[-1] != final_push:
        raise AssertionError("normal-field endpoint push paths changed")
    state_core_push_checks = state_push_self_checks = transversality_checks = 0
    for core_state, push_state, normal in zip(core_states, push_states, normals):
        core_segments = list(pairwise(core_state))
        push_segments = list(pairwise(push_state))
        for first in range(5):
            transversality_checks += 1
            tangent = subtract(core_segments[first][1], core_segments[first][0])
            if cross(tangent, normal) == (0, 0, 0):
                raise AssertionError("normal field is tangent to a core segment")
            for second in range(5):
                state_core_push_checks += 1
                if segment_intersects(core_segments[first], push_segments[second]):
                    raise AssertionError("normal-field state core meets push")
        for first in range(5):
            for second in range(first + 2, 5):
                state_push_self_checks += 1
                if segment_intersects(push_segments[first], push_segments[second]):
                    raise AssertionError("normal-field push state self-intersects")
    transitions = []
    push_rank_checks = push_self_checks = core_push_checks = 0
    for index, core_transition in enumerate(core["transitions"]):
        core_vertices = [
            point(value) for value in core_transition["spacetime_vertices"]
        ]
        first_normal, second_normal = normals[index : index + 2]
        push_vertices = [
            (
                *add(
                    vertex[:3],
                    first_normal if vertex[3] == 0 else second_normal,
                ),
                vertex[3],
            )
            for vertex in core_vertices
        ]
        core_cells = core_transition["trace_triangles"]
        push_cells = complementary_cells(core_transition["triangulation_mode"])
        core_triangles = [
            tuple(core_vertices[vertex] for vertex in cell) for cell in core_cells
        ]
        push_triangles = [
            tuple(push_vertices[vertex] for vertex in cell) for cell in push_cells
        ]
        for triangle in push_triangles:
            push_rank_checks += 1
            if not rank_two(triangle, (0, 1, 2)):
                raise AssertionError("normal-field push trace triangle degenerates")
        for first_edge in range(5):
            for second_edge in range(first_edge + 2, 5):
                for first in push_triangles[2 * first_edge : 2 * first_edge + 2]:
                    for second in push_triangles[2 * second_edge : 2 * second_edge + 2]:
                        push_self_checks += 1
                        if triangles_intersect(first, second):
                            raise AssertionError(
                                "normal-field push trace self-intersects"
                            )
        for core_index, first in enumerate(core_triangles):
            for push_index, second in enumerate(push_triangles):
                core_push_checks += 1
                if triangles_intersect(first, second):
                    raise AssertionError(
                        "normal-field core and push traces intersect: "
                        f"transition={index} core={core_index} push={push_index}"
                    )
        transitions.append(
            {
                "transition_index": index,
                "triangulation_mode": core_transition["triangulation_mode"],
                "start_normal": [str(value) for value in first_normal],
                "end_normal": [str(value) for value in second_normal],
                "push_spacetime_vertices": [
                    [str(coordinate) for coordinate in vertex]
                    for vertex in push_vertices
                ],
                "trace_triangles": push_cells,
            }
        )
    expected = (110, 550, 132, 210, 504, 2100)
    actual = (
        transversality_checks,
        state_core_push_checks,
        state_push_self_checks,
        push_rank_checks,
        push_self_checks,
        core_push_checks,
    )
    if actual != expected:
        raise AssertionError(f"normal-field verification totals changed: {actual}")
    result = {
        "schema": "t73_x_m1_outer_collar_v7_normal_field/v1",
        "explicit_core_detour_sha256": core["sha256"],
        "constant_normal_obstruction_sha256": obstruction["sha256"],
        "interface_index": INTERFACE,
        "candidate_normal_scale": "1/500",
        "candidate_direction_alphabet": [-1, 0, 1],
        "normal_path_candidate_indices": list(normal_indices),
        "source_normal": [str(value) for value in source_normal],
        "state_count": len(core_states),
        "normal_path": [[str(value) for value in normal] for normal in normals],
        "push_states": [encode_state(state) for state in push_states],
        "transition_count": len(transitions),
        "push_transitions": transitions,
        "push_diagonal_policy": "COMPLEMENT_CORE_DIAGONAL_ON_EACH_EDGE",
        "framing_transversality_check_count": transversality_checks,
        "state_core_push_segment_check_count": state_core_push_checks,
        "push_state_self_segment_check_count": state_push_self_checks,
        "push_trace_triangle_count": push_rank_checks,
        "push_trace_triangle_rank_check_count": push_rank_checks,
        "push_trace_self_triangle_check_count": push_self_checks,
        "core_push_trace_exact_triangle_check_count": core_push_checks,
        "forbidden_internal_intersection_count": 0,
        "internal_framed_one_skeleton_clearance": True,
        "static_one_skeleton_clearance_status": "OPEN",
        "ribbon_world_volume_status": "OPEN",
        "classification": "RATIONAL_NORMAL_FIELD_CANDIDATE",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_NORMAL_FIELD_3017_INTERNAL",
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
        raise AssertionError("normal field 3017 is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "states": result["state_count"],
                "transitions": result["transition_count"],
                "push_triangles": result["push_trace_triangle_count"],
                "core_push_checks": result[
                    "core_push_trace_exact_triangle_check_count"
                ],
                "forbidden": result["forbidden_internal_intersection_count"],
                "static": result["static_one_skeleton_clearance_status"],
                "ribbon": result["ribbon_world_volume_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
