#!/usr/bin/env python3
"""Construct the complete twentieth framed parallel of post-cancel m1."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from build_t73_t_hcs_cancellation_readiness import final_states

ROOT = Path(__file__).resolve().parents[1]
EXTERIOR = ROOT / "geometry/t73_t_hcs_framing_exteriorization.json"
SURFACE = ROOT / "geometry/t73_x_band0_attachment_surface.json"
CHARTS = ROOT / "geometry/t73_x_band0_chart_transitions.json"
OUTPUT = ROOT / "geometry/t73_x_band0_m1_parallel.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def exteriorized_normals(normals, record):
    replacements = {
        item["vertex_index"]: point(item["new_normal"])
        for item in record["normal_replacements"]
    }
    return [replacements.get(index, value) for index, value in enumerate(normals)]


def build() -> dict:
    exterior = json.loads(EXTERIOR.read_text(encoding="utf-8"))
    surface = json.loads(SURFACE.read_text(encoding="utf-8"))
    charts = json.loads(CHARTS.read_text(encoding="utf-8"))
    points, original_normals, seams = final_states()["m_1"]
    normals = exteriorized_normals(original_normals, exterior["components"]["m_1"])
    coefficient = surface["target_parallel_coefficient"]
    offsets_before_local_adjustment = [
        tuple(coefficient * coordinate for coordinate in normal)
        for normal in normals
    ]
    offsets = list(offsets_before_local_adjustment)
    local_target_offset = tuple(
        coefficient * coordinate for coordinate in point(surface["target_parallel_normal"])
    )
    target_start, target_end = charts["target_germ"]["global_vertex_range"]
    global_target_offset = (
        -local_target_offset[0],
        local_target_offset[1],
        local_target_offset[2],
        Fraction(0),
    )
    for index in range(target_start, target_end + 1):
        offsets[index] = global_target_offset
    parallel = [
        tuple(value[axis] + offset[axis] for axis in range(4))
        for value, offset in zip(points, offsets)
    ]
    if tuple(parallel[-1][axis] - parallel[0][axis] for axis in range(3)) != (
        -4,
        0,
        4,
    ):
        raise AssertionError("m1 parallel lost its closing deck translation")
    result = {
        "schema": "t73_x_band0_m1_parallel/v1",
        "framing_exteriorization_sha256": exterior["sha256"],
        "surface_sha256": surface["sha256"],
        "chart_transitions_sha256": charts["sha256"],
        "parallel_coefficient": coefficient,
        "base_component": "m_1",
        "base_vertices": [encode(value) for value in points],
        "framing_offsets_before_local_adjustment": [
            encode(value) for value in offsets_before_local_adjustment
        ],
        "framing_offsets": [encode(value) for value in offsets],
        "parallel_vertices": [encode(value) for value in parallel],
        "mapping_torus_seam_segment_indices": sorted(seams),
        "local_adjustment_vertex_range": [target_start, target_end],
        "local_adjustment_rule": (
            "replace 20 times the exteriorized normal by the homotopic global "
            "y-offset on the reflected bottom x-arc"
        ),
        "target_interval_global": charts["target_germ"]["global_parallel_interval"],
        "completion_status": "X_BAND0_COMPLETE_FRAMED_M1_PARALLEL_CONSTRUCTED",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("x-band 0 m1 parallel is stale")
    print("T73_X_BAND0_M1_PARALLEL=X_BAND0_COMPLETE_FRAMED_M1_PARALLEL_CONSTRUCTED")


if __name__ == "__main__":
    main()
