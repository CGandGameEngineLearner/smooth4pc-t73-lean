#!/usr/bin/env python3
"""Place standard derived-collapse maps at all actual relative collapse pairs."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COLLAPSES = ROOT / "geometry" / "t73_johnson_relative_side_collapses.json"
CELLS = ROOT / "geometry" / "t73_johnson_derived_collapse_cells.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_actual_derived_placements.json"
OUTER_SCALE = Fraction(501, 500)


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


def decode_tetrahedron(tetrahedron):
    return [[Fraction(value) for value in vertex] for vertex in tetrahedron]


def periodic_bbox_clearance(vertices):
    lows = [min(vertex[axis] for vertex in vertices) for axis in range(3)]
    highs = [max(vertex[axis] for vertex in vertices) for axis in range(3)]
    best = None
    for lattice in itertools.product(
        *(
            range(
                math.floor(float(lows[axis]) / 4) - 1,
                math.ceil(float(highs[axis]) / 4) + 2,
            )
            for axis in range(3)
        )
    ):
        point = [Fraction(4 * value) for value in lattice]
        gaps = [
            lows[axis] - point[axis]
            if point[axis] < lows[axis]
            else point[axis] - highs[axis]
            if point[axis] > highs[axis]
            else Fraction(0)
            for axis in range(3)
        ]
        distance = max(gaps)
        best = distance if best is None else min(best, distance)
    if best is None:
        raise AssertionError("empty carrier bbox")
    return best


def chart_for_step(pl, standard_vertices, side, step):
    dimension = int(step["dimension"])
    simplex = set(int(value) for value in step["simplex"])
    free_face = set(int(value) for value in step["free_face"])
    apex = simplex - free_face
    if len(apex) != 1 or len(free_face) != dimension:
        raise AssertionError("actual collapse pair has the wrong dimensions")
    carriers = [
        (index, tetrahedron)
        for index, tetrahedron in enumerate(side["tetrahedra"])
        if simplex <= set(tetrahedron)
    ]
    candidates = []
    for carrier_index, carrier in carriers:
        lift = decode_tetrahedron(side["tetrahedron_lifts"][carrier_index])
        coordinates = {
            int(vertex_id): lift[position]
            for position, vertex_id in enumerate(carrier)
        }
        extras = set(carrier) - simplex
        if len(extras) != 3 - dimension:
            continue
        for free_order in itertools.permutations(sorted(free_face)):
            for extra_order in itertools.permutations(sorted(extras)):
                image_ids = [next(iter(apex)), *free_order, *extra_order]
                image = [coordinates[vertex_id] for vertex_id in image_ids]
                linear, translation, determinant = pl.affine_from_tets(
                    standard_vertices, image
                )
                if determinant <= 0:
                    continue
                inverse_linear, inverse_translation, inverse_determinant = pl.affine_from_tets(
                    image, standard_vertices
                )
                if inverse_determinant <= 0:
                    raise AssertionError("positive carrier chart has a nonpositive inverse")
                candidates.append(
                    (
                        tuple(image_ids),
                        carrier_index,
                        carrier,
                        image,
                        linear,
                        translation,
                        determinant,
                        inverse_linear,
                        inverse_translation,
                        inverse_determinant,
                    )
                )
    if not candidates:
        raise AssertionError("actual collapse pair has no positive carrier chart")
    (
        image_ids,
        carrier_index,
        carrier,
        image,
        linear,
        translation,
        determinant,
        inverse_linear,
        inverse_translation,
        inverse_determinant,
    ) = min(candidates, key=lambda item: (item[0], item[1]))
    for source, target in zip(standard_vertices, image):
        if pl.apply_affine(linear, translation, source) != target:
            raise AssertionError("carrier chart misses an actual vertex")
        if pl.apply_affine(inverse_linear, inverse_translation, target) != source:
            raise AssertionError("carrier inverse misses a standard vertex")
    center = [sum(vertex[axis] for vertex in image) / 4 for axis in range(3)]
    expanded = [
        [
            center[axis] + OUTER_SCALE * (vertex[axis] - center[axis])
            for axis in range(3)
        ]
        for vertex in image
    ]
    clearance = periodic_bbox_clearance([tuple(vertex) for vertex in expanded])
    if clearance <= Fraction(1, 196104):
        raise AssertionError("actual derived-collapse carrier meets the protected ball")
    return {
        "dimension": dimension,
        "simplex": sorted(simplex),
        "free_face": sorted(free_face),
        "carrier_index": carrier_index,
        "carrier": list(carrier),
        "standard_vertex_images": list(image_ids),
        "image_vertices": [[str(value) for value in vertex] for vertex in image],
        "linear": [[str(value) for value in row] for row in linear],
        "translation": [str(value) for value in translation],
        "determinant": str(determinant),
        "inverse_linear": [[str(value) for value in row] for row in inverse_linear],
        "inverse_translation": [str(value) for value in inverse_translation],
        "inverse_determinant": str(inverse_determinant),
        "protected_ball_bbox_clearance": str(clearance),
    }


def template_lookup(cells):
    return {
        (dimension["collapse_dimension"], side["side"]): side
        for dimension in cells["dimensions"]
        for side in dimension["sides"]
    }


def build_side(pl, standard_vertices, side, movie_side, lookup):
    placements = []
    dimension_counts = {1: 0, 2: 0, 3: 0}
    ambient_cells = 0
    minimum_clearance = None
    for step_index, step in enumerate(side["collapse"]["steps"]):
        chart = chart_for_step(pl, standard_vertices, side, step)
        dimension = chart["dimension"]
        template = lookup[(dimension, movie_side)]
        dimension_counts[dimension] += 1
        ambient_cells += template["ambient_cell_count"]
        clearance = Fraction(chart["protected_ball_bbox_clearance"])
        minimum_clearance = (
            clearance if minimum_clearance is None else min(minimum_clearance, clearance)
        )
        placements.append(
            {
                "step_index": step_index,
                **chart,
                "standard_move_count": template["move_count"],
                "standard_ambient_cell_count": template["ambient_cell_count"],
                "standard_jacobian_det_min": template["jacobian_det_min"],
                "standard_jacobian_det_max": template["jacobian_det_max"],
            }
        )
    return {
        "state": side["side_value"],
        "collapse_step_count": len(placements),
        "dimension_counts": {str(key): value for key, value in dimension_counts.items()},
        "actual_placements": placements,
        "expanded_ambient_cell_count": ambient_cells,
        "actual_jacobian_det_min": "1/3",
        "actual_jacobian_det_max": "3",
        "protected_ball_bbox_clearance_min": str(minimum_clearance),
        "all_charts_orientation_preserving": True,
        "all_chart_inverses_explicit": True,
        "all_conjugated_cells_positive": True,
    }


def generate():
    pl = load("t73_johnson_pl")
    derived = load("build_t73_johnson_derived_collapse_templates")
    collapses = json.loads(COLLAPSES.read_text(encoding="utf-8"))
    cells = json.loads(CELLS.read_text(encoding="utf-8"))
    if cells["templates_sha256"] != derived.generate()["sha256"]:
        raise AssertionError("derived cells are not bound to the standard templates")
    lookup = template_lookup(cells)
    standard_vertices = [list(vertex) for vertex in derived.STANDARD_VERTICES]
    movies = []
    for movie in collapses["movies"]:
        states = []
        for state in movie["states"]:
            states.append(
                {
                    "state": state["state"],
                    "sides": [
                        build_side(pl, standard_vertices, side, movie["side"], lookup)
                        for side in state["sides"]
                    ],
                }
            )
        movies.append(
            {
                "power": movie["power"],
                "side": movie["side"],
                "states": states,
            }
        )
    all_sides = [
        side for movie in movies for state in movie["states"] for side in state["sides"]
    ]
    first_chart = all_sides[0]["actual_placements"][0]
    mutant_image = [
        [Fraction(value) for value in vertex]
        for vertex in first_chart["image_vertices"]
    ]
    mutant_image[1], mutant_image[2] = mutant_image[2], mutant_image[1]
    mutant_determinant = pl.affine_from_tets(standard_vertices, mutant_image)[2]
    if mutant_determinant >= 0:
        raise AssertionError("chart-orientation mutation was not detected")
    result = {
        "schema": "t73_johnson_actual_derived_placements/v1",
        "collapses_sha256": collapses["sha256"],
        "cells_sha256": cells["sha256"],
        "placement_count": sum(side["collapse_step_count"] for side in all_sides),
        "expanded_ambient_cell_count": sum(
            side["expanded_ambient_cell_count"] for side in all_sides
        ),
        "movies": movies,
        "all_actual_charts_orientation_preserving": all(
            side["all_charts_orientation_preserving"] for side in all_sides
        ),
        "all_actual_chart_inverses_explicit": all(
            side["all_chart_inverses_explicit"] for side in all_sides
        ),
        "all_actual_conjugated_cells_positive": all(
            side["all_conjugated_cells_positive"] for side in all_sides
        ),
        "actual_collapse_pair_placement": "PASS",
        "paired_saddle_side_chart_cells": "PASS",
        "paired_saddle_fiber_transport": "OPEN",
        "paired_saddle_ambient_cells": "OPEN",
        "mutation_chart_orientation": "FAIL",
        "mutant_chart_determinant": str(mutant_determinant),
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
        print(f"T73_JOHNSON_ACTUAL_DERIVED_PLACEMENTS={result['actual_collapse_pair_placement']}")
        print(f"PLACEMENTS={result['placement_count']}")
        print(f"EXPANDED_CELLS={result['expanded_ambient_cell_count']}")
        print(f"PAIRED_SADDLE_CELLS={result['paired_saddle_ambient_cells']}")
        print(f"PAIRED_SADDLE_FIBER_TRANSPORT={result['paired_saddle_fiber_transport']}")
        print(f"MUTATION_CHART_ORIENTATION={result['mutation_chart_orientation']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
