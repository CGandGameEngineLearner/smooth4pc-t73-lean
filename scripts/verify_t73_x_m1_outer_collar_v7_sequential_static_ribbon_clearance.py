#!/usr/bin/env python3
"""Independently replay ordered final/source ribbon clearance."""

from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    cross,
    dot,
    float_bounds,
    point,
    resolve,
    subtract,
)
from verify_t73_candidate_t_band0_surface import triangles_intersect
from verify_t73_x_m1_outer_collar_v7_sequential_static_one_skeleton_clearance import (
    canonical_sha,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_static_ribbon_clearance.json"
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
ONE_SKELETON = (
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


def exact_bounds(vertices):
    return (
        tuple(min(vertex[axis] for vertex in vertices) for axis in range(3)),
        tuple(max(vertex[axis] for vertex in vertices) for axis in range(3)),
    )


def triangulate(quad):
    return ((quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3]))


def lift(triangle):
    return tuple((*vertex, 0) for vertex in triangle)


def opposite_star(first, second, edge):
    a, b = edge

    def normal(rectangle):
        triangle = next(
            triangle
            for triangle in rectangle["triangles"]
            if a in triangle and b in triangle
        )
        third = next(vertex for vertex in triangle if vertex not in edge)
        return cross(subtract(b, a), subtract(third, a))

    first_normal, second_normal = normal(first), normal(second)
    return (
        cross(first_normal, second_normal) == (0, 0, 0)
        and dot(first_normal, second_normal) < 0
    )


def load(receipt):
    sources = []
    finals = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as stream:
        stream.readline()
        for line in stream:
            record = json.loads(line)
            interface = record["interface_index"]
            source_core = [point(value) for value in record["source_core_segment"]]
            source_push = [point(value) for value in record["source_push_segment"]]
            source_quad = (
                source_core[0],
                source_core[1],
                source_push[1],
                source_push[0],
            )
            sources.append(
                {
                    "interface": interface,
                    "neighbor_id": record["neighbor_id"],
                    "quad": source_quad,
                    "triangles": triangulate(source_quad),
                    "bounds": exact_bounds(source_quad),
                }
            )
            core = [point(value) for value in record["final_core_vertices"]]
            push = [point(value) for value in record["final_push_vertices"]]
            for local in range(6):
                quad = (core[local], core[local + 1], push[local + 1], push[local])
                finals.append(
                    {
                        "interface": interface,
                        "neighbor_id": record["neighbor_id"],
                        "type": local,
                        "quad": quad,
                        "triangles": triangulate(quad),
                        "bounds": exact_bounds(quad),
                    }
                )
    return sources, finals


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    collars = json.loads(COLLARS.read_text())
    one_skeleton = json.loads(ONE_SKELETON.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or data["ordered_mixed_static_one_skeleton_clearance_sha256"]
        != one_skeleton["sha256"]
        or not one_skeleton["ordered_mixed_static_one_skeleton_clearance"]
    ):
        raise AssertionError("ordered ribbon bindings changed")
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
    type_counts = {value: 0 for value in TYPE_NAMES}
    stars = []
    intersections = 0
    for final in finals:
        for source_index in tree.intersection(float_bounds(final["bounds"])):
            source = sources[source_index]
            if final["interface"] >= source["interface"]:
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
                    raise AssertionError("independent ordered ribbon star failed")
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
        (broad, nonincident, triangle_checks, len(stars), intersections)
        != (3022, 3018, 12072, 4, 0)
        or filtered_types != data["candidate_count_by_final_rectangle_type"]
        or stars != data["permitted_local_stars"]
        or not data["ordered_mixed_static_ribbon_clearance"]
    ):
        raise AssertionError("independent ordered ribbon replay changed")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_SEQUENTIAL_STATIC_RIBBON_CLEARANCE_INDEPENDENT",
        "outward_float_aabb_candidates": broad,
        "permitted_coplanar_opposite_stars": len(stars),
        "nonincident_rectangle_candidates": nonincident,
        "exact_triangle_pair_checks": triangle_checks,
        "nonpermitted_intersections": intersections,
        "ordered_mixed_static_ribbon_clearance": True,
        "moving_static_status": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
