#!/usr/bin/env python3
"""Verify the standard cancelling pair, actual binding, and post-link manifest."""

from __future__ import annotations

import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

from sympy import Matrix

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_t_hcs_handle_pair_deletion.json"
CANCELLATION = ROOT / "geometry/t73_cancel_t_hcs.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
BELTS = ROOT / "geometry/t73_belt_spheres.json"
MOVIE = ROOT / "geometry/t73_t_band_sequential_movie.json"
FRAMING = ROOT / "geometry/t73_t_hcs_framing_exteriorization.json"
COLLAR = ROOT / "geometry/t73_t_hcs_collar_ejection_map.json"


def all_faces(maximal_simplices):
    dimensions = {dimension: set() for dimension in range(5)}
    for simplex in maximal_simplices:
        for size in range(1, len(simplex) + 1):
            dimensions[size - 1].update(
                tuple(sorted(face)) for face in itertools.combinations(simplex, size)
            )
    return dimensions


def monotone_paths(first_dimension, second_dimension):
    steps = [0] * first_dimension + [1] * second_dimension
    for permutation in sorted(set(itertools.permutations(steps))):
        first = second = 0
        path = [(first, second)]
        for step in permutation:
            if step == 0:
                first += 1
            else:
                second += 1
            path.append((first, second))
        yield path


def independently_expected_products():
    h1_vertex = lambda first, second: 4 * first + second
    h2_vertex = lambda first, second: (
        h1_vertex(first, second + 1) if first < 2 else 8 + second
    )
    h1 = [
        [h1_vertex(first, second) for first, second in path]
        for path in monotone_paths(1, 3)
    ]
    h2 = [
        [h2_vertex(first, second) for first, second in path]
        for path in monotone_paths(2, 2)
    ]
    interface = [
        [h1_vertex(first, second + 1) for first, second in path]
        for path in monotone_paths(1, 2)
    ]
    return h1, h2, interface


def boundary_tetrahedra(four_simplices):
    counts = Counter(
        tuple(sorted(face))
        for simplex in four_simplices
        for face in itertools.combinations(simplex, 4)
    )
    if set(counts.values()) - {1, 2}:
        raise AssertionError("4-complex is not a pseudomanifold with boundary")
    return sorted(face for face, count in counts.items() if count == 1)


def betti_numbers(maximal_simplices, top_dimension):
    faces = all_faces(maximal_simplices)
    ranks = [0] * (top_dimension + 1)
    for dimension in range(1, top_dimension + 1):
        rows = sorted(faces[dimension - 1])
        columns = sorted(faces[dimension])
        row_index = {face: index for index, face in enumerate(rows)}
        matrix = [[0] * len(columns) for _ in rows]
        for column_index, simplex in enumerate(columns):
            for removed in range(len(simplex)):
                face = simplex[:removed] + simplex[removed + 1 :]
                matrix[row_index[face]][column_index] = -1 if removed % 2 else 1
        ranks[dimension] = Matrix(matrix).rank()
    return [
        len(faces[dimension])
        - ranks[dimension]
        - (ranks[dimension + 1] if dimension < top_dimension else 0)
        for dimension in range(top_dimension + 1)
    ]


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    cancellation = json.loads(CANCELLATION.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    movie = json.loads(MOVIE.read_text(encoding="utf-8"))
    framing = json.loads(FRAMING.read_text(encoding="utf-8"))
    collar = json.loads(COLLAR.read_text(encoding="utf-8"))
    if data["completion_status"] != "T_HCS_STANDARD_PAIR_AND_ACTUAL_CELL_BINDING_CONSTRUCTED":
        raise AssertionError("handle-pair deletion status changed")
    expected_hashes = {
        "legacy_cancellation_sha256": cancellation["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "belt_spheres_sha256": belts["sha256"],
        "sequential_movie_sha256": movie["sha256"],
        "framing_exteriorization_sha256": framing["sha256"],
        "collar_ejection_map_sha256": collar["sha256"],
    }
    if any(data[field] != value for field, value in expected_hashes.items()):
        raise AssertionError("handle-pair deletion has stale source bindings")

    standard = data["standard_pair"]
    h1 = standard["h1_four_simplices"]
    h2 = standard["h2_four_simplices"]
    interface = {tuple(value) for value in standard["glued_attaching_patch_tetrahedra"]}
    union = standard["union_four_simplices"]
    if len(h1) != 4 or len(h2) != 6 or len(interface) != 3 or len(union) != 10:
        raise AssertionError("standard product-handle simplex counts changed")
    expected_h1, expected_h2, expected_interface = independently_expected_products()
    if h1 != expected_h1 or h2 != expected_h2 or interface != {
        tuple(value) for value in expected_interface
    }:
        raise AssertionError("saved handles are not the standard staircase product triangulations")
    h1_boundary = set(boundary_tetrahedra(h1))
    h2_boundary = set(boundary_tetrahedra(h2))
    if not interface <= h1_boundary or not interface <= h2_boundary:
        raise AssertionError("attaching patch is not a boundary 3-ball of both handles")
    common = all_faces(h1)[3] & all_faces(h2)[3]
    if common != interface:
        raise AssertionError("the two handles meet outside the declared attaching patch")
    interface_betti = betti_numbers(list(interface), 3)
    union_betti = betti_numbers(union, 4)
    union_boundary = boundary_tetrahedra(union)
    boundary_betti = betti_numbers(union_boundary, 3)
    if interface_betti != [1, 0, 0, 0]:
        raise AssertionError("attaching patch is not a rational-homology 3-ball")
    if union_betti != [1, 0, 0, 0, 0] or boundary_betti != [1, 0, 0, 1]:
        raise AssertionError("standard glued pair does not have 4-ball/S3 homology")

    binding = data["actual_cell_binding"]
    belt = belts["t_handle"]["belt_sphere"]
    face_vertices = [
        tuple(Fraction(value) for value in belt["vertices"][index])
        for index in binding["actual_belt_face_vertex_indices"]
    ]
    barycenter = tuple(
        sum(vertex[axis] for vertex in face_vertices) / 3 for axis in range(4)
    )
    intersection = tuple(Fraction(value) for value in binding["actual_hcs_belt_intersection"])
    attaching = [
        tuple(Fraction(value) for value in item)
        for item in binding["actual_hcs_attaching_endpoints"]
    ]
    if intersection[:3] != barycenter[:3] or intersection[3] != Fraction(1, 2):
        raise AssertionError("actual belt-face binding lost its barycentric intersection")
    if attaching[0][:3] != intersection[:3] or attaching[1][:3] != intersection[:3]:
        raise AssertionError("actual h_CS arc misses the bound belt point")
    if (attaching[0][3], attaching[1][3]) != (0, 1):
        raise AssertionError("actual h_CS crossing arc is not transverse in u")
    hcs = ar_link["components"]["h_CS"]
    framing_offset = tuple(
        Fraction(value) for value in binding["actual_hcs_framing_offset"]
    )
    if list(binding["actual_hcs_attaching_endpoints"]) != hcs["core_polyline_T3xI"]:
        raise AssertionError("bound h_CS core differs from the actual AR link")
    if list(binding["actual_hcs_framing_offset"]) != hcs["framing_annulus"]["offset"]:
        raise AssertionError("bound h_CS framing differs from the actual AR annulus")
    if not any(framing_offset) or sum(framing_offset) != 0:
        raise AssertionError("h_CS offset is not a nonzero tangent of the positive belt face")
    if (
        hcs["framing_annulus"]["epsilon"] != 0
        or hcs["framing_annulus"]["relative_twist"] != 0
        or hcs["product_framing"] != "PASS"
        or binding["relative_twist"] != 0
    ):
        raise AssertionError("actual AR framing annulus does not have zero relative twist")

    remaining = data["deletion"]["remaining_components"]
    if set(remaining) != {"m_1", "m_2", "m_3", "r_xy", "r_yz", "r_zx"}:
        raise AssertionError("post-cancel component inventory changed")
    for component in ("m_1", "m_2", "m_3"):
        if remaining[component]["state6_core_sha256"] != movie["final_component_manifest"][component]["final_polyline_sha256"]:
            raise AssertionError("post-cancel core manifest changed")
        if remaining[component]["exteriorized_push_off_sha256"] != framing["components"][component]["exteriorized_push_off_sha256"]:
            raise AssertionError("post-cancel framing manifest changed")
    if data["deletion"]["deleted_handles"] != ["t", "h_CS"]:
        raise AssertionError("wrong handles were deleted")
    return {
        "verdict": "PASS_T_HCS_HANDLE_PAIR_DELETION_AND_POST_LINK_STATE",
        "standard_union_vertices": standard["glued_vertex_count"],
        "standard_union_four_simplices": len(union),
        "attaching_patch_tetrahedra": len(interface),
        "union_betti": union_betti,
        "boundary_betti": boundary_betti,
        "actual_belt_intersections": 1,
        "relative_twist": 0,
        "post_cancel_components": len(remaining),
        "next_consumer": data["deletion"]["consumer"],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
