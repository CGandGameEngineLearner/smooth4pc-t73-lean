#!/usr/bin/env python3
"""Build a finite PL collar map ejecting the state-6 link from the t-ball."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BELTS = ROOT / "geometry/t73_belt_spheres.json"
READINESS = ROOT / "audit/t73_t_hcs_cancellation_readiness.json"
FRAMING = ROOT / "geometry/t73_t_hcs_framing_exteriorization.json"
OUTPUT = ROOT / "geometry/t73_t_hcs_collar_ejection_map.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(values):
    return [[str(coordinate) for coordinate in value] for value in values]


def scale_spatial(value, factor):
    return tuple(factor * coordinate for coordinate in value[:3]) + (value[3],)


def prism_tetrahedra(face, top_offset):
    first, second, third = sorted(face)
    top_first = first + top_offset
    top_second = second + top_offset
    top_third = third + top_offset
    return [
        [first, second, third, top_third],
        [first, second, top_second, top_third],
        [first, top_first, top_second, top_third],
    ]


def build() -> dict:
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    framing = json.loads(FRAMING.read_text(encoding="utf-8"))
    if readiness["verdict"] != "READY_FOR_EXPLICIT_T_HCS_CANCELLATION_MAP":
        raise AssertionError("state-6 framed link is not ready for collar ejection")
    sphere = belts["t_handle"]["belt_sphere"]
    inner = [point(value) for value in sphere["vertices"]]
    source_outer = [scale_spatial(value, Fraction(2)) for value in inner]
    target_inner = [scale_spatial(value, Fraction(3, 2)) for value in inner]
    source_vertices = [*inner, *source_outer]
    target_vertices = [*target_inner, *source_outer]
    tetrahedra = [
        tetrahedron
        for face in sphere["faces"]
        for tetrahedron in prism_tetrahedra(face, len(inner))
    ]
    result = {
        "schema": "t73_t_hcs_collar_ejection_map/v1",
        "belt_spheres_sha256": belts["sha256"],
        "cancellation_readiness_sha256": readiness["sha256"],
        "framing_exteriorization_sha256": framing["sha256"],
        "source_vertices": encode(source_vertices),
        "target_vertex_images": encode(target_vertices),
        "tetrahedra": tetrahedra,
        "source_inner_boundary_triangles": [sorted(face) for face in sphere["faces"]],
        "source_outer_boundary_triangles": [
            sorted(vertex + len(inner) for vertex in face) for face in sphere["faces"]
        ],
        "radial_levels": {
            "source_inner": sphere["radius"],
            "target_inner": str(Fraction(3, 2) * Fraction(sphere["radius"])),
            "fixed_outer": str(2 * Fraction(sphere["radius"])),
        },
        "outside_rule": "identity for octahedral L1 radius at least 2r",
        "cell_rule": "affine extension on each listed tetrahedron",
        "map_scope": (
            "homeomorphism from the complement of the open r-octahedron to "
            "the complement of the open 3r/2-octahedron, fixed outside 2r"
        ),
        "completion_status": "T_HCS_COLLAR_EJECTION_CELL_MAP_CONSTRUCTED",
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
        raise AssertionError("t-h_CS collar ejection map is stale")
    print("T73_T_HCS_COLLAR_EJECTION=T_HCS_COLLAR_EJECTION_CELL_MAP_CONSTRUCTED")


if __name__ == "__main__":
    main()
