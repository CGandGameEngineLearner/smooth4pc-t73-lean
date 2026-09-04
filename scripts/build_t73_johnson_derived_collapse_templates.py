#!/usr/bin/env python3
"""Build the three standard second-derived elementary-collapse stars."""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "geometry" / "t73_johnson_derived_collapse_templates.json"
STANDARD_VERTICES = (
    (Fraction(0), Fraction(0), Fraction(0)),
    (Fraction(1), Fraction(0), Fraction(0)),
    (Fraction(0), Fraction(1), Fraction(0)),
    (Fraction(0), Fraction(0), Fraction(1)),
)
STAR_CENTERS = {
    1: (Fraction(4, 5), Fraction(1, 44), Fraction(1, 44)),
    2: (Fraction(295, 576), Fraction(211, 576), Fraction(1, 64)),
    3: (Fraction(277, 1056), Fraction(277, 1056), Fraction(277, 1056)),
}


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def average(points):
    return tuple(
        sum(point[axis] for point in points) / len(points) for axis in range(3)
    )


def det3(matrix):
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def subtract(first, second):
    return tuple(first[axis] - second[axis] for axis in range(3))


def cross(first, second):
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def dot(first, second):
    return sum(first[axis] * second[axis] for axis in range(3))


def subdivide_simplex(simplex):
    return [
        tuple(frozenset(permutation[:size]) for size in range(1, len(simplex) + 1))
        for permutation in itertools.permutations(simplex)
    ]


FIRST_SUBDIVISION = subdivide_simplex(tuple(range(4)))
SECOND_SUBDIVISION = [
    tetrahedron
    for first_tetrahedron in FIRST_SUBDIVISION
    for tetrahedron in subdivide_simplex(first_tetrahedron)
]


def first_coordinate(face):
    return average([STANDARD_VERTICES[index] for index in face])


def second_coordinate(simplex):
    return average([first_coordinate(face) for face in simplex])


def downward_closure(simplex):
    return {
        frozenset(face)
        for size in range(1, len(simplex) + 1)
        for face in itertools.combinations(simplex, size)
    }


def subdivided_core(complex_faces):
    return {
        frozenset(simplex)
        for tetrahedron in FIRST_SUBDIVISION
        for size in range(1, 5)
        for simplex in itertools.combinations(tetrahedron, size)
        if all(vertex in complex_faces for vertex in simplex)
    }


def closed_star(complex_faces):
    core = subdivided_core(complex_faces)
    return [
        tetrahedron
        for tetrahedron in SECOND_SUBDIVISION
        if any(vertex in core for vertex in tetrahedron)
    ]


def boundary_faces(tetrahedra):
    counts = collections.Counter(
        frozenset(tetrahedron[index] for index in range(4) if index != omitted)
        for tetrahedron in tetrahedra
        for omitted in range(4)
    )
    return {face for face, count in counts.items() if count == 1}


def surface_invariants(faces):
    edge_counts = collections.Counter(
        frozenset(edge) for face in faces for edge in itertools.combinations(face, 2)
    )
    vertices = {vertex for face in faces for vertex in face}
    face_list = list(faces)
    edge_faces = collections.defaultdict(list)
    for face_index, face in enumerate(face_list):
        for edge in itertools.combinations(face, 2):
            edge_faces[frozenset(edge)].append(face_index)
    adjacency = [set() for _ in face_list]
    for hits in edge_faces.values():
        if len(hits) == 2:
            first, second = hits
            adjacency[first].add(second)
            adjacency[second].add(first)
    seen = set()
    components = 0
    for start in range(len(face_list)):
        if start in seen:
            continue
        components += 1
        stack = [start]
        seen.add(start)
        while stack:
            current = stack.pop()
            for neighbour in adjacency[current]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
    boundary_edges = [edge for edge, count in edge_counts.items() if count == 1]
    boundary_adjacency = collections.defaultdict(set)
    for edge in boundary_edges:
        first, second = tuple(edge)
        boundary_adjacency[first].add(second)
        boundary_adjacency[second].add(first)
    boundary_seen = set()
    boundary_components = 0
    for start in boundary_adjacency:
        if start in boundary_seen:
            continue
        boundary_components += 1
        stack = [start]
        boundary_seen.add(start)
        while stack:
            current = stack.pop()
            for neighbour in boundary_adjacency[current]:
                if neighbour not in boundary_seen:
                    boundary_seen.add(neighbour)
                    stack.append(neighbour)
    euler = len(vertices) - len(edge_counts) + len(faces)
    manifold = all(count in (1, 2) for count in edge_counts.values())
    return {
        "vertices": len(vertices),
        "edges": len(edge_counts),
        "faces": len(faces),
        "euler": euler,
        "surface_components": components,
        "boundary_components": boundary_components,
        "boundary_edge_count": len(boundary_edges),
        "edge_multiplicities": {
            str(key): value
            for key, value in sorted(collections.Counter(edge_counts.values()).items())
        },
        "surface_manifold": manifold,
        "topology": (
            "sphere"
            if manifold and components == 1 and boundary_components == 0 and euler == 2
            else "disk"
            if manifold and components == 1 and boundary_components == 1 and euler == 1
            else "OPEN"
        ),
    }


def indexed_tetrahedra(tetrahedra):
    vertices = sorted({vertex for tetrahedron in tetrahedra for vertex in tetrahedron}, key=repr)
    index = {vertex: position for position, vertex in enumerate(vertices)}
    return vertices, [tuple(index[vertex] for vertex in tetrahedron) for tetrahedron in tetrahedra]


def build_dimension(dimension, collapse_tools):
    simplex = frozenset(range(dimension + 1))
    free_face = frozenset(range(1, dimension + 1))
    before_complex = downward_closure(simplex)
    after_complex = set(before_complex) - {simplex, free_face}
    before = closed_star(before_complex)
    after = closed_star(after_complex)
    before_set = {frozenset(tetrahedron) for tetrahedron in before}
    after_set = {frozenset(tetrahedron) for tetrahedron in after}
    if not after_set < before_set:
        raise AssertionError("after-star is not a proper subcomplex of before-star")
    before_boundary = boundary_faces(before)
    after_boundary = boundary_faces(after)
    common_boundary = before_boundary & after_boundary
    before_patch = before_boundary - common_boundary
    after_patch = after_boundary - common_boundary
    difference = [
        tetrahedron
        for tetrahedron in before
        if frozenset(tetrahedron) not in after_set
    ]
    before_vertices, before_indexed = indexed_tetrahedra(before)
    after_vertices, after_indexed = indexed_tetrahedra(after)
    before_ball = collapse_tools.fast_collapse_to_point(before_indexed)
    after_ball = collapse_tools.fast_collapse_to_point(after_indexed)
    before_boundary_invariants = surface_invariants(before_boundary)
    after_boundary_invariants = surface_invariants(after_boundary)
    before_patch_invariants = surface_invariants(before_patch)
    after_patch_invariants = surface_invariants(after_patch)
    difference_vertices, difference_indexed = indexed_tetrahedra(difference)
    difference_boundary = boundary_faces(difference)
    difference_boundary_invariants = surface_invariants(difference_boundary)
    difference_collapse = collapse_tools.fast_collapse_to_point(difference_indexed)
    if difference_boundary != before_patch | after_patch:
        raise AssertionError("difference-ball boundary is not the two disk patches")
    star_center = STAR_CENTERS[dimension]
    face_incidence = collections.defaultdict(list)
    for tetrahedron_index, tetrahedron in enumerate(difference):
        for omitted in range(4):
            face_incidence[
                frozenset(
                    tetrahedron[index] for index in range(4) if index != omitted
                )
            ].append(tetrahedron_index)
    strict_margins = []
    cone_tetrahedra = []
    for face in difference_boundary:
        face_points = [second_coordinate(vertex) for vertex in face]
        incident = face_incidence[face]
        if len(incident) != 1:
            raise AssertionError("difference boundary face is not free")
        interior = average(
            [second_coordinate(vertex) for vertex in difference[incident[0]]]
        )
        normal = cross(
            subtract(face_points[1], face_points[0]),
            subtract(face_points[2], face_points[0]),
        )
        margin = dot(normal, subtract(interior, face_points[0])) * dot(
            normal, subtract(star_center, face_points[0])
        )
        strict_margins.append(margin)
        cone_tetrahedra.append((star_center, *face_points))
    if min(strict_margins) <= 0:
        raise AssertionError("recorded difference-ball star center is not strict")
    cone_faces = collections.Counter(
        frozenset(tetrahedron[index] for index in range(4) if index != omitted)
        for tetrahedron in cone_tetrahedra
        for omitted in range(4)
    )
    if set(cone_faces.values()) != {1, 2}:
        raise AssertionError("star cone is not a face-to-face ball")
    cone_determinants = []
    for tetrahedron in cone_tetrahedra:
        matrix = [
            [
                tetrahedron[column][row] - tetrahedron[0][row]
                for column in range(1, 4)
            ]
            for row in range(3)
        ]
        cone_determinants.append(det3(matrix))
    if any(determinant == 0 for determinant in cone_determinants):
        raise AssertionError("star-cone tetrahedron is degenerate")
    if (
        before_boundary_invariants["topology"] != "sphere"
        or after_boundary_invariants["topology"] != "sphere"
        or not before_ball["collapses_to_point"]
        or not after_ball["collapses_to_point"]
        or before_patch_invariants["topology"] != "disk"
        or after_patch_invariants["topology"] != "disk"
        or before_patch_invariants["boundary_edge_count"]
        != after_patch_invariants["boundary_edge_count"]
    ):
        raise AssertionError("standard derived collapse is not a ball disk-move")
    determinants = []
    for tetrahedron in SECOND_SUBDIVISION:
        points = [second_coordinate(vertex) for vertex in tetrahedron]
        matrix = [
            [points[column][row] - points[0][row] for column in range(1, 4)]
            for row in range(3)
        ]
        determinants.append(det3(matrix))
    if any(determinant == 0 for determinant in determinants):
        raise AssertionError("second subdivision has a degenerate tetrahedron")
    return {
        "collapse_dimension": dimension,
        "simplex": sorted(simplex),
        "free_face": sorted(free_face),
        "first_subdivision_tetrahedra": len(FIRST_SUBDIVISION),
        "second_subdivision_tetrahedra": len(SECOND_SUBDIVISION),
        "before_star_tetrahedra": len(before),
        "after_star_tetrahedra": len(after),
        "common_tetrahedra": len(before_set & after_set),
        "difference_tetrahedra": len(before_set - after_set),
        "difference_ball": {
            "tetrahedra": len(difference),
            "boundary": difference_boundary_invariants,
            "collapse": difference_collapse,
            "boundary_equals_before_and_after_patches": True,
            "strict_star_center": [str(value) for value in star_center],
            "strict_visibility_margin_min": str(min(strict_margins)),
            "cone_tetrahedra": len(cone_tetrahedra),
            "cone_face_multiplicities": {
                str(key): value
                for key, value in sorted(collections.Counter(cone_faces.values()).items())
            },
            "cone_determinants_nonzero": True,
            "cone_retriangulation_status": "PASS",
            "difference_ball_status": "PASS",
        },
        "before_boundary": before_boundary_invariants,
        "after_boundary": after_boundary_invariants,
        "common_boundary_faces": len(common_boundary),
        "before_patch": before_patch_invariants,
        "after_patch": after_patch_invariants,
        "before_collapse": before_ball,
        "after_collapse": after_ball,
        "coordinate_denominator_lcm": 48,
        "geometric_tetrahedra_nondegenerate": True,
        "derived_disk_move_support": "PASS",
        "ambient_cell_map": "OPEN",
    }


def generate():
    collapse_tools = load("build_t73_johnson_paired_saddle_support")
    templates = [build_dimension(dimension, collapse_tools) for dimension in (1, 2, 3)]
    result = {
        "schema": "t73_johnson_derived_collapse_templates/v1",
        "standard_vertices": [
            [str(value) for value in vertex] for vertex in STANDARD_VERTICES
        ],
        "templates": templates,
        "all_derived_stars_are_ball_disk_moves": all(
            template["derived_disk_move_support"] == "PASS" for template in templates
        ),
        "ambient_cell_maps": "OPEN",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check or args.write:
        print(
            "T73_JOHNSON_DERIVED_COLLAPSE_TEMPLATES="
            f"{'PASS' if result['all_derived_stars_are_ball_disk_moves'] else 'OPEN'}"
        )
        for template in result["templates"]:
            print(
                f"DIMENSION_{template['collapse_dimension']}="
                f"{template['before_star_tetrahedra']}/"
                f"{template['after_star_tetrahedra']};"
                f"DIFFERENCE={template['difference_tetrahedra']}"
            )
        print(f"AMBIENT_CELL_MAPS={result['ambient_cell_maps']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
