#!/usr/bin/env python3
"""Verify every ordered final/source core pair in the sequential schedule."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import sys
from collections import Counter
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_core_push_clearance import segment_intersects

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
FINAL_CLEARANCE = ROOT / "audit/t73_x_m1_outer_collar_v7_one_skeleton_clearance.json"
SEQUENTIAL = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_isotopy_trace_receipt.json"
)
SEQUENTIAL_VERIFY = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_isotopy_trace_verification.json"
)
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_static_core_clearance.json"
TYPE_NAMES = (
    "retained_source_germ",
    "start_skew_lift",
    "first_exterior_ray",
    "staggered_height_bridge",
    "staggered_last_exterior_ray",
    "end_skew_lift",
)


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


def exact_bounds(segment):
    return (
        tuple(min(segment[0][axis], segment[1][axis]) for axis in range(3)),
        tuple(max(segment[0][axis], segment[1][axis]) for axis in range(3)),
    )


def float_bounds(bounds):
    return tuple(
        math.nextafter(float(value), -math.inf) for value in bounds[0]
    ) + tuple(math.nextafter(float(value), math.inf) for value in bounds[1])


def subtract(first, second):
    return tuple(a - b for a, b in zip(first, second))


def cross(first, second):
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def dot(first, second):
    return sum(a * b for a, b in zip(first, second))


def load(receipt):
    sources = []
    finals = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            interface = record["interface_index"]
            source_segment = tuple(
                point(value) for value in record["source_core_segment"]
            )
            sources.append(
                {
                    "interface": interface,
                    "neighbor_id": record["neighbor_id"],
                    "segment": source_segment,
                    "bounds": exact_bounds(source_segment),
                }
            )
            vertices = [point(value) for value in record["final_core_vertices"]]
            for local, segment in enumerate(pairwise(vertices)):
                finals.append(
                    {
                        "interface": interface,
                        "neighbor_id": record["neighbor_id"],
                        "type": local,
                        "segment": segment,
                        "bounds": exact_bounds(segment),
                    }
                )
    return sources, finals


def build():
    collars = json.loads(COLLARS.read_text())
    final_clearance = json.loads(FINAL_CLEARANCE.read_text())
    sequential = json.loads(SEQUENTIAL.read_text())
    verification = json.loads(SEQUENTIAL_VERIFY.read_text())
    if (
        final_clearance["core_clearance"]["outer_collars_v7_receipt_sha256"]
        != collars["sha256"]
        or not final_clearance["core_clearance"]["global_core_clearance"]
        or verification["construction_receipt_sha256"] != sequential["sha256"]
        or not verification["full_result"][
            "moving_sheet_interiors_pairwise_time_disjoint"
        ]
    ):
        raise AssertionError("ordered mixed-core inputs are stale or failed")
    sources, finals = load(collars)
    if len(sources) != 3026 or len(finals) != 18156:
        raise AssertionError("ordered mixed-core inventory changed")
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        (
            (index, float_bounds(value["bounds"]), None)
            for index, value in enumerate(sources)
        ),
        properties=properties,
    )
    broad = exact_checks = separated = 0
    type_counts = Counter()
    permitted = []
    for final in finals:
        for source_index in tree.intersection(float_bounds(final["bounds"])):
            source = sources[source_index]
            if final["interface"] >= source["interface"]:
                continue
            broad += 1
            type_counts[TYPE_NAMES[final["type"]]] += 1
            exact_checks += 1
            if not segment_intersects(final["segment"], source["segment"]):
                separated += 1
                continue
            shared = set(final["segment"]) & set(source["segment"])
            if (
                final["type"] != 0
                or final["neighbor_id"] != source["neighbor_id"]
                or len(shared) != 1
            ):
                raise AssertionError(
                    "nonpermitted ordered final/source core intersection"
                )
            common = next(iter(shared))
            final_other = next(value for value in final["segment"] if value != common)
            source_other = next(value for value in source["segment"] if value != common)
            final_direction = subtract(final_other, common)
            source_direction = subtract(source_other, common)
            if (
                cross(final_direction, source_direction) != (0, 0, 0)
                or dot(final_direction, source_direction) >= 0
            ):
                raise AssertionError("shared dual germ is not collinear-opposite")
            permitted.append(
                {
                    "final_interface": final["interface"],
                    "source_interface": source["interface"],
                    "neighbor_id": final["neighbor_id"],
                    "shared_endpoint": [str(value) for value in common],
                    "relation": "COLLINEAR_OPPOSITE_GERMS",
                }
            )
    if (broad, exact_checks, separated, len(permitted)) != (3022, 3022, 3018, 4):
        raise AssertionError("ordered mixed-core totals changed")
    result = {
        "schema": "t73_x_m1_outer_collar_v7_sequential_static_core_clearance/v1",
        "outer_collars_v7_receipt_sha256": collars["sha256"],
        "v7_final_core_clearance_sha256": final_clearance["core_clearance"]["sha256"],
        "sequential_trace_receipt_sha256": sequential["sha256"],
        "sequential_trace_verification_sha256": verification["sha256"],
        "schedule_order_rule": "final_interface < source_interface",
        "source_core_segment_count": len(sources),
        "final_core_segment_count": len(finals),
        "outward_float_aabb_candidate_count": broad,
        "candidate_count_by_final_segment_type": dict(sorted(type_counts.items())),
        "exact_segment_check_count": exact_checks,
        "exact_separated_pair_count": separated,
        "permitted_opposite_germ_incidence_count": len(permitted),
        "permitted_opposite_germ_incidences": permitted,
        "nonpermitted_intersection_count": 0,
        "ordered_mixed_static_core_clearance": True,
        "push_and_ribbon_status": "OPEN",
        "moving_static_status": "OPEN",
        "classification": "PARTIAL_GLOBAL_SEQUENTIAL_CLEARANCE",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_SEQUENTIAL_STATIC_CORE_CLEARANCE",
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
        raise AssertionError("ordered mixed static core clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "broad": result["outward_float_aabb_candidate_count"],
                "separated": result["exact_separated_pair_count"],
                "permitted": result["permitted_opposite_germ_incidence_count"],
                "nonpermitted": result["nonpermitted_intersection_count"],
                "ribbon": result["push_and_ribbon_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
