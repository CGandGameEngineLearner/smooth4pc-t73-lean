#!/usr/bin/env python3
"""Build the framed ribbon world-volume for the reverse V7 schedule."""

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
    file_sha,
    point,
)
from build_t73_x_m1_outer_collar_v7_reverse_sequential_isotopy_trace import (
    load_local_records,
)
from build_t73_x_m1_outer_collar_v7_sequential_framed_isotopy_volume import (
    PRISM_TETRAHEDRA,
    add_family,
    empty_family,
    ribbon_triangles,
)

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
REVERSE = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_isotopy_trace_receipt.json"
)
REVERSE_VERIFY = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_isotopy_trace_verification.json"
)
STATIC_RIBBON = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_static_ribbon_clearance.json"
)
OUTPUT_RECEIPT = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_framed_isotopy_volume_receipt.json"
)
DEFAULT_OUTPUT = (
    Path.home()
    / ".cache/t73_x_m1_outer_collar_v7_reverse_sequential_framed_isotopy_volume.jsonl.gz"
)
TRACE_COUNT = 3026


def build(output_path):
    v1 = json.loads(V1.read_text())
    reverse = json.loads(REVERSE.read_text())
    verification = json.loads(REVERSE_VERIFY.read_text())
    static_ribbon = json.loads(STATIC_RIBBON.read_text())
    if (
        reverse["local_trace_receipt_sha256"] != v1["sha256"]
        or verification["construction_receipt_sha256"] != reverse["sha256"]
        or static_ribbon["outer_collars_v7_receipt_sha256"]
        != v1["outer_collars_v7_receipt_sha256"]
        or not static_ribbon["reverse_mixed_static_ribbon_clearance"]
    ):
        raise AssertionError("reverse framed-volume inputs are stale or failed")
    records = load_local_records(v1)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_outer_collar_v7_reverse_sequential_framed_isotopy_volume/v1",
        "reverse_trace_receipt_sha256": reverse["sha256"],
        "reverse_trace_verification_sha256": verification["sha256"],
        "reverse_static_ribbon_clearance_sha256": static_ribbon["sha256"],
        "triangular_prism_tetrahedra": [list(value) for value in PRISM_TETRAHEDRA],
        "classification": "CANDIDATE_UNVERIFIED_UNTIL_REVERSE_R4_VOLUME_CLEARANCE_AND_AMBIENT_SUPPORT",
    }
    counts = {
        "records": 0,
        "source_stationary": 0,
        "phase_one_moving": 0,
        "phase_two_stationary_prefix": 0,
        "phase_two_moving_terminal": 0,
        "final_stationary": 0,
        "rank": 0,
        "boundary_matches": 0,
    }
    order = list(reversed(range(TRACE_COUNT)))
    with (
        output_path.open("wb") as raw,
        gzip.GzipFile(
            filename="", fileobj=raw, mode="wb", compresslevel=6, mtime=0
        ) as output,
    ):
        encoded = (canonical(header) + "\n").encode()
        output.write(encoded)
        digest.update(encoded)
        for position, interface in enumerate(order):
            old = records[interface]
            start = Fraction(position, TRACE_COUNT)
            middle = Fraction(2 * position + 1, 2 * TRACE_COUNT)
            end = Fraction(position + 1, TRACE_COUNT)
            initial_core = [point(value) for value in old["initial_core_subdivision"]]
            initial_push = [
                point(value) for value in old["phase_one_push_initial_subdivision"]
            ]
            final_core = [point(value) for value in old["final_core_route"]]
            constant_push = [
                point(value)
                for value in old["phase_one_push_final_constant_normal_route"]
            ]
            local_terminal = [
                point(value) for value in old["phase_two_push_spacetime_vertices"]
            ]
            final_push = constant_push[:-1] + [local_terminal[2][:3]]
            initial_ribbon = ribbon_triangles(initial_core, initial_push)
            constant_ribbon = ribbon_triangles(final_core, constant_push)
            final_ribbon = ribbon_triangles(final_core, final_push)
            record = {
                "record": "outer_collar_v7_reverse_sequential_framed_isotopy_volume",
                "schedule_position": position,
                "interface_index": interface,
                "band_index": old["band_index"],
                "component": old["component"],
                "side": old["side"],
                "neighbor_kind": old["neighbor_kind"],
                "neighbor_id": old["neighbor_id"],
                "time_interval": [str(start), str(end)],
                "phase_one_interval": [str(start), str(middle)],
                "phase_two_interval": [str(middle), str(end)],
            }
            if start:
                add_family(
                    record,
                    counts,
                    "source_stationary",
                    initial_ribbon,
                    initial_ribbon,
                    Fraction(0),
                    start,
                )
            else:
                empty_family(record, "source_stationary")
            add_family(
                record,
                counts,
                "phase_one_moving",
                initial_ribbon,
                constant_ribbon,
                start,
                middle,
            )
            add_family(
                record,
                counts,
                "phase_two_stationary_prefix",
                constant_ribbon[:-2],
                constant_ribbon[:-2],
                middle,
                end,
            )
            add_family(
                record,
                counts,
                "phase_two_moving_terminal",
                constant_ribbon[-2:],
                final_ribbon[-2:],
                middle,
                end,
            )
            if end < 1:
                add_family(
                    record,
                    counts,
                    "final_stationary",
                    final_ribbon,
                    final_ribbon,
                    end,
                    Fraction(1),
                )
            else:
                empty_family(record, "final_stationary")
            counts["boundary_matches"] += 5
            record.update(
                {
                    "boundary_match_count": 5,
                    "moving_volume_interiors_pairwise_time_disjoint": True,
                    "reverse_moving_static_volume_clearance_status": "OPEN",
                    "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_EXTENSION",
                    "classification": "CANDIDATE_UNVERIFIED",
                }
            )
            encoded = (canonical(record) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            counts["records"] += 1
    expected = {
        "records": 3026,
        "source_stationary": 90750,
        "phase_one_moving": 90780,
        "phase_two_stationary_prefix": 72624,
        "phase_two_moving_terminal": 18156,
        "final_stationary": 90750,
        "rank": 363060,
        "boundary_matches": 15130,
    }
    if counts != expected:
        raise AssertionError(f"reverse framed-volume totals changed: {counts}")
    receipt = {
        "schema": "t73_x_m1_outer_collar_v7_reverse_sequential_framed_isotopy_volume_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha(Path(__file__)),
        "reverse_trace_receipt_sha256": reverse["sha256"],
        "reverse_trace_verification_sha256": verification["sha256"],
        "reverse_static_ribbon_clearance_sha256": static_ribbon["sha256"],
        "schedule_order": "REVERSE_INTERFACE_INDEX",
        "trace_count": counts["records"],
        "source_stationary_tetrahedron_count": counts["source_stationary"],
        "phase_one_moving_tetrahedron_count": counts["phase_one_moving"],
        "phase_two_stationary_prefix_tetrahedron_count": counts[
            "phase_two_stationary_prefix"
        ],
        "phase_two_moving_terminal_tetrahedron_count": counts[
            "phase_two_moving_terminal"
        ],
        "final_stationary_tetrahedron_count": counts["final_stationary"],
        "total_r4_tetrahedron_count": counts["rank"],
        "r4_tetrahedron_rank_check_count": counts["rank"],
        "boundary_match_count": counts["boundary_matches"],
        "moving_volume_interiors_pairwise_time_disjoint": True,
        "reverse_moving_static_volume_clearance_status": "OPEN",
        "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_EXTENSION",
        "classification": "CANDIDATE_UNVERIFIED",
        "completion_status": "COMPLETE_REVERSE_SEQUENTIAL_FRAMED_RIBBON_WORLD_VOLUME",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_REVERSE_SEQUENTIAL_FRAMED_ISOTOPY_VOLUME_LOCAL",
    }
    receipt["sha256"] = canonical_sha(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(
        os.environ.get("T73_X_M1_V7_REVERSE_VOLUME_CACHE", DEFAULT_OUTPUT)
    )
    result = build(output)
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "traces": result["trace_count"],
                "tetrahedra": result["total_r4_tetrahedron_count"],
                "rank_checks": result["r4_tetrahedron_rank_check_count"],
                "boundary_matches": result["boundary_match_count"],
                "time_disjoint": result[
                    "moving_volume_interiors_pairwise_time_disjoint"
                ],
                "classification": result["classification"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
