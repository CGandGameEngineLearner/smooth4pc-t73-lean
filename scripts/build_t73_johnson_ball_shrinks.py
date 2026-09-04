#!/usr/bin/env python3
"""Build fixed-boundary radial PL shrink maps for Johnson mismatch balls."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MISMATCH = ROOT / "geometry" / "t73_johnson_arm_mismatch.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_ball_shrinks.json"
CORE_SCALE = Fraction(1, 4)
OUTER_SCALE = Fraction(3, 2)


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


def scaled(pl, center, point, factor):
    return pl.add(center, pl.scale(factor, pl.sub(point, center)))


def oriented_cell(pl, source, image):
    source = [list(vertex) for vertex in source]
    image = [list(vertex) for vertex in image]
    source_det = pl.det3(
        [[source[column][row] - source[0][row] for column in range(1, 4)] for row in range(3)]
    )
    if source_det == 0:
        raise AssertionError("shrink source tetrahedron is degenerate")
    if source_det < 0:
        source[1], source[2] = source[2], source[1]
        image[1], image[2] = image[2], image[1]
    linear, translation, jacobian = pl.affine_from_tets(source, image)
    inverse_linear, inverse_translation, inverse_jacobian = pl.affine_from_tets(image, source)
    if jacobian <= 0 or inverse_jacobian <= 0:
        raise AssertionError("radial shrink reverses a tetrahedron")
    return {
        "source": [pl.encode(vertex) for vertex in source],
        "image": [pl.encode(vertex) for vertex in image],
        "linear": [[str(value) for value in row] for row in linear],
        "translation": pl.encode(translation),
        "jacobian_det": str(jacobian),
        "inverse_linear": [[str(value) for value in row] for row in inverse_linear],
        "inverse_translation": pl.encode(inverse_translation),
        "inverse_jacobian_det": str(inverse_jacobian),
    }


def component_boundary(analyzer, pl, template, component):
    occurrences = defaultdict(list)
    shifts = {
        int(index): [Fraction(value) for value in shift]
        for index, shift in component["piece_lift_shifts"].items()
    }
    for piece_index in component["piece_indices"]:
        shift = shifts[piece_index]
        vertices = [
            pl.add(pl.decode(vertex), shift)
            for vertex in template["pieces"][piece_index]["vertices"]
        ]
        for facet in analyzer.polytope_facets(pl, [pl.encode(vertex) for vertex in vertices]):
            occurrences[facet].append(piece_index)
    boundary = [facet for facet, hits in occurrences.items() if len(hits) == 1]
    triangles = []
    for facet in boundary:
        triangles.extend(analyzer.triangulate_face(pl, facet))
    return triangles


def prism_cells(pl, bottom, top, image_bottom, image_top):
    a, b, c = bottom
    d, e, f = top
    ia, ib, ic = image_bottom
    id_, ie, iff = image_top
    source_candidates = ([a, b, c, d], [b, c, d, e], [c, d, e, f])
    image_candidates = ([ia, ib, ic, id_], [ib, ic, id_, ie], [ic, id_, ie, iff])
    try:
        return [
            oriented_cell(pl, source, image)
            for source, image in zip(source_candidates, image_candidates)
        ]
    except AssertionError:
        source_candidates = ([a, b, c, f], [a, b, e, f], [a, d, e, f])
        image_candidates = ([ia, ib, ic, iff], [ia, ib, ie, iff], [ia, id_, ie, iff])
        return [
            oriented_cell(pl, source, image)
            for source, image in zip(source_candidates, image_candidates)
        ]


def build_component(analyzer, pl, template, component):
    center = pl.decode(component["triangulation"]["star_center"])
    boundary = component_boundary(analyzer, pl, template, component)
    cells = []
    for triangle in boundary:
        core_triangle = [scaled(pl, center, vertex, CORE_SCALE) for vertex in triangle]
        outer_triangle = [scaled(pl, center, vertex, OUTER_SCALE) for vertex in triangle]
        cells.append(oriented_cell(pl, [center, *triangle], [center, *core_triangle]))
        cells.extend(
            prism_cells(
                pl,
                triangle,
                outer_triangle,
                core_triangle,
                outer_triangle,
            )
        )
    source_faces = Counter()
    image_faces = Counter()
    for cell in cells:
        for key, counts in (("source", source_faces), ("image", image_faces)):
            tetrahedron = [tuple(pl.decode(vertex)) for vertex in cell[key]]
            for omitted in range(4):
                counts[frozenset(tetrahedron[index] for index in range(4) if index != omitted)] += 1
    if any(value not in (1, 2) for value in source_faces.values()):
        raise AssertionError("source shrink cells are not face-to-face")
    if any(value not in (1, 2) for value in image_faces.values()):
        raise AssertionError("image shrink cells are not face-to-face")
    outer_vertices = {
        tuple(scaled(pl, center, vertex, OUTER_SCALE)) for triangle in boundary for vertex in triangle
    }
    for vertex in outer_vertices:
        images = []
        for cell in cells:
            source = [pl.decode(point) for point in cell["source"]]
            if pl.point_in_tet(source, vertex):
                images.append(
                    pl.apply_affine(
                        [[Fraction(value) for value in row] for row in cell["linear"]],
                        pl.decode(cell["translation"]),
                        vertex,
                    )
                )
        if not images or any(image != list(vertex) for image in images):
            raise AssertionError("shrink map does not fix its outer boundary")
    determinants = [Fraction(cell["jacobian_det"]) for cell in cells]
    return {
        "component_id": component["component_id"],
        "source_owner": component["source_owner"],
        "center": pl.encode(center),
        "core_scale": str(CORE_SCALE),
        "outer_scale": str(OUTER_SCALE),
        "boundary_triangle_count": len(boundary),
        "cell_count": len(cells),
        "jacobian_det_min": str(min(determinants)),
        "jacobian_det_max": str(max(determinants)),
        "outer_boundary_identity": True,
        "explicit_inverse": True,
        "cells": cells,
    }


def generate():
    pl = load("t73_johnson_pl")
    analyzer = load("analyze_t73_johnson_arm_mismatch")
    mismatch = json.loads(MISMATCH.read_text(encoding="utf-8"))
    templates = []
    for template in mismatch["templates"]:
        components = [build_component(analyzer, pl, template, component) for component in template["components"]]
        templates.append(
            {
                "source_axis": template["source_axis"],
                "prefix_axis": template["prefix_axis"],
                "power": template["power"],
                "components": components,
                "all_outer_boundaries_fixed": all(item["outer_boundary_identity"] for item in components),
                "all_jacobians_positive": all(Fraction(item["jacobian_det_min"]) > 0 for item in components),
            }
        )
    result = {
        "schema": "t73_johnson_ball_shrinks/v1",
        "mismatch_sha256": mismatch["sha256"],
        "core_scale": str(CORE_SCALE),
        "outer_scale": str(OUTER_SCALE),
        "templates": templates,
        "fixed_boundary_radial_shrinks": "PASS",
        "ball_exchange_status": "OPEN",
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
        print(f"T73_JOHNSON_BALL_SHRINKS={result['fixed_boundary_radial_shrinks']}")
        print(f"BALL_EXCHANGE={result['ball_exchange_status']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
