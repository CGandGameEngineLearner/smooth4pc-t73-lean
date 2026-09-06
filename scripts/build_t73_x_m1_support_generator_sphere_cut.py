#!/usr/bin/env python3
"""Cut the collar-support S2xS1 along its explicit cubical generator S2."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
TOPOLOGY = ROOT / "audit/t73_x_m1_collar_boundary_topology.json"
REGINA = ROOT / "audit/t73_x_m1_regina_boundary_recognition.json"
OUTPUT = ROOT / "geometry/t73_x_m1_support_generator_sphere_cut.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def facets(simplex):
    return [tuple(sorted(face)) for face in itertools.combinations(simplex, len(simplex) - 1)]


def connected_components(faces):
    adjacency = defaultdict(set)
    for face in faces:
        for left, right in itertools.combinations(face, 2):
            adjacency[left].add(right)
            adjacency[right].add(left)
    vertices = {vertex for face in faces for vertex in face}
    components = []
    while vertices:
        start = min(vertices)
        stack = [start]
        component = set()
        while stack:
            vertex = stack.pop()
            if vertex in component:
                continue
            component.add(vertex)
            stack.extend(adjacency[vertex] - component)
        vertices -= component
        components.append(component)
    return components


def build():
    product = json.loads(PRODUCT.read_text())
    topology = json.loads(TOPOLOGY.read_text())
    regina = json.loads(REGINA.read_text())
    four = [tuple(value) for value in product["four_simplices"]]
    counts = Counter(face for simplex in four for face in facets(simplex))
    boundary = sorted(face for face, count in counts.items() if count == 1)
    layers = {
        "A_x1_inner": set(range(0, 8)),
        "B_x1_outer": set(range(8, 16)),
        "C_x3_inner": set(range(16, 24)),
        "D_x3_outer": set(range(24, 32)),
    }
    generator = sorted(
        face
        for tetrahedron in boundary
        for face in facets(tetrahedron)
        if set(face) <= layers["A_x1_inner"]
    )
    generator = sorted(set(generator))
    duplicate = {vertex: 32 + vertex for vertex in layers["A_x1_inner"]}
    class_counts = Counter()
    cut_tetrahedra = []
    for tetrahedron in boundary:
        used = "".join(
            label[0] for label, vertices in layers.items() if set(tetrahedron) & vertices
        )
        class_counts[used] += 1
        if used == "AC":
            tetrahedron = tuple(sorted(duplicate.get(vertex, vertex) for vertex in tetrahedron))
        cut_tetrahedra.append(tetrahedron)
    cut_face_counts = Counter(face for tetrahedron in cut_tetrahedra for face in facets(tetrahedron))
    cut_boundary = sorted(face for face, count in cut_face_counts.items() if count == 1)
    components = connected_components(cut_boundary)
    component_records = []
    capped_tetrahedra = list(cut_tetrahedra)
    cap_vertices = []
    for component_index, component in enumerate(sorted(components, key=min)):
        faces = [face for face in cut_boundary if set(face) <= component]
        edges = {edge for face in faces for edge in itertools.combinations(face, 2)}
        cap_vertex = 40 + component_index
        cap_vertices.append(cap_vertex)
        capped_tetrahedra.extend(
            tuple(sorted((*face, cap_vertex))) for face in faces
        )
        component_records.append({
            "component_index": component_index,
            "vertices": sorted(component),
            "edges": [list(edge) for edge in sorted(edges)],
            "triangles": [list(face) for face in sorted(faces)],
            "simplex_counts": [len(component), len(edges), len(faces)],
            "euler_characteristic": len(component) - len(edges) + len(faces),
            "cap_vertex": cap_vertex,
        })
    capped_face_counts = Counter(face for tetrahedron in capped_tetrahedra for face in facets(tetrahedron))
    if set(capped_face_counts.values()) != {2}:
        raise AssertionError("capped generator cut is not closed")

    vertices = [
        {"kind": "source_product_vertex", "source_vertex": index}
        for index in range(32)
    ] + [
        {"kind": "cut_copy", "source_vertex": index}
        for index in range(8)
    ] + [
        {"kind": "sphere_cap", "boundary_component": index}
        for index in range(2)
    ]
    result = {
        "schema": "t73_x_m1_support_generator_sphere_cut/v1",
        "x_m1_collar_product_extension_sha256": product["sha256"],
        "x_m1_collar_boundary_topology_sha256": topology["sha256"],
        "x_m1_regina_boundary_recognition_sha256": regina["sha256"],
        "product_vertex_layers": {
            name: sorted(values) for name, values in layers.items()
        },
        "boundary_tetrahedron_class_counts": dict(sorted(class_counts.items())),
        "generator_sphere_vertices": sorted(layers["A_x1_inner"]),
        "generator_sphere_triangles": [list(face) for face in generator],
        "generator_sphere_simplex_counts": [8, 18, 12],
        "cut_duplicate_vertex_map": [[old, new] for old, new in sorted(duplicate.items())],
        "cut_side_rule": "AB keeps A=0..7; AC uses the copied A=32..39",
        "cut_vertices": vertices[:40],
        "cut_tetrahedra": [list(value) for value in cut_tetrahedra],
        "cut_boundary_components": component_records,
        "cut_boundary_component_count": len(component_records),
        "cut_boundary_triangle_count": len(cut_boundary),
        "capped_vertices": vertices,
        "cap_vertices": cap_vertices,
        "capped_tetrahedra": [list(value) for value in capped_tetrahedra],
        "capped_recognition_status": "OPEN_REGINA_S3_CHECK",
        "cut_product_type_status": "OPEN_UNTIL_CAPPED_S3_CHECK",
        "completion_status": "EXPLICIT_SUPPORT_GENERATOR_SPHERE_CUT_CONSTRUCTED",
    }
    result["sha256"] = canonical_sha256(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("support generator sphere cut is stale")
    print(json.dumps({
        "generator": result["generator_sphere_simplex_counts"],
        "cut_tetrahedra": len(result["cut_tetrahedra"]),
        "boundary_components": result["cut_boundary_component_count"],
        "boundary_triangles": result["cut_boundary_triangle_count"],
        "capped_tetrahedra": len(result["capped_tetrahedra"]),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
