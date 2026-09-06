#!/usr/bin/env python3
"""Verify the rational solid-torus chart used by the x/m1 middle paths."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_canonical_r3_annulus_chart.json"
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
EJECTION = ROOT / "geometry/t73_m1_parallel_annulus_ambient_ejection.json"


def canonical_sha256(value: dict) -> str:
    unsigned = {key: item for key, item in value.items() if key != "sha256"}
    encoded = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def determinant(first, second, third):
    return (
        first[0] * (second[1] * third[2] - second[2] * third[1])
        - first[1] * (second[0] * third[2] - second[2] * third[0])
        + first[2] * (second[0] * third[1] - second[1] * third[0])
    )


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def faces(tetrahedron):
    return [
        tuple(sorted(tetrahedron[:index] + tetrahedron[index + 1:]))
        for index in range(4)
    ]


def verify() -> dict:
    data = json.loads(DATA.read_text())
    foliation = json.loads(FOLIATION.read_text())
    ejection = json.loads(EJECTION.read_text())
    if data["sha256"] != canonical_sha256(data):
        raise AssertionError("canonical R3 annulus chart SHA mismatch")
    if data["x_m1_parallel_foliation_sha256"] != foliation["sha256"]:
        raise AssertionError("canonical chart foliation binding changed")
    if data["m1_annulus_ambient_ejection_sha256"] != ejection["sha256"]:
        raise AssertionError("canonical chart ejection binding changed")

    vertices = [point(value) for value in data["vertices"]]
    tetrahedra = data["tetrahedra"]
    if len(vertices) != 204 or len(tetrahedra) != 408:
        raise AssertionError("canonical solid-torus inventory changed")
    if len({tuple(tetrahedron) for tetrahedron in tetrahedra}) != len(tetrahedra):
        raise AssertionError("duplicate canonical tetrahedron")
    used_vertices = {vertex for tetrahedron in tetrahedra for vertex in tetrahedron}
    if used_vertices != set(range(len(vertices))):
        raise AssertionError("canonical solid torus has unused vertices")

    nonzero_volumes = 0
    for tetrahedron in tetrahedra:
        a, b, c, d = [vertices[index] for index in tetrahedron]
        volume6 = determinant(subtract(b, a), subtract(c, a), subtract(d, a))
        if volume6 == 0:
            raise AssertionError("canonical solid torus has a flat tetrahedron")
        nonzero_volumes += 1

    face_counts = Counter(face for tetrahedron in tetrahedra for face in faces(tetrahedron))
    if set(face_counts.values()) != {1, 2}:
        raise AssertionError("canonical chart has nonmanifold face multiplicity")
    boundary_faces = {face for face, count in face_counts.items() if count == 1}
    if boundary_faces != {tuple(face) for face in data["boundary_triangles"]}:
        raise AssertionError("canonical boundary face list changed")
    boundary_edge_counts = Counter(
        tuple(sorted((face[left], face[right])))
        for face in boundary_faces
        for left, right in ((0, 1), (0, 2), (1, 2))
    )
    if set(boundary_edge_counts.values()) != {2}:
        raise AssertionError("canonical boundary is not a closed surface")
    boundary_vertices = {vertex for edge in boundary_edge_counts for vertex in edge}
    euler = len(boundary_vertices) - len(boundary_edge_counts) + len(boundary_faces)
    if euler != 0:
        raise AssertionError("canonical boundary is not a torus by Euler characteristic")

    adjacency = defaultdict(set)
    for edge in boundary_edge_counts:
        adjacency[edge[0]].add(edge[1])
        adjacency[edge[1]].add(edge[0])
    reached = set()
    queue = deque([next(iter(boundary_vertices))])
    while queue:
        vertex = queue.popleft()
        if vertex in reached:
            continue
        reached.add(vertex)
        queue.extend(adjacency[vertex] - reached)
    if reached != boundary_vertices:
        raise AssertionError("canonical torus boundary is disconnected")

    return {
        "verdict": "PASS_X_M1_CANONICAL_R3_SOLID_TORUS_CHART",
        "vertices": len(vertices),
        "tetrahedra": len(tetrahedra),
        "nonzero_exact_tetrahedron_volumes": nonzero_volumes,
        "boundary_triangles": len(boundary_faces),
        "boundary_euler_characteristic": euler,
        "boundary_connected": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
