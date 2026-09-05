#!/usr/bin/env python3
"""Build the finite cubical collar map before cancelling x against m1."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BELTS = ROOT / "geometry/t73_belt_spheres.json"
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
HYBRID_MOVIE = ROOT / "geometry/t73_x_band_hybrid_movie.json"
OUTPUT = ROOT / "geometry/t73_x_m1_collar_ejection_map.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(values):
    return [[str(coordinate) for coordinate in value] for value in values]


def cube_boundary_triangles():
    triangles = []
    for bit in range(3):
        for value in (0, 1):
            vertices = sorted(
                index for index in range(8) if ((index >> (2 - bit)) & 1) == value
            )
            first, second, third, fourth = vertices
            triangles.extend([
                [first, second, fourth],
                [first, third, fourth],
            ])
    return triangles


def prism_tetrahedra(triangle, offset):
    first, second, third = sorted(triangle)
    return [
        [first, second, third, third + offset],
        [first, second, second + offset, third + offset],
        [first, first + offset, second + offset, third + offset],
    ]


def scale_transverse(value, factor):
    return (value[0],) + tuple(factor * coordinate for coordinate in value[1:])


def build() -> dict:
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    local_movie = json.loads(LOCAL_MOVIE.read_text(encoding="utf-8"))
    hybrid_movie = json.loads(HYBRID_MOVIE.read_text(encoding="utf-8"))
    belt = belts["x_handle"]["belt_sphere"]
    inner = [point(value) for value in belt["vertices"]]
    outer = [scale_transverse(value, Fraction(2)) for value in inner]
    target_inner = [scale_transverse(value, Fraction(3, 2)) for value in inner]
    source_vertices = [*inner, *outer]
    target_vertices = [*target_inner, *outer]
    boundary_triangles = cube_boundary_triangles()
    tetrahedra = [
        tetrahedron
        for triangle in boundary_triangles
        for tetrahedron in prism_tetrahedra(triangle, len(inner))
    ]
    result = {
        "schema": "t73_x_m1_collar_ejection_map/v1",
        "belt_spheres_sha256": belts["sha256"],
        "x_local_movie_sha256": local_movie["sha256"],
        "x_hybrid_movie_sha256": hybrid_movie["sha256"],
        "source_vertices": encode(source_vertices),
        "target_vertex_images": encode(target_vertices),
        "tetrahedra": tetrahedra,
        "source_inner_boundary_triangles": boundary_triangles,
        "source_outer_boundary_triangles": [
            [index + len(inner) for index in triangle]
            for triangle in boundary_triangles
        ],
        "transverse_cube_levels": {
            "source_inner": "1",
            "target_inner": "3/2",
            "fixed_outer": "2",
        },
        "outside_rule": "identity for transverse L-infinity radius at least 2",
        "cell_rule": "affine extension on each listed tetrahedron",
        "remaining_core_segment_state_sha256": local_movie[
            "final_local_segments_sha256"
        ],
        "cancelling_passage_source": "m_1:C_i",
        "map_scope": "remaining core ejection; framed-neighborhood check separate",
        "completion_status": "X_M1_CORE_COLLAR_EJECTION_CELL_MAP_CONSTRUCTED",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("x/m1 collar ejection map is stale")
    print("T73_X_M1_COLLAR=X_M1_CORE_COLLAR_EJECTION_CELL_MAP_CONSTRUCTED")


if __name__ == "__main__":
    main()
