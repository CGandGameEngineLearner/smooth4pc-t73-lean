#!/usr/bin/env python3
"""Independently replay the reverse sequential ribbon world-volume."""

from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

from verify_t73_x_m1_outer_collar_v7_sequential_framed_isotopy_volume import (
    PRISM_TETRAHEDRA,
    encode,
    file_sha,
    point,
    resolve,
    ribbon_triangles,
    verify_prism_template,
    volume,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_framed_isotopy_volume_receipt.json"
)
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
    verify_prism_template()
    data = json.loads(DATA.read_text())
    v1 = json.loads(V1.read_text())
    reverse = json.loads(REVERSE.read_text())
    reverse_verification = json.loads(REVERSE_VERIFY.read_text())
    static_ribbon = json.loads(STATIC_RIBBON.read_text())
    if (
        data["reverse_trace_receipt_sha256"] != reverse["sha256"]
        or data["reverse_trace_verification_sha256"] != reverse_verification["sha256"]
        or data["reverse_static_ribbon_clearance_sha256"] != static_ribbon["sha256"]
        or reverse["local_trace_receipt_sha256"] != v1["sha256"]
    ):
        raise AssertionError("reverse framed-volume bindings changed")
    path = resolve(data["cache_path"])
    if (
        path.stat().st_size != data["cache_size"]
        or file_sha(path) != data["cache_sha256"]
    ):
        raise AssertionError("reverse framed-volume cache bytes changed")
    records = load_records(v1)
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
            != "t73_x_m1_outer_collar_v7_reverse_sequential_framed_isotopy_volume/v1"
            or header["triangular_prism_tetrahedra"]
            != [list(value) for value in PRISM_TETRAHEDRA]
            or not header["classification"].startswith("CANDIDATE_UNVERIFIED")
        ):
            raise AssertionError("reverse framed-volume header changed")
        for position, (interface, line) in enumerate(
            zip(order, candidate, strict=True)
        ):
            digest.update(line.encode())
            old = records[interface]
            new = json.loads(line)
            start = Fraction(position, TRACE_COUNT)
            middle = Fraction(2 * position + 1, 2 * TRACE_COUNT)
            end = Fraction(position + 1, TRACE_COUNT)
            if start != previous_end:
                raise AssertionError("reverse volume slots overlap or leave a gap")
            previous_end = end
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
            initial = ribbon_triangles(initial_core, initial_push)
            constant = ribbon_triangles(final_core, constant_push)
            final = ribbon_triangles(final_core, final_push)
            families = {
                "source_stationary": (
                    volume(initial, initial, Fraction(0), start) if start else ([], [])
                ),
                "phase_one_moving": volume(initial, constant, start, middle),
                "phase_two_stationary_prefix": volume(
                    constant[:-2], constant[:-2], middle, end
                ),
                "phase_two_moving_terminal": volume(
                    constant[-2:], final[-2:], middle, end
                ),
                "final_stationary": (
                    volume(final, final, end, Fraction(1)) if end < 1 else ([], [])
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
                "boundary_match_count": 5,
                "moving_volume_interiors_pairwise_time_disjoint": True,
                "reverse_moving_static_volume_clearance_status": "OPEN",
                "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_EXTENSION",
                "classification": "CANDIDATE_UNVERIFIED",
            }
            prism_counts = {
                "source_stationary": len(initial) if start else 0,
                "phase_one_moving": len(initial),
                "phase_two_stationary_prefix": len(constant) - 2,
                "phase_two_moving_terminal": 2,
                "final_stationary": len(final) if end < 1 else 0,
            }
            for name, (vertices, tetrahedra) in families.items():
                expected[f"{name}_spacetime_vertices"] = encode(vertices)
                expected[f"{name}_tetrahedra"] = tetrahedra
                expected[f"{name}_prism_count"] = prism_counts[name]
                counts[name] += len(tetrahedra)
                counts["rank"] += len(tetrahedra)
            if any(new.get(key) != value for key, value in expected.items()):
                raise AssertionError("reverse volume reconstruction changed")
            counts["records"] += 1
            counts["boundary_matches"] += 5
    if previous_end != 1:
        raise AssertionError("reverse volume does not cover global time")
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("reverse volume stream changed")
    expected_counts = Counter(
        {
            "records": 3026,
            "source_stationary": 90750,
            "phase_one_moving": 90780,
            "phase_two_stationary_prefix": 72624,
            "phase_two_moving_terminal": 18156,
            "final_stationary": 90750,
            "rank": 363060,
            "boundary_matches": 15130,
        }
    )
    if counts != expected_counts:
        raise AssertionError(f"reverse volume totals changed: {counts}")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_REVERSE_SEQUENTIAL_FRAMED_ISOTOPY_VOLUME_FULL_LOCAL_CANDIDATE",
        "cache_sha_checked": True,
        "schedule_first_interface": order[0],
        "schedule_last_interface": order[-1],
        "traces_reconstructed": counts["records"],
        "triangular_prisms_reconstructed": counts["rank"] // 3,
        "r4_tetrahedra": counts["rank"],
        "r4_rank_checks": counts["rank"],
        "boundary_matches": counts["boundary_matches"],
        "moving_volume_interiors_pairwise_time_disjoint": True,
        "reverse_moving_static_volume_clearance": "OPEN",
        "ambient_support": "OPEN",
        "classification": "CANDIDATE_UNVERIFIED",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
