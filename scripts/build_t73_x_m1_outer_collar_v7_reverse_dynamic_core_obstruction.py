#!/usr/bin/env python3
"""Save the exact reverse-order dynamic core obstruction."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_core_push_clearance import segment_intersects
from build_t73_x_m1_outer_collar_v7_reverse_dynamic_core_candidate_matrix import (
    COLLARS,
    LOCAL,
    load_active,
    load_static,
)
from build_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import resolve
from verify_t73_candidate_t_band0_surface import (
    point_in_triangle,
    segment_triangle_parameter_interval,
    triangles_intersect,
)

ROOT = Path(__file__).resolve().parents[1]
MATRIX = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_dynamic_core_candidate_matrix.json"
)
REVERSE_VOLUME = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_framed_isotopy_volume_receipt.json"
)
FORWARD_OBSTRUCTION = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_midpoint_obstruction.json"
)
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_dynamic_core_obstruction.json"


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def contact_points(source, target):
    contacts = []
    for edge_index in range(3):
        segment = (source[edge_index], source[(edge_index + 1) % 3])
        interval = segment_triangle_parameter_interval(segment, target)
        if interval is None:
            continue
        for parameter in sorted(set(interval)):
            value = tuple(
                segment[0][axis] + parameter * (segment[1][axis] - segment[0][axis])
                for axis in range(4)
            )
            if not point_in_triangle(value, target):
                raise AssertionError("reported contact is not in target triangle")
            contacts.append(
                {
                    "edge_index": edge_index,
                    "parameter_interval": [str(item) for item in interval],
                    "witness_parameter": str(parameter),
                    "point": [str(item) for item in value],
                }
            )
    return contacts


def build():
    local = json.loads(LOCAL.read_text())
    collars = json.loads(COLLARS.read_text())
    matrix = json.loads(MATRIX.read_text())
    volume = json.loads(REVERSE_VOLUME.read_text())
    forward = json.loads(FORWARD_OBSTRUCTION.read_text())
    if (
        matrix["local_trace_receipt_sha256"] != local["sha256"]
        or matrix["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or matrix["reverse_framed_volume_receipt_sha256"] != volume["sha256"]
        or matrix["classification"] != "CANDIDATE_MATRIX_ONLY"
        or forward["active_interface"] != 2
        or forward["obstacle_interface"] != 0
        or forward["linear_spatial_interpolation_status"] != "REFUTED"
    ):
        raise AssertionError("reverse obstruction inputs are stale or inconsistent")
    active = load_active(local)
    sources, _finals = load_static(collars)
    active_triangle = next(
        triangle
        for interface, _type, local_index, triangle in active
        if interface == 2 and local_index == 0
    )
    source_triangle = next(
        triangle
        for interface, half, triangle in sources
        if interface == 0 and half == 1
    )
    if not triangles_intersect(active_triangle, source_triangle):
        raise AssertionError("reverse dynamic obstruction disappeared")
    contacts = contact_points(source_triangle, active_triangle)
    if [value["edge_index"] for value in contacts] != [0, 2]:
        raise AssertionError("reverse contact boundary changed")
    if len({value["point"][3] for value in contacts}) != 1:
        raise AssertionError("reverse contacts do not form one time slice")
    source_records = {}
    with gzip.open(resolve(local["cache_path"]), "rt", encoding="utf-8") as stream:
        stream.readline()
        for line in stream:
            record = json.loads(line)
            if record["interface_index"] in (0, 2):
                source_records[record["interface_index"]] = record
    source_segments = {
        interface: tuple(
            tuple(Fraction(coordinate) for coordinate in value)
            for value in source_records[interface]["initial_core_subdivision"][::5]
        )
        for interface in (0, 2)
    }
    if segment_intersects(source_segments[0], source_segments[2]):
        raise AssertionError("static source segments unexpectedly intersect")
    local_time = contacts[0]["point"][3]
    result = {
        "schema": "t73_x_m1_outer_collar_v7_reverse_dynamic_core_obstruction/v1",
        "reverse_dynamic_core_candidate_matrix_sha256": matrix["sha256"],
        "reverse_framed_volume_receipt_sha256": volume["sha256"],
        "forward_schedule_obstruction_sha256": forward["sha256"],
        "active_interface": 2,
        "active_local_triangle": 0,
        "active_semantic_type": "source_to_start_skew",
        "obstacle_kind": "LATER_SOURCE_COLLAR",
        "obstacle_interface": 0,
        "obstacle_vertical_half": 1,
        "local_phase_one_time": local_time,
        "intersection_dimension": 1,
        "intersection_segment_endpoints": [value["point"] for value in contacts],
        "static_source_segments_intersect": False,
        "contacts": contacts,
        "forward_order_0_before_2_status": "REFUTED_BY_FINAL_COLLISION",
        "reverse_order_2_before_0_status": "REFUTED_BY_SOURCE_COLLISION",
        "sequential_reordering_only_status": "REFUTED_FOR_INTERFACE_PAIR_0_2",
        "reverse_linear_trace_status": "CANDIDATE_REFUTED",
        "reverse_framed_volume_status": "CANDIDATE_REFUTED",
        "required_repair": "CHANGE_PHASE_ONE_SPATIAL_MOVIE_FOR_INTERFACE_2_RELATIVE_TO_INTERFACE_0",
        "verdict": "REFUTED_X_M1_OUTER_COLLAR_V7_REVERSE_DYNAMIC_CORE_CLEARANCE",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("reverse dynamic core obstruction is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "active": result["active_interface"],
                "obstacle": result["obstacle_interface"],
                "time": result["local_phase_one_time"],
                "dimension": result["intersection_dimension"],
                "reordering": result["sequential_reordering_only_status"],
                "repair": result["required_repair"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
