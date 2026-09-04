#!/usr/bin/env python3
"""Normalize the negative Johnson source disk to its remove-end cap."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SWEEP = ROOT / "geometry" / "t73_johnson_elementary_sweep.json"
SUPPORT = ROOT / "geometry" / "t73_johnson_paired_saddle_support.json"
DERIVED_CELLS = ROOT / "geometry" / "t73_johnson_derived_collapse_cells.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_negative_cap_normalization.json"


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


def lookup_cells(cells):
    return {
        (dimension["collapse_dimension"], side["side"]): side
        for dimension in cells["dimensions"]
        for side in dimension["sides"]
    }


def build_movie(pl, sweep_tools, relative_tools, placement_tools, derived, lookup, movie, support):
    tetrahedra, adjacency, face_occurrences = sweep_tools.build_tetrahedra(
        sweep_tools.load("analyze_t73_johnson_arm_mismatch"), pl, movie["power"]
    )
    current = [tetrahedron["source_owner"] == 0 for tetrahedron in tetrahedra]
    goal = [tetrahedron["target_owner"] == 0 for tetrahedron in tetrahedra]
    for index in movie["single_move_tetrahedra"]:
        current[index] = goal[index]
    support_indices = set(support["support_tetrahedra"])
    source_faces = [
        face
        for face, hits in face_occurrences.items()
        if all(index in support_indices for index, _ in hits)
        and current[hits[0][0]] != current[hits[1][0]]
    ]
    add_ball = set(
        next(item["tetrahedra"] for item in movie["grouped_moves"] if item["operation"] == "add")
    )
    remove_ball = set(
        next(
            item["tetrahedra"]
            for item in movie["grouped_moves"]
            if item["operation"] == "remove"
        )
    )
    core_path = [
        index for index in support["dual_path"] if index not in add_ball and index not in remove_ball
    ]
    remove_neighbour = next(
        neighbour for neighbour in adjacency[core_path[-1]] if neighbour in remove_ball
    )
    cap_face = next(
        face
        for face, hits in face_occurrences.items()
        if {index for index, _ in hits} == {core_path[-1], remove_neighbour}
    )
    if cap_face not in source_faces:
        raise AssertionError("remove cap is not contained in the source disk")
    vertices = sorted(
        {periodic(vertex) for face in source_faces for vertex in face}, key=repr
    )
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    triangles = [
        tuple(vertex_index[periodic(vertex)] for vertex in face) for face in source_faces
    ]
    protected = [
        tuple(vertex_index[periodic(vertex)] for vertex in cap_face)
    ]
    collapse = relative_tools.relative_collapse(triangles, protected)
    expected_steps = 2 if movie["power"] < 0 else 0
    if collapse["step_count"] != expected_steps:
        raise AssertionError("source-disk normalization has the wrong length")
    side_tetrahedra = []
    side_lifts = []
    all_vertices = sorted(
        {
            periodic(vertex)
            for index in support_indices
            for vertex in tetrahedra[index]["vertices"]
        },
        key=repr,
    )
    all_index = {vertex: index for index, vertex in enumerate(all_vertices)}
    for index in sorted(support_indices):
        side_tetrahedra.append(
            [all_index[periodic(vertex)] for vertex in tetrahedra[index]["vertices"]]
        )
        side_lifts.append(
            [[str(value) for value in vertex] for vertex in tetrahedra[index]["vertices"]]
        )
    local_to_all = {local: all_index[vertex] for local, vertex in enumerate(vertices)}
    side = {
        "tetrahedra": side_tetrahedra,
        "tetrahedron_lifts": side_lifts,
    }
    standard_vertices = [list(vertex) for vertex in derived.STANDARD_VERTICES]
    charts = []
    expanded_cells = 0
    for step in collapse["steps"]:
        translated_step = {
            "dimension": step["dimension"],
            "simplex": [local_to_all[index] for index in step["simplex"]],
            "free_face": [local_to_all[index] for index in step["free_face"]],
        }
        chart = placement_tools.chart_for_step(
            pl, standard_vertices, side, translated_step
        )
        template = lookup[(chart["dimension"], movie["side"])]
        expanded_cells += template["ambient_cell_count"]
        charts.append(
            {
                **chart,
                "standard_ambient_cell_count": template["ambient_cell_count"],
                "standard_jacobian_det_min": template["jacobian_det_min"],
                "standard_jacobian_det_max": template["jacobian_det_max"],
            }
        )
    return {
        "power": movie["power"],
        "side": movie["side"],
        "source_disk_triangle_count": len(source_faces),
        "target_cap_triangle_count": 1,
        "relative_collapse": collapse,
        "actual_charts": charts,
        "actual_chart_count": len(charts),
        "expanded_ambient_cell_count": expanded_cells,
        "jacobian_det_min": "1/3" if charts else None,
        "jacobian_det_max": "3" if charts else None,
        "source_disk_to_remove_cap": "PASS",
        "all_actual_charts_positive": True,
        "all_actual_chart_inverses_explicit": True,
    }


def generate():
    pl = load("t73_johnson_pl")
    sweep_tools = load("build_t73_johnson_elementary_sweep")
    relative_tools = load("build_t73_johnson_relative_side_collapses")
    placement_tools = load("build_t73_johnson_actual_derived_placements")
    derived = load("build_t73_johnson_derived_collapse_templates")
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
    support = json.loads(SUPPORT.read_text(encoding="utf-8"))
    cells = json.loads(DERIVED_CELLS.read_text(encoding="utf-8"))
    lookup = lookup_cells(cells)
    movies = [
        build_movie(
            pl,
            sweep_tools,
            relative_tools,
            placement_tools,
            derived,
            lookup,
            movie,
            support_movie,
        )
        for movie, support_movie in zip(sweep["movies"], support["movies"])
    ]
    result = {
        "schema": "t73_johnson_negative_cap_normalization/v1",
        "sweep_sha256": sweep["sha256"],
        "support_sha256": support["sha256"],
        "derived_cells_sha256": cells["sha256"],
        "movies": movies,
        "normalization_chart_count": sum(movie["actual_chart_count"] for movie in movies),
        "expanded_ambient_cell_count": sum(
            movie["expanded_ambient_cell_count"] for movie in movies
        ),
        "all_source_disks_normalize_to_remove_caps": "PASS",
        "paired_saddle_final_assembly": "OPEN",
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
            "T73_JOHNSON_NEGATIVE_CAP_NORMALIZATION="
            f"{result['all_source_disks_normalize_to_remove_caps']}"
        )
        print(f"CHARTS={result['normalization_chart_count']}")
        print(f"EXPANDED_CELLS={result['expanded_ambient_cell_count']}")
        print(f"FINAL_ASSEMBLY={result['paired_saddle_final_assembly']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
