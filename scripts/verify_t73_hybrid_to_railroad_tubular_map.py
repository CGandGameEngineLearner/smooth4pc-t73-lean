#!/usr/bin/env python3
"""Verify the five common solid-torus templates and framed homeomorphisms."""

from __future__ import annotations

import json
from collections import Counter
from itertools import combinations
from pathlib import Path

from verify_t73_hybrid_to_railroad_graph_map import verify as verify_graph

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_hybrid_to_railroad_tubular_map.json"
GRAPH = ROOT / "geometry/t73_hybrid_to_railroad_graph_map.json"
RAILROAD = ROOT / "geometry/t73_actual_railroad_core_coordinates.json"
FRAMINGS = ROOT / "geometry/t73_railroad_product_framings.json"
PD = ROOT / "geometry/t73_source_bound_standard_pd_candidate.json"


def expected_tetrahedra(segment_count):
    tetrahedra = []
    for segment in range(segment_count):
        next_segment = (segment + 1) % segment_count
        first = [3 * segment + index for index in range(3)]
        second = [3 * next_segment + index for index in range(3)]
        tetrahedra.extend([
            [first[0], first[1], first[2], second[2]],
            [first[0], first[1], second[1], second[2]],
            [first[0], second[0], second[1], second[2]],
        ])
    return tetrahedra


def verify() -> dict:
    if verify_graph()["verdict"] != "PASS_HYBRID_TO_RAILROAD_FRAMED_GRAPH_ISOMORPHISM_ONLY":
        raise AssertionError("framed graph map did not verify")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    railroad = json.loads(RAILROAD.read_text(encoding="utf-8"))
    framings = json.loads(FRAMINGS.read_text(encoding="utf-8"))
    pd = json.loads(PD.read_text(encoding="utf-8"))
    if data["completion_status"] != "HYBRID_TO_RAILROAD_FRAMED_TUBULAR_HOMEOMORPHISM_CONSTRUCTED":
        raise AssertionError("tubular-map scope changed")
    expected_hashes = {
        "hybrid_to_railroad_graph_map_sha256": graph["sha256"],
        "railroad_core_coordinates_sha256": railroad["sha256"],
        "railroad_product_framings_sha256": framings["sha256"],
        "source_bound_standard_pd_sha256": pd["sha256"],
    }
    if any(data[field] != value for field, value in expected_hashes.items()):
        raise AssertionError("tubular map has stale sources")
    total_tetrahedra = total_boundary = 0
    component_euler = {}
    for component in data["components"]:
        segment_count = component["target_segment_count"]
        tetrahedra = component["tetrahedra"]
        if tetrahedra != expected_tetrahedra(segment_count):
            raise AssertionError("solid-torus staircase tetrahedra changed")
        face_counts = Counter(
            tuple(sorted(face))
            for tetrahedron in tetrahedra
            for face in combinations(tetrahedron, 3)
        )
        if set(face_counts.values()) - {1, 2}:
            raise AssertionError("solid-torus template is not a 3-manifold")
        boundary = {face for face, count in face_counts.items() if count == 1}
        declared_boundary = {
            tuple(sorted(face)) for face in component["boundary_triangles"]
        }
        if boundary != declared_boundary or len(boundary) != 6 * segment_count:
            raise AssertionError("solid-torus boundary triangulation changed")
        edges = {
            tuple(sorted(edge))
            for tetrahedron in tetrahedra
            for edge in combinations(tetrahedron, 2)
        }
        faces = set(face_counts)
        vertices = {vertex for tetrahedron in tetrahedra for vertex in tetrahedron}
        euler = len(vertices) - len(edges) + len(faces) - len(tetrahedra)
        if euler != 0:
            raise AssertionError("solid-torus template Euler characteristic changed")
        boundary_edges = Counter(
            tuple(sorted(edge))
            for triangle in boundary
            for edge in combinations(triangle, 2)
        )
        if set(boundary_edges.values()) != {2} or len(vertices) - len(boundary_edges) + len(boundary) != 0:
            raise AssertionError("solid-torus boundary is not a closed Euler-zero surface")
        covered = set()
        subdivision_total = 0
        for source_edge in component["source_edge_subdivision"]:
            start, end = source_edge["target_segment_range"]
            values = set(range(start, end + 1))
            if covered & values:
                raise AssertionError("two source edges share a target tube segment")
            covered.update(values)
            subdivision_total += source_edge["subdivision_segment_count"]
        if covered != set(range(segment_count)) or subdivision_total != segment_count:
            raise AssertionError("source edge subdivisions do not cover the target tube")
        if component["closing_fiber_map"] != [0, 1, 2] or component["relative_twist"] != 0:
            raise AssertionError("solid-torus closing map changed the product framing")
        component_euler[component["component"]] = euler
        total_tetrahedra += len(tetrahedra)
        total_boundary += len(boundary)
    if data["complement_extension_status"] != "OPEN_HANDLEBODY_COMPLEMENT_CELL_MAP_REQUIRED":
        raise AssertionError("tubular map overstates complement extension")
    return {
        "verdict": "PASS_HYBRID_TO_RAILROAD_FRAMED_TUBULAR_HOMEOMORPHISMS_ONLY",
        "components": len(data["components"]),
        "tetrahedra": total_tetrahedra,
        "boundary_triangles": total_boundary,
        "component_euler_characteristics": component_euler,
        "relative_twists": [0, 0, 0, 0, 0],
        "complement_extension_status": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
