#!/usr/bin/env python3
"""Verify the local PL tubular frame of the complete m1 parallel annulus."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from verify_t73_candidate_t_band0_surface import triangles_intersect
from verify_t73_x_m1_parallel_foliation import translate_triangle, triangle_translations, verify as verify_foliation

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_m1_parallel_annulus_tubular_frame.json"
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def determinant3(first, second, third, axes):
    matrix = [[value[axis] for value in (first, second, third)] for axis in axes]
    return matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]) - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0]) + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])


def verify():
    if verify_foliation()["verdict"] != "PASS_ALL_1513_M1_PARALLELS_IN_EMBEDDED_QUOTIENT_ANNULUS":
        raise AssertionError("source m1 annulus did not verify")
    data = json.loads(DATA.read_text(encoding="utf-8")); foliation = json.loads(FOLIATION.read_text(encoding="utf-8")); product = json.loads(PRODUCT.read_text(encoding="utf-8"))
    if data["sha256"] != canonical_sha({key: value for key, value in data.items() if key != "sha256"}) or data["m1_parallel_foliation_sha256"] != foliation["sha256"] or data["x_m1_collar_product_extension_sha256"] != product["sha256"]:
        raise AssertionError("m1 tubular-frame hashes changed")
    base = [point(value) for value in foliation["base_vertices"]]; normals = [point(value) for value in foliation["unit_normal_field"]]
    outward = point(data["outward_integer_vector"]); certificates = data["segment_transversality_certificates"]
    if outward != (-3, -3, -2, -3) or len(certificates) != 34:
        raise AssertionError("canonical outward frame changed")
    for index, certificate in enumerate(certificates):
        tangent = tuple(base[index + 1][axis] - base[index][axis] for axis in range(4)); axes = tuple(certificate["coordinate_minor"])
        first, second = determinant3(tangent, normals[index], outward, axes), determinant3(tangent, normals[index + 1], outward, axes)
        if str(first) != certificate["start_determinant"] or str(second) != certificate["end_determinant"] or first * second <= 0:
            raise AssertionError("m1 tubular transversality certificate changed")
    source = [point(value) for value in data["source_annulus_vertices"]]; pushed = [point(value) for value in data["pushed_annulus_vertices"]]; displacement = point(data["outward_displacement"])
    expected_source = base + [point(value) for value in foliation["outer_vertices"]]
    if source != expected_source or any(pushed[index] != tuple(source[index][axis] + displacement[axis] for axis in range(4)) for index in range(70)):
        raise AssertionError("m1 tubular boundary vertices changed")
    triangle_ids = data["annulus_triangles"]; source_triangles = [tuple(source[index] for index in ids) for ids in triangle_ids]; push_triangles = [tuple(pushed[index] for index in ids) for ids in triangle_ids]
    separation_checks = 0
    for first in source_triangles:
        for second in push_triangles:
            for deck in triangle_translations(first, second):
                separation_checks += 1
                if triangles_intersect(first, translate_triangle(second, tuple(deck))):
                    raise AssertionError("source and pushed m1 annuli intersect in the quotient")
    vertices = [point(value) for value in data["tubular_vertices"]]; tetrahedra = data["tubular_tetrahedra"]
    if vertices != source + pushed or len(tetrahedra) != 204:
        raise AssertionError("m1 tubular prism counts changed")
    for tetrahedron in tetrahedra:
        origin = vertices[tetrahedron[0]]; vectors = [tuple(vertices[index][axis] - origin[axis] for axis in range(4)) for index in tetrahedron[1:]]
        if not any(determinant3(*vectors, axes) for axes in combinations(range(4), 3)):
            raise AssertionError("m1 tubular prism has a degenerate tetrahedron")
    faces = Counter(tuple(sorted(face)) for tetrahedron in tetrahedra for face in combinations(tetrahedron, 3))
    if max(faces.values()) != 2 or any(value not in (1, 2) for value in faces.values()):
        raise AssertionError("m1 tubular prisms do not form a pseudomanifold")
    if data["completion_status"] != "M1_PARALLEL_ANNULUS_LOCAL_TUBULAR_FRAME_CONSTRUCTED" or data["nonlocal_tetrahedron_clearance_status"] != "OPEN_EXACT_NONINCIDENT_CELL_CHECK":
        raise AssertionError("m1 tubular-frame scope changed")
    return {"verdict": "PASS_M1_PARALLEL_ANNULUS_LOCAL_TUBULAR_FRAME", "annulus_triangles": 68, "tubular_tetrahedra": 204, "segment_transversality_checks": 34, "source_push_quotient_separation_checks": separation_checks, "nonlocal_tetrahedron_clearance_status": data["nonlocal_tetrahedron_clearance_status"]}


if __name__ == "__main__": print(json.dumps(verify(), sort_keys=True))
