#!/usr/bin/env python3
"""Compose both V7 trace phases in one global time and add stationary sheets."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path

from build_t73_x_m1_framed_outer_interface_collars import (
    canonical,
    canonical_sha,
    encode,
    file_sha,
    point,
)

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
V1_VERIFY = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_verification.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_v2_receipt.json"
DEFAULT_OUTPUT = (
    Path.home() / ".cache/t73_x_m1_outer_collar_v7_isotopy_trace_v2.jsonl.gz"
)
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


def rescale_phase_one(value):
    coordinates = point(value)
    return (*coordinates[:3], coordinates[3] * HALF)


def rescale_phase_two(value):
    coordinates = point(value)
    return (*coordinates[:3], HALF + coordinates[3] * HALF)


def stationary_vertices(path):
    return [(*value, HALF) for value in path] + [
        (*value, Fraction(1)) for value in path
    ]


def trace_triangles(size):
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


def build(output_path):
    v1 = json.loads(V1.read_text())
    verification = json.loads(V1_VERIFY.read_text())
    if verification["construction_receipt_sha256"] != v1["sha256"]:
        raise AssertionError("V1 trace verification is stale")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_outer_collar_v7_isotopy_trace/v2",
        "local_phase_trace_receipt_sha256": v1["sha256"],
        "local_phase_trace_verification_sha256": verification["sha256"],
        "global_phase_intervals": {
            "phase_one": ["0", "1/2"],
            "phase_two": ["1/2", "1"],
        },
        "classification": "CANDIDATE_UNVERIFIED_UNTIL_R4_GLOBAL_CLEARANCE_AND_AMBIENT_SUPPORT",
    }
    counts = {
        "records": 0,
        "phase_one_core": 0,
        "phase_two_core": 0,
        "phase_one_push": 0,
        "phase_two_push_prefix": 0,
        "phase_two_push_terminal": 0,
        "rank_checks": 0,
        "phase_boundary_matches": 0,
    }
    with (
        gzip.open(resolve(v1["cache_path"]), "rt", encoding="utf-8") as source,
        output_path.open("wb") as raw,
        gzip.GzipFile(
            filename="", fileobj=raw, mode="wb", compresslevel=6, mtime=0
        ) as output,
    ):
        source.readline()
        encoded = (canonical(header) + "\n").encode()
        output.write(encoded)
        digest.update(encoded)
        for line in source:
            old = json.loads(line)
            final_core = [point(value) for value in old["final_core_route"]]
            final_constant_push = [
                point(value)
                for value in old["phase_one_push_final_constant_normal_route"]
            ]
            phase_one_core_vertices = [
                rescale_phase_one(value)
                for value in old["phase_one_core_spacetime_vertices"]
            ]
            phase_one_push_vertices = [
                rescale_phase_one(value)
                for value in old["phase_one_push_spacetime_vertices"]
            ]
            phase_two_core_vertices = stationary_vertices(final_core)
            phase_two_push_prefix_vertices = stationary_vertices(
                final_constant_push[:-1]
            )
            phase_two_push_terminal_vertices = [
                rescale_phase_two(value)
                for value in old["phase_two_push_spacetime_vertices"]
            ]
            phase_one_cells = old["phase_one_core_trace_triangles"]
            phase_two_core_cells = trace_triangles(len(final_core))
            phase_two_push_prefix_cells = trace_triangles(len(final_constant_push) - 1)
            phase_two_terminal_cells = old["phase_two_push_trace_triangles"]
            families = (
                (phase_one_core_vertices, phase_one_cells),
                (phase_one_push_vertices, phase_one_cells),
                (phase_two_core_vertices, phase_two_core_cells),
                (phase_two_push_prefix_vertices, phase_two_push_prefix_cells),
                (phase_two_push_terminal_vertices, phase_two_terminal_cells),
            )
            for vertices, cells in families:
                for triangle in cells:
                    if not rank_two(vertices, triangle):
                        raise AssertionError(
                            "comprehensive V7 trace has a degenerate R4 triangle"
                        )
                    counts["rank_checks"] += 1
            if [
                value[:3] for value in phase_one_core_vertices[len(final_core) :]
            ] != final_core:
                raise AssertionError(
                    "phase-one core endpoint differs from phase-two core"
                )
            if [
                value[:3] for value in phase_one_push_vertices[len(final_core) : -1]
            ] != final_constant_push[:-1]:
                raise AssertionError(
                    "phase-one push prefix differs from phase-two prefix"
                )
            counts["phase_boundary_matches"] += 2
            record = {
                "record": "outer_collar_v7_comprehensive_isotopy_trace",
                "interface_index": old["interface_index"],
                "band_index": old["band_index"],
                "component": old["component"],
                "side": old["side"],
                "neighbor_kind": old["neighbor_kind"],
                "neighbor_id": old["neighbor_id"],
                "phase_one_core_spacetime_vertices": [
                    encode(value) for value in phase_one_core_vertices
                ],
                "phase_one_core_trace_triangles": phase_one_cells,
                "phase_two_stationary_core_spacetime_vertices": [
                    encode(value) for value in phase_two_core_vertices
                ],
                "phase_two_stationary_core_trace_triangles": phase_two_core_cells,
                "phase_one_push_spacetime_vertices": [
                    encode(value) for value in phase_one_push_vertices
                ],
                "phase_one_push_trace_triangles": phase_one_cells,
                "phase_two_stationary_push_prefix_spacetime_vertices": [
                    encode(value) for value in phase_two_push_prefix_vertices
                ],
                "phase_two_stationary_push_prefix_trace_triangles": phase_two_push_prefix_cells,
                "phase_two_terminal_push_spacetime_vertices": [
                    encode(value) for value in phase_two_push_terminal_vertices
                ],
                "phase_two_terminal_push_trace_triangles": phase_two_terminal_cells,
                "global_phase_boundary": "1/2",
                "phase_boundary_core_push_matches": 2,
                "spacetime_global_embeddedness_status": "OPEN",
                "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_EXTENSION",
                "classification": "CANDIDATE_UNVERIFIED",
            }
            encoded = (canonical(record) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            counts["records"] += 1
            counts["phase_one_core"] += len(phase_one_cells)
            counts["phase_two_core"] += len(phase_two_core_cells)
            counts["phase_one_push"] += len(phase_one_cells)
            counts["phase_two_push_prefix"] += len(phase_two_push_prefix_cells)
            counts["phase_two_push_terminal"] += len(phase_two_terminal_cells)
    receipt = {
        "schema": "t73_x_m1_outer_collar_v7_isotopy_trace_v2_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha(Path(__file__)),
        "local_phase_trace_receipt_sha256": v1["sha256"],
        "local_phase_trace_verification_sha256": verification["sha256"],
        "trace_count": counts["records"],
        "phase_one_core_trace_triangle_count": counts["phase_one_core"],
        "phase_two_stationary_core_trace_triangle_count": counts["phase_two_core"],
        "complete_core_trace_triangle_count": counts["phase_one_core"]
        + counts["phase_two_core"],
        "phase_one_push_trace_triangle_count": counts["phase_one_push"],
        "phase_two_stationary_push_prefix_triangle_count": counts[
            "phase_two_push_prefix"
        ],
        "phase_two_terminal_push_trace_triangle_count": counts[
            "phase_two_push_terminal"
        ],
        "complete_push_trace_triangle_count": counts["phase_one_push"]
        + counts["phase_two_push_prefix"]
        + counts["phase_two_push_terminal"],
        "r4_triangle_rank_check_count": counts["rank_checks"],
        "phase_boundary_core_push_match_count": counts["phase_boundary_matches"],
        "global_phase_intervals": {
            "phase_one": ["0", "1/2"],
            "phase_two": ["1/2", "1"],
        },
        "classification": "CANDIDATE_UNVERIFIED",
        "spacetime_global_embeddedness_status": "OPEN",
        "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_EXTENSION",
        "completion_status": "COMPLETE_CORE_AND_PUSH_WORLD_SHEETS_IN_ONE_GLOBAL_TIME",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_COMPREHENSIVE_ISOTOPY_TRACE_V2_LOCAL",
    }
    receipt["sha256"] = canonical_sha(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build(
        args.output
        or Path(os.environ.get("T73_X_M1_V7_TRACE_V2_CACHE", DEFAULT_OUTPUT))
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "traces": result["trace_count"],
                "core_triangles": result["complete_core_trace_triangle_count"],
                "push_triangles": result["complete_push_trace_triangle_count"],
                "rank_checks": result["r4_triangle_rank_check_count"],
                "phase_matches": result["phase_boundary_core_push_match_count"],
                "classification": result["classification"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
