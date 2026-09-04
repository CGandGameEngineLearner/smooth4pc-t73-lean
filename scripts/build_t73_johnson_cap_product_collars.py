#!/usr/bin/env python3
"""Build actual product collars between the two Johnson path cap disks."""

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
SWEEP = ROOT / "geometry" / "t73_johnson_elementary_sweep.json"
SUPPORT = ROOT / "geometry" / "t73_johnson_paired_saddle_support.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_cap_product_collars.json"
INSET = Fraction(1, 1000)


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


def periodic(vertex):
    return tuple(value % 4 for value in vertex)


def subdivide_tetrahedron(tetrahedron):
    return [
        tuple(frozenset(permutation[:size]) for size in range(1, 5))
        for permutation in itertools.permutations(tetrahedron)
    ]


def unwrap_path(tetrahedra, path):
    lifts = []
    for position, tetrahedron_index in enumerate(path):
        raw = [tuple(vertex) for vertex in tetrahedra[tetrahedron_index]["vertices"]]
        if position == 0:
            aligned = raw
        else:
            candidates = []
            for shift in itertools.product(range(-8, 9, 4), repeat=3):
                candidate = [
                    tuple(vertex[axis] + shift[axis] for axis in range(3))
                    for vertex in raw
                ]
                if len(set(candidate) & set(lifts[-1])) == 3:
                    candidates.append(candidate)
            if len(candidates) != 1:
                raise AssertionError("dual path does not have a unique continuous lift")
            aligned = candidates[0]
        lifts.append(aligned)
    return lifts


def average(points):
    return tuple(
        sum(point[axis] for point in points) / len(points) for axis in range(3)
    )


def build_structure(sweep_tools, tetrahedra, adjacency, path, add_ball, remove_ball):
    core_path = [index for index in path if index not in add_ball and index not in remove_ball]
    original = [
        tuple(periodic(vertex) for vertex in tetrahedra[index]["vertices"])
        for index in core_path
    ]
    lifts = unwrap_path(tetrahedra, core_path)
    coordinates = {}
    for identifiers, points in zip(original, lifts):
        for identifier, point in zip(identifiers, points):
            if identifier in coordinates and coordinates[identifier] != point:
                raise AssertionError("path lift gives two coordinates to one vertex")
            coordinates[identifier] = point
    full = [frozenset(tetrahedron) for tetrahedron in original]
    shared = [
        frozenset(set(original[index]) & set(original[index + 1]))
        for index in range(len(original) - 1)
    ]
    add_neighbour = next(
        neighbour for neighbour in adjacency[core_path[0]] if neighbour in add_ball
    )
    remove_neighbour = next(
        neighbour for neighbour in adjacency[core_path[-1]] if neighbour in remove_ball
    )
    caps = [
        frozenset(
            set(original[0])
            & {
                periodic(vertex)
                for vertex in tetrahedra[add_neighbour]["vertices"]
            }
        ),
        frozenset(
            set(original[-1])
            & {
                periodic(vertex)
                for vertex in tetrahedra[remove_neighbour]["vertices"]
            }
        ),
    ]
    core_vertices = set(full) | set(shared) | set(caps)
    core_edges = {
        frozenset((caps[0], full[0])),
        frozenset((full[-1], caps[1])),
    }
    core_edges.update(
        frozenset((full[index], shared[index])) for index in range(len(shared))
    )
    core_edges.update(
        frozenset((shared[index], full[index + 1]))
        for index in range(len(shared))
    )
    subdivided_core = {frozenset((vertex,)) for vertex in core_vertices} | core_edges
    first = [
        simplex
        for tetrahedron in original
        for simplex in subdivide_tetrahedron(tetrahedron)
    ]
    second = [
        simplex
        for tetrahedron in first
        for simplex in subdivide_tetrahedron(tetrahedron)
    ]
    star = [
        tetrahedron
        for tetrahedron in second
        if any(vertex in subdivided_core for vertex in tetrahedron)
    ]
    vertices = sorted({vertex for tetrahedron in star for vertex in tetrahedron}, key=repr)
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    indexed = [
        tuple(vertex_index[vertex] for vertex in tetrahedron) for tetrahedron in star
    ]

    def coordinate(second_vertex):
        return average(
            [
                average([coordinates[original_vertex] for original_vertex in first_vertex])
                for first_vertex in second_vertex
            ]
        )

    face_occurrences = collections.defaultdict(list)
    for tetrahedron_index, tetrahedron in enumerate(indexed):
        for omitted in range(4):
            face_occurrences[
                frozenset(
                    tetrahedron[index] for index in range(4) if index != omitted
                )
            ].append(tetrahedron_index)

    def carrier(vertex_id):
        return frozenset(
            original_vertex
            for first_vertex in vertices[vertex_id]
            for original_vertex in first_vertex
        )

    cap_faces = [
        [
            face
            for face, hits in face_occurrences.items()
            if len(hits) == 1 and all(carrier(vertex) <= cap for vertex in face)
        ]
        for cap in caps
    ]
    path_centers = [average(points) for points in lifts]
    return {
        "vertices": vertices,
        "indexed": indexed,
        "coordinate": coordinate,
        "face_occurrences": face_occurrences,
        "cap_faces": cap_faces,
        "path_centers": path_centers,
    }


def build_movie(pl, sweep_tools, cell_tools, movie, support):
    tetrahedra, adjacency, _ = sweep_tools.build_tetrahedra(
        sweep_tools.load("analyze_t73_johnson_arm_mismatch"), pl, movie["power"]
    )
    add_ball = set(
        next(move["tetrahedra"] for move in movie["grouped_moves"] if move["operation"] == "add")
    )
    remove_ball = set(
        next(
            move["tetrahedra"]
            for move in movie["grouped_moves"]
            if move["operation"] == "remove"
        )
    )
    structure = build_structure(
        sweep_tools, tetrahedra, adjacency, support["dual_path"], add_ball, remove_ball
    )
    selected_orientation = "preserving" if movie["power"] < 0 else "reversing"
    rejected_orientation = "reversing" if movie["power"] < 0 else "preserving"
    isomorphisms = {
        item["orientation"]: item
        for item in support["regular_path_neighbourhood"]["cap_isomorphisms"]
    }
    source_faces = structure["cap_faces"][0]
    target_faces = structure["cap_faces"][1]
    target_face_set = {frozenset(face) for face in target_faces}
    source_direction_target = structure["path_centers"][0]
    target_direction_target = structure["path_centers"][-1]

    def cells_for(orientation, require_positive):
        vertex_map = {
            int(source): int(target)
            for source, target in isomorphisms[orientation]["vertex_map"]
        }
        cells = []
        determinants = []
        for source_face in source_faces:
            order = sorted(source_face)
            target_order = [vertex_map[vertex] for vertex in order]
            if frozenset(target_order) not in target_face_set:
                raise AssertionError("fan isomorphism misses a target cap triangle")
            bottom = [structure["coordinate"](structure["vertices"][vertex]) for vertex in order]
            image_bottom = [
                structure["coordinate"](structure["vertices"][vertex])
                for vertex in target_order
            ]
            top = [
                tuple(
                    (1 - INSET) * bottom[index][axis]
                    + INSET * source_direction_target[axis]
                    for axis in range(3)
                )
                for index in range(3)
            ]
            image_top = [
                tuple(
                    (1 - INSET) * image_bottom[index][axis]
                    + INSET * target_direction_target[axis]
                    for axis in range(3)
                )
                for index in range(3)
            ]
            source_tets = (
                (bottom[0], bottom[1], bottom[2], top[2]),
                (bottom[0], bottom[1], top[1], top[2]),
                (bottom[0], top[0], top[1], top[2]),
            )
            image_tets = (
                (image_bottom[0], image_bottom[1], image_bottom[2], image_top[2]),
                (image_bottom[0], image_bottom[1], image_top[1], image_top[2]),
                (image_bottom[0], image_top[0], image_top[1], image_top[2]),
            )
            for index in range(3):
                determinant = pl.affine_from_tets(
                    [list(vertex) for vertex in source_tets[index]],
                    [list(vertex) for vertex in image_tets[index]],
                )[2]
                determinants.append(determinant)
                if require_positive:
                    cells.append(
                        cell_tools.oriented_cell(
                            pl, source_tets[index], image_tets[index]
                        )
                    )
        return cells, determinants

    cells, determinants = cells_for(selected_orientation, True)
    _, mutant_determinants = cells_for(rejected_orientation, False)
    if min(determinants) <= 0 or max(mutant_determinants) >= 0:
        raise AssertionError("cap collar orientation gate failed")
    source_multiplicities, _ = load("build_t73_johnson_octahedral_halfturn").face_multiplicities(
        pl, cells, "source"
    )
    image_multiplicities, _ = load("build_t73_johnson_octahedral_halfturn").face_multiplicities(
        pl, cells, "image"
    )
    if set(source_multiplicities) != {1, 2} or set(image_multiplicities) != {1, 2}:
        raise AssertionError("cap product collar is not face-to-face")
    return {
        "power": movie["power"],
        "side": movie["side"],
        "inset": str(INSET),
        "selected_cap_orientation": selected_orientation,
        "rejected_cap_orientation": rejected_orientation,
        "cap_triangle_count": len(source_faces),
        "cell_count": len(cells),
        "jacobian_det_min": str(min(determinants)),
        "jacobian_det_max": str(max(determinants)),
        "rejected_jacobian_det_min": str(min(mutant_determinants)),
        "rejected_jacobian_det_max": str(max(mutant_determinants)),
        "source_face_multiplicities": {
            str(key): value for key, value in sorted(source_multiplicities.items())
        },
        "image_face_multiplicities": {
            str(key): value for key, value in sorted(image_multiplicities.items())
        },
        "explicit_cellwise_inverse": True,
        "cells": cells,
        "cap_product_collar": "PASS",
        "mutation_cap_orientation": "FAIL",
    }


def generate():
    pl = load("t73_johnson_pl")
    sweep_tools = load("build_t73_johnson_elementary_sweep")
    cell_tools = load("build_t73_johnson_ball_shrinks")
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
    support = json.loads(SUPPORT.read_text(encoding="utf-8"))
    movies = [
        build_movie(pl, sweep_tools, cell_tools, movie, support_movie)
        for movie, support_movie in zip(sweep["movies"], support["movies"])
    ]
    result = {
        "schema": "t73_johnson_cap_product_collars/v1",
        "sweep_sha256": sweep["sha256"],
        "support_sha256": support["sha256"],
        "movies": movies,
        "all_cap_product_collars": "PASS",
        "all_orientation_mutations": "FAIL",
        "cap_collapse_chart_assembly": "OPEN",
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
        print(f"T73_JOHNSON_CAP_PRODUCT_COLLARS={result['all_cap_product_collars']}")
        for movie in result["movies"]:
            print(
                f"POWER_{movie['power']}_{movie['side']}="
                f"{movie['cell_count']};JACOBIAN={movie['jacobian_det_min']}.."
                f"{movie['jacobian_det_max']};ORIENTATION={movie['selected_cap_orientation']}"
            )
        print(f"CAP_COLLAPSE_ASSEMBLY={result['cap_collapse_chart_assembly']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
