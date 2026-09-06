#!/usr/bin/env python3
"""Verify reverse-ordered final/source framed-ribbon mixtures."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from build_t73_x_m1_outer_collar_v7_reverse_static_core_clearance import canonical_sha
from build_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    float_bounds,
)
from build_t73_x_m1_outer_collar_v7_sequential_static_ribbon_clearance import (
    TYPE_NAMES,
    load,
    star_relation,
    triangles_intersect,
)
from rtree import index as rtree_index

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
ONE_SKELETON = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_static_one_skeleton_clearance.json"
)
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_static_ribbon_clearance.json"


def build():
    collars = json.loads(COLLARS.read_text())
    one_skeleton = json.loads(ONE_SKELETON.read_text())
    payload = {key: value for key, value in one_skeleton.items() if key != "sha256"}
    if (
        one_skeleton["sha256"] != canonical_sha(payload)
        or one_skeleton["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or not one_skeleton["reverse_mixed_static_one_skeleton_clearance"]
    ):
        raise AssertionError("reverse ribbon inputs are stale or failed")
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
    broad = nonincident = triangle_checks = 0
    type_counts = Counter()
    stars = []
    intersections = []
    for final in finals:
        for source_index in tree.intersection(float_bounds(final["bounds"])):
            source = sources[source_index]
            if final["interface"] <= source["interface"]:
                continue
            broad += 1
            type_counts[TYPE_NAMES[final["type"]]] += 1
            shared = set(final["quad"]) & set(source["quad"])
            if shared:
                if (
                    final["type"] != 0
                    or final["neighbor_id"] != source["neighbor_id"]
                    or len(shared) != 2
                ):
                    raise AssertionError("unexpected reverse ribbon incidence")
                edge = tuple(shared)
                relation = star_relation(final, source, edge)
                if relation != "COPLANAR_OPPOSITE_SIDES":
                    raise AssertionError("reverse ribbon star folds or crosses")
                stars.append(
                    {
                        "final_interface": final["interface"],
                        "source_interface": source["interface"],
                        "neighbor_id": final["neighbor_id"],
                        "shared_edge": sorted(
                            [str(value) for value in vertex] for vertex in edge
                        ),
                        "relation": relation,
                    }
                )
                continue
            nonincident += 1
            for first in final["triangles"]:
                for second in source["triangles"]:
                    triangle_checks += 1
                    if triangles_intersect(first, second):
                        intersections.append(
                            {
                                "final_interface": final["interface"],
                                "source_interface": source["interface"],
                                "final_type": TYPE_NAMES[final["type"]],
                            }
                        )
    if (broad, len(stars), nonincident, triangle_checks, len(intersections)) != (
        8,
        4,
        4,
        16,
        0,
    ):
        raise AssertionError("reverse ribbon totals changed")
    result = {
        "schema": "t73_x_m1_outer_collar_v7_reverse_static_ribbon_clearance/v1",
        "outer_collars_v7_receipt_sha256": collars["sha256"],
        "reverse_static_one_skeleton_clearance_sha256": one_skeleton["sha256"],
        "schedule_order_rule": "final_interface > source_interface",
        "source_ribbon_rectangle_count": len(sources),
        "final_ribbon_rectangle_count": len(finals),
        "outward_float_aabb_candidate_count": broad,
        "candidate_count_by_final_rectangle_type": dict(sorted(type_counts.items())),
        "permitted_local_star_relation_counts": {"COPLANAR_OPPOSITE_SIDES": 4},
        "permitted_local_star_count": len(stars),
        "permitted_local_stars": stars,
        "nonincident_rectangle_candidate_count": nonincident,
        "exact_triangle_pair_check_count": triangle_checks,
        "nonpermitted_intersection_count": len(intersections),
        "nonpermitted_intersections": intersections,
        "reverse_mixed_static_ribbon_clearance": not intersections,
        "reverse_dynamic_status": "OPEN",
        "classification": "PARTIAL_GLOBAL_REVERSE_SEQUENTIAL_CLEARANCE",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_REVERSE_STATIC_RIBBON_CLEARANCE",
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
        raise AssertionError("reverse ribbon clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "broad": result["outward_float_aabb_candidate_count"],
                "stars": result["permitted_local_star_count"],
                "nonincident": result["nonincident_rectangle_candidate_count"],
                "triangle_checks": result["exact_triangle_pair_check_count"],
                "intersections": result["nonpermitted_intersection_count"],
                "dynamic": result["reverse_dynamic_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
