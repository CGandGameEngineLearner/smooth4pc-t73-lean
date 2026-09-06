#!/usr/bin/env python3
"""Independently replay the reverse-interface V7 schedule."""

from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

from verify_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import (
    cylinder,
    expected_family,
    file_sha,
    point,
    rescale,
    resolve,
    triangles,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_isotopy_trace_receipt.json"
)
V1 = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
V1_VERIFY = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_verification.json"
FORWARD_OBSTRUCTION = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_midpoint_obstruction.json"
)
TRACE_COUNT = 3026


def load_records(receipt):
    records = {}
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            records[record["interface_index"]] = record
    return records


def verify_full():
    data = json.loads(DATA.read_text())
    v1 = json.loads(V1.read_text())
    v1_verification = json.loads(V1_VERIFY.read_text())
    obstruction = json.loads(FORWARD_OBSTRUCTION.read_text())
    if (
        data["local_trace_receipt_sha256"] != v1["sha256"]
        or data["local_trace_verification_sha256"] != v1_verification["sha256"]
        or data["forward_schedule_obstruction_sha256"] != obstruction["sha256"]
        or obstruction["linear_spatial_interpolation_status"] != "REFUTED"
    ):
        raise AssertionError("reverse trace bindings changed")
    path = resolve(data["cache_path"])
    if (
        path.stat().st_size != data["cache_size"]
        or file_sha(path) != data["cache_sha256"]
    ):
        raise AssertionError("reverse trace cache bytes changed")
    local_records = load_records(v1)
    digest = hashlib.sha256()
    counts = Counter()
    previous_end = Fraction(0)
    order = list(reversed(range(TRACE_COUNT)))
    with gzip.open(path, "rt", encoding="utf-8") as candidate:
        header_line = candidate.readline()
        digest.update(header_line.encode())
        header = json.loads(header_line)
        if (
            header["schema"]
            != "t73_x_m1_outer_collar_v7_reverse_sequential_isotopy_trace/v1"
            or header["forward_schedule_obstruction_sha256"] != obstruction["sha256"]
            or not header["classification"].startswith("CANDIDATE_UNVERIFIED")
        ):
            raise AssertionError("reverse trace header changed")
        for position, (interface, new_line) in enumerate(
            zip(order, candidate, strict=True)
        ):
            digest.update(new_line.encode())
            old = local_records[interface]
            new = json.loads(new_line)
            start = Fraction(position, TRACE_COUNT)
            middle = Fraction(2 * position + 1, 2 * TRACE_COUNT)
            end = Fraction(position + 1, TRACE_COUNT)
            if start != previous_end:
                raise AssertionError("reverse slots overlap or leave a gap")
            previous_end = end
            initial_core = [point(value) for value in old["initial_core_subdivision"]]
            final_core = [point(value) for value in old["final_core_route"]]
            initial_push = [
                point(value) for value in old["phase_one_push_initial_subdivision"]
            ]
            constant_push = [
                point(value)
                for value in old["phase_one_push_final_constant_normal_route"]
            ]
            local_terminal = [
                point(value) for value in old["phase_two_push_spacetime_vertices"]
            ]
            final_push = constant_push[:-1] + [local_terminal[2][:3]]
            cells = triangles(6)
            prefix_cells = triangles(5)
            terminal_cells = old["phase_two_push_trace_triangles"]
            families = {
                "source_core": (
                    cylinder(initial_core, Fraction(0), start) if start else [],
                    cells if start else [],
                ),
                "moving_core": (
                    rescale(old["phase_one_core_spacetime_vertices"], start, middle),
                    cells,
                ),
                "final_core": (cylinder(final_core, middle, Fraction(1)), cells),
                "source_push": (
                    cylinder(initial_push, Fraction(0), start) if start else [],
                    cells if start else [],
                ),
                "moving_push": (
                    rescale(old["phase_one_push_spacetime_vertices"], start, middle),
                    cells,
                ),
                "phase_two_push_prefix": (
                    cylinder(constant_push[:-1], middle, end),
                    prefix_cells,
                ),
                "phase_two_push_terminal": (
                    rescale(old["phase_two_push_spacetime_vertices"], middle, end),
                    terminal_cells,
                ),
                "final_push": (
                    cylinder(final_push, end, Fraction(1)) if end < 1 else [],
                    cells if end < 1 else [],
                ),
            }
            expected = {
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
                "moving_sheet_interiors_pairwise_time_disjoint": True,
                "reverse_dynamic_clearance_status": "OPEN",
                "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_EXTENSION",
                "classification": "CANDIDATE_UNVERIFIED",
            }
            for name, (vertices, family_cells) in families.items():
                encoded_vertices, encoded_cells = expected_family(
                    vertices, family_cells
                )
                expected[f"{name}_spacetime_vertices"] = encoded_vertices
                expected[f"{name}_trace_triangles"] = encoded_cells
                counts[name] += len(family_cells)
                counts["rank"] += len(family_cells)
            if any(new.get(key) != value for key, value in expected.items()):
                raise AssertionError("reverse trace reconstruction changed")
            counts["records"] += 1
            counts["boundary_matches"] += 5
    if previous_end != 1:
        raise AssertionError("reverse schedule does not cover global time")
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("reverse decompressed stream changed")
    expected_counts = Counter(
        {
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
    )
    if counts != expected_counts:
        raise AssertionError(f"reverse trace totals changed: {counts}")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_REVERSE_SEQUENTIAL_ISOTOPY_TRACE_FULL_LOCAL_CANDIDATE",
        "cache_sha_checked": True,
        "schedule_first_interface": order[0],
        "schedule_last_interface": order[-1],
        "traces_reconstructed": counts["records"],
        "complete_core_world_sheet_triangles": counts["source_core"]
        + counts["moving_core"]
        + counts["final_core"],
        "complete_push_world_sheet_triangles": counts["source_push"]
        + counts["moving_push"]
        + counts["phase_two_push_prefix"]
        + counts["phase_two_push_terminal"]
        + counts["final_push"],
        "r4_triangle_rank_checks": counts["rank"],
        "boundary_matches": counts["boundary_matches"],
        "moving_sheet_interiors_pairwise_time_disjoint": True,
        "reverse_dynamic_clearance": "OPEN",
        "ambient_support": "OPEN",
        "classification": "CANDIDATE_UNVERIFIED",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
