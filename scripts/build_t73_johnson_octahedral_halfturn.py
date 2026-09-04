#!/usr/bin/env python3
"""Build the compact polar PL half-turn used by Johnson disk moves."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "geometry" / "t73_johnson_octahedral_halfturn.json"
RADII = (Fraction(1), Fraction(1001, 1000), Fraction(501, 500))


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


def standard_vertices():
    return (
        (Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1), Fraction(0)),
        (Fraction(-1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(-1), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(1)),
        (Fraction(0), Fraction(0), Fraction(-1)),
    )


def octahedron_faces():
    return tuple((cap, sector, (sector + 1) % 4) for cap in (4, 5) for sector in range(4))


def point(vertices, label, radius):
    return tuple(radius * coordinate for coordinate in vertices[label])


def image_label(label, shift):
    return (label + shift) % 4 if label < 4 else label


def staircase_cells(pl, cell_tools, vertices, face, lower, upper, lower_shift, upper_shift, side):
    cap, first, second = face
    order = (cap, first, second) if side == "prefix-first" else (cap, second, first)
    bottom = [point(vertices, label, lower) for label in order]
    top = [point(vertices, label, upper) for label in order]
    image_bottom = [
        point(vertices, image_label(label, lower_shift), lower) for label in order
    ]
    image_top = [
        point(vertices, image_label(label, upper_shift), upper) for label in order
    ]
    source = (
        (bottom[0], bottom[1], bottom[2], top[2]),
        (bottom[0], bottom[1], top[1], top[2]),
        (bottom[0], top[0], top[1], top[2]),
    )
    image = (
        (image_bottom[0], image_bottom[1], image_bottom[2], image_top[2]),
        (image_bottom[0], image_bottom[1], image_top[1], image_top[2]),
        (image_bottom[0], image_top[0], image_top[1], image_top[2]),
    )
    return [
        cell_tools.oriented_cell(pl, source[index], image[index]) for index in range(3)
    ]


def face_multiplicities(pl, cells, key):
    counts = Counter()
    for cell in cells:
        tetrahedron = [tuple(pl.decode(vertex)) for vertex in cell[key]]
        for omitted in range(4):
            counts[
                frozenset(
                    tetrahedron[index] for index in range(4) if index != omitted
                )
            ] += 1
    return Counter(counts.values()), counts


def build_side(pl, cell_tools, side):
    vertices = standard_vertices()
    faces = octahedron_faces()
    center = (Fraction(0), Fraction(0), Fraction(0))
    intermediate_shift = 1 if side == "prefix-first" else 3
    cells = []
    for face in faces:
        source = [center, *(point(vertices, label, RADII[0]) for label in face)]
        image = [
            center,
            *(point(vertices, image_label(label, 2), RADII[0]) for label in face),
        ]
        cells.append(cell_tools.oriented_cell(pl, source, image))
    for face in faces:
        cells.extend(
            staircase_cells(
                pl,
                cell_tools,
                vertices,
                face,
                RADII[0],
                RADII[1],
                2,
                intermediate_shift,
                side,
            )
        )
        cells.extend(
            staircase_cells(
                pl,
                cell_tools,
                vertices,
                face,
                RADII[1],
                RADII[2],
                intermediate_shift,
                0,
                side,
            )
        )
    determinants = [Fraction(cell["jacobian_det"]) for cell in cells]
    inverse_determinants = [Fraction(cell["inverse_jacobian_det"]) for cell in cells]
    if min(determinants) <= 0 or min(inverse_determinants) <= 0:
        raise AssertionError("octahedral half-turn has a nonpositive cell")
    source_multiplicities, source_faces = face_multiplicities(pl, cells, "source")
    image_multiplicities, image_faces = face_multiplicities(pl, cells, "image")
    if set(source_multiplicities) != {1, 2} or set(image_multiplicities) != {1, 2}:
        raise AssertionError("octahedral half-turn cells are not face-to-face balls")
    outer_vertices = {point(vertices, label, RADII[2]) for label in range(6)}
    outer_source_faces = [
        face
        for face, count in source_faces.items()
        if count == 1 and face <= outer_vertices
    ]
    outer_image_faces = [
        face for face, count in image_faces.items() if count == 1 and face <= outer_vertices
    ]
    if len(outer_source_faces) != 8 or set(outer_source_faces) != set(outer_image_faces):
        raise AssertionError("outer octahedral boundary is not fixed")
    return {
        "side": side,
        "sector_shifts": [2, intermediate_shift, 0],
        "radii": [str(radius) for radius in RADII],
        "inner_cone_cells": 8,
        "first_shell_cells": 24,
        "second_shell_cells": 24,
        "cell_count": len(cells),
        "jacobian_det_min": str(min(determinants)),
        "jacobian_det_max": str(max(determinants)),
        "inverse_jacobian_det_min": str(min(inverse_determinants)),
        "source_face_multiplicities": {
            str(key): value for key, value in sorted(source_multiplicities.items())
        },
        "image_face_multiplicities": {
            str(key): value for key, value in sorted(image_multiplicities.items())
        },
        "outer_boundary_triangle_count": len(outer_source_faces),
        "outer_boundary_identity": True,
        "explicit_cellwise_inverse": True,
        "cells": cells,
    }


def generate():
    pl = load("t73_johnson_pl")
    cell_tools = load("build_t73_johnson_ball_shrinks")
    sides = [
        build_side(pl, cell_tools, side)
        for side in ("prefix-first", "target-first")
    ]
    result = {
        "schema": "t73_johnson_octahedral_halfturn/v1",
        "coordinate_model": (
            "four rational angular sectors and two axial caps; adjacent radial "
            "layers differ by one sector"
        ),
        "radii": [str(radius) for radius in RADII],
        "sides": sides,
        "all_cells_positive": all(Fraction(side["jacobian_det_min"]) > 0 for side in sides),
        "all_outer_boundaries_fixed": all(side["outer_boundary_identity"] for side in sides),
        "ambient_halfturn_template": "PASS",
        "sweep_placement_status": "OPEN",
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
        print(f"T73_JOHNSON_OCTAHEDRAL_HALFTURN={result['ambient_halfturn_template']}")
        for side in result["sides"]:
            print(
                f"{side['side']}={side['cell_count']};"
                f"JACOBIAN={side['jacobian_det_min']}..{side['jacobian_det_max']}"
            )
        print(f"SWEEP_PLACEMENT={result['sweep_placement_status']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
