#!/usr/bin/env python3
"""Independently replay every local simplicial V7 isotopy trace."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
COUNT = 5


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def add(first, second):
    return tuple(a + b for a, b in zip(first, second))


def subtract(first, second):
    return tuple(a - b for a, b in zip(first, second))


def subdivide(first, second):
    delta = subtract(second, first)
    return [
        tuple(first[axis] + Fraction(index, COUNT) * delta[axis] for axis in range(3))
        for index in range(COUNT + 1)
    ]


def spacetime(value, time):
    return (*value, Fraction(time))


def triangles(size):
    return [
        triangle
        for index in range(size - 1)
        for triangle in (
            [index, index + 1, size + index + 1],
            [index, size + index + 1, size + index],
        )
    ]


def rank_two(vertices, triangle):
    a, b, c = (vertices[index] for index in triangle)
    first = tuple(b[axis] - a[axis] for axis in range(4))
    second = tuple(c[axis] - a[axis] for axis in range(4))
    return any(
        first[i] * second[j] - first[j] * second[i]
        for i in range(4)
        for j in range(i + 1, 4)
    )


def affine_zero(first, second):
    parameter = None
    for left, right in zip(first, second):
        if left == right:
            if left:
                return False
            continue
        candidate = -left / (right - left)
        if parameter is None:
            parameter = candidate
        elif parameter != candidate:
            return False
    return parameter is not None and 0 <= parameter <= 1


def verify_full():
    data = json.loads(DATA.read_text())
    collars = json.loads(COLLARS.read_text())
    if data["outer_collars_v7_receipt_sha256"] != collars["sha256"]:
        raise AssertionError("trace receipt is stale relative to V7 collars")
    path = resolve(data["cache_path"])
    if (
        path.stat().st_size != data["cache_size"]
        or file_sha(path) != data["cache_sha256"]
    ):
        raise AssertionError("trace cache bytes changed")
    digest = hashlib.sha256()
    records = edge_checks = core_triangles = push_triangles = phase_two = 0
    with (
        gzip.open(
            resolve(collars["cache_path"]), "rt", encoding="utf-8"
        ) as collar_source,
        gzip.open(path, "rt", encoding="utf-8") as trace_source,
    ):
        collar_source.readline()
        header_line = trace_source.readline()
        digest.update(header_line.encode())
        for collar_line, trace_line in zip(collar_source, trace_source, strict=True):
            digest.update(trace_line.encode())
            collar, trace = json.loads(collar_line), json.loads(trace_line)
            core = [point(value) for value in collar["final_core_vertices"]]
            normals = [point(value) for value in collar["final_normal_field"]]
            initial = subdivide(core[1], point(collar["source_core_segment"][-1]))
            final = core[1:]
            source_normal, target_normal = normals[1], normals[-1]
            initial_push = [add(value, source_normal) for value in initial]
            final_constant_push = [add(value, source_normal) for value in final]
            core_r4 = [spacetime(value, 0) for value in initial] + [
                spacetime(value, 1) for value in final
            ]
            push_r4 = [spacetime(value, 0) for value in initial_push] + [
                spacetime(value, 1) for value in final_constant_push
            ]
            cells = triangles(len(initial))
            expected = {
                "interface_index": collar["interface_index"],
                "initial_core_subdivision": [
                    [str(item) for item in value] for value in initial
                ],
                "final_core_route": [[str(item) for item in value] for value in final],
                "phase_one_core_spacetime_vertices": [
                    [str(item) for item in value] for value in core_r4
                ],
                "phase_one_core_trace_triangles": cells,
                "phase_one_push_initial_subdivision": [
                    [str(item) for item in value] for value in initial_push
                ],
                "phase_one_push_final_constant_normal_route": [
                    [str(item) for item in value] for value in final_constant_push
                ],
                "phase_one_push_spacetime_vertices": [
                    [str(item) for item in value] for value in push_r4
                ],
                "phase_one_push_trace_triangles": cells,
            }
            if any(trace[key] != value for key, value in expected.items()):
                raise AssertionError(
                    "trace geometry differs from independent reconstruction"
                )
            for initial_first, initial_second, final_first, final_second in zip(
                initial, initial[1:], final, final[1:]
            ):
                if affine_zero(
                    subtract(initial_second, initial_first),
                    subtract(final_second, final_first),
                ):
                    raise AssertionError("independent trace edge collapses")
                edge_checks += 1
            if not all(
                rank_two(core_r4, cell) and rank_two(push_r4, cell) for cell in cells
            ):
                raise AssertionError("independent phase-one R4 rank check failed")
            pivot = final_constant_push[-2]
            phase_two_vertices = [
                spacetime(pivot, 0),
                spacetime(final_constant_push[-1], 0),
                spacetime(add(final[-1], target_normal), 1),
                spacetime(pivot, 1),
            ]
            phase_two_cells = [[0, 1, 2], [0, 2, 3]]
            if [
                point(value) for value in trace["phase_two_push_spacetime_vertices"]
            ] != phase_two_vertices or trace[
                "phase_two_push_trace_triangles"
            ] != phase_two_cells:
                raise AssertionError("independent phase-two trace changed")
            if not all(rank_two(phase_two_vertices, cell) for cell in phase_two_cells):
                raise AssertionError("independent phase-two R4 rank check failed")
            if (
                trace["classification"] != "CANDIDATE_UNVERIFIED"
                or trace["spacetime_global_embeddedness_status"] != "OPEN"
            ):
                raise AssertionError("local trace overclaims global completion")
            records += 1
            core_triangles += len(cells)
            push_triangles += len(cells)
            phase_two += len(phase_two_cells)
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("trace decompressed stream changed")
    if (records, edge_checks, core_triangles, push_triangles, phase_two) != (
        3026,
        15130,
        30260,
        30260,
        6052,
    ):
        raise AssertionError("trace replay totals changed")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_ISOTOPY_TRACE_FULL_LOCAL_CANDIDATE",
        "cache_sha_checked": True,
        "traces_reconstructed": records,
        "edge_noncollapse_checks": edge_checks,
        "core_trace_triangles": core_triangles,
        "push_trace_triangles": push_triangles,
        "phase_two_push_trace_triangles": phase_two,
        "classification": "CANDIDATE_UNVERIFIED",
        "spacetime_global_embeddedness": "OPEN",
        "ambient_support": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
