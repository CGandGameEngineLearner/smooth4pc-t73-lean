#!/usr/bin/env python3
"""Independently replay reverse mixed framed-ribbon clearance."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from verify_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    canonical_sha,
)
from verify_t73_x_m1_outer_collar_v7_sequential_static_ribbon_clearance import (
    TYPE_NAMES,
    float_bounds,
    lift,
    load,
    opposite_star,
    triangles_intersect,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_static_ribbon_clearance.json"
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
ONE_SKELETON = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_static_one_skeleton_clearance.json"
)


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    collars = json.loads(COLLARS.read_text())
    one_skeleton = json.loads(ONE_SKELETON.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or data["reverse_static_one_skeleton_clearance_sha256"]
        != one_skeleton["sha256"]
        or not one_skeleton["reverse_mixed_static_one_skeleton_clearance"]
    ):
        raise AssertionError("reverse ribbon bindings changed")
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
    broad = nonincident = triangle_checks = intersections = 0
    type_counts = {value: 0 for value in TYPE_NAMES}
    stars = []
    for final in finals:
        for source_index in tree.intersection(float_bounds(final["bounds"])):
            source = sources[source_index]
            if final["interface"] <= source["interface"]:
                continue
            broad += 1
            type_counts[TYPE_NAMES[final["type"]]] += 1
            shared = set(final["quad"]) & set(source["quad"])
            if shared:
                edge = tuple(shared)
                if (
                    final["type"] != 0
                    or final["neighbor_id"] != source["neighbor_id"]
                    or len(edge) != 2
                    or not opposite_star(final, source, edge)
                ):
                    raise AssertionError("independent reverse ribbon star failed")
                stars.append(
                    {
                        "final_interface": final["interface"],
                        "source_interface": source["interface"],
                        "neighbor_id": final["neighbor_id"],
                        "shared_edge": sorted(
                            [str(value) for value in vertex] for vertex in edge
                        ),
                        "relation": "COPLANAR_OPPOSITE_SIDES",
                    }
                )
                continue
            nonincident += 1
            for first in final["triangles"]:
                for second in source["triangles"]:
                    triangle_checks += 1
                    intersections += triangles_intersect(lift(first), lift(second))
    filtered_types = {key: value for key, value in type_counts.items() if value}
    if (
        (broad, len(stars), nonincident, triangle_checks, intersections)
        != (8, 4, 4, 16, 0)
        or filtered_types != data["candidate_count_by_final_rectangle_type"]
        or stars != data["permitted_local_stars"]
        or not data["reverse_mixed_static_ribbon_clearance"]
    ):
        raise AssertionError("independent reverse ribbon replay changed")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_REVERSE_STATIC_RIBBON_CLEARANCE_INDEPENDENT",
        "outward_float_aabb_candidates": broad,
        "permitted_coplanar_opposite_stars": len(stars),
        "nonincident_rectangle_candidates": nonincident,
        "exact_triangle_pair_checks": triangle_checks,
        "nonpermitted_intersections": intersections,
        "reverse_mixed_static_ribbon_clearance": True,
        "reverse_dynamic_status": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
