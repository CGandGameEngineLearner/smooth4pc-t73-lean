#!/usr/bin/env python3
"""Build the exact 22-state normal field for the interface-3017 core detour."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from fractions import Fraction
from itertools import pairwise
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
    scale = Fraction(1, 500)
    negative = -scale
    return [
        *([source_normal] * 6),
        (Fraction(0), scale, Fraction(0)),
        *([(negative, negative, negative)] * 7),
        *([(negative, negative, scale)] * 2),
        (negative, negative, Fraction(0)),
        (scale, negative, scale),
        *([source_normal] * 4),
    ]


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
    normals = normal_path(source_normal)
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
        cells = core_transition["trace_triangles"]
        core_triangles = [
            tuple(core_vertices[vertex] for vertex in cell) for cell in cells
        ]
        push_triangles = [
            tuple(push_vertices[vertex] for vertex in cell) for cell in cells
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
        for first in core_triangles:
            for second in push_triangles:
                core_push_checks += 1
                if triangles_intersect(first, second):
                    raise AssertionError("normal-field core and push traces intersect")
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
                "trace_triangles": cells,
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
        "source_normal": [str(value) for value in source_normal],
        "state_count": len(core_states),
        "normal_path": [[str(value) for value in normal] for normal in normals],
        "push_states": [encode_state(state) for state in push_states],
        "transition_count": len(transitions),
        "push_transitions": transitions,
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
