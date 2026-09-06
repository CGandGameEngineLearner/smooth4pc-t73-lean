#!/usr/bin/env python3
"""Independently replay v2 against scheduled static collar ribbon volumes."""

from __future__ import annotations

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
from build_t73_x_m1_outer_collar_v7_ribbon_volume_v2_static_clearance_3017 import (
    STATIC_RIBBON,
    TYPE_NAMES,
    VOLUME,
    load_static,
)
from t73_exact_simplex import tetrahedra_intersect
from verify_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    canonical_sha,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_ribbon_volume_v2_static_clearance_3017.json"
)


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    volume = json.loads(VOLUME.read_text())
    collars = json.loads(COLLARS.read_text())
    static_ribbon = json.loads(STATIC_RIBBON.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["ribbon_volume_v2_sha256"] != volume["sha256"]
        or data["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or data["reverse_static_ribbon_clearance_sha256"] != static_ribbon["sha256"]
    ):
        raise AssertionError("v2 static ribbon-volume bindings changed")
    static = load_static(collars)
    properties = rtree_index.Property()
    properties.dimension = len(FUNCTIONALS)
    tree = rtree_index.Index(
        ((index, functional_box(value[5]), None) for index, value in enumerate(static)),
        properties=properties,
    )
    matrix = {}
    checks = intersections = 0
    for transition in volume["transitions"]:
        start, end = (Fraction(value) for value in transition["global_time_interval"])
        vertices = [point(value) for value in transition["spacetime_vertices"]]
        normalized = [
            (*value[:3], (value[3] - start) / (end - start)) for value in vertices
        ]
        for cell in transition["tetrahedra"]:
            moving = tuple(normalized[index] for index in cell)
            for static_index in tree.intersection(functional_box(moving)):
                kind, _interface, semantic_type, _triangle, _local, obstacle = static[
                    static_index
                ]
                key = (
                    f"{kind}/{TYPE_NAMES[semantic_type]}"
                    if kind == "final"
                    else "source/source_ribbon"
                )
                matrix[key] = matrix.get(key, 0) + 1
                checks += 1
                intersections += tetrahedra_intersect(moving, obstacle)
    expected = {
        "final/end_skew_lift": 1604,
        "final/first_exterior_ray": 654,
        "final/staggered_last_exterior_ray": 2398,
        "final/start_skew_lift": 392,
    }
    if (
        matrix != expected
        or matrix != data["exact_candidate_matrix"]
        or checks != 5048
        or intersections != 0
        or not data["scheduled_static_collar_ribbon_volume_clearance"]
        or data["retained_replacement_ribbon_volume_status"] != "OPEN"
    ):
        raise AssertionError("independent v2 static ribbon-volume replay changed")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_RIBBON_VOLUME_V2_STATIC_CLEARANCE_3017_INDEPENDENT",
        "moving_tetrahedra": volume["r4_tetrahedron_count"],
        "static_tetrahedra": len(static),
        "semantic_matrices_replayed": len(matrix),
        "exact_tetrahedron_checks": checks,
        "source_candidates": 0,
        "final_candidates": checks,
        "forbidden_intersections": intersections,
        "scheduled_static_collar_ribbon_volume_clearance": True,
        "retained_replacement_ribbon_volume": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
