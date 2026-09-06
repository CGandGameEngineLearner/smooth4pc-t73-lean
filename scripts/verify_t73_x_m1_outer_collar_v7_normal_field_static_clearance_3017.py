#!/usr/bin/env python3
"""Independently replay interface-3017 framed static clearance."""

from __future__ import annotations

import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v7_normal_field_static_clearance_3017 import (
    COLLARS,
    CORE,
    FUNCTIONALS,
    NORMAL,
    STATIC,
    functional_box,
    load_static,
)
from verify_t73_candidate_t_band0_surface import triangles_intersect
from verify_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    canonical_sha,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_outer_collar_v7_normal_field_static_clearance_3017.json"


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    core = json.loads(CORE.read_text())
    normal = json.loads(NORMAL.read_text())
    collars = json.loads(COLLARS.read_text())
    static = json.loads(STATIC.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["explicit_core_detour_sha256"] != core["sha256"]
        or data["normal_field_sha256"] != normal["sha256"]
        or data["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or data["reverse_static_one_skeleton_clearance_sha256"] != static["sha256"]
    ):
        raise AssertionError("normal-field static bindings changed")
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
    intersections = 0
    for core_record, push_record in zip(
        core["transitions"], normal["push_transitions"]
    ):
        for moving_strand, record, key in (
            ("core", core_record, "spacetime_vertices"),
            ("push", push_record, "push_spacetime_vertices"),
        ):
            vertices = [point(value) for value in record[key]]
            for cell in record["trace_triangles"]:
                moving = tuple(vertices[index] for index in cell)
                for static_index in tree.intersection(functional_box(moving)):
                    kind, static_strand, _interface, _type, _half, obstacle = (
                        static_triangles[static_index]
                    )
                    matrix[f"moving_{moving_strand}/{kind}_{static_strand}"] += 1
                    intersections += triangles_intersect(moving, obstacle)
    expected = {
        "moving_core/final_core": 333,
        "moving_core/final_push": 333,
        "moving_push/final_core": 333,
        "moving_push/final_push": 333,
    }
    if (
        dict(sorted(matrix.items())) != expected
        or data["exact_candidate_matrix"] != expected
        or intersections != 0
        or data["forbidden_intersection_count"] != 0
        or not data["global_framed_one_skeleton_clearance"]
    ):
        raise AssertionError("independent normal-field static replay changed")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_NORMAL_FIELD_STATIC_CLEARANCE_3017_INDEPENDENT",
        "static_vertical_triangles": len(static_triangles),
        "semantic_matrices_replayed": len(matrix),
        "exact_triangle_checks": sum(matrix.values()),
        "source_static_candidates": 0,
        "final_static_candidates": sum(matrix.values()),
        "forbidden_intersections": intersections,
        "global_framed_one_skeleton_clearance": True,
        "ribbon_world_volume": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
