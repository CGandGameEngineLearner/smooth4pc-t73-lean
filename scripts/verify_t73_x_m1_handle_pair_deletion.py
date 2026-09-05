#!/usr/bin/env python3
"""Verify x/m1 standard 4-ball deletion and the five-component output state."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from verify_t73_t_hcs_handle_pair_deletion import (
    betti_numbers,
    boundary_tetrahedra,
    independently_expected_products,
)
from verify_t73_x_band_hybrid_movie import verify as verify_hybrid
from verify_t73_x_m1_collar_ejection_map import verify as verify_collar
from verify_t73_x_m1_framing_exteriorization import verify as verify_framing

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"
BELTS = ROOT / "geometry/t73_belt_spheres.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
HYBRID_MOVIE = ROOT / "geometry/t73_x_band_hybrid_movie.json"
FRAMING = ROOT / "geometry/t73_x_m1_framing_exteriorization.json"
COLLAR = ROOT / "geometry/t73_x_m1_collar_ejection_map.json"
CHARTS = ROOT / "geometry/t73_x_band0_chart_transitions.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def determinant2(origin, first, second):
    return (first[0] - origin[0]) * (second[1] - origin[1]) - (
        first[1] - origin[1]
    ) * (second[0] - origin[0])


def verify() -> dict:
    prerequisites = {
        "hybrid_movie": verify_hybrid()["verdict"],
        "collar": verify_collar()["verdict"],
        "framing": verify_framing()["verdict"],
    }
    data = json.loads(DATA.read_text(encoding="utf-8"))
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    hybrid = json.loads(HYBRID_MOVIE.read_text(encoding="utf-8"))
    framing = json.loads(FRAMING.read_text(encoding="utf-8"))
    collar = json.loads(COLLAR.read_text(encoding="utf-8"))
    charts = json.loads(CHARTS.read_text(encoding="utf-8"))
    if data["completion_status"] != "X_M1_STANDARD_PAIR_AND_ACTUAL_CUBICAL_BINDING_CONSTRUCTED":
        raise AssertionError("x/m1 deletion scope changed")
    expected_hashes = {
        "belt_spheres_sha256": belts["sha256"],
        "x_cancellation_sha256": cancellation["sha256"],
        "x_hybrid_movie_sha256": hybrid["sha256"],
        "x_framing_exteriorization_sha256": framing["sha256"],
        "x_collar_ejection_map_sha256": collar["sha256"],
        "x_band0_chart_transitions_sha256": charts["sha256"],
    }
    if any(data[field] != value for field, value in expected_hashes.items()):
        raise AssertionError("x/m1 deletion has stale source bindings")

    standard = data["standard_pair"]
    expected_h1, expected_h2, expected_interface = independently_expected_products()
    if standard["h1_four_simplices"] != expected_h1 or standard["h2_four_simplices"] != expected_h2 or standard["glued_attaching_patch_tetrahedra"] != expected_interface:
        raise AssertionError("x/m1 pair is not the standard product triangulation")
    union = standard["union_four_simplices"]
    union_betti = betti_numbers(union, 4)
    boundary = boundary_tetrahedra(union)
    boundary_betti = betti_numbers(boundary, 3)
    if union_betti != [1, 0, 0, 0, 0] or boundary_betti != [1, 0, 0, 1]:
        raise AssertionError("x/m1 standard pair is not a PL 4-ball candidate with S3 boundary")

    binding = data["actual_cell_binding"]
    actual_vertices = [point(value)[1:3] for value in binding["actual_refinement_vertices"]]
    standard_vertices = [point(value) for value in binding["standard_face_refinement_vertices"]]
    actual_signs = []
    standard_signs = []
    for triangle in binding["refinement_triangles"]:
        actual_determinant = determinant2(*(actual_vertices[index] for index in triangle))
        standard_determinant = determinant2(*(standard_vertices[index] for index in triangle))
        if not actual_determinant or not standard_determinant:
            raise AssertionError("cubical-to-standard face refinement is degenerate")
        actual_signs.append(1 if actual_determinant > 0 else -1)
        standard_signs.append(1 if standard_determinant > 0 else -1)
    if len(set(actual_signs)) != 1 or len(set(standard_signs)) != 1:
        raise AssertionError("face refinement does not define a PL disk homeomorphism")
    face_map_orientation = actual_signs[0] * standard_signs[0]

    crossing = [point(value) for value in binding["actual_m1_crossing_arc"]]
    intersection = point(binding["actual_belt_intersection"])
    crossing_indices = [
        index for index, value in enumerate(crossing) if value[0] == Fraction(2)
    ]
    if crossing_indices != [2] or crossing[2] != intersection:
        raise AssertionError("m1 arc does not cross the cubical belt center once")
    if any(
        value[axis] != intersection[axis]
        for value in crossing
        for axis in (1, 2, 3)
    ):
        raise AssertionError("m1 crossing is not transverse in the x direction")
    local_framing = point(binding["actual_local_framing_vector"])
    if local_framing[0] or local_framing[3] or not local_framing[1] or not local_framing[2]:
        raise AssertionError("m1 local framing is not a nonzero positive-face tangent")
    if binding["relative_twist"] != 0:
        raise AssertionError("x/m1 pair has nonzero relative twist")

    remaining = data["deletion"]["remaining_components"]
    if set(remaining) != {"m_2", "m_3", "r_xy", "r_yz", "r_zx"}:
        raise AssertionError("post-x-cancel component inventory changed")
    for component in ("m_2", "m_3", "r_xy", "r_zx"):
        if remaining[component]["hybrid_state_sha256"] != hybrid["final_component_states"][component]["state_sha256"]:
            raise AssertionError("post-x-cancel hybrid component state changed")
    if data["deletion"]["deleted_handles"] != ["x", "m_1"] or data["deletion"]["remaining_one_handles"] != ["y", "z"]:
        raise AssertionError("x/m1 deletion handle inventory changed")
    return {
        "verdict": "PASS_X_M1_HANDLE_PAIR_DELETION_AND_FIVE_COMPONENT_STATE",
        "standard_union_vertices": standard["glued_vertex_count"],
        "standard_union_four_simplices": len(union),
        "union_betti": union_betti,
        "boundary_betti": boundary_betti,
        "cubical_face_refinement_triangles": len(binding["refinement_triangles"]),
        "face_map_orientation": face_map_orientation,
        "actual_belt_intersections": 1,
        "relative_twist": 0,
        "post_cancel_components": len(remaining),
        "remaining_one_handles": ["y", "z"],
        "prerequisite_verdicts": prerequisites,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
