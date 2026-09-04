#!/usr/bin/env python3
"""Extend the paired-saddle boundary curve movie through an outer PL collar."""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import itertools
import json
import math
import random
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SWEEP = ROOT / "geometry" / "t73_johnson_elementary_sweep.json"
SUPPORT = ROOT / "geometry" / "t73_johnson_paired_saddle_support.json"
DERIVED_CELLS = ROOT / "geometry" / "t73_johnson_derived_collapse_cells.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_outer_curve_collar.json"
OUTSET = Fraction(1, 1000)


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
        raise AssertionError("outer curve carrier is empty")
    return best


def face_edges(sweep_tools, face):
    return {
        tuple(
            sorted(
                (
                    sweep_tools.periodic_vertex(face[first]),
                    sweep_tools.periodic_vertex(face[second]),
                )
            )
        )
        for first, second in ((0, 1), (0, 2), (1, 2))
    }


def boundary_edges(sweep_tools, faces):
    counts = collections.Counter(
        edge for face in faces for edge in face_edges(sweep_tools, face)
    )
    return {edge for edge, count in counts.items() if count == 1}


def is_cycle(edges):
    adjacency = collections.defaultdict(set)
    for first, second in edges:
        adjacency[first].add(second)
        adjacency[second].add(first)
    if not adjacency or any(len(neighbours) != 2 for neighbours in adjacency.values()):
        return False
    start = next(iter(adjacency))
    reached = {start}
    stack = [start]
    while stack:
        current = stack.pop()
        for neighbour in adjacency[current]:
            if neighbour not in reached:
                reached.add(neighbour)
                stack.append(neighbour)
    return len(reached) == len(adjacency)


def complement_regions(sweep_tools, sphere, cuts):
    edge_faces = collections.defaultdict(list)
    for face_index, face in enumerate(sphere):
        for edge in face_edges(sweep_tools, face):
            edge_faces[edge].append(face_index)
    adjacency = [set() for _ in sphere]
    for edge, hits in edge_faces.items():
        if edge in cuts:
            continue
        if len(hits) != 2:
            raise AssertionError("support sphere edge does not have two faces")
        first, second = hits
        adjacency[first].add(second)
        adjacency[second].add(first)
    seen = set()
    regions = []
    for start in range(len(sphere)):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        component = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbour in adjacency[current]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        regions.append([sphere[index] for index in component])
    return regions


def curve_sweep(sweep_tools, region, source, target, side):
    for trial in range(5000):
        rng = random.Random(73000 + trial + (100000 if side == "target-first" else 0))
        current = set(source)
        remaining = set(range(len(region)))
        sequence = []
        while remaining:
            candidates = []
            for index in remaining:
                image = current ^ face_edges(sweep_tools, region[index])
                if is_cycle(image):
                    candidates.append(
                        (len(image ^ target), repr(region[index]), index, image)
                    )
            if not candidates:
                break
            minimum = min(item[0] for item in candidates)
            choices = [
                item for item in candidates if item[0] <= minimum + trial % 3
            ]
            _, _, index, image = rng.choice(choices)
            before_local = current & face_edges(sweep_tools, region[index])
            after_local = image & face_edges(sweep_tools, region[index])
            if {len(before_local), len(after_local)} != {1, 2}:
                raise AssertionError("curve triangle is not a one-two move")
            sequence.append(
                {
                    "region_triangle": index,
                    "before_local_edges": sorted(before_local),
                    "after_local_edges": sorted(after_local),
                    "direction": "one_to_two" if len(before_local) == 1 else "two_to_one",
                }
            )
            current = image
            remaining.remove(index)
        if not remaining and current == target:
            return trial, sequence
    raise AssertionError("no simple-curve sweep crosses the selected region")


def positive_chart(pl, standard_vertices, triangle, free_edge, outer_point):
    triangle_vertices = list(triangle)
    free_vertices = list(free_edge)
    apex = next(vertex for vertex in triangle_vertices if vertex not in free_edge)
    candidates = []
    for order in itertools.permutations(free_vertices):
        image = [list(apex), list(order[0]), list(order[1]), list(outer_point)]
        linear, translation, determinant = pl.affine_from_tets(
            standard_vertices, image
        )
        if determinant <= 0:
            continue
        inverse_linear, inverse_translation, inverse_determinant = pl.affine_from_tets(
            image, standard_vertices
        )
        candidates.append(
            (
                tuple(order),
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
        raise AssertionError("outer curve triangle has no positive carrier chart")
    (
        order,
        image,
        linear,
        translation,
        determinant,
        inverse_linear,
        inverse_translation,
        inverse_determinant,
    ) = min(candidates, key=lambda item: item[0])
    if inverse_determinant <= 0:
        raise AssertionError("outer curve carrier inverse is not positive")
    return {
        "image_vertices": [[str(value) for value in vertex] for vertex in image],
        "linear": [[str(value) for value in row] for row in linear],
        "translation": [str(value) for value in translation],
        "determinant": str(determinant),
        "inverse_linear": [[str(value) for value in row] for row in inverse_linear],
        "inverse_translation": [str(value) for value in inverse_translation],
        "inverse_determinant": str(inverse_determinant),
    }


def build_movie(pl, sweep_tools, derived, template, movie, support):
    tetrahedra, adjacency, face_occurrences = sweep_tools.build_tetrahedra(
        sweep_tools.load("analyze_t73_johnson_arm_mismatch"), pl, movie["power"]
    )
    current = [tetrahedron["source_owner"] == 0 for tetrahedron in tetrahedra]
    goal = [tetrahedron["target_owner"] == 0 for tetrahedron in tetrahedra]
    for index in movie["single_move_tetrahedra"]:
        current[index] = goal[index]
    support_indices = set(support["support_tetrahedra"])
    sphere = []
    source_patch = []
    target_patch = []
    sphere_incident = {}
    for face, hits in face_occurrences.items():
        (first, _), (second, _) = hits
        first_inside = first in support_indices
        second_inside = second in support_indices
        if first_inside != second_inside:
            sphere.append(face)
            sphere_incident[face] = first if first_inside else second
        elif first_inside:
            if current[first] != current[second]:
                source_patch.append(face)
            if goal[first] != goal[second]:
                target_patch.append(face)
    source_curve = boundary_edges(sweep_tools, source_patch)
    target_curve = boundary_edges(sweep_tools, target_patch)
    symmetric_difference = source_curve ^ target_curve
    regions = complement_regions(
        sweep_tools, sphere, source_curve | target_curve
    )
    candidates = [
        region
        for region in regions
        if boundary_edges(sweep_tools, region) == symmetric_difference
    ]
    if len(candidates) != 1:
        raise AssertionError("outer curve movie does not have a unique transition region")
    region = candidates[0]
    expected_topology = "disk" if movie["power"] < 0 else "annulus"
    if sweep_tools.patch_invariants(region)["topology"] != expected_topology:
        raise AssertionError("outer curve transition region has the wrong topology")
    trial, sequence = curve_sweep(
        sweep_tools, region, source_curve, target_curve, movie["side"]
    )
    standard_vertices = [list(vertex) for vertex in derived.STANDARD_VERTICES]
    placements = []
    determinant_min = None
    determinant_max = None
    clearance_min = None
    for position, move in enumerate(sequence):
        face = region[move["region_triangle"]]
        inside_tetrahedron = sphere_incident[face]
        inside_center = [
            sum(tetrahedra[inside_tetrahedron]["vertices"][index][axis] for index in range(4))
            / 4
            for axis in range(3)
        ]
        face_center = [
            sum(face[index][axis] for index in range(3)) / 3 for axis in range(3)
        ]
        outer_point = [
            face_center[axis] + OUTSET * (face_center[axis] - inside_center[axis])
            for axis in range(3)
        ]
        singleton = (
            move["before_local_edges"][0]
            if move["direction"] == "one_to_two"
            else move["after_local_edges"][0]
        )
        free_periodic = {tuple(singleton[0]), tuple(singleton[1])}
        free_edge = {
            vertex
            for vertex in face
            if sweep_tools.periodic_vertex(vertex) in free_periodic
        }
        if len(free_edge) != 2:
            raise AssertionError("free curve edge does not lift into its triangle")
        chart = positive_chart(
            pl, standard_vertices, face, free_edge, outer_point
        )
        determinant = Fraction(chart["determinant"])
        determinant_min = determinant if determinant_min is None else min(determinant_min, determinant)
        determinant_max = determinant if determinant_max is None else max(determinant_max, determinant)
        carrier_vertices = [list(vertex) for vertex in face] + [outer_point]
        carrier_center = [
            sum(vertex[axis] for vertex in carrier_vertices) / 4
            for axis in range(3)
        ]
        expanded_carrier = [
            [
                carrier_center[axis]
                + Fraction(501, 500) * (vertex[axis] - carrier_center[axis])
                for axis in range(3)
            ]
            for vertex in carrier_vertices
        ]
        clearance = periodic_bbox_clearance(expanded_carrier)
        if clearance <= Fraction(1, 196104):
            raise AssertionError("outer curve collar meets the protected ball")
        clearance_min = clearance if clearance_min is None else min(clearance_min, clearance)
        placements.append(
            {
                "position": position,
                **move,
                "before_local_edges": [
                    [[str(value) for value in vertex] for vertex in edge]
                    for edge in move["before_local_edges"]
                ],
                "after_local_edges": [
                    [[str(value) for value in vertex] for vertex in edge]
                    for edge in move["after_local_edges"]
                ],
                "actual_face": [[str(value) for value in vertex] for vertex in face],
                "outer_point": [str(value) for value in outer_point],
                "chart": chart,
                "protected_ball_bbox_clearance": str(clearance),
                "standard_map_direction": (
                    "inverse" if move["direction"] == "one_to_two" else "forward"
                ),
                "standard_ambient_cell_count": template["ambient_cell_count"],
                "conjugated_jacobian_det_min": template["jacobian_det_min"],
                "conjugated_jacobian_det_max": template["jacobian_det_max"],
            }
        )
    return {
        "power": movie["power"],
        "side": movie["side"],
        "transition_region_topology": expected_topology,
        "transition_region_triangles": len(region),
        "search_trial": trial,
        "curve_move_count": len(sequence),
        "placements": placements,
        "expanded_ambient_cell_count": len(sequence) * template["ambient_cell_count"],
        "chart_determinant_min": str(determinant_min),
        "chart_determinant_max": str(determinant_max),
        "protected_ball_bbox_clearance_min": str(clearance_min),
        "conjugated_jacobian_det_min": template["jacobian_det_min"],
        "conjugated_jacobian_det_max": template["jacobian_det_max"],
        "all_intermediate_curves_simple": True,
        "final_curve_equals_target": True,
        "all_actual_charts_positive": True,
        "all_actual_chart_inverses_explicit": True,
        "all_carriers_miss_protected_ball": True,
        "outer_curve_collar": "PASS",
    }


def generate():
    pl = load("t73_johnson_pl")
    sweep_tools = load("build_t73_johnson_elementary_sweep")
    derived = load("build_t73_johnson_derived_collapse_templates")
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
    support = json.loads(SUPPORT.read_text(encoding="utf-8"))
    cells = json.loads(DERIVED_CELLS.read_text(encoding="utf-8"))
    dimension_two = next(
        dimension for dimension in cells["dimensions"] if dimension["collapse_dimension"] == 2
    )
    templates = {side["side"]: side for side in dimension_two["sides"]}
    movies = [
        build_movie(
            pl,
            sweep_tools,
            derived,
            templates[movie["side"]],
            movie,
            support_movie,
        )
        for movie, support_movie in zip(sweep["movies"], support["movies"])
    ]
    result = {
        "schema": "t73_johnson_outer_curve_collar/v1",
        "sweep_sha256": sweep["sha256"],
        "support_sha256": support["sha256"],
        "derived_cells_sha256": cells["sha256"],
        "movies": movies,
        "curve_move_count": sum(movie["curve_move_count"] for movie in movies),
        "expanded_ambient_cell_count": sum(
            movie["expanded_ambient_cell_count"] for movie in movies
        ),
        "all_outer_curve_collars": "PASS",
        "outer_paired_support_boundary_extension": "PASS",
        "final_restore_assembly": "OPEN",
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
        print(f"T73_JOHNSON_OUTER_CURVE_COLLAR={result['all_outer_curve_collars']}")
        print(f"CURVE_MOVES={result['curve_move_count']}")
        print(f"EXPANDED_CELLS={result['expanded_ambient_cell_count']}")
        print(
            "OUTER_BOUNDARY_EXTENSION="
            f"{result['outer_paired_support_boundary_extension']}"
        )
        print(f"FINAL_RESTORE_ASSEMBLY={result['final_restore_assembly']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
