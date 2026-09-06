#!/usr/bin/env python3
"""Build a rational R3 realization of the quotient annulus-times-interval."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
EJECTION = ROOT / "geometry/t73_m1_parallel_annulus_ambient_ejection.json"
OUTPUT = ROOT / "geometry/t73_x_m1_canonical_r3_annulus_chart.json"
ANGLE_COUNT = 34
RADIAL_SIDES = 2
HEIGHTS = (Fraction(-1), Fraction(0), Fraction(1))


def canonical_sha256(value: dict) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def encode(point):
    return [str(value) for value in point]


def polygon_vertex(index: int):
    return Fraction(index), Fraction(index * index)


def polygon_centroid():
    return Fraction(33, 2), Fraction(737, 2)


def annulus_vertex(angle: int, radial_side: int):
    outer = polygon_vertex(angle)
    center = polygon_centroid()
    alpha = Fraction(radial_side, 2)
    return tuple(
        (1 - alpha) * outer[axis] + alpha * center[axis]
        for axis in range(2)
    )


def vertex_index(height_layer: int, radial_side: int, angle: int):
    return (
        height_layer * (RADIAL_SIDES * ANGLE_COUNT)
        + radial_side * ANGLE_COUNT
        + angle
    )


def annulus_triangles(layer: int):
    triangles = []
    for angle in range(ANGLE_COUNT):
        following = (angle + 1) % ANGLE_COUNT
        outer = vertex_index(layer, 0, angle)
        outer_next = vertex_index(layer, 0, following)
        inner = vertex_index(layer, 1, angle)
        inner_next = vertex_index(layer, 1, following)
        triangles.extend(
            ([outer, outer_next, inner_next], [outer, inner_next, inner])
        )
    return triangles


def staircase_prism(lower_triangle, layer_offset):
    layer_size = RADIAL_SIDES * ANGLE_COUNT
    local = sorted(vertex % layer_size for vertex in lower_triangle)
    lower = [layer_offset * layer_size + vertex for vertex in local]
    upper = [(layer_offset + 1) * layer_size + vertex for vertex in local]
    a, b, c = lower
    upper_a, upper_b, upper_c = upper
    return [
        [a, b, c, upper_c],
        [a, b, upper_b, upper_c],
        [a, upper_a, upper_b, upper_c],
    ]


def faces(tetrahedron):
    return [
        tuple(sorted(tetrahedron[:index] + tetrahedron[index + 1:]))
        for index in range(4)
    ]


def build() -> dict:
    foliation = json.loads(FOLIATION.read_text())
    ejection = json.loads(EJECTION.read_text())
    vertices = []
    for height in HEIGHTS:
        for radial_side in range(RADIAL_SIDES):
            for angle in range(ANGLE_COUNT):
                x, y = annulus_vertex(angle, radial_side)
                vertices.append(encode((x, y, height)))

    base_triangles = annulus_triangles(0)
    tetrahedra = []
    for layer in range(2):
        for triangle in base_triangles:
            tetrahedra.extend(staircase_prism(triangle, layer))
    face_counts = Counter(
        face for tetrahedron in tetrahedra for face in faces(tetrahedron)
    )
    boundary_faces = [
        list(face) for face, count in sorted(face_counts.items()) if count == 1
    ]
    if set(face_counts.values()) != {1, 2}:
        raise AssertionError("canonical annulus chart is not a 3-manifold with boundary")

    result = {
        "schema": "t73_x_m1_canonical_r3_annulus_chart/v1",
        "x_m1_parallel_foliation_sha256": foliation["sha256"],
        "m1_annulus_ambient_ejection_sha256": ejection["sha256"],
        "construction": (
            "homothetic convex 34-gon annulus times a three-layer interval"
        ),
        "mapping_torus_quotient_rule": (
            "source angular indices 0 and 34 map to canonical angle 0"
        ),
        "angle_count": ANGLE_COUNT,
        "radial_side_count": RADIAL_SIDES,
        "height_layers": [str(value) for value in HEIGHTS],
        "outer_polygon_vertices": [
            encode(polygon_vertex(index)) for index in range(ANGLE_COUNT)
        ],
        "polygon_centroid": encode(polygon_centroid()),
        "inner_homothety": "1/2",
        "vertices": vertices,
        "tetrahedra": tetrahedra,
        "boundary_triangles": boundary_faces,
        "vertex_count": len(vertices),
        "tetrahedron_count": len(tetrahedra),
        "boundary_triangle_count": len(boundary_faces),
        "topological_type": "S1 x I x I (solid torus)",
        "completion_status": "CANONICAL_RATIONAL_R3_ANNULUS_CHART_CONSTRUCTED",
    }
    result["sha256"] = canonical_sha256(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("canonical R3 annulus chart is stale")
    print(json.dumps({
        "vertices": result["vertex_count"],
        "tetrahedra": result["tetrahedron_count"],
        "boundary_triangles": result["boundary_triangle_count"],
        "type": result["topological_type"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
