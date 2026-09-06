#!/usr/bin/env python3
"""Verify the interface-3017 normal field against the static one-skeleton."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import pairwise
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
from verify_t73_candidate_t_band0_surface import triangles_intersect

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "geometry/t73_x_m1_outer_collar_v7_explicit_core_detour_3017.json"
NORMAL = ROOT / "geometry/t73_x_m1_outer_collar_v7_normal_field_3017.json"
STATIC = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_static_one_skeleton_clearance.json"
)
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v7_normal_field_static_clearance_3017.json"
INTERFACE = 3017


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


def vertical_triangles(segment):
    vertices = (
        (*segment[0], Fraction(0)),
        (*segment[1], Fraction(0)),
        (*segment[0], Fraction(1)),
        (*segment[1], Fraction(1)),
    )
    return (
        (vertices[0], vertices[1], vertices[3]),
        (vertices[0], vertices[3], vertices[2]),
    )


def load_static(receipt):
    triangles = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            interface = record["interface_index"]
            if interface < INTERFACE:
                for strand, key in (
                    ("core", "source_core_segment"),
                    ("push", "source_push_segment"),
                ):
                    segment = tuple(point(value) for value in record[key])
                    triangles.extend(
                        ("source", strand, interface, 0, half, triangle)
                        for half, triangle in enumerate(vertical_triangles(segment))
                    )
            elif interface > INTERFACE:
                for strand, key in (
                    ("core", "final_core_vertices"),
                    ("push", "final_push_vertices"),
                ):
                    vertices = [point(value) for value in record[key]]
                    for semantic_type, segment in enumerate(pairwise(vertices)):
                        triangles.extend(
                            ("final", strand, interface, semantic_type, half, triangle)
                            for half, triangle in enumerate(vertical_triangles(segment))
                        )
    return triangles


def build():
    core = json.loads(CORE.read_text())
    normal = json.loads(NORMAL.read_text())
    collars = json.loads(COLLARS.read_text())
    static = json.loads(STATIC.read_text())
    normal_payload = {key: value for key, value in normal.items() if key != "sha256"}
    if (
        normal["sha256"] != canonical_sha(normal_payload)
        or normal["explicit_core_detour_sha256"] != core["sha256"]
        or static["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or not static["reverse_mixed_static_one_skeleton_clearance"]
        or not normal["internal_framed_one_skeleton_clearance"]
    ):
        raise AssertionError("normal-field static-clearance inputs are stale")
    static_triangles = load_static(collars)
    properties = rtree_index.Property()
    properties.dimension = len(FUNCTIONALS)
    tree = rtree_index.Index(
        (
            (index, functional_box(value[5]), None)
            for index, value in enumerate(static_triangles)
        ),
        properties=properties,
    )
    matrix = Counter()
    intersections = []
    for transition, (core_record, push_record) in enumerate(
        zip(core["transitions"], normal["push_transitions"])
    ):
        for moving_strand, record, vertex_key in (
            ("core", core_record, "spacetime_vertices"),
            ("push", push_record, "push_spacetime_vertices"),
        ):
            vertices = [point(value) for value in record[vertex_key]]
            triangles = [
                tuple(vertices[index] for index in cell)
                for cell in record["trace_triangles"]
            ]
            for moving_index, moving in enumerate(triangles):
                for static_index in tree.intersection(functional_box(moving)):
                    kind, static_strand, interface, semantic_type, half, obstacle = (
                        static_triangles[static_index]
                    )
                    key = f"moving_{moving_strand}/{kind}_{static_strand}"
                    matrix[key] += 1
                    if triangles_intersect(moving, obstacle):
                        intersections.append(
                            {
                                "transition": transition,
                                "moving_strand": moving_strand,
                                "moving_triangle": moving_index,
                                "static_kind": kind,
                                "static_strand": static_strand,
                                "static_interface": interface,
                                "static_type": semantic_type,
                                "static_half": half,
                            }
                        )
    expected_matrix = {
        "moving_core/final_core": 333,
        "moving_core/final_push": 333,
        "moving_push/final_core": 447,
        "moving_push/final_push": 447,
    }
    if dict(sorted(matrix.items())) != expected_matrix or intersections:
        raise AssertionError(
            "normal-field static one-skeleton clearance changed: "
            f"matrix={dict(sorted(matrix.items()))} intersections={intersections[:3]}"
        )
    result = {
        "schema": "t73_x_m1_outer_collar_v7_normal_field_static_clearance/v1",
        "explicit_core_detour_sha256": core["sha256"],
        "normal_field_sha256": normal["sha256"],
        "outer_collars_v7_receipt_sha256": collars["sha256"],
        "reverse_static_one_skeleton_clearance_sha256": static["sha256"],
        "interface_index": INTERFACE,
        "moving_core_triangle_count": core["trace_triangle_count"],
        "moving_push_triangle_count": normal["push_trace_triangle_count"],
        "static_vertical_triangle_count": len(static_triangles),
        "exact_candidate_matrix": expected_matrix,
        "exact_triangle_check_count": sum(matrix.values()),
        "source_static_candidate_count": 0,
        "final_static_candidate_count": sum(matrix.values()),
        "forbidden_intersection_count": 0,
        "global_framed_one_skeleton_clearance": True,
        "ribbon_world_volume_status": "OPEN",
        "classification": "RATIONAL_FRAMED_ONE_SKELETON_CANDIDATE",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_NORMAL_FIELD_STATIC_CLEARANCE_3017",
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
        raise AssertionError("normal-field static clearance 3017 is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "static_triangles": result["static_vertical_triangle_count"],
                "exact_checks": result["exact_triangle_check_count"],
                "source_candidates": result["source_static_candidate_count"],
                "final_candidates": result["final_static_candidate_count"],
                "forbidden": result["forbidden_intersection_count"],
                "ribbon": result["ribbon_world_volume_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
