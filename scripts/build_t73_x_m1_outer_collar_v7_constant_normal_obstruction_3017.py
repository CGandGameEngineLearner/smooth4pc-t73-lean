#!/usr/bin/env python3
"""Refute every synchronous constant-normal push triangulation at transition 6."""

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

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "geometry/t73_x_m1_outer_collar_v7_explicit_core_detour_3017.json"
LOCAL = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v7_constant_normal_obstruction_3017.json"
INTERFACE = 3017
TRANSITION = 6


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


def load_local_record(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            if record["interface_index"] == INTERFACE:
                return record
    raise AssertionError("interface 3017 local trace is absent")


def push_cells(mask):
    size = 6
    result = []
    for edge in range(5):
        if mask & (1 << edge):
            result.extend(
                (
                    [size + edge, size + edge + 1, edge + 1],
                    [size + edge, edge + 1, edge],
                )
            )
        else:
            result.extend(
                (
                    [edge, edge + 1, size + edge + 1],
                    [edge, size + edge + 1, size + edge],
                )
            )
    return result


def build():
    core = json.loads(CORE.read_text())
    local = json.loads(LOCAL.read_text())
    core_payload = {key: value for key, value in core.items() if key != "sha256"}
    if (
        core["sha256"] != canonical_sha(core_payload)
        or core["local_trace_receipt_sha256"] != local["sha256"]
    ):
        raise AssertionError("constant-normal obstruction inputs are stale")
    record = load_local_record(local)
    initial_core = [point(value) for value in record["initial_core_subdivision"]]
    initial_push = [
        point(value) for value in record["phase_one_push_initial_subdivision"]
    ]
    normal = subtract(initial_push[0], initial_core[0])
    states = [[point(vertex) for vertex in state] for state in core["states"]]
    push_states = [[add(vertex, normal) for vertex in state] for state in states]
    state_core_push_checks = push_state_self_checks = 0
    for core_state, push_state in zip(states, push_states):
        core_segments = list(pairwise(core_state))
        push_segments = list(pairwise(push_state))
        for first in core_segments:
            for second in push_segments:
                state_core_push_checks += 1
                if segment_intersects(first, second):
                    raise AssertionError("constant-normal state core meets push")
        for first in range(5):
            for second in range(first + 2, 5):
                push_state_self_checks += 1
                if segment_intersects(push_segments[first], push_segments[second]):
                    raise AssertionError("constant-normal push state self-intersects")
    core_transition = core["transitions"][TRANSITION]
    core_vertices = [point(value) for value in core_transition["spacetime_vertices"]]
    core_triangles = [
        tuple(core_vertices[index] for index in cell)
        for cell in core_transition["trace_triangles"]
    ]
    push_vertices = [(*add(vertex[:3], normal), vertex[3]) for vertex in core_vertices]
    invalid_masks = []
    first_collision_by_mask = []
    exact_checks = 0
    for mask in range(32):
        cells = push_cells(mask)
        push_triangles = [
            tuple(push_vertices[index] for index in cell) for cell in cells
        ]
        collision = None
        for core_index, first in enumerate(core_triangles):
            for push_index, second in enumerate(push_triangles):
                exact_checks += 1
                if triangles_intersect(first, second):
                    collision = {
                        "core_triangle": core_index,
                        "push_triangle": push_index,
                    }
                    break
            if collision:
                break
        if collision:
            invalid_masks.append(mask)
            first_collision_by_mask.append({"push_diagonal_mask": mask, **collision})
    if invalid_masks != list(range(32)):
        raise AssertionError("a synchronous constant-normal mask unexpectedly passes")
    canonical = first_collision_by_mask[0]
    if canonical != {"push_diagonal_mask": 0, "core_triangle": 0, "push_triangle": 2}:
        raise AssertionError("canonical constant-normal collision changed")
    result = {
        "schema": "t73_x_m1_outer_collar_v7_constant_normal_obstruction/v1",
        "explicit_core_detour_sha256": core["sha256"],
        "local_trace_receipt_sha256": local["sha256"],
        "interface_index": INTERFACE,
        "transition_index": TRANSITION,
        "changed_core_vertices": [2],
        "source_normal": [str(value) for value in normal],
        "state_count": len(states),
        "state_core_push_segment_check_count": state_core_push_checks,
        "push_state_self_segment_check_count": push_state_self_checks,
        "push_diagonal_mask_count": 32,
        "invalid_push_diagonal_masks": invalid_masks,
        "first_collision_by_mask": first_collision_by_mask,
        "exact_triangle_checks_until_first_collision": exact_checks,
        "canonical_collision": canonical,
        "constant_normal_statewise_clearance": True,
        "synchronous_constant_normal_trace_status": "REFUTED_ALL_32_DIAGONAL_MASKS",
        "required_repair": "INTERLEAVE_CORE_PUSH_AND_INSERT_LOCAL_PUSH_WAYPOINTS",
        "verdict": "REFUTED_X_M1_OUTER_COLLAR_V7_CONSTANT_NORMAL_FRAMING_3017",
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
        raise AssertionError("constant-normal obstruction 3017 is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "transition": result["transition_index"],
                "state_checks": result["state_core_push_segment_check_count"],
                "masks": result["push_diagonal_mask_count"],
                "invalid_masks": len(result["invalid_push_diagonal_masks"]),
                "repair": result["required_repair"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
