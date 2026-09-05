#!/usr/bin/env python3
"""Independently verify the finite t-h_CS collar ejection map."""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_t_hcs_collar_ejection_map.json"
BELTS = ROOT / "geometry/t73_belt_spheres.json"
READINESS = ROOT / "audit/t73_t_hcs_cancellation_readiness.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def determinant3(columns):
    first, second, third = columns
    return (
        first[0] * (second[1] * third[2] - second[2] * third[1])
        - second[0] * (first[1] * third[2] - first[2] * third[1])
        + third[0] * (first[1] * second[2] - first[2] * second[1])
    )


def tetrahedron_determinant(vertices, tetrahedron):
    origin = vertices[tetrahedron[0]]
    columns = [
        tuple(vertices[index][axis] - origin[axis] for axis in range(3))
        for index in tetrahedron[1:]
    ]
    return determinant3(columns)


def tetrahedron_faces(tetrahedron):
    return [tuple(sorted(face)) for face in combinations(tetrahedron, 3)]


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    if data["completion_status"] != "T_HCS_COLLAR_EJECTION_CELL_MAP_CONSTRUCTED":
        raise AssertionError("collar ejection status changed")
    if readiness["verdict"] != "READY_FOR_EXPLICIT_T_HCS_CANCELLATION_MAP":
        raise AssertionError("collar map is not bound to a cancellation-ready framed link")
    if data["belt_spheres_sha256"] != belts["sha256"] or data["cancellation_readiness_sha256"] != readiness["sha256"]:
        raise AssertionError("collar map has stale source hashes")
    source = [point(value) for value in data["source_vertices"]]
    target = [point(value) for value in data["target_vertex_images"]]
    tetrahedra = data["tetrahedra"]
    if len(source) != 12 or len(target) != 12 or len(tetrahedra) != 24:
        raise AssertionError("octahedral collar has the wrong finite-cell counts")

    radius = Fraction(data["radial_levels"]["source_inner"])
    target_radius = Fraction(data["radial_levels"]["target_inner"])
    outer_radius = Fraction(data["radial_levels"]["fixed_outer"])
    if target_radius != Fraction(3, 2) * radius or outer_radius != 2 * radius:
        raise AssertionError("collar radial levels changed")
    for index in range(6):
        if sum(abs(value) for value in source[index][:3]) != radius:
            raise AssertionError("source inner vertex left the r-octahedron")
        if sum(abs(value) for value in target[index][:3]) != target_radius:
            raise AssertionError("target inner vertex left the 3r/2-octahedron")
        if source[index + 6] != target[index + 6]:
            raise AssertionError("outer collar boundary is not fixed")
        if sum(abs(value) for value in source[index + 6][:3]) != outer_radius:
            raise AssertionError("outer vertex left the 2r-octahedron")

    orientation_ratios = []
    for tetrahedron in tetrahedra:
        source_determinant = tetrahedron_determinant(source, tetrahedron)
        target_determinant = tetrahedron_determinant(target, tetrahedron)
        if not source_determinant or not target_determinant:
            raise AssertionError("collar map contains a degenerate tetrahedron")
        ratio = target_determinant / source_determinant
        if ratio <= 0:
            raise AssertionError("collar affine cell reverses orientation")
        orientation_ratios.append(ratio)

    face_counts = Counter(
        face for tetrahedron in tetrahedra for face in tetrahedron_faces(tetrahedron)
    )
    if set(face_counts.values()) - {1, 2}:
        raise AssertionError("collar tetrahedra do not form a 3-manifold")
    boundary = {face for face, count in face_counts.items() if count == 1}
    expected_boundary = {
        *[tuple(face) for face in data["source_inner_boundary_triangles"]],
        *[tuple(face) for face in data["source_outer_boundary_triangles"]],
    }
    if boundary != expected_boundary:
        raise AssertionError("collar boundary is not the two declared octahedral spheres")
    return {
        "verdict": "PASS_T_HCS_COLLAR_EJECTION_CELL_MAP",
        "vertices": len(source),
        "tetrahedra": len(tetrahedra),
        "boundary_triangles": len(boundary),
        "orientation_preserving_cells": len(orientation_ratios),
        "minimum_affine_determinant_ratio": str(min(orientation_ratios)),
        "state6_framed_link_in_domain": True,
        "scope": "COLLAR_EJECTION_ONLY_HANDLE_PAIR_DELETION_OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
