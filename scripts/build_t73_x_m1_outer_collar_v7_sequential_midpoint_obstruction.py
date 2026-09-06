#!/usr/bin/env python3
"""Save the first exact collision in the sequential linear ribbon motion."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
from fractions import Fraction
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v2_ribbon_self_clearance import (
    triangle_intersection_witness,
)
from verify_t73_x_m1_transition_transition_ribbon_clearance_gmp import (
    triangles_intersect,
)

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
VOLUME = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_sequential_framed_isotopy_volume_receipt.json"
)
VOLUME_VERIFY = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_sequential_framed_isotopy_volume_verification.json"
)
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_midpoint_obstruction.json"


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def midpoint(first, second):
    return tuple((a + b) / 2 for a, b in zip(first, second))


def ribbon_segment(core, push, index):
    quad = (core[index], core[index + 1], push[index + 1], push[index])
    return ((quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3]))


def encode_triangle(triangle):
    return [[str(coordinate) for coordinate in vertex] for vertex in triangle]


def load_records(receipt):
    records = {}
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            if record["interface_index"] in (0, 2):
                records[record["interface_index"]] = record
    return records


def build():
    local = json.loads(LOCAL.read_text())
    volume = json.loads(VOLUME.read_text())
    verification = json.loads(VOLUME_VERIFY.read_text())
    if (
        verification["construction_receipt_sha256"] != volume["sha256"]
        or verification["cache_sha256"] != volume["cache_sha256"]
        or verification["full_result"]["moving_static_volume_clearance"] != "OPEN"
        or volume["classification"] != "CANDIDATE_UNVERIFIED"
    ):
        raise AssertionError("midpoint obstruction inputs are stale or overclaimed")
    records = load_records(local)
    active = records[2]
    obstacle = records[0]
    initial_core = [point(value) for value in active["initial_core_subdivision"]]
    initial_push = [
        point(value) for value in active["phase_one_push_initial_subdivision"]
    ]
    final_core = [point(value) for value in active["final_core_route"]]
    constant_push = [
        point(value) for value in active["phase_one_push_final_constant_normal_route"]
    ]
    active_triangles = ribbon_segment(
        [midpoint(a, b) for a, b in zip(initial_core, final_core)],
        [midpoint(a, b) for a, b in zip(initial_push, constant_push)],
        0,
    )
    obstacle_triangles = ribbon_segment(
        [point(value) for value in obstacle["final_core_route"]],
        [
            point(value)
            for value in obstacle["phase_one_push_final_constant_normal_route"]
        ],
        0,
    )
    collisions = []
    for active_index, first in enumerate(active_triangles):
        for obstacle_index, second in enumerate(obstacle_triangles):
            if not triangles_intersect(first, second):
                continue
            witness = triangle_intersection_witness(first, second)
            if witness is None:
                raise AssertionError("collision lacks an exact witness")
            collisions.append(
                {
                    "active_triangle": active_index,
                    "obstacle_triangle": obstacle_index,
                    "active_vertices": encode_triangle(first),
                    "obstacle_vertices": encode_triangle(second),
                    "witness": witness,
                }
            )
    if [
        (value["active_triangle"], value["obstacle_triangle"]) for value in collisions
    ] != [
        (0, 0),
        (0, 1),
        (1, 1),
    ]:
        raise AssertionError("midpoint collision pattern changed")
    result = {
        "schema": "t73_x_m1_outer_collar_v7_sequential_midpoint_obstruction/v1",
        "local_trace_receipt_sha256": local["sha256"],
        "framed_isotopy_volume_receipt_sha256": volume["sha256"],
        "framed_isotopy_volume_verification_sha256": verification["sha256"],
        "active_interface": 2,
        "active_segment": 0,
        "obstacle_kind": "PRIOR_FINAL_COLLAR",
        "obstacle_interface": 0,
        "obstacle_segment": 0,
        "local_phase_one_parameter": "1/2",
        "global_time": "9/12104",
        "collision_triangle_pair_count": len(collisions),
        "collisions": collisions,
        "sequential_time_schedule_status": "RETAINED",
        "linear_spatial_interpolation_status": "REFUTED",
        "framed_isotopy_volume_status": "CANDIDATE_REFUTED",
        "required_repair": "REPLACE_LINEAR_PHASE_ONE_BY_OBSTACLE_AVOIDING_LOCAL_FRAMED_MOVIE",
        "verdict": "REFUTED_X_M1_OUTER_COLLAR_V7_SEQUENTIAL_LINEAR_FRAMED_ISOTOPY",
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
        raise AssertionError("sequential midpoint obstruction is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "active": result["active_interface"],
                "obstacle": result["obstacle_interface"],
                "time": result["global_time"],
                "triangle_pairs": result["collision_triangle_pair_count"],
                "repair": result["required_repair"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
