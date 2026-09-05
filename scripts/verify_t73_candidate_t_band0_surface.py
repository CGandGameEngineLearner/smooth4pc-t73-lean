#!/usr/bin/env python3
"""Independently verify the first candidate framed band disk."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SURFACE = ROOT / "geometry/t73_candidate_t_band0_surface.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def edge(first: int, second: int):
    return tuple(sorted((first, second)))


def triangle_nondegenerate(vertices, triangle) -> bool:
    origin, first, second = (vertices[index] for index in triangle)
    left = tuple(first[i] - origin[i] for i in range(4))
    right = tuple(second[i] - origin[i] for i in range(4))
    return any(
        left[j] * right[i] - left[i] * right[j] != 0
        for i in range(4) for j in range(i + 1, 4)
    )


def chain_edges(chain):
    return {edge(first, second) for first, second in zip(chain, chain[1:])}


def verify() -> dict:
    data = json.loads(SURFACE.read_text(encoding="utf-8"))
    if data["completion_status"] != "CANDIDATE_FRAMED_BAND_DISK":
        raise AssertionError("candidate band-disk status changed")
    vertices = [point(value) for value in data["vertices"]]
    triangles = data["triangles"]
    if any(not triangle_nondegenerate(vertices, triangle) for triangle in triangles):
        raise AssertionError("candidate band disk has a degenerate triangle")
    edge_counts = Counter(
        edge(triangle[i], triangle[(i + 1) % 3])
        for triangle in triangles for i in range(3)
    )
    if set(edge_counts.values()) - {1, 2}:
        raise AssertionError("candidate band disk is not a triangle manifold")
    boundary_edges = {item for item, count in edge_counts.items() if count == 1}
    boundary = data["boundary"]
    expected_boundary = {
        edge(*boundary["source_attachment"]),
        edge(*boundary["target_attachment"]),
        *chain_edges(boundary["left_lane"]),
        *chain_edges(boundary["right_lane"]),
    }
    if boundary_edges != expected_boundary:
        raise AssertionError("candidate band-disk boundary decomposition changed")
    euler = len(vertices) - len(edge_counts) + len(triangles)
    if euler != 1:
        raise AssertionError("candidate band surface is not a disk")
    normals = [point(value) for value in data["normal_field"]]
    push_vertices = [point(value) for value in data["push_off_vertices"]]
    if len(normals) != len(vertices) or len(push_vertices) != len(vertices):
        raise AssertionError("candidate band framing arrays have the wrong length")
    for vertex, normal, pushed in zip(vertices, normals, push_vertices):
        if not any(normal):
            raise AssertionError("candidate band disk has a zero normal")
        if tuple(vertex[i] + normal[i] for i in range(4)) != pushed:
            raise AssertionError("candidate band push-off is not vertex plus normal")
    return {
        "verdict": "PASS_CANDIDATE_FRAMED_BAND_DISK_COMBINATORICS_ONLY",
        "vertices": len(vertices),
        "triangles": len(triangles),
        "boundary_edges": len(boundary_edges),
        "euler_characteristic": euler,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
