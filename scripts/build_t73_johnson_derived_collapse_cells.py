#!/usr/bin/env python3
"""Build positive ambient cells for the three derived-collapse templates."""

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
TEMPLATES = ROOT / "geometry" / "t73_johnson_derived_collapse_templates.json"
HALFTURN = ROOT / "geometry" / "t73_johnson_octahedral_halfturn.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_derived_collapse_cells.json"


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


def build_cone(derived, dimension):
    simplex = frozenset(range(dimension + 1))
    free_face = frozenset(range(1, dimension + 1))
    before_complex = derived.downward_closure(simplex)
    after_complex = set(before_complex) - {simplex, free_face}
    before = derived.closed_star(before_complex)
    after = derived.closed_star(after_complex)
    after_set = {frozenset(tetrahedron) for tetrahedron in after}
    difference = [
        tetrahedron
        for tetrahedron in before
        if frozenset(tetrahedron) not in after_set
    ]
    before_boundary = derived.boundary_faces(before)
    after_boundary = derived.boundary_faces(after)
    common = before_boundary & after_boundary
    before_patch = before_boundary - common
    after_patch = after_boundary - common
    center = derived.STAR_CENTERS[dimension]
    cone = []
    for patch_name, patch in (("before", before_patch), ("after", after_patch)):
        for face in sorted(patch, key=repr):
            cone.append(
                {
                    "patch": patch_name,
                    "base_face": face,
                    "vertices": (center, *(derived.second_coordinate(vertex) for vertex in face)),
                }
            )
    if len(cone) != len(derived.boundary_faces(difference)):
        raise AssertionError("cone does not have one tetrahedron per difference boundary face")
    face_occurrences = collections.defaultdict(list)
    for index, tetrahedron in enumerate(cone):
        for omitted in range(4):
            face = frozenset(
                tetrahedron["vertices"][vertex]
                for vertex in range(4)
                if vertex != omitted
            )
            face_occurrences[face].append((index, omitted))
    if set(map(len, face_occurrences.values())) != {1, 2}:
        raise AssertionError("cone is not a face-to-face ball")
    adjacency = [[None, None, None, None] for _ in cone]
    boundary_slots = {}
    for face, hits in face_occurrences.items():
        if len(hits) == 2:
            (first, first_slot), (second, second_slot) = hits
            adjacency[first][first_slot] = second
            adjacency[second][second_slot] = first
        else:
            index, slot = hits[0]
            boundary_slots[(index, slot)] = cone[index]["patch"]
    return cone, adjacency, boundary_slots


def interface_faces(cone, adjacency, boundary_slots, active):
    faces = set()
    for index, tetrahedron in enumerate(cone):
        for slot in range(4):
            neighbour = adjacency[index][slot]
            if neighbour is not None:
                if index < neighbour and active[index] != active[neighbour]:
                    faces.add(
                        frozenset(
                            tetrahedron["vertices"][vertex]
                            for vertex in range(4)
                            if vertex != slot
                        )
                    )
            else:
                outside_active = boundary_slots[(index, slot)] == "before"
                if active[index] != outside_active:
                    faces.add(
                        frozenset(
                            tetrahedron["vertices"][vertex]
                            for vertex in range(4)
                            if vertex != slot
                        )
                    )
    return faces


def attachment_slots(index, adjacency, boundary_slots, active):
    slots = []
    for slot in range(4):
        neighbour = adjacency[index][slot]
        if neighbour is not None:
            if active[neighbour]:
                slots.append(slot)
        elif boundary_slots[(index, slot)] == "before":
            slots.append(slot)
    return slots


def build_side(pl, derived, disk_tools, cell_tools, halfturn_tools, dimension, side):
    cone, adjacency, boundary_slots = build_cone(derived, dimension)
    active = [False] * len(cone)
    initial_interface = derived.surface_invariants(
        interface_faces(cone, adjacency, boundary_slots, active)
    )
    if initial_interface["topology"] != "disk":
        raise AssertionError("cone movie does not start at the before disk")
    moves = []
    determinant_min = None
    determinant_max = None
    for phase in ("before", "after"):
        remaining = {
            index
            for index, tetrahedron in enumerate(cone)
            if tetrahedron["patch"] == phase
        }
        while remaining:
            candidates = []
            for index in remaining:
                slots = attachment_slots(index, adjacency, boundary_slots, active)
                if 1 <= len(slots) <= 3:
                    candidates.append((repr(cone[index]["base_face"]), index, slots))
            if not candidates:
                raise AssertionError("cone disk sweep is stuck")
            chosen = None
            for _, candidate_index, candidate_slots in sorted(candidates):
                active[candidate_index] = True
                candidate_interface = derived.surface_invariants(
                    interface_faces(cone, adjacency, boundary_slots, active)
                )
                if candidate_interface["topology"] == "disk":
                    chosen = (
                        candidate_index,
                        candidate_slots,
                        candidate_interface,
                    )
                    break
                active[candidate_index] = False
            if chosen is None:
                raise AssertionError("cone disk sweep has no manifold candidate")
            index, slots, interface = chosen
            vertices = cone[index]["vertices"]
            kind, octahedron, center = disk_tools.octahedral_chart(vertices, slots, side)
            _, cells, _ = disk_tools.cells_for_chart(
                pl, cell_tools, halfturn_tools, octahedron, center, side
            )
            determinants = [Fraction(cell["jacobian_det"]) for cell in cells]
            if min(determinants) <= 0:
                raise AssertionError("derived cone move has a nonpositive Jacobian")
            determinant_min = (
                min(determinants)
                if determinant_min is None
                else min(determinant_min, *determinants)
            )
            determinant_max = (
                max(determinants)
                if determinant_max is None
                else max(determinant_max, *determinants)
            )
            remaining.remove(index)
            moves.append(
                {
                    "position": len(moves),
                    "phase": phase,
                    "cone_tetrahedron": index,
                    "attachment_slots": slots,
                    "move_kind": kind,
                    "cell_count": len(cells),
                    "jacobian_det_min": str(min(determinants)),
                    "jacobian_det_max": str(max(determinants)),
                    "cells_sha256": canonical_sha(cells),
                    "interface": interface,
                }
            )
    final_interface = derived.surface_invariants(
        interface_faces(cone, adjacency, boundary_slots, active)
    )
    if final_interface["topology"] != "disk" or not all(active):
        raise AssertionError("cone movie does not finish at the after disk")
    return {
        "side": side,
        "move_count": len(moves),
        "moves": moves,
        "ambient_cell_count": sum(move["cell_count"] for move in moves),
        "jacobian_det_min": str(determinant_min),
        "jacobian_det_max": str(determinant_max),
        "initial_interface": initial_interface,
        "final_interface": final_interface,
        "all_intermediate_interfaces_are_disks": True,
        "all_cells_positive": True,
        "explicit_cellwise_inverses": True,
    }


def build_dimension(pl, derived, disk_tools, cell_tools, halfturn_tools, dimension):
    sides = [
        build_side(pl, derived, disk_tools, cell_tools, halfturn_tools, dimension, side)
        for side in ("prefix-first", "target-first")
    ]
    return {
        "collapse_dimension": dimension,
        "sides": sides,
        "derived_collapse_ambient_cells": "PASS",
    }


def generate():
    pl = load("t73_johnson_pl")
    derived = load("build_t73_johnson_derived_collapse_templates")
    disk_tools = load("build_t73_johnson_disk_move_cells")
    cell_tools = load("build_t73_johnson_ball_shrinks")
    halfturn_tools = load("build_t73_johnson_octahedral_halfturn")
    templates = json.loads(TEMPLATES.read_text(encoding="utf-8"))
    halfturn = json.loads(HALFTURN.read_text(encoding="utf-8"))
    dimensions = [
        build_dimension(pl, derived, disk_tools, cell_tools, halfturn_tools, dimension)
        for dimension in (1, 2, 3)
    ]
    result = {
        "schema": "t73_johnson_derived_collapse_cells/v1",
        "templates_sha256": templates["sha256"],
        "halfturn_sha256": halfturn["sha256"],
        "dimensions": dimensions,
        "all_standard_derived_collapse_cells": "PASS",
        "actual_collapse_pair_placement": "OPEN",
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
        print(f"T73_JOHNSON_DERIVED_COLLAPSE_CELLS={result['all_standard_derived_collapse_cells']}")
        for dimension in result["dimensions"]:
            for side in dimension["sides"]:
                print(
                    f"DIM_{dimension['collapse_dimension']}_{side['side']}="
                    f"{side['move_count']};CELLS={side['ambient_cell_count']};"
                    f"JACOBIAN={side['jacobian_det_min']}..{side['jacobian_det_max']}"
                )
        print(f"ACTUAL_PLACEMENT={result['actual_collapse_pair_placement']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
