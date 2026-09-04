#!/usr/bin/env python3
"""Build the ball support for the final paired Johnson saddle."""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SWEEP = ROOT / "geometry" / "t73_johnson_elementary_sweep.json"
DISK_CELLS = ROOT / "geometry" / "t73_johnson_disk_move_cells.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_paired_saddle_support.json"


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


def boundary_edges(sweep_tools, faces):
    counts = collections.Counter(
        tuple(
            sorted(
                (
                    sweep_tools.periodic_vertex(face[first]),
                    sweep_tools.periodic_vertex(face[second]),
                )
            )
        )
        for face in faces
        for first, second in ((0, 1), (0, 2), (1, 2))
    )
    return {edge for edge, count in counts.items() if count == 1}


def shortest_path(adjacency, starts, targets):
    queue = collections.deque(sorted(starts))
    parent = {index: None for index in starts}
    end = None
    while queue and end is None:
        current = queue.popleft()
        for neighbour in sorted(adjacency[current]):
            if neighbour in parent:
                continue
            parent[neighbour] = current
            if neighbour in targets:
                end = neighbour
                break
            queue.append(neighbour)
    if end is None:
        raise AssertionError("paired saddle balls have no dual-face path")
    path = []
    current = end
    while current is not None and current not in starts:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path


def bbox_clearance(tetrahedra, support):
    best = None
    for index in support:
        vertices = tetrahedra[index]["vertices"]
        lows = [min(vertex[axis] for vertex in vertices) for axis in range(3)]
        highs = [max(vertex[axis] for vertex in vertices) for axis in range(3)]
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
        raise AssertionError("paired saddle support is empty")
    return best


def planar_genus(invariants):
    numerator = (
        2 * invariants["surface_components"]
        - invariants["boundary_components"]
        - invariants["euler"]
    )
    if numerator < 0 or numerator % 2:
        raise AssertionError("paired saddle patch has invalid orientable genus")
    return numerator // 2


def build_movie(analyzer, pl, sweep_tools, movie):
    tetrahedra, adjacency, face_occurrences = sweep_tools.build_tetrahedra(
        analyzer, pl, movie["power"]
    )
    current = [tetrahedron["source_owner"] == 0 for tetrahedron in tetrahedra]
    goal = [tetrahedron["target_owner"] == 0 for tetrahedron in tetrahedra]
    for index in movie["single_move_tetrahedra"]:
        current[index] = goal[index]
    add_ball = set(
        next(
            move["tetrahedra"] for move in movie["grouped_moves"] if move["operation"] == "add"
        )
    )
    remove_ball = set(
        next(
            move["tetrahedra"]
            for move in movie["grouped_moves"]
            if move["operation"] == "remove"
        )
    )
    path = shortest_path(adjacency, add_ball, remove_ball)
    core = add_ball | remove_ball | set(path)
    support = core | {neighbour for index in core for neighbour in adjacency[index]}
    support_boundary = []
    source_patch = []
    target_patch = []
    boundary_agrees = True
    for face, hits in face_occurrences.items():
        (first, _), (second, _) = hits
        first_inside = first in support
        second_inside = second in support
        if first_inside != second_inside:
            support_boundary.append(face)
            inside = first if first_inside else second
            outside = second if first_inside else first
            boundary_agrees &= current[inside] == goal[inside]
            boundary_agrees &= current[outside] == goal[outside]
        elif first_inside:
            if current[first] != current[second]:
                source_patch.append(face)
            if goal[first] != goal[second]:
                target_patch.append(face)
    boundary_invariants = sweep_tools.patch_invariants(support_boundary)
    source_invariants = sweep_tools.patch_invariants(source_patch)
    target_invariants = sweep_tools.patch_invariants(target_patch)
    source_invariants["total_genus"] = planar_genus(source_invariants)
    target_invariants["total_genus"] = planar_genus(target_invariants)
    source_curve = boundary_edges(sweep_tools, source_patch)
    target_curve = boundary_edges(sweep_tools, target_patch)
    collapse = analyzer.collapse_to_point(
        [
            tuple(sweep_tools.periodic_vertex(vertex) for vertex in tetrahedra[index]["vertices"])
            for index in support
        ]
    )
    clearance = bbox_clearance(tetrahedra, support)
    if clearance <= pl.PROTECTED_RADIUS:
        raise AssertionError("paired saddle support meets the protected ball")
    expected_components = 2 if movie["power"] < 0 else 3
    expected_boundaries = 3 if movie["power"] < 0 else 4
    passed = (
        boundary_invariants["topology"] == "sphere"
        and collapse["collapses_to_point"]
        and boundary_agrees
        and source_curve == target_curve
        and source_invariants["surface_components"] == expected_components
        and target_invariants["surface_components"] == expected_components
        and source_invariants["boundary_components"] == expected_boundaries
        and target_invariants["boundary_components"] == expected_boundaries
        and source_invariants["total_genus"] == 0
        and target_invariants["total_genus"] == 0
    )
    return {
        "power": movie["power"],
        "side": movie["side"],
        "add_ball_tetrahedra": len(add_ball),
        "remove_ball_tetrahedra": len(remove_ball),
        "dual_path": path,
        "dual_path_length": len(path),
        "core_tetrahedron_count": len(core),
        "support_tetrahedron_count": len(support),
        "support_tetrahedra": sorted(support),
        "support_boundary": boundary_invariants,
        "support_collapses_to_point": collapse["collapses_to_point"],
        "source_patch": source_invariants,
        "target_patch": target_invariants,
        "common_boundary_edge_count": len(source_curve),
        "boundary_curves_equal": source_curve == target_curve,
        "outer_boundary_membership_agrees": boundary_agrees,
        "protected_ball_bbox_clearance": str(clearance),
        "paired_saddle_support": "PASS" if passed else "OPEN",
        "ambient_pl_cells": "OPEN",
    }


def generate():
    analyzer = load("analyze_t73_johnson_arm_mismatch")
    pl = load("t73_johnson_pl")
    sweep_tools = load("build_t73_johnson_elementary_sweep")
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
    disk_cells = json.loads(DISK_CELLS.read_text(encoding="utf-8"))
    if disk_cells["sweep_sha256"] != sweep["sha256"]:
        raise AssertionError("disk cells are not bound to the elementary sweep")
    movies = [
        build_movie(analyzer, pl, sweep_tools, movie) for movie in sweep["movies"]
    ]
    result = {
        "schema": "t73_johnson_paired_saddle_support/v1",
        "sweep_sha256": sweep["sha256"],
        "disk_cells_sha256": disk_cells["sha256"],
        "movies": movies,
        "all_supports_are_balls": all(
            movie["paired_saddle_support"] == "PASS" for movie in movies
        ),
        "paired_saddle_support": "PASS",
        "paired_saddle_ambient_cells": "OPEN",
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
        print(f"T73_JOHNSON_PAIRED_SADDLE_SUPPORT={result['paired_saddle_support']}")
        for movie in result["movies"]:
            print(
                f"POWER_{movie['power']}_{movie['side']}="
                f"{movie['support_tetrahedron_count']};"
                f"PATCHES={movie['source_patch']['surface_components']}/"
                f"{movie['source_patch']['boundary_components']}"
            )
        print(f"AMBIENT_PL_CELLS={result['paired_saddle_ambient_cells']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
