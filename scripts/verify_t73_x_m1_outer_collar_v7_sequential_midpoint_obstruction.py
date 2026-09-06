#!/usr/bin/env python3
"""Independently verify the sequential midpoint ribbon collision."""

from __future__ import annotations

import gzip
import json
import sys
from fractions import Fraction
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from verify_t73_candidate_t_band0_surface import triangles_intersect
from verify_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    canonical_sha,
    point,
    resolve,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_midpoint_obstruction.json"
LOCAL = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
VOLUME = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_sequential_framed_isotopy_volume_receipt.json"
)
VOLUME_VERIFY = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_sequential_framed_isotopy_volume_verification.json"
)


def midpoint(first, second):
    return tuple((a + b) / 2 for a, b in zip(first, second))


def ribbon_segment(core, push):
    quad = (core[0], core[1], push[1], push[0])
    return ((quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3]))


def lift(triangle):
    return tuple((*vertex, Fraction(0)) for vertex in triangle)


def point_in_triangle(value, triangle):
    origin, first, second = triangle
    u = tuple(first[axis] - origin[axis] for axis in range(3))
    v = tuple(second[axis] - origin[axis] for axis in range(3))
    delta = tuple(value[axis] - origin[axis] for axis in range(3))
    axes = next(
        (
            (i, j)
            for i in range(3)
            for j in range(i + 1, 3)
            if u[i] * v[j] - u[j] * v[i]
        ),
        None,
    )
    if axes is None:
        raise AssertionError("obstruction triangle is degenerate")
    i, j = axes
    determinant = u[i] * v[j] - u[j] * v[i]
    alpha = (delta[i] * v[j] - delta[j] * v[i]) / determinant
    beta = (u[i] * delta[j] - u[j] * delta[i]) / determinant
    return (
        alpha >= 0
        and beta >= 0
        and alpha + beta <= 1
        and all(
            origin[axis] + alpha * u[axis] + beta * v[axis] == value[axis]
            for axis in range(3)
        )
    )


def load_records(receipt):
    records = {}
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as stream:
        stream.readline()
        for line in stream:
            record = json.loads(line)
            if record["interface_index"] in (0, 2):
                records[record["interface_index"]] = record
    return records


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    local = json.loads(LOCAL.read_text())
    volume = json.loads(VOLUME.read_text())
    verification = json.loads(VOLUME_VERIFY.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["local_trace_receipt_sha256"] != local["sha256"]
        or data["framed_isotopy_volume_receipt_sha256"] != volume["sha256"]
        or data["framed_isotopy_volume_verification_sha256"] != verification["sha256"]
    ):
        raise AssertionError("midpoint obstruction bindings changed")
    records = load_records(local)
    active, obstacle = records[2], records[0]
    initial_core = [point(value) for value in active["initial_core_subdivision"]]
    initial_push = [
        point(value) for value in active["phase_one_push_initial_subdivision"]
    ]
    final_core = [point(value) for value in active["final_core_route"]]
    constant_push = [
        point(value) for value in active["phase_one_push_final_constant_normal_route"]
    ]
    active_triangles = ribbon_segment(
        [midpoint(initial_core[index], final_core[index]) for index in (0, 1)],
        [midpoint(initial_push[index], constant_push[index]) for index in (0, 1)],
    )
    obstacle_triangles = ribbon_segment(
        [point(value) for value in obstacle["final_core_route"][:2]],
        [
            point(value)
            for value in obstacle["phase_one_push_final_constant_normal_route"][:2]
        ],
    )
    exact_pairs = []
    for active_index, first in enumerate(active_triangles):
        for obstacle_index, second in enumerate(obstacle_triangles):
            if triangles_intersect(lift(first), lift(second)):
                exact_pairs.append((active_index, obstacle_index))
    if exact_pairs != [(0, 0), (0, 1), (1, 1)]:
        raise AssertionError("independent collision pattern changed")
    for collision in data["collisions"]:
        first = active_triangles[collision["active_triangle"]]
        second = obstacle_triangles[collision["obstacle_triangle"]]
        if collision["active_vertices"] != [
            [str(coordinate) for coordinate in vertex] for vertex in first
        ] or collision["obstacle_vertices"] != [
            [str(coordinate) for coordinate in vertex] for vertex in second
        ]:
            raise AssertionError("saved collision triangles changed")
        witness = point(collision["witness"]["point"])
        if not point_in_triangle(witness, first) or not point_in_triangle(
            witness, second
        ):
            raise AssertionError("saved exact witness is not in both triangles")
    start = Fraction(2, 3026)
    middle = Fraction(5, 6052)
    if str((start + middle) / 2) != data["global_time"]:
        raise AssertionError("global collision time changed")
    if (
        data["linear_spatial_interpolation_status"] != "REFUTED"
        or data["framed_isotopy_volume_status"] != "CANDIDATE_REFUTED"
        or data["sequential_time_schedule_status"] != "RETAINED"
    ):
        raise AssertionError("midpoint obstruction conclusion changed")
    return {
        "verdict": "REFUTED_X_M1_OUTER_COLLAR_V7_SEQUENTIAL_LINEAR_FRAMED_ISOTOPY_INDEPENDENT",
        "active_interface": 2,
        "obstacle_interface": 0,
        "global_time": data["global_time"],
        "collision_triangle_pairs": len(exact_pairs),
        "saved_witnesses_replayed": len(data["collisions"]),
        "sequential_time_schedule": "RETAINED",
        "linear_spatial_interpolation": "REFUTED",
        "required_repair": data["required_repair"],
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
