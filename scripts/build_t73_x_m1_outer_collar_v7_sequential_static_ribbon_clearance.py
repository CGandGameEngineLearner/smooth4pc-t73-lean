#!/usr/bin/env python3
"""Verify ordered final/source framed-ribbon mixtures."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v2_ribbon_self_clearance import star_relation
from build_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    float_bounds,
    point,
    resolve,
)
from verify_t73_x_m1_transition_transition_ribbon_clearance_gmp import (
    triangles_intersect,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
ONE_SKELETON = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_sequential_static_one_skeleton_clearance.json"
)
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_static_ribbon_clearance.json"
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


def exact_bounds(vertices):
    return (
        tuple(min(vertex[axis] for vertex in vertices) for axis in range(3)),
        tuple(max(vertex[axis] for vertex in vertices) for axis in range(3)),
    )


def source_rectangle(record):
    core = [point(value) for value in record["source_core_segment"]]
    push = [point(value) for value in record["source_push_segment"]]
    quad = (core[0], core[1], push[1], push[0])
    return {
        "interface": record["interface_index"],
        "neighbor_id": record["neighbor_id"],
        "quad": quad,
        "triangles": ((quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3])),
        "bounds": exact_bounds(quad),
    }


def final_rectangles(record):
    core = [point(value) for value in record["final_core_vertices"]]
    push = [point(value) for value in record["final_push_vertices"]]
    vertices = core + push
    size = len(core)
    result = []
    for local in range(size - 1):
        quad = (core[local], core[local + 1], push[local + 1], push[local])
        triangles = tuple(
            tuple(vertices[index] for index in cell)
            for cell in record["final_ribbon_triangles"][2 * local : 2 * local + 2]
        )
        result.append(
            {
                "interface": record["interface_index"],
                "neighbor_id": record["neighbor_id"],
                "type": local,
                "quad": quad,
                "triangles": triangles,
                "bounds": exact_bounds(quad),
            }
        )
    return result


def load(receipt):
    sources = []
    finals = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as stream:
        stream.readline()
        for line in stream:
            record = json.loads(line)
            sources.append(source_rectangle(record))
            finals.extend(final_rectangles(record))
    return sources, finals


def build():
    collars = json.loads(COLLARS.read_text())
    one_skeleton = json.loads(ONE_SKELETON.read_text())
    one_payload = {key: value for key, value in one_skeleton.items() if key != "sha256"}
    if (
        one_skeleton["sha256"] != canonical_sha(one_payload)
        or one_skeleton["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or not one_skeleton["ordered_mixed_static_one_skeleton_clearance"]
    ):
        raise AssertionError("ordered ribbon inputs are stale or failed")
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
    broad = triangle_checks = nonincident = 0
    type_counts = Counter()
    star_counts = Counter()
    incidences = []
    intersections = []
    for final in finals:
        for source_index in tree.intersection(float_bounds(final["bounds"])):
            source = sources[source_index]
            if final["interface"] >= source["interface"]:
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
                    raise AssertionError("unexpected ordered ribbon incidence")
                edge = tuple(shared)
                relation = star_relation(final, source, edge)
                if relation != "COPLANAR_OPPOSITE_SIDES":
                    raise AssertionError("ordered ribbon incidence folds or crosses")
                star_counts[relation] += 1
                incidences.append(
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
    if (
        broad,
        nonincident,
        triangle_checks,
        len(incidences),
        len(intersections),
    ) != (3022, 3018, 12072, 4, 0):
        raise AssertionError("ordered ribbon totals changed")
    result = {
        "schema": "t73_x_m1_outer_collar_v7_sequential_static_ribbon_clearance/v1",
        "outer_collars_v7_receipt_sha256": collars["sha256"],
        "ordered_mixed_static_one_skeleton_clearance_sha256": one_skeleton["sha256"],
        "schedule_order_rule": "final_interface < source_interface",
        "source_ribbon_rectangle_count": len(sources),
        "final_ribbon_rectangle_count": len(finals),
        "outward_float_aabb_candidate_count": broad,
        "candidate_count_by_final_rectangle_type": dict(sorted(type_counts.items())),
        "permitted_local_star_relation_counts": dict(sorted(star_counts.items())),
        "permitted_local_star_count": len(incidences),
        "permitted_local_stars": incidences,
        "nonincident_rectangle_candidate_count": nonincident,
        "exact_triangle_pair_check_count": triangle_checks,
        "nonpermitted_intersection_count": len(intersections),
        "nonpermitted_intersections": intersections,
        "ordered_mixed_static_ribbon_clearance": not intersections,
        "moving_static_status": "OPEN",
        "classification": "PARTIAL_GLOBAL_SEQUENTIAL_CLEARANCE",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_SEQUENTIAL_STATIC_RIBBON_CLEARANCE",
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
        raise AssertionError("ordered mixed ribbon clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "broad": result["outward_float_aabb_candidate_count"],
                "stars": result["permitted_local_star_count"],
                "nonincident": result["nonincident_rectangle_candidate_count"],
                "triangle_checks": result["exact_triangle_pair_check_count"],
                "intersections": result["nonpermitted_intersection_count"],
                "moving": result["moving_static_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
