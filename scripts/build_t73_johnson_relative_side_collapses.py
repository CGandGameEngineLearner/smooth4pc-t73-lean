#!/usr/bin/env python3
"""Collapse every paired-saddle side ball relative to its cutting disk."""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SWEEP = ROOT / "geometry" / "t73_johnson_elementary_sweep.json"
SUPPORT = ROOT / "geometry" / "t73_johnson_paired_saddle_support.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_relative_side_collapses.json"


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


def downward(tetrahedra):
    simplices = [set() for _ in range(4)]
    for tetrahedron in tetrahedra:
        for size in range(1, 5):
            simplices[size - 1].update(
                frozenset(simplex)
                for simplex in itertools.combinations(tetrahedron, size)
            )
    return simplices


def protected_disk(faces):
    protected = [set() for _ in range(4)]
    for face in faces:
        for size in range(1, 4):
            protected[size - 1].update(
                frozenset(simplex) for simplex in itertools.combinations(face, size)
            )
    return protected


def relative_collapse(tetrahedra, disk_faces):
    simplices = downward(tetrahedra)
    protected = protected_disk(disk_faces)
    steps = []
    histogram = collections.Counter()
    for dimension in (3, 2, 1):
        while True:
            cofaces = collections.defaultdict(set)
            for simplex in simplices[dimension]:
                for face in itertools.combinations(simplex, dimension):
                    cofaces[frozenset(face)].add(simplex)
            candidates = []
            for face in simplices[dimension - 1] - protected[dimension - 1]:
                hosts = cofaces[face] & simplices[dimension]
                if len(hosts) != 1:
                    continue
                simplex = next(iter(hosts))
                if simplex in protected[dimension]:
                    continue
                candidates.append(
                    (tuple(sorted(simplex)), tuple(sorted(face)), simplex, face)
                )
            if not candidates:
                break
            simplex_key, face_key, simplex, face = min(candidates)
            simplices[dimension].remove(simplex)
            simplices[dimension - 1].remove(face)
            histogram[dimension] += 1
            steps.append(
                {
                    "dimension": dimension,
                    "simplex": list(simplex_key),
                    "free_face": list(face_key),
                }
            )
    equality = [simplices[dimension] == protected[dimension] for dimension in range(4)]
    if equality != [True, True, True, True]:
        raise AssertionError("side ball does not collapse exactly to its cutting disk")
    return {
        "steps": steps,
        "step_count": len(steps),
        "dimension_histogram": {
            str(key): value for key, value in sorted(histogram.items())
        },
        "remaining_simplex_counts": [len(simplices[dimension]) for dimension in range(4)],
        "protected_simplex_counts": [len(protected[dimension]) for dimension in range(4)],
        "remaining_equals_protected_disk_by_dimension": equality,
        "relative_collapse_status": "PASS",
    }


def face_components(indices, adjacency):
    available = set(indices)
    components = []
    while available:
        start = min(available)
        available.remove(start)
        stack = [start]
        component = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbour in adjacency[current]:
                if neighbour in available:
                    available.remove(neighbour)
                    stack.append(neighbour)
        components.append(sorted(component))
    return components


def build_movie(analyzer, pl, sweep_tools, movie, support):
    tetrahedra, adjacency, face_occurrences = sweep_tools.build_tetrahedra(
        analyzer, pl, movie["power"]
    )
    source = [tetrahedron["source_owner"] == 0 for tetrahedron in tetrahedra]
    for index in movie["single_move_tetrahedra"]:
        source[index] = tetrahedra[index]["target_owner"] == 0
    target = [tetrahedron["target_owner"] == 0 for tetrahedron in tetrahedra]
    support_indices = set(support["support_tetrahedra"])
    states = []
    for state_name, state in (("source", source), ("target", target)):
        disk_faces = [
            face
            for face, hits in face_occurrences.items()
            if all(index in support_indices for index, _ in hits)
            and state[hits[0][0]] != state[hits[1][0]]
        ]
        side_records = []
        for side_value in (False, True):
            side_indices = [
                index for index in support_indices if state[index] == side_value
            ]
            components = face_components(side_indices, adjacency)
            if len(components) != 1:
                raise AssertionError("cutting disk does not split the support into two side balls")
            component = components[0]
            vertices = sorted(
                {
                    sweep_tools.periodic_vertex(vertex)
                    for index in component
                    for vertex in tetrahedra[index]["vertices"]
                },
                key=repr,
            )
            vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
            indexed_tetrahedra = [
                tuple(
                    vertex_index[sweep_tools.periodic_vertex(vertex)]
                    for vertex in tetrahedra[index]["vertices"]
                )
                for index in component
            ]
            indexed_disk = [
                tuple(
                    vertex_index[sweep_tools.periodic_vertex(vertex)] for vertex in face
                )
                for face in disk_faces
                if all(
                    sweep_tools.periodic_vertex(vertex) in vertex_index for vertex in face
                )
            ]
            if len(indexed_disk) != len(disk_faces):
                raise AssertionError("a side ball does not contain the whole cutting disk")
            collapse = relative_collapse(indexed_tetrahedra, indexed_disk)
            side_records.append(
                {
                    "side_value": side_value,
                    "tetrahedron_count": len(component),
                    "vertex_count": len(vertices),
                    "vertex_table": [
                        [str(value) for value in vertex] for vertex in vertices
                    ],
                    "disk_face_count": len(indexed_disk),
                    "disk_faces": [list(face) for face in indexed_disk],
                    "collapse": collapse,
                }
            )
        states.append(
            {
                "state": state_name,
                "disk_face_count": len(disk_faces),
                "sides": side_records,
                "both_sides_collapse_to_disk": all(
                    side["collapse"]["relative_collapse_status"] == "PASS"
                    for side in side_records
                ),
            }
        )
    return {
        "power": movie["power"],
        "side": movie["side"],
        "support_sha256": canonical_sha(support),
        "states": states,
        "all_four_side_collapses": all(
            state["both_sides_collapse_to_disk"] for state in states
        ),
    }


def generate():
    analyzer = load("analyze_t73_johnson_arm_mismatch")
    pl = load("t73_johnson_pl")
    sweep_tools = load("build_t73_johnson_elementary_sweep")
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
    support = json.loads(SUPPORT.read_text(encoding="utf-8"))
    if support["sweep_sha256"] != sweep["sha256"]:
        raise AssertionError("paired support is not bound to the sweep")
    movies = [
        build_movie(analyzer, pl, sweep_tools, movie, support_movie)
        for movie, support_movie in zip(sweep["movies"], support["movies"])
    ]
    result = {
        "schema": "t73_johnson_relative_side_collapses/v1",
        "sweep_sha256": sweep["sha256"],
        "support_sha256": support["sha256"],
        "movies": movies,
        "side_ball_count": sum(
            len(state["sides"]) for movie in movies for state in movie["states"]
        ),
        "all_side_balls_collapse_relative_to_disk": all(
            movie["all_four_side_collapses"] for movie in movies
        ),
        "derived_star_chart_cells": "OPEN",
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
            "T73_JOHNSON_RELATIVE_SIDE_COLLAPSES="
            f"{'PASS' if result['all_side_balls_collapse_relative_to_disk'] else 'OPEN'}"
        )
        print(f"SIDE_BALLS={result['side_ball_count']}")
        print(f"DERIVED_STAR_CELLS={result['derived_star_chart_cells']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
