#!/usr/bin/env python3
"""Verify the explicit cubical generator sphere and cut-open complex."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict, deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_support_generator_sphere_cut.json"
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def facets(simplex):
    return [tuple(sorted(face)) for face in itertools.combinations(simplex, len(simplex) - 1)]


def verify():
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("generator-sphere cut payload SHA mismatch")
    product = json.loads(PRODUCT.read_text())
    if data["x_m1_collar_product_extension_sha256"] != product["sha256"]:
        raise AssertionError("generator-sphere cut product binding changed")
    four = [tuple(value) for value in product["four_simplices"]]
    face_counts = Counter(face for simplex in four for face in facets(simplex))
    boundary = sorted(face for face, count in face_counts.items() if count == 1)
    sphere = sorted(
        set(face for tetrahedron in boundary for face in facets(tetrahedron) if set(face) <= set(range(8)))
    )
    sphere_edges = Counter(edge for face in sphere for edge in itertools.combinations(face, 2))
    if (len(set(vertex for face in sphere for vertex in face)), len(sphere_edges), len(sphere)) != (8, 18, 12):
        raise AssertionError("generator sphere inventory changed")
    if set(sphere_edges.values()) != {2} or 8 - 18 + 12 != 2:
        raise AssertionError("generator subcomplex is not a closed 2-sphere")
    if [list(face) for face in sphere] != data["generator_sphere_triangles"]:
        raise AssertionError("saved generator sphere changed")

    duplicate = dict(data["cut_duplicate_vertex_map"])
    expected_cut = []
    class_counts = Counter()
    layers = {name: set(values) for name, values in data["product_vertex_layers"].items()}
    for tetrahedron in boundary:
        used = "".join(label[0] for label, values in layers.items() if set(tetrahedron) & values)
        class_counts[used] += 1
        expected_cut.append(tuple(sorted(duplicate.get(vertex, vertex) for vertex in tetrahedron)) if used == "AC" else tetrahedron)
    if [list(value) for value in expected_cut] != data["cut_tetrahedra"]:
        raise AssertionError("cut tetrahedron map changed")
    if class_counts != Counter({"AB": 36, "AC": 36, "BD": 36, "CD": 36}):
        raise AssertionError("product boundary class inventory changed")
    cut_faces = Counter(face for tetrahedron in expected_cut for face in facets(tetrahedron))
    if set(cut_faces.values()) != {1, 2}:
        raise AssertionError("cut complex has nonmanifold face degree")
    cut_boundary = sorted(face for face, count in cut_faces.items() if count == 1)
    if len(cut_boundary) != 24:
        raise AssertionError("cut boundary triangle count changed")
    for component in data["cut_boundary_components"]:
        faces = [tuple(value) for value in component["triangles"]]
        edges = Counter(edge for face in faces for edge in itertools.combinations(face, 2))
        if component["simplex_counts"] != [8, 18, 12] or component["euler_characteristic"] != 2:
            raise AssertionError("cut boundary component is not a sphere")
        if set(edges.values()) != {2}:
            raise AssertionError("cut boundary sphere has wrong edge degree")
    capped = [tuple(value) for value in data["capped_tetrahedra"]]
    capped_faces = Counter(face for tetrahedron in capped for face in facets(tetrahedron))
    if len(capped) != 168 or set(capped_faces.values()) != {2}:
        raise AssertionError("capped cut complex is not closed")
    return {
        "verdict": "PASS_X_M1_SUPPORT_GENERATOR_SPHERE_CUT",
        "generator_sphere_triangles": 12,
        "cut_tetrahedra": 144,
        "cut_boundary_spheres": 2,
        "cut_boundary_triangles": 24,
        "capped_tetrahedra": 168,
        "capped_recognition": data["capped_recognition_status"],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
