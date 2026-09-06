#!/usr/bin/env python3
"""Realize the cut-open x/m1 support as a rational cubical shell in R3."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CUT = ROOT / "geometry/t73_x_m1_support_generator_sphere_cut.json"
REGINA = ROOT / "audit/t73_x_m1_support_generator_sphere_cut_regina_verification.json"
OUTPUT = ROOT / "geometry/t73_x_m1_support_cut_r3_shell.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def coordinate(vertex):
    if vertex < 8:
        radius = 1
    elif vertex < 16:
        radius = 2
    elif vertex < 24:
        radius = 4
    elif vertex < 32:
        radius = 3
    else:
        radius = 5
    corner = vertex % 8
    return [
        str(radius * (1 if (corner >> bit) & 1 else -1))
        for bit in (2, 1, 0)
    ]


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def determinant(first, second, third):
    return (
        first[0] * (second[1] * third[2] - second[2] * third[1])
        - first[1] * (second[0] * third[2] - second[2] * third[0])
        + first[2] * (second[0] * third[1] - second[1] * third[0])
    )


def build():
    cut = json.loads(CUT.read_text())
    regina = json.loads(REGINA.read_text())
    vertices = [coordinate(index) for index in range(40)]
    exact_determinants = []
    for tetrahedron in cut["cut_tetrahedra"]:
        a, b, c, d = [tuple(Fraction(value) for value in vertices[index]) for index in tetrahedron]
        exact_determinants.append(
            determinant(subtract(b, a), subtract(c, a), subtract(d, a))
        )
    if any(value == 0 for value in exact_determinants):
        raise AssertionError("cut-shell R3 tetrahedron is degenerate")
    absolute_volume = sum(abs(value) for value in exact_determinants) / 6
    if absolute_volume != 10**3 - 2**3:
        raise AssertionError("cut-shell tetrahedra do not fill the cubical shell volume")
    result = {
        "schema": "t73_x_m1_support_cut_r3_shell/v1",
        "support_generator_sphere_cut_sha256": cut["sha256"],
        "support_cut_regina_verification_sha256": regina["sha256"],
        "layer_order": ["A", "B", "D", "C", "A_copy"],
        "layer_radii": [1, 2, 3, 4, 5],
        "vertex_layer_ranges": {
            "A": [0, 7],
            "B": [8, 15],
            "D": [24, 31],
            "C": [16, 23],
            "A_copy": [32, 39],
        },
        "vertices": vertices,
        "tetrahedra": cut["cut_tetrahedra"],
        "vertex_count": len(vertices),
        "tetrahedron_count": len(cut["cut_tetrahedra"]),
        "nonzero_exact_tetrahedron_determinants": len(exact_determinants),
        "positive_stored_orientation_count": sum(value > 0 for value in exact_determinants),
        "negative_stored_orientation_count": sum(value < 0 for value in exact_determinants),
        "exact_absolute_volume": str(absolute_volume),
        "expected_cubical_shell_volume": "992",
        "inner_boundary_radius": 1,
        "outer_boundary_radius": 5,
        "recognized_topological_type": "S2 x I",
        "completion_status": "SUPPORT_CUT_REALIZED_AS_EXACT_R3_CUBICAL_SHELL",
    }
    result["sha256"] = canonical_sha256(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("support cut R3 shell is stale")
    print(json.dumps({
        "vertices": result["vertex_count"],
        "tetrahedra": result["tetrahedron_count"],
        "exact_volume": result["exact_absolute_volume"],
        "type": result["recognized_topological_type"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
