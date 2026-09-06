#!/usr/bin/env python3
"""Independently reconstruct the comprehensive global-time V7 trace."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_v2_receipt.json"
V1 = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
V1_VERIFY = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_verification.json"
HALF = Fraction(1, 2)


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


def encode(value):
    return [str(coordinate) for coordinate in value]


def rescale(value, offset):
    coordinates = point(value)
    return (*coordinates[:3], offset + coordinates[3] * HALF)


def stationary(path):
    return [(*value, HALF) for value in path] + [
        (*value, Fraction(1)) for value in path
    ]


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


def verify_full():
    data = json.loads(DATA.read_text())
    v1 = json.loads(V1.read_text())
    v1_verification = json.loads(V1_VERIFY.read_text())
    if (
        data["local_phase_trace_receipt_sha256"] != v1["sha256"]
        or data["local_phase_trace_verification_sha256"] != v1_verification["sha256"]
        or v1_verification["construction_receipt_sha256"] != v1["sha256"]
    ):
        raise AssertionError("comprehensive trace is stale relative to verified V1")
    path = resolve(data["cache_path"])
    if (
        path.stat().st_size != data["cache_size"]
        or file_sha(path) != data["cache_sha256"]
    ):
        raise AssertionError("comprehensive trace cache bytes changed")

    digest = hashlib.sha256()
    counts = {
        "records": 0,
        "phase_one_core": 0,
        "phase_two_core": 0,
        "phase_one_push": 0,
        "phase_two_push_prefix": 0,
        "phase_two_push_terminal": 0,
        "rank": 0,
        "matches": 0,
    }
    with (
        gzip.open(resolve(v1["cache_path"]), "rt", encoding="utf-8") as source,
        gzip.open(path, "rt", encoding="utf-8") as candidate,
    ):
        source.readline()
        header_line = candidate.readline()
        digest.update(header_line.encode())
        header = json.loads(header_line)
        if (
            header["schema"] != "t73_x_m1_outer_collar_v7_isotopy_trace/v2"
            or header["global_phase_intervals"]
            != {"phase_one": ["0", "1/2"], "phase_two": ["1/2", "1"]}
            or not header["classification"].startswith("CANDIDATE_UNVERIFIED")
        ):
            raise AssertionError("comprehensive trace header changed")

        for old_line, new_line in zip(source, candidate, strict=True):
            digest.update(new_line.encode())
            old, new = json.loads(old_line), json.loads(new_line)
            final_core = [point(value) for value in old["final_core_route"]]
            final_push = [
                point(value)
                for value in old["phase_one_push_final_constant_normal_route"]
            ]
            phase_one_core = [
                rescale(value, Fraction(0))
                for value in old["phase_one_core_spacetime_vertices"]
            ]
            phase_one_push = [
                rescale(value, Fraction(0))
                for value in old["phase_one_push_spacetime_vertices"]
            ]
            phase_two_core = stationary(final_core)
            phase_two_push_prefix = stationary(final_push[:-1])
            phase_two_push_terminal = [
                rescale(value, HALF)
                for value in old["phase_two_push_spacetime_vertices"]
            ]
            phase_one_cells = old["phase_one_core_trace_triangles"]
            phase_two_core_cells = triangles(len(final_core))
            phase_two_push_prefix_cells = triangles(len(final_push) - 1)
            phase_two_terminal_cells = old["phase_two_push_trace_triangles"]

            expected = {
                "interface_index": old["interface_index"],
                "band_index": old["band_index"],
                "component": old["component"],
                "side": old["side"],
                "neighbor_kind": old["neighbor_kind"],
                "neighbor_id": old["neighbor_id"],
                "phase_one_core_spacetime_vertices": [
                    encode(value) for value in phase_one_core
                ],
                "phase_one_core_trace_triangles": phase_one_cells,
                "phase_two_stationary_core_spacetime_vertices": [
                    encode(value) for value in phase_two_core
                ],
                "phase_two_stationary_core_trace_triangles": phase_two_core_cells,
                "phase_one_push_spacetime_vertices": [
                    encode(value) for value in phase_one_push
                ],
                "phase_one_push_trace_triangles": phase_one_cells,
                "phase_two_stationary_push_prefix_spacetime_vertices": [
                    encode(value) for value in phase_two_push_prefix
                ],
                "phase_two_stationary_push_prefix_trace_triangles": phase_two_push_prefix_cells,
                "phase_two_terminal_push_spacetime_vertices": [
                    encode(value) for value in phase_two_push_terminal
                ],
                "phase_two_terminal_push_trace_triangles": phase_two_terminal_cells,
                "global_phase_boundary": "1/2",
                "phase_boundary_core_push_matches": 2,
                "spacetime_global_embeddedness_status": "OPEN",
                "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_EXTENSION",
                "classification": "CANDIDATE_UNVERIFIED",
            }
            if any(new.get(key) != value for key, value in expected.items()):
                raise AssertionError("trace differs from independent reconstruction")

            families = (
                (phase_one_core, phase_one_cells, "phase_one_core"),
                (phase_two_core, phase_two_core_cells, "phase_two_core"),
                (phase_one_push, phase_one_cells, "phase_one_push"),
                (
                    phase_two_push_prefix,
                    phase_two_push_prefix_cells,
                    "phase_two_push_prefix",
                ),
                (
                    phase_two_push_terminal,
                    phase_two_terminal_cells,
                    "phase_two_push_terminal",
                ),
            )
            for vertices, cells, count_key in families:
                if not all(rank_two(vertices, cell) for cell in cells):
                    raise AssertionError("independent R4 rank check failed")
                counts[count_key] += len(cells)
                counts["rank"] += len(cells)

            core_end = phase_one_core[len(final_core) :]
            push_end = phase_one_push[len(final_push) :]
            if (
                [value[:3] for value in core_end] != final_core
                or [value[:3] for value in push_end[:-1]] != final_push[:-1]
                or any(value[3] != HALF for value in core_end + push_end)
                or phase_two_core[: len(final_core)] != core_end
                or phase_two_push_prefix[: len(final_push) - 1] != push_end[:-1]
                or phase_two_push_terminal[0] != push_end[-2]
                or phase_two_push_terminal[1] != push_end[-1]
            ):
                raise AssertionError("phase boundary does not glue exactly")
            counts["records"] += 1
            counts["matches"] += 2

    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("comprehensive decompressed stream changed")
    expected_counts = {
        "records": 3026,
        "phase_one_core": 30260,
        "phase_two_core": 30260,
        "phase_one_push": 30260,
        "phase_two_push_prefix": 24208,
        "phase_two_push_terminal": 6052,
        "rank": 121040,
        "matches": 6052,
    }
    if counts != expected_counts:
        raise AssertionError(f"comprehensive replay totals changed: {counts}")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_COMPREHENSIVE_ISOTOPY_TRACE_V2_LOCAL",
        "cache_sha_checked": True,
        "traces_reconstructed": counts["records"],
        "complete_core_trace_triangles": counts["phase_one_core"]
        + counts["phase_two_core"],
        "complete_push_trace_triangles": counts["phase_one_push"]
        + counts["phase_two_push_prefix"]
        + counts["phase_two_push_terminal"],
        "r4_triangle_rank_checks": counts["rank"],
        "phase_boundary_core_push_matches": counts["matches"],
        "classification": "CANDIDATE_UNVERIFIED",
        "spacetime_global_embeddedness": "OPEN",
        "ambient_support": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
