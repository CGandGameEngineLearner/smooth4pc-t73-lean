#!/usr/bin/env python3
"""Repair straight outer collars by retaining source terminal germs."""

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
    cross,
    encode,
    file_sha,
    point,
    subtract,
)

ROOT = Path(__file__).resolve().parents[1]
GAP = ROOT / "audit/t73_x_m1_complete_framed_outer_interface_gap.json"
V1 = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_receipt.json"
OBSTRUCTION = ROOT / "audit/t73_x_m1_outer_collar_ribbon_self_clearance.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v2_receipt.json"
DEFAULT_OUTPUT = (
    Path.home() / ".cache/t73_x_m1_framed_outer_interface_collars_v2.jsonl.gz"
)
GERM_FRACTION = Fraction(1, 1_000_000)


def scale(factor, value):
    return tuple(factor * coordinate for coordinate in value)


def build(output_path):
    gap = json.loads(GAP.read_text())
    v1 = json.loads(V1.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    if obstruction["classification"] != "CANDIDATE_REFUTED":
        raise AssertionError(
            "v2 collar repair requires the saved v1 ribbon obstruction"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_framed_outer_interface_collars/v2",
        "outer_interface_gap_sha256": gap["sha256"],
        "refuted_v1_receipt_sha256": v1["sha256"],
        "v1_ribbon_obstruction_sha256": obstruction["sha256"],
        "source_germ_fraction": str(GERM_FRACTION),
        "construction_classification": "CANDIDATE_UNVERIFIED_UNTIL_GLOBAL_CLEARANCE_AND_AMBIENT_SUPPORT",
    }
    records = segments = triangles = phase_one_checks = phase_two_checks = 0
    with (
        output_path.open("wb") as raw,
        gzip.GzipFile(
            filename="", fileobj=raw, mode="wb", compresslevel=6, mtime=0
        ) as output,
    ):
        encoded = (canonical(header) + "\n").encode()
        output.write(encoded)
        digest.update(encoded)
        for interface in gap["interfaces"]:
            inner = point(interface["source_inner_core"])
            source = point(interface["source_core_port"])
            target = point(interface["target_core_port"])
            source_normal = subtract(point(interface["source_push_port"]), source)
            target_normal = subtract(point(interface["target_push_port"]), target)
            germ = add(inner, scale(GERM_FRACTION, subtract(source, inner)))
            germ_push = add(germ, source_normal)
            inner_push = add(inner, source_normal)
            target_push = add(target, target_normal)
            constant_target_push = add(target, source_normal)
            if germ in (inner, source):
                raise AssertionError("v2 source collar germ collapsed")
            retained_tangent = subtract(germ, inner)
            initial_moving_tangent = subtract(source, germ)
            final_moving_tangent = subtract(target, germ)
            if cross(retained_tangent, source_normal) == (0, 0, 0):
                raise AssertionError("v2 retained source germ loses transversality")
            if affine_vector_hits_zero(initial_moving_tangent, final_moving_tangent):
                raise AssertionError("v2 moving core segment collapses")
            if affine_vector_hits_zero(
                cross(initial_moving_tangent, source_normal),
                cross(final_moving_tangent, source_normal),
            ):
                raise AssertionError("v2 phase-one source normal becomes tangent")
            if affine_vector_hits_zero(
                cross(final_moving_tangent, source_normal),
                cross(final_moving_tangent, target_normal),
            ):
                raise AssertionError("v2 phase-two endpoint normal becomes tangent")
            core = [inner, germ, target]
            push = [inner_push, germ_push, target_push]
            record = {
                "record": "framed_outer_interface_collar_v2",
                "interface_index": interface["interface_index"],
                "band_index": interface["band_index"],
                "component": interface["component"],
                "side": interface["side"],
                "neighbor_kind": interface["neighbor_kind"],
                "neighbor_id": interface["neighbor_id"],
                "source_core_segment": [
                    interface["source_inner_core"],
                    interface["source_core_port"],
                ],
                "source_push_segment": [
                    interface["source_inner_push"],
                    interface["source_push_port"],
                ],
                "source_germ_fraction": str(GERM_FRACTION),
                "final_core_vertices": [encode(value) for value in core],
                "final_normal_field": [
                    encode(source_normal),
                    encode(source_normal),
                    encode(target_normal),
                ],
                "final_push_vertices": [encode(value) for value in push],
                "final_ribbon_triangles": [[0, 1, 4], [0, 4, 3], [1, 2, 5], [1, 5, 4]],
                "phase_one_core_isotopy_trace_triangle": [
                    encode(germ),
                    encode(source),
                    encode(target),
                ],
                "phase_one_constant_push_trace_triangle": [
                    encode(germ_push),
                    interface["source_push_port"],
                    encode(constant_target_push),
                ],
                "phase_two_terminal_push_interval": [
                    encode(constant_target_push),
                    encode(target_push),
                ],
                "retained_source_germ": True,
                "phase_one_core_noncollapse": True,
                "phase_one_normal_transversality": True,
                "phase_two_normal_transversality": True,
                "relative_twist": 0,
                "global_core_push_ribbon_clearance_status": "OPEN",
                "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_ISOTOPY_EXTENSION",
                "classification": "CANDIDATE_UNVERIFIED",
            }
            encoded = (canonical(record) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            records += 1
            segments += 2
            triangles += 4
            phase_one_checks += 3
            phase_two_checks += 1
    receipt = {
        "schema": "t73_x_m1_framed_outer_interface_collars_v2_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha(Path(__file__)),
        "outer_interface_gap_sha256": gap["sha256"],
        "refuted_v1_receipt_sha256": v1["sha256"],
        "v1_ribbon_obstruction_sha256": obstruction["sha256"],
        "source_germ_fraction": str(GERM_FRACTION),
        "collar_count": records,
        "final_core_segment_count": segments,
        "final_push_segment_count": segments,
        "final_ribbon_triangle_count": triangles,
        "phase_one_exact_parameter_checks": phase_one_checks,
        "phase_two_exact_parameter_checks": phase_two_checks,
        "relative_twist_sum": 0,
        "classification": "CANDIDATE_UNVERIFIED",
        "global_clearance_status": "OPEN",
        "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_ISOTOPY_EXTENSION",
        "completion_status": "ALL_OUTER_INTERFACE_COLLAR_V2_CANDIDATES_RETAIN_SOURCE_GERMS",
        "verdict": "PASS_X_M1_FRAMED_OUTER_INTERFACE_COLLARS_V2_LOCAL_CANDIDATE",
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
        or Path(os.environ.get("T73_X_M1_OUTER_COLLAR_V2_CACHE", DEFAULT_OUTPUT))
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "collars": result["collar_count"],
                "segments": result["final_core_segment_count"],
                "triangles": result["final_ribbon_triangle_count"],
                "classification": result["classification"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
