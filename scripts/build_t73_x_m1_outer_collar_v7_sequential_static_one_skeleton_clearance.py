#!/usr/bin/env python3
"""Verify the remaining ordered final/source one-skeleton pairs."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter
from itertools import pairwise
from pathlib import Path

from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_core_push_clearance import segment_intersects
from build_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    cross,
    dot,
    float_bounds,
    point,
    resolve,
    subtract,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
CORE = ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_static_core_clearance.json"
OUTPUT = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_sequential_static_one_skeleton_clearance.json"
)
TYPE_NAMES = (
    "retained_source_germ",
    "start_skew_lift",
    "first_exterior_ray",
    "staggered_height_bridge",
    "staggered_last_exterior_ray",
    "end_skew_lift",
)
MATRICES = (
    ("push_push", "final_push_vertices", "source_push_segment", True),
    ("core_push", "final_core_vertices", "source_push_segment", False),
    ("push_core", "final_push_vertices", "source_core_segment", False),
)


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def exact_bounds(segment):
    return (
        tuple(min(segment[0][axis], segment[1][axis]) for axis in range(3)),
        tuple(max(segment[0][axis], segment[1][axis]) for axis in range(3)),
    )


def load(receipt):
    records = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            raw = json.loads(line)
            records.append(
                {
                    "interface": raw["interface_index"],
                    "neighbor_id": raw["neighbor_id"],
                    "source_core_segment": tuple(
                        point(value) for value in raw["source_core_segment"]
                    ),
                    "source_push_segment": tuple(
                        point(value) for value in raw["source_push_segment"]
                    ),
                    "final_core_vertices": [
                        point(value) for value in raw["final_core_vertices"]
                    ],
                    "final_push_vertices": [
                        point(value) for value in raw["final_push_vertices"]
                    ],
                }
            )
    return records


def run_matrix(records, name, final_key, source_key, allow_opposite_germs):
    sources = [
        (record["interface"], record["neighbor_id"], record[source_key])
        for record in records
    ]
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        (
            (index, float_bounds(exact_bounds(segment)), None)
            for index, (*_, segment) in enumerate(sources)
        ),
        properties=properties,
    )
    broad = separated = 0
    type_counts = Counter()
    permitted = []
    for record in records:
        for local, final_segment in enumerate(pairwise(record[final_key])):
            query = float_bounds(exact_bounds(final_segment))
            for source_index in tree.intersection(query):
                source_interface, source_neighbor, source_segment = sources[
                    source_index
                ]
                if record["interface"] >= source_interface:
                    continue
                broad += 1
                type_counts[TYPE_NAMES[local]] += 1
                if not segment_intersects(final_segment, source_segment):
                    separated += 1
                    continue
                shared = set(final_segment) & set(source_segment)
                if (
                    not allow_opposite_germs
                    or local != 0
                    or record["neighbor_id"] != source_neighbor
                    or len(shared) != 1
                ):
                    raise AssertionError(f"forbidden ordered {name} intersection")
                common = next(iter(shared))
                final_other = next(value for value in final_segment if value != common)
                source_other = next(
                    value for value in source_segment if value != common
                )
                first = subtract(final_other, common)
                second = subtract(source_other, common)
                if cross(first, second) != (0, 0, 0) or dot(first, second) >= 0:
                    raise AssertionError(f"ordered {name} germ is not opposite")
                permitted.append(
                    {
                        "final_interface": record["interface"],
                        "source_interface": source_interface,
                        "neighbor_id": record["neighbor_id"],
                        "shared_endpoint": [str(value) for value in common],
                        "relation": "COLLINEAR_OPPOSITE_GERMS",
                    }
                )
    return {
        "matrix": name,
        "schedule_order_rule": "final_interface < source_interface",
        "outward_float_aabb_candidate_count": broad,
        "candidate_count_by_final_segment_type": dict(sorted(type_counts.items())),
        "exact_segment_check_count": broad,
        "exact_separated_pair_count": separated,
        "permitted_opposite_germ_incidence_count": len(permitted),
        "permitted_opposite_germ_incidences": permitted,
        "nonpermitted_intersection_count": 0,
        "status": "PASS",
    }


def build():
    collars = json.loads(COLLARS.read_text())
    core = json.loads(CORE.read_text())
    core_payload = {key: value for key, value in core.items() if key != "sha256"}
    if (
        core["sha256"] != canonical_sha(core_payload)
        or core["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or not core["ordered_mixed_static_core_clearance"]
    ):
        raise AssertionError("ordered mixed core input is stale or failed")
    records = load(collars)
    matrices = [run_matrix(records, *definition) for definition in MATRICES]
    expected = {
        "push_push": (3022, 3018, 4),
        "core_push": (3018, 3018, 0),
        "push_core": (3018, 3018, 0),
    }
    for matrix in matrices:
        actual = (
            matrix["outward_float_aabb_candidate_count"],
            matrix["exact_separated_pair_count"],
            matrix["permitted_opposite_germ_incidence_count"],
        )
        if actual != expected[matrix["matrix"]]:
            raise AssertionError(f"ordered mixed {matrix['matrix']} totals changed")
    result = {
        "schema": "t73_x_m1_outer_collar_v7_sequential_static_one_skeleton_clearance/v1",
        "outer_collars_v7_receipt_sha256": collars["sha256"],
        "ordered_mixed_static_core_clearance_sha256": core["sha256"],
        "source_core_segment_count": 3026,
        "source_push_segment_count": 3026,
        "final_core_segment_count": 18156,
        "final_push_segment_count": 18156,
        "remaining_directed_matrices": matrices,
        "remaining_outward_float_aabb_candidate_count": sum(
            value["outward_float_aabb_candidate_count"] for value in matrices
        ),
        "remaining_exact_segment_check_count": sum(
            value["exact_segment_check_count"] for value in matrices
        ),
        "remaining_exact_separated_pair_count": sum(
            value["exact_separated_pair_count"] for value in matrices
        ),
        "remaining_permitted_opposite_germ_incidence_count": sum(
            value["permitted_opposite_germ_incidence_count"] for value in matrices
        ),
        "remaining_nonpermitted_intersection_count": 0,
        "ordered_mixed_static_one_skeleton_clearance": True,
        "ribbon_status": "OPEN",
        "moving_static_status": "OPEN",
        "classification": "PARTIAL_GLOBAL_SEQUENTIAL_CLEARANCE",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_SEQUENTIAL_STATIC_ONE_SKELETON_CLEARANCE",
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
        raise AssertionError("ordered mixed one-skeleton clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "candidates": result["remaining_outward_float_aabb_candidate_count"],
                "separated": result["remaining_exact_separated_pair_count"],
                "permitted": result[
                    "remaining_permitted_opposite_germ_incidence_count"
                ],
                "nonpermitted": result["remaining_nonpermitted_intersection_count"],
                "ribbon": result["ribbon_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
