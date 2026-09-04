#!/usr/bin/env python3
"""Audit the full Johnson overlay and reject fiber-only restore cutoffs."""

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
OUTPUT = ROOT / "geometry" / "t73_johnson_restore_overlay.json"


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


def build_overlay(analyzer, pl, power):
    source, prefix = 0, 1
    matrix = pl.transvection_matrix(source, prefix, power)
    owners = pl.johnson_owners()
    pieces = []
    active_vertices = set()
    mismatch_vertices = set()
    for source_owner, index, source_tetrahedron in analyzer.source_tetrahedra():
        tetrahedron = [pl.matvec(matrix, vertex) for vertex in source_tetrahedron]
        lows = [math.floor(min(vertex[axis] for vertex in tetrahedron)) for axis in range(3)]
        highs = [math.ceil(max(vertex[axis] for vertex in tetrahedron)) for axis in range(3)]
        for cube in itertools.product(*(range(lows[axis], highs[axis]) for axis in range(3))):
            vertices = analyzer.intersection_vertices(pl, tetrahedron, cube)
            if not analyzer.rank3(pl, vertices):
                continue
            target_owner = owners[tuple(value % pl.PERIOD for value in cube)]
            moved_cube = list(cube)
            moved_cube[prefix] += 2
            moved_target_owner = owners[tuple(value % pl.PERIOD for value in moved_cube)]
            inactive_good = source_owner == target_owner
            active_good = source_owner == moved_target_owner
            classification = (
                "flexible"
                if inactive_good and active_good
                else "mandatory_active"
                if active_good
                else "mandatory_inactive"
                if inactive_good
                else "impossible"
            )
            piece = {
                "vertices": vertices,
                "source_owner": source_owner,
                "target_owner": target_owner,
                "cube": cube,
                "classification": classification,
            }
            pieces.append(piece)
            if active_good:
                active_vertices.update(tuple(value % 4 for value in vertex) for vertex in vertices)
            if source_owner != target_owner:
                mismatch_vertices.update(tuple(value % 4 for value in vertex) for vertex in vertices)
    if any(piece["classification"] == "impossible" for piece in pieces):
        raise AssertionError("overlay has a cell with no valid endpoint choice")

    cells_by_cube = collections.defaultdict(list)
    slopes = []
    for piece in pieces:
        vertices = piece["vertices"]
        center = [sum(vertex[axis] for vertex in vertices) / len(vertices) for axis in range(3)]
        active = piece["classification"] in ("mandatory_active", "flexible")
        cube = piece["cube"]
        shift = [Fraction((cube[axis] // 4) * 4) for axis in range(3)]
        cube_key = tuple(cube[axis] % 4 for axis in range(3))
        for facet in analyzer.polytope_facets(pl, [pl.encode(vertex) for vertex in vertices]):
            for triangle in analyzer.triangulate_face(pl, facet):
                source_tet = [list(triangle[0]), list(triangle[1]), list(triangle[2]), center]
                weights = [
                    Fraction(tuple(value % 4 for value in vertex) in active_vertices)
                    for vertex in triangle
                ] + [Fraction(active)]
                canonical_tet = [
                    [vertex[axis] - shift[axis] for axis in range(3)] for vertex in source_tet
                ]
                cells_by_cube[cube_key].append((canonical_tet, weights))
                image_tet = [list(vertex) for vertex in source_tet]
                for index, weight in enumerate(weights):
                    image_tet[index][prefix] += weight
                slopes.append(pl.affine_from_tets(source_tet, image_tet)[2] - 1)
    steps = 1
    while any(1 + Fraction(2, steps) * slope <= 0 for slope in slopes):
        steps += 1
    delta = Fraction(2, steps)

    def cutoff(point):
        reduced = [value % 4 for value in point]
        cube_key = tuple(min(3, int(value)) for value in reduced)
        for tetrahedron, weights in cells_by_cube[cube_key]:
            barycentric = pl.barycentric(tetrahedron, reduced)
            if barycentric is not None and all(value >= 0 for value in barycentric):
                return sum(barycentric[index] * weights[index] for index in range(4))
        raise AssertionError("overlay cutoff has no containing tetrahedron")

    def fiber_restore(point):
        image = list(point)
        for step in range(steps):
            probe = list(image)
            probe[prefix] -= step * delta
            image[prefix] += delta * cutoff(probe)
        return image

    cube_mismatches = 0
    tetrahedron_mismatches = 0
    for origin in itertools.product(range(4), repeat=3):
        expected_owner = owners[origin]
        center = [Fraction(value) + Fraction(1, 2) for value in origin]
        image = fiber_restore(pl.matvec(matrix, center))
        cube_mismatches += pl.point_owner(image, owners) != expected_owner
        for permutation in itertools.permutations(range(3)):
            current = [Fraction(value) for value in origin]
            vertices = [current]
            for axis in permutation:
                current = list(current)
                current[axis] += 1
                vertices.append(current)
            barycenter = [
                sum(vertex[axis] for vertex in vertices) / 4 for axis in range(3)
            ]
            image = fiber_restore(pl.matvec(matrix, barycenter))
            tetrahedron_mismatches += pl.point_owner(image, owners) != expected_owner

    mismatch_transport_failures = 0
    for vertex in mismatch_vertices:
        image = fiber_restore(list(vertex))
        expected = list(vertex)
        expected[prefix] += 2
        if any((image[axis] - expected[axis]) % 4 != 0 for axis in range(3)):
            mismatch_transport_failures += 1
    return {
        "power": power,
        "canonical_source_axis": source,
        "canonical_prefix_axis": prefix,
        "overlay_piece_count": len(pieces),
        "overlay_tetrahedron_count": sum(len(cells) for cells in cells_by_cube.values()),
        "endpoint_classification": dict(
            sorted(collections.Counter(piece["classification"] for piece in pieces).items())
        ),
        "mismatch_vertex_count": len(mismatch_vertices),
        "fiber_cutoff_steps": steps,
        "fiber_cutoff_delta": str(delta),
        "fiber_cutoff_step_jacobian_min": str(
            min(1 + delta * slope for slope in slopes)
        ),
        "mismatch_vertex_transport_failures": mismatch_transport_failures,
        "cube_owner_mismatches": cube_mismatches,
        "tetrahedron_owner_mismatches": tetrahedron_mismatches,
        "fiber_preserving_restore_status": "REJECTED",
        "required_next_geometry": (
            "transverse Johnson-square motion through the flexible overlay cells"
        ),
    }


def generate():
    analyzer = load("analyze_t73_johnson_arm_mismatch")
    pl = load("t73_johnson_pl")
    templates = [build_overlay(analyzer, pl, power) for power in (-1, 1)]
    result = {
        "schema": "t73_johnson_restore_overlay/v1",
        "canonical_axis_pair": [0, 1],
        "axis_permutation_symmetry": True,
        "templates": templates,
        "fiber_preserving_restore_status": "REJECTED",
        "johnson_restore_status": "OPEN",
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
        print("T73_JOHNSON_RESTORE_OVERLAY=PASS")
        print(f"FIBER_PRESERVING={result['fiber_preserving_restore_status']}")
        for template in result["templates"]:
            print(
                f"POWER_{template['power']}_OWNER_MISMATCHES="
                f"{template['cube_owner_mismatches']}/{template['tetrahedron_owner_mismatches']}"
            )
        print(f"JOHNSON_RESTORE={result['johnson_restore_status']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
