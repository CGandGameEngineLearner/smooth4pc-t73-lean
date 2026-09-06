#!/usr/bin/env python3
"""Verify ribbon-volume v2 against the scheduled static collar ribbons."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v7_reverse_dynamic_core_candidate_matrix import (
    COLLARS,
    FUNCTIONALS,
    functional_box,
)
from build_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import resolve
from t73_exact_simplex import tetrahedra_intersect

ROOT = Path(__file__).resolve().parents[1]
VOLUME = ROOT / "geometry/t73_x_m1_outer_collar_v7_ribbon_volume_v2_3017.json"
STATIC_RIBBON = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_static_ribbon_clearance.json"
)
OUTPUT = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_ribbon_volume_v2_static_clearance_3017.json"
)
PRISM = ((0, 1, 2, 5), (0, 1, 4, 5), (0, 3, 4, 5))
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


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def append_rectangle(result, kind, interface, semantic_type, core, push):
    quad = (core[0], core[1], push[1], push[0])
    triangles = ((quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3]))
    for triangle_index, triangle in enumerate(triangles):
        vertices = [(*value, Fraction(0)) for value in triangle] + [
            (*value, Fraction(1)) for value in triangle
        ]
        result.extend(
            (
                kind,
                interface,
                semantic_type,
                triangle_index,
                local,
                tuple(vertices[index] for index in cell),
            )
            for local, cell in enumerate(PRISM)
        )


def load_static(receipt):
    tetrahedra = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            interface = record["interface_index"]
            if interface < 3017:
                append_rectangle(
                    tetrahedra,
                    "source",
                    interface,
                    0,
                    [point(value) for value in record["source_core_segment"]],
                    [point(value) for value in record["source_push_segment"]],
                )
            elif interface > 3017:
                core = [point(value) for value in record["final_core_vertices"]]
                push = [point(value) for value in record["final_push_vertices"]]
                for semantic_type in range(6):
                    append_rectangle(
                        tetrahedra,
                        "final",
                        interface,
                        semantic_type,
                        core[semantic_type : semantic_type + 2],
                        push[semantic_type : semantic_type + 2],
                    )
    return tetrahedra


def build():
    volume = json.loads(VOLUME.read_text())
    collars = json.loads(COLLARS.read_text())
    static_ribbon = json.loads(STATIC_RIBBON.read_text())
    volume_payload = {key: value for key, value in volume.items() if key != "sha256"}
    if (
        volume["sha256"] != canonical_sha(volume_payload)
        or static_ribbon["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or not static_ribbon["reverse_mixed_static_ribbon_clearance"]
        or not volume["internal_ribbon_volume_self_clearance"]
    ):
        raise AssertionError("v2 static ribbon-volume inputs are stale or failed")
    static = load_static(collars)
    if len(static) != 18390:
        raise AssertionError("static ribbon-volume inventory changed")
    properties = rtree_index.Property()
    properties.dimension = len(FUNCTIONALS)
    tree = rtree_index.Index(
        ((index, functional_box(value[5]), None) for index, value in enumerate(static)),
        properties=properties,
    )
    matrix = {}
    checks = 0
    intersections = []
    for transition in volume["transitions"]:
        start = Fraction(transition["global_time_interval"][0])
        end = Fraction(transition["global_time_interval"][1])
        vertices = [point(value) for value in transition["spacetime_vertices"]]
        normalized = [
            (*value[:3], (value[3] - start) / (end - start)) for value in vertices
        ]
        for moving_index, cell in enumerate(transition["tetrahedra"]):
            moving = tuple(normalized[index] for index in cell)
            for static_index in tree.intersection(functional_box(moving)):
                kind, interface, semantic_type, triangle, local, obstacle = static[
                    static_index
                ]
                key = (
                    f"{kind}/{TYPE_NAMES[semantic_type]}"
                    if kind == "final"
                    else "source/source_ribbon"
                )
                matrix[key] = matrix.get(key, 0) + 1
                checks += 1
                if tetrahedra_intersect(moving, obstacle):
                    intersections.append(
                        {
                            "transition": transition["transition_index"],
                            "moving_tetrahedron": moving_index,
                            "static_kind": kind,
                            "static_interface": interface,
                            "static_type": semantic_type,
                            "static_triangle": triangle,
                            "static_tetrahedron": local,
                        }
                    )
    expected = {
        "final/end_skew_lift": 1604,
        "final/first_exterior_ray": 654,
        "final/staggered_last_exterior_ray": 2398,
        "final/start_skew_lift": 392,
    }
    if matrix != expected or checks != 5048 or intersections:
        raise AssertionError("v2 static ribbon-volume clearance changed")
    result = {
        "schema": "t73_x_m1_outer_collar_v7_ribbon_volume_v2_static_clearance/v1",
        "ribbon_volume_v2_sha256": volume["sha256"],
        "outer_collars_v7_receipt_sha256": collars["sha256"],
        "reverse_static_ribbon_clearance_sha256": static_ribbon["sha256"],
        "interface_index": 3017,
        "time_normalization": "each [k/25,(k+1)/25] maps affinely to [0,1]",
        "moving_tetrahedron_count": volume["r4_tetrahedron_count"],
        "static_tetrahedron_count": len(static),
        "exact_candidate_matrix": matrix,
        "exact_tetrahedron_check_count": checks,
        "source_candidate_count": 0,
        "final_candidate_count": checks,
        "forbidden_intersection_count": 0,
        "scheduled_static_collar_ribbon_volume_clearance": True,
        "retained_replacement_ribbon_volume_status": "OPEN",
        "classification": "RATIONAL_RIBBON_VOLUME_CANDIDATE",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_RIBBON_VOLUME_V2_STATIC_CLEARANCE_3017",
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
        raise AssertionError("v2 static ribbon-volume clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "moving": result["moving_tetrahedron_count"],
                "static": result["static_tetrahedron_count"],
                "checks": result["exact_tetrahedron_check_count"],
                "source": result["source_candidate_count"],
                "final": result["final_candidate_count"],
                "forbidden": result["forbidden_intersection_count"],
                "external": result["retained_replacement_ribbon_volume_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
