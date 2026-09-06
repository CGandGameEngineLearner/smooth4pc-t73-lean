#!/usr/bin/env python3
"""Construct the two-phase simplicial spacetime trace for every V7 collar."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path

from build_t73_x_m1_framed_outer_interface_collars import (
    add,
    affine_vector_hits_zero,
    canonical,
    canonical_sha,
    encode,
    file_sha,
    point,
    subtract,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
INTERNAL = ROOT / "audit/t73_x_m1_outer_collar_v7_ribbon_clearance.json"
REPLACEMENT = ROOT / "audit/t73_x_m1_outer_collar_v7_replacement_ribbon_clearance.json"
RETAINED = ROOT / "audit/t73_x_m1_outer_collar_v7_retained_ribbon_clearance.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_m1_outer_collar_v7_isotopy_trace.jsonl.gz"
MOVING_SEGMENT_COUNT = 5


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def scale(factor, value):
    return tuple(factor * coordinate for coordinate in value)


def subdivide(first, second, count):
    delta = subtract(second, first)
    return [
        add(first, scale(Fraction(index, count), delta)) for index in range(count + 1)
    ]


def spacetime(value, time):
    return (*value, Fraction(time))


def trace_triangles(size):
    return [
        triangle
        for index in range(size - 1)
        for triangle in (
            [index, index + 1, size + index + 1],
            [index, size + index + 1, size + index],
        )
    ]


def rank_two_triangle(vertices, triangle):
    a, b, c = (vertices[index] for index in triangle)
    first = tuple(b[axis] - a[axis] for axis in range(4))
    second = tuple(c[axis] - a[axis] for axis in range(4))
    return any(
        first[i] * second[j] - first[j] * second[i]
        for i in range(4)
        for j in range(i + 1, 4)
    )


def build(output_path):
    collars = json.loads(COLLARS.read_text())
    internal = json.loads(INTERNAL.read_text())
    replacement = json.loads(REPLACEMENT.read_text())
    retained = json.loads(RETAINED.read_text())
    if (
        internal["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or not internal["global_ribbon_clearance"]
    ):
        raise AssertionError("V7 internal ribbon clearance is stale or failed")
    if (
        replacement["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or not replacement["global_replacement_cross_clearance"]
    ):
        raise AssertionError("V7 replacement cross-clearance is stale or failed")
    if (
        retained["candidate_matrix_sha256"] == ""
        or not retained["global_retained_cross_clearance"]
    ):
        raise AssertionError("V7 retained cross-clearance is stale or failed")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_outer_collar_v7_isotopy_trace/v1",
        "outer_collars_v7_receipt_sha256": collars["sha256"],
        "internal_ribbon_clearance_sha256": internal["sha256"],
        "replacement_cross_clearance_sha256": replacement["sha256"],
        "retained_cross_clearance_sha256": retained["sha256"],
        "initial_moving_segment_subdivision_count": MOVING_SEGMENT_COUNT,
        "phase_order": [
            "phase1_core_route_with_constant_source_normal",
            "phase2_terminal_normal_homotopy_at_fixed_core",
        ],
        "classification": "CANDIDATE_UNVERIFIED_UNTIL_SPACETIME_EMBEDDEDNESS_AND_AMBIENT_SUPPORT",
    }
    records = edge_checks = core_triangles = push_triangles = phase_two_triangles = 0
    with (
        gzip.open(resolve(collars["cache_path"]), "rt", encoding="utf-8") as source,
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
            collar = json.loads(line)
            core = [point(value) for value in collar["final_core_vertices"]]
            normals = [point(value) for value in collar["final_normal_field"]]
            germ = core[1]
            source_port = point(collar["source_core_segment"][-1])
            final_route = core[1:]
            initial_route = subdivide(germ, source_port, MOVING_SEGMENT_COUNT)
            if (
                len(initial_route) != len(final_route)
                or initial_route[0] != final_route[0]
            ):
                raise AssertionError("V7 trace boundary subdivision changed")
            for initial_first, initial_second, final_first, final_second in zip(
                initial_route,
                initial_route[1:],
                final_route,
                final_route[1:],
            ):
                if affine_vector_hits_zero(
                    subtract(initial_second, initial_first),
                    subtract(final_second, final_first),
                ):
                    raise AssertionError(
                        "V7 phase-one edge collapses at an intermediate time"
                    )
                edge_checks += 1
            source_normal = normals[1]
            target_normal = normals[-1]
            initial_push = [add(value, source_normal) for value in initial_route]
            constant_final_push = [add(value, source_normal) for value in final_route]
            core_vertices_r4 = [spacetime(value, 0) for value in initial_route] + [
                spacetime(value, 1) for value in final_route
            ]
            push_vertices_r4 = [spacetime(value, 0) for value in initial_push] + [
                spacetime(value, 1) for value in constant_final_push
            ]
            triangles = trace_triangles(len(initial_route))
            if not all(
                rank_two_triangle(core_vertices_r4, triangle) for triangle in triangles
            ):
                raise AssertionError("V7 core trace triangle degenerates in R4")
            if not all(
                rank_two_triangle(push_vertices_r4, triangle) for triangle in triangles
            ):
                raise AssertionError("V7 push trace triangle degenerates in R4")
            phase_two_pivot = constant_final_push[-2]
            phase_two_source = constant_final_push[-1]
            phase_two_target = add(final_route[-1], target_normal)
            phase_two_vertices_r4 = [
                spacetime(phase_two_pivot, 0),
                spacetime(phase_two_source, 0),
                spacetime(phase_two_target, 1),
                spacetime(phase_two_pivot, 1),
            ]
            phase_two_cells = [[0, 1, 2], [0, 2, 3]]
            if not all(
                rank_two_triangle(phase_two_vertices_r4, triangle)
                for triangle in phase_two_cells
            ):
                raise AssertionError(
                    "V7 phase-two push trace triangle degenerates in R4"
                )
            record = {
                "record": "outer_collar_v7_two_phase_isotopy_trace",
                "interface_index": collar["interface_index"],
                "band_index": collar["band_index"],
                "component": collar["component"],
                "side": collar["side"],
                "neighbor_kind": collar["neighbor_kind"],
                "neighbor_id": collar["neighbor_id"],
                "initial_core_subdivision": [encode(value) for value in initial_route],
                "final_core_route": [encode(value) for value in final_route],
                "phase_one_core_spacetime_vertices": [
                    encode(value) for value in core_vertices_r4
                ],
                "phase_one_core_trace_triangles": triangles,
                "phase_one_push_initial_subdivision": [
                    encode(value) for value in initial_push
                ],
                "phase_one_push_final_constant_normal_route": [
                    encode(value) for value in constant_final_push
                ],
                "phase_one_push_spacetime_vertices": [
                    encode(value) for value in push_vertices_r4
                ],
                "phase_one_push_trace_triangles": triangles,
                "phase_two_push_spacetime_vertices": [
                    encode(value) for value in phase_two_vertices_r4
                ],
                "phase_two_push_trace_triangles": phase_two_cells,
                "phase_one_edge_noncollapse_checks": MOVING_SEGMENT_COUNT,
                "relative_germ_track_fixed_in_r3": True,
                "phase_one_source_normal_constant": True,
                "phase_two_core_fixed": True,
                "relative_twist": 0,
                "spacetime_global_embeddedness_status": "OPEN",
                "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_EXTENSION",
                "classification": "CANDIDATE_UNVERIFIED",
            }
            encoded = (canonical(record) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            records += 1
            core_triangles += len(triangles)
            push_triangles += len(triangles)
            phase_two_triangles += len(phase_two_cells)
    receipt = {
        "schema": "t73_x_m1_outer_collar_v7_isotopy_trace_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha(Path(__file__)),
        "outer_collars_v7_receipt_sha256": collars["sha256"],
        "internal_ribbon_clearance_sha256": internal["sha256"],
        "replacement_cross_clearance_sha256": replacement["sha256"],
        "retained_cross_clearance_sha256": retained["sha256"],
        "trace_count": records,
        "initial_moving_segment_subdivision_count": MOVING_SEGMENT_COUNT,
        "phase_one_edge_noncollapse_check_count": edge_checks,
        "phase_one_core_trace_triangle_count": core_triangles,
        "phase_one_push_trace_triangle_count": push_triangles,
        "phase_two_push_trace_triangle_count": phase_two_triangles,
        "relative_twist_sum": 0,
        "classification": "CANDIDATE_UNVERIFIED",
        "spacetime_global_embeddedness_status": "OPEN",
        "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_EXTENSION",
        "completion_status": "ALL_V7_TWO_PHASE_SIMPLICIAL_ISOTOPY_TRACE_CANDIDATES_CONSTRUCTED",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_ISOTOPY_TRACE_LOCAL_CANDIDATE",
    }
    receipt["sha256"] = canonical_sha(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build(
        args.output or Path(os.environ.get("T73_X_M1_V7_TRACE_CACHE", DEFAULT_OUTPUT))
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "traces": result["trace_count"],
                "edge_checks": result["phase_one_edge_noncollapse_check_count"],
                "core_triangles": result["phase_one_core_trace_triangle_count"],
                "push_triangles": result["phase_one_push_trace_triangle_count"],
                "phase_two_triangles": result["phase_two_push_trace_triangle_count"],
                "classification": result["classification"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
