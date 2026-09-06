#!/usr/bin/env python3
"""Schedule the V7 collar isotopies in reverse interface order."""

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
from build_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import (
    add_family,
    cylinder_vertices,
    rescale,
    resolve,
    trace_triangles,
)

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
V1_VERIFY = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_verification.json"
FORWARD_OBSTRUCTION = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_midpoint_obstruction.json"
)
OUTPUT_RECEIPT = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_isotopy_trace_receipt.json"
)
DEFAULT_OUTPUT = (
    Path.home()
    / ".cache/t73_x_m1_outer_collar_v7_reverse_sequential_isotopy_trace.jsonl.gz"
)
TRACE_COUNT = 3026


def load_local_records(receipt):
    records = {}
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            records[record["interface_index"]] = record
    if set(records) != set(range(TRACE_COUNT)):
        raise AssertionError("local trace interface inventory changed")
    return records


def build(output_path):
    v1 = json.loads(V1.read_text())
    verification = json.loads(V1_VERIFY.read_text())
    obstruction = json.loads(FORWARD_OBSTRUCTION.read_text())
    if (
        verification["construction_receipt_sha256"] != v1["sha256"]
        or obstruction["local_trace_receipt_sha256"] != v1["sha256"]
        or obstruction["linear_spatial_interpolation_status"] != "REFUTED"
        or obstruction["sequential_time_schedule_status"] != "RETAINED"
    ):
        raise AssertionError("reverse schedule inputs are stale or inconsistent")
    records = load_local_records(v1)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_outer_collar_v7_reverse_sequential_isotopy_trace/v1",
        "local_trace_receipt_sha256": v1["sha256"],
        "local_trace_verification_sha256": verification["sha256"],
        "forward_schedule_obstruction_sha256": obstruction["sha256"],
        "schedule": "position p moves interface 3025-p in [p/3026,(p+1)/3026]",
        "classification": "CANDIDATE_UNVERIFIED_UNTIL_REVERSE_DYNAMIC_CLEARANCE_AND_AMBIENT_SUPPORT",
    }
    counts = {
        "records": 0,
        "source_core": 0,
        "moving_core": 0,
        "final_core": 0,
        "source_push": 0,
        "moving_push": 0,
        "phase_two_push_prefix": 0,
        "phase_two_push_terminal": 0,
        "final_push": 0,
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
            final_core = [point(value) for value in old["final_core_route"]]
            initial_push = [
                point(value) for value in old["phase_one_push_initial_subdivision"]
            ]
            constant_push = [
                point(value)
                for value in old["phase_one_push_final_constant_normal_route"]
            ]
            phase_two_local = [
                point(value) for value in old["phase_two_push_spacetime_vertices"]
            ]
            final_push = constant_push[:-1] + [phase_two_local[2][:3]]
            cells = trace_triangles(len(initial_core))
            prefix_cells = trace_triangles(len(constant_push) - 1)
            terminal_cells = old["phase_two_push_trace_triangles"]
            families = {}
            if start:
                add_family(
                    families,
                    counts,
                    "source_core",
                    cylinder_vertices(initial_core, Fraction(0), start),
                    cells,
                )
                add_family(
                    families,
                    counts,
                    "source_push",
                    cylinder_vertices(initial_push, Fraction(0), start),
                    cells,
                )
            else:
                families["source_core_spacetime_vertices"] = []
                families["source_core_trace_triangles"] = []
                families["source_push_spacetime_vertices"] = []
                families["source_push_trace_triangles"] = []
            moving_core = rescale(
                old["phase_one_core_spacetime_vertices"], start, middle
            )
            moving_push = rescale(
                old["phase_one_push_spacetime_vertices"], start, middle
            )
            add_family(families, counts, "moving_core", moving_core, cells)
            add_family(families, counts, "moving_push", moving_push, cells)
            add_family(
                families,
                counts,
                "final_core",
                cylinder_vertices(final_core, middle, Fraction(1)),
                cells,
            )
            add_family(
                families,
                counts,
                "phase_two_push_prefix",
                cylinder_vertices(constant_push[:-1], middle, end),
                prefix_cells,
            )
            terminal = rescale(old["phase_two_push_spacetime_vertices"], middle, end)
            add_family(
                families,
                counts,
                "phase_two_push_terminal",
                terminal,
                terminal_cells,
            )
            if end < 1:
                add_family(
                    families,
                    counts,
                    "final_push",
                    cylinder_vertices(final_push, end, Fraction(1)),
                    cells,
                )
            else:
                families["final_push_spacetime_vertices"] = []
                families["final_push_trace_triangles"] = []
            if (
                [value[:3] for value in moving_core[: len(initial_core)]]
                != initial_core
                or [value[:3] for value in moving_core[len(initial_core) :]]
                != final_core
                or [value[:3] for value in moving_push[: len(initial_push)]]
                != initial_push
                or [value[:3] for value in moving_push[len(initial_push) :]]
                != constant_push
                or [value[:3] for value in terminal[:2]] != constant_push[-2:]
                or terminal[2][:3] != final_push[-1]
            ):
                raise AssertionError("reverse trace boundary mismatch")
            counts["boundary_matches"] += 5
            record = {
                "record": "outer_collar_v7_reverse_sequential_isotopy_trace",
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
                **families,
                "moving_sheet_interiors_pairwise_time_disjoint": True,
                "reverse_dynamic_clearance_status": "OPEN",
                "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_EXTENSION",
                "classification": "CANDIDATE_UNVERIFIED",
            }
            encoded = (canonical(record) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            counts["records"] += 1
    expected = {
        "records": 3026,
        "source_core": 30250,
        "moving_core": 30260,
        "final_core": 30260,
        "source_push": 30250,
        "moving_push": 30260,
        "phase_two_push_prefix": 24208,
        "phase_two_push_terminal": 6052,
        "final_push": 30250,
        "rank": 211790,
        "boundary_matches": 15130,
    }
    if counts != expected:
        raise AssertionError(f"reverse trace totals changed: {counts}")
    receipt = {
        "schema": "t73_x_m1_outer_collar_v7_reverse_sequential_isotopy_trace_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha(Path(__file__)),
        "local_trace_receipt_sha256": v1["sha256"],
        "local_trace_verification_sha256": verification["sha256"],
        "forward_schedule_obstruction_sha256": obstruction["sha256"],
        "schedule_order": "REVERSE_INTERFACE_INDEX",
        "schedule_first_interface": order[0],
        "schedule_last_interface": order[-1],
        "trace_count": counts["records"],
        "complete_core_world_sheet_triangle_count": counts["source_core"]
        + counts["moving_core"]
        + counts["final_core"],
        "complete_push_world_sheet_triangle_count": counts["source_push"]
        + counts["moving_push"]
        + counts["phase_two_push_prefix"]
        + counts["phase_two_push_terminal"]
        + counts["final_push"],
        "r4_triangle_rank_check_count": counts["rank"],
        "boundary_match_count": counts["boundary_matches"],
        "moving_sheet_interiors_pairwise_time_disjoint": True,
        "reverse_dynamic_clearance_status": "OPEN",
        "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_EXTENSION",
        "classification": "CANDIDATE_UNVERIFIED",
        "completion_status": "COMPLETE_REVERSE_SEQUENTIAL_CORE_AND_PUSH_WORLD_SHEETS",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_REVERSE_SEQUENTIAL_ISOTOPY_TRACE_LOCAL",
    }
    receipt["sha256"] = canonical_sha(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(
        os.environ.get("T73_X_M1_V7_REVERSE_TRACE_CACHE", DEFAULT_OUTPUT)
    )
    result = build(output)
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "first": result["schedule_first_interface"],
                "last": result["schedule_last_interface"],
                "traces": result["trace_count"],
                "core_triangles": result["complete_core_world_sheet_triangle_count"],
                "push_triangles": result["complete_push_world_sheet_triangle_count"],
                "rank_checks": result["r4_triangle_rank_check_count"],
                "classification": result["classification"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
