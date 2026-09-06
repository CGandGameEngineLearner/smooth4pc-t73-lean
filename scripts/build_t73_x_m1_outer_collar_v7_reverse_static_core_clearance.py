#!/usr/bin/env python3
"""Verify every reverse-ordered final/source core pair."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
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
    load,
    subtract,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
FINAL_CLEARANCE = ROOT / "audit/t73_x_m1_outer_collar_v7_one_skeleton_clearance.json"
REVERSE = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_isotopy_trace_receipt.json"
)
REVERSE_VERIFY = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_isotopy_trace_verification.json"
)
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_static_core_clearance.json"
TYPE_NAMES = (
    "retained_source_germ",
    "start_skew_lift",
    "first_exterior_ray",
    "staggered_height_bridge",
    "staggered_last_exterior_ray",
    "end_skew_lift",
)


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def build():
    collars = json.loads(COLLARS.read_text())
    final_clearance = json.loads(FINAL_CLEARANCE.read_text())
    reverse = json.loads(REVERSE.read_text())
    verification = json.loads(REVERSE_VERIFY.read_text())
    if (
        final_clearance["core_clearance"]["outer_collars_v7_receipt_sha256"]
        != collars["sha256"]
        or not final_clearance["core_clearance"]["global_core_clearance"]
        or verification["construction_receipt_sha256"] != reverse["sha256"]
        or reverse["schedule_order"] != "REVERSE_INTERFACE_INDEX"
    ):
        raise AssertionError("reverse mixed-core inputs are stale or failed")
    sources, finals = load(collars)
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        (
            (index, float_bounds(value["bounds"]), None)
            for index, value in enumerate(sources)
        ),
        properties=properties,
    )
    broad = separated = 0
    type_counts = Counter()
    permitted = []
    for final in finals:
        for source_index in tree.intersection(float_bounds(final["bounds"])):
            source = sources[source_index]
            if final["interface"] <= source["interface"]:
                continue
            broad += 1
            type_counts[TYPE_NAMES[final["type"]]] += 1
            if not segment_intersects(final["segment"], source["segment"]):
                separated += 1
                continue
            shared = set(final["segment"]) & set(source["segment"])
            if (
                final["type"] != 0
                or final["neighbor_id"] != source["neighbor_id"]
                or len(shared) != 1
            ):
                raise AssertionError("forbidden reverse final/source core intersection")
            common = next(iter(shared))
            final_other = next(value for value in final["segment"] if value != common)
            source_other = next(value for value in source["segment"] if value != common)
            first = subtract(final_other, common)
            second = subtract(source_other, common)
            if cross(first, second) != (0, 0, 0) or dot(first, second) >= 0:
                raise AssertionError("reverse shared dual germ is not opposite")
            permitted.append(
                {
                    "final_interface": final["interface"],
                    "source_interface": source["interface"],
                    "neighbor_id": final["neighbor_id"],
                    "shared_endpoint": [str(value) for value in common],
                    "relation": "COLLINEAR_OPPOSITE_GERMS",
                }
            )
    if (broad, separated, len(permitted)) != (8, 4, 4):
        raise AssertionError("reverse mixed-core totals changed")
    result = {
        "schema": "t73_x_m1_outer_collar_v7_reverse_static_core_clearance/v1",
        "outer_collars_v7_receipt_sha256": collars["sha256"],
        "v7_final_core_clearance_sha256": final_clearance["core_clearance"]["sha256"],
        "reverse_trace_receipt_sha256": reverse["sha256"],
        "reverse_trace_verification_sha256": verification["sha256"],
        "schedule_order_rule": "final_interface > source_interface",
        "source_core_segment_count": len(sources),
        "final_core_segment_count": len(finals),
        "outward_float_aabb_candidate_count": broad,
        "candidate_count_by_final_segment_type": dict(sorted(type_counts.items())),
        "exact_segment_check_count": broad,
        "exact_separated_pair_count": separated,
        "permitted_opposite_germ_incidence_count": len(permitted),
        "permitted_opposite_germ_incidences": permitted,
        "nonpermitted_intersection_count": 0,
        "reverse_mixed_static_core_clearance": True,
        "push_and_ribbon_status": "OPEN",
        "reverse_dynamic_status": "OPEN",
        "classification": "PARTIAL_GLOBAL_REVERSE_SEQUENTIAL_CLEARANCE",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_REVERSE_STATIC_CORE_CLEARANCE",
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
        raise AssertionError("reverse mixed static core clearance is stale")
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
