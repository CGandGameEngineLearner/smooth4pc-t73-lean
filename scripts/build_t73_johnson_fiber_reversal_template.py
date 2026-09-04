#!/usr/bin/env python3
"""Certify the octahedral half-turn as a cap-to-cap fiber reversal."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HALFTURN = ROOT / "geometry" / "t73_johnson_octahedral_halfturn.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_fiber_reversal_template.json"


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


def disk(axis_value):
    radius = Fraction(1, 2)
    center = (axis_value, Fraction(0), Fraction(0))
    boundary = (
        (axis_value, radius, Fraction(0)),
        (axis_value, Fraction(0), radius),
        (axis_value, -radius, Fraction(0)),
        (axis_value, Fraction(0), -radius),
    )
    triangles = tuple((center, boundary[index], boundary[(index + 1) % 4]) for index in range(4))
    return center, boundary, triangles


def rotate_halfturn(point):
    return (-point[0], -point[1], point[2])


def apply_cells(pl, cells, point):
    images = []
    for cell in cells:
        source = [pl.decode(vertex) for vertex in cell["source"]]
        if pl.point_in_tet(source, point, tol=Fraction(0)):
            image = pl.apply_affine(
                [[Fraction(value) for value in row] for row in cell["linear"]],
                pl.decode(cell["translation"]),
                point,
            )
            images.append(tuple(image))
    if not images:
        raise AssertionError("fiber disk point is outside the half-turn cells")
    if len(set(images)) != 1:
        raise AssertionError("half-turn cells disagree on a fiber disk point")
    return images[0]


def build_side(pl, side):
    source_center, source_boundary, source_triangles = disk(Fraction(-1, 2))
    target_center, target_boundary, target_triangles = disk(Fraction(1, 2))
    cells = side["cells"]
    source_vertices = {source_center, *source_boundary}
    target_vertices = {target_center, *target_boundary}
    vertex_images = {vertex: apply_cells(pl, cells, vertex) for vertex in source_vertices}
    for vertex, image in vertex_images.items():
        if image != rotate_halfturn(vertex):
            raise AssertionError("inner fiber is not moved by the rigid half-turn")
    if set(vertex_images.values()) != target_vertices:
        raise AssertionError("source fiber vertices do not land on the target fiber")
    image_triangles = {
        frozenset(vertex_images[vertex] for vertex in triangle)
        for triangle in source_triangles
    }
    if image_triangles != {frozenset(triangle) for triangle in target_triangles}:
        raise AssertionError("source fiber triangulation does not map to the target")
    return {
        "side": side["side"],
        "source_axis_value": "-1/2",
        "target_axis_value": "1/2",
        "source_center": [str(value) for value in source_center],
        "source_boundary": [[str(value) for value in vertex] for vertex in source_boundary],
        "target_center": [str(value) for value in target_center],
        "target_boundary": [[str(value) for value in vertex] for vertex in target_boundary],
        "disk_triangle_count": len(source_triangles),
        "source_to_target_disk": "PASS",
        "ambient_cell_count": side["cell_count"],
        "jacobian_det_min": side["jacobian_det_min"],
        "jacobian_det_max": side["jacobian_det_max"],
        "outer_boundary_identity": side["outer_boundary_identity"],
        "explicit_cellwise_inverse": side["explicit_cellwise_inverse"],
    }


def generate():
    pl = load("t73_johnson_pl")
    halfturn = json.loads(HALFTURN.read_text(encoding="utf-8"))
    sides = [build_side(pl, side) for side in halfturn["sides"]]
    result = {
        "schema": "t73_johnson_fiber_reversal_template/v1",
        "halfturn_sha256": halfturn["sha256"],
        "model": "diamond D^2 fibers at x=-1/2 and x=1/2 inside the unit octahedron",
        "sides": sides,
        "standard_fiber_reversal": "PASS",
        "actual_regular_neighbourhood_chart": "OPEN",
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
        print(f"T73_JOHNSON_FIBER_REVERSAL={result['standard_fiber_reversal']}")
        for side in result["sides"]:
            print(
                f"{side['side']}={side['ambient_cell_count']};"
                f"JACOBIAN={side['jacobian_det_min']}..{side['jacobian_det_max']}"
            )
        print(f"ACTUAL_CHART={result['actual_regular_neighbourhood_chart']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
