#!/usr/bin/env python3
"""Place the octahedral half-turn in every elementary Johnson disk move."""

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
SWEEP = ROOT / "geometry" / "t73_johnson_elementary_sweep.json"
HALFTURN = ROOT / "geometry" / "t73_johnson_octahedral_halfturn.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_disk_move_cells.json"


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


def midpoint(first, second):
    return tuple((first[axis] + second[axis]) / 2 for axis in range(3))


def vertex_key(vertex, side):
    if side == "prefix-first":
        return (vertex[1], vertex[0], vertex[2])
    return (vertex[0], vertex[1], vertex[2])


def octahedral_chart(vertices, attachment_slots, side):
    center = average(vertices)
    slots = sorted(attachment_slots)
    if len(slots) in (1, 3):
        apex_index = slots[0] if len(slots) == 1 else next(index for index in range(4) if index not in slots)
        face_indices = [index for index in range(4) if index != apex_index]
        ordered = sorted(face_indices, key=lambda index: vertex_key(vertices[index], side))
        first, second, fixed = ordered
        face_center = average([vertices[index] for index in face_indices])
        edge_midpoint = midpoint(vertices[first], vertices[second])
        octahedron = (
            vertices[apex_index],
            vertices[first],
            face_center,
            vertices[second],
            vertices[fixed],
            edge_midpoint,
        )
        kind = "one_three"
    elif len(slots) == 2:
        first_side = sorted(slots, key=lambda index: vertex_key(vertices[index], side))
        second_side = sorted(
            [index for index in range(4) if index not in slots],
            key=lambda index: vertex_key(vertices[index], side),
        )
        if side == "target-first":
            second_side.reverse()
        octahedron = (
            vertices[first_side[0]],
            vertices[first_side[1]],
            vertices[second_side[0]],
            vertices[second_side[1]],
            midpoint(vertices[first_side[0]], vertices[second_side[0]]),
            midpoint(vertices[first_side[1]], vertices[second_side[1]]),
        )
        kind = "two_two"
    else:
        raise AssertionError("disk move does not have one, two, or three attachment faces")
    return kind, octahedron, center


def actual_point(pl, center, octahedron, label, radius):
    return tuple(pl.add(center, pl.scale(radius, pl.sub(octahedron[label], center))))


def image_label(label, shift):
    return (label + shift) % 4 if label < 4 else label


def cells_for_chart(pl, cell_tools, halfturn_tools, octahedron, center, side):
    radii = halfturn_tools.RADII
    intermediate = 1 if side == "prefix-first" else 3
    cells = []
    for face in halfturn_tools.octahedron_faces():
        source = [center, *(actual_point(pl, center, octahedron, label, radii[0]) for label in face)]
        image = [
            center,
            *(
                actual_point(
                    pl, center, octahedron, image_label(label, 2), radii[0]
                )
                for label in face
            ),
        ]
        cells.append(cell_tools.oriented_cell(pl, source, image))
    for lower, upper, lower_shift, upper_shift in (
        (radii[0], radii[1], 2, intermediate),
        (radii[1], radii[2], intermediate, 0),
    ):
        for cap, first, second in halfturn_tools.octahedron_faces():
            order = (
                (cap, first, second)
                if side == "prefix-first"
                else (cap, second, first)
            )
            bottom = [actual_point(pl, center, octahedron, label, lower) for label in order]
            top = [actual_point(pl, center, octahedron, label, upper) for label in order]
            image_bottom = [
                actual_point(
                    pl, center, octahedron, image_label(label, lower_shift), lower
                )
                for label in order
            ]
            image_top = [
                actual_point(
                    pl, center, octahedron, image_label(label, upper_shift), upper
                )
                for label in order
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
            cells.extend(
                cell_tools.oriented_cell(pl, source_tets[index], image_tets[index])
                for index in range(3)
            )
    source_multiplicities, source_faces = halfturn_tools.face_multiplicities(
        pl, cells, "source"
    )
    image_multiplicities, image_faces = halfturn_tools.face_multiplicities(
        pl, cells, "image"
    )
    if set(source_multiplicities) != {1, 2} or set(image_multiplicities) != {1, 2}:
        raise AssertionError("placed half-turn is not a face-to-face ball")
    outer_vertices = {
        actual_point(pl, center, octahedron, label, radii[2]) for label in range(6)
    }
    source_outer_faces = {
        face for face, count in source_faces.items() if count == 1 and face <= outer_vertices
    }
    image_outer_faces = {
        face for face, count in image_faces.items() if count == 1 and face <= outer_vertices
    }
    if len(source_outer_faces) != 8 or source_outer_faces != image_outer_faces:
        raise AssertionError("placed half-turn does not fix its outer boundary")
    return center, cells, outer_vertices


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
        raise AssertionError("support clearance has no lattice comparison")
    return best


def attachment_slots(current, tetrahedron_index, adjacency):
    return [
        slot
        for slot, neighbour in enumerate(adjacency[tetrahedron_index])
        if current[tetrahedron_index] != current[neighbour]
    ]


def build_movie(pl, sweep_tools, cell_tools, halfturn_tools, movie):
    tetrahedra, adjacency, _ = sweep_tools.build_tetrahedra(
        sweep_tools.load("analyze_t73_johnson_arm_mismatch"), pl, movie["power"]
    )
    current = [tetrahedron["source_owner"] == 0 for tetrahedron in tetrahedra]
    records = []
    global_min = None
    global_max = None
    global_clearance = None
    for position, tetrahedron_index in enumerate(movie["single_move_tetrahedra"]):
        slots = attachment_slots(current, tetrahedron_index, adjacency)
        if len(slots) not in (1, 2, 3):
            raise AssertionError("stored sweep move is not a disk move on replay")
        vertices = tuple(tuple(vertex) for vertex in tetrahedra[tetrahedron_index]["vertices"])
        kind, octahedron, chart_center = octahedral_chart(vertices, slots, movie["side"])
        center, cells, outer_vertices = cells_for_chart(
            pl, cell_tools, halfturn_tools, octahedron, chart_center, movie["side"]
        )
        determinants = [Fraction(cell["jacobian_det"]) for cell in cells]
        if min(determinants) <= 0:
            raise AssertionError("placed octahedral half-turn reverses a cell")
        global_min = min(determinants) if global_min is None else min(global_min, *determinants)
        global_max = max(determinants) if global_max is None else max(global_max, *determinants)
        clearance = periodic_bbox_clearance(outer_vertices)
        if clearance <= pl.PROTECTED_RADIUS:
            raise AssertionError("placed disk-move collar meets the protected ball")
        global_clearance = (
            clearance if global_clearance is None else min(global_clearance, clearance)
        )
        records.append(
            {
                "position": position,
                "tetrahedron_index": tetrahedron_index,
                "attachment_slots": slots,
                "move_kind": kind,
                "center": pl.encode(center),
                "octahedron_vertices": [pl.encode(vertex) for vertex in octahedron],
                "cell_count": len(cells),
                "jacobian_det_min": str(min(determinants)),
                "jacobian_det_max": str(max(determinants)),
                "outer_boundary_identity": True,
                "protected_ball_bbox_clearance": str(clearance),
                "cells_sha256": canonical_sha(cells),
            }
        )
        current[tetrahedron_index] = not current[tetrahedron_index]
    return {
        "power": movie["power"],
        "side": movie["side"],
        "move_count": len(records),
        "moves": records,
        "cell_count": sum(record["cell_count"] for record in records),
        "jacobian_det_min": str(global_min),
        "jacobian_det_max": str(global_max),
        "protected_ball_bbox_clearance_min": str(global_clearance),
        "all_outer_boundaries_fixed": True,
        "all_supports_miss_protected_ball": True,
        "all_disk_move_cells_positive": True,
        "paired_saddle_cells": "OPEN",
    }


def generate():
    pl = load("t73_johnson_pl")
    sweep_tools = load("build_t73_johnson_elementary_sweep")
    cell_tools = load("build_t73_johnson_ball_shrinks")
    halfturn_tools = load("build_t73_johnson_octahedral_halfturn")
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
    halfturn = json.loads(HALFTURN.read_text(encoding="utf-8"))
    if sweep["ambient_pl_cell_status"] != "OPEN":
        raise AssertionError("unexpected sweep ambient-cell boundary")
    movies = [
        build_movie(pl, sweep_tools, cell_tools, halfturn_tools, movie)
        for movie in sweep["movies"]
    ]
    result = {
        "schema": "t73_johnson_disk_move_cells/v1",
        "sweep_sha256": sweep["sha256"],
        "halfturn_sha256": halfturn["sha256"],
        "movies": movies,
        "all_disk_move_cells_positive": all(
            movie["all_disk_move_cells_positive"] for movie in movies
        ),
        "disk_move_ambient_cells": "PASS",
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
        print(f"T73_JOHNSON_DISK_MOVE_CELLS={result['disk_move_ambient_cells']}")
        for movie in result["movies"]:
            print(
                f"POWER_{movie['power']}_{movie['side']}={movie['move_count']};"
                f"CELLS={movie['cell_count']};"
                f"JACOBIAN={movie['jacobian_det_min']}..{movie['jacobian_det_max']}"
            )
        print(f"PAIRED_SADDLE_CELLS={result['paired_saddle_ambient_cells']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
