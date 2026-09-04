#!/usr/bin/env python3
"""Build a small complete seven-component framed-link exporter fixture.

This is a truth example for the input/output contract, not the T73 Kirby
diagram.  Seven separated polygonal Reidemeister-I unknots make every
component visible in ordinary PD notation.  The first five have explicit
translated push-offs (whose linking framings are computed, not asserted).
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "geometry" / "examples" / "seven_component_framed_unlink_input.json"
NAMES = ["m_2", "m_3", "r_xy", "r_yz", "r_zx", "dotted_y", "dotted_z"]


def encode(points: list[list[Fraction]]) -> list[list[str]]:
    return [[str(value) for value in point] for point in points]


def translated(points: list[list[Fraction]], shift: list[Fraction]) -> list[list[Fraction]]:
    return [[value + shift[index] for index, value in enumerate(point)] for point in points]


def build() -> dict[str, Any]:
    base = [
        [Fraction(-2), Fraction(-1), Fraction(0)],
        [Fraction(2), Fraction(1), Fraction(2)],
        [Fraction(-2), Fraction(1), Fraction(0)],
        [Fraction(2), Fraction(-1), Fraction(-2)],
        [Fraction(-2), Fraction(-1), Fraction(0)],
    ]
    components = []
    for index, name in enumerate(NAMES):
        core = translated(base, [Fraction(10 * index), Fraction(0), Fraction(0)])
        component = {
            "name": name,
            "component_kind": "two_handle" if index < 5 else "dotted_one_handle",
            "closed_core_polyline": encode(core),
            "cyclic_segment_successor": [1, 2, 3, 0],
        }
        if index < 5:
            push = translated(core, [Fraction(1, 7), Fraction(1, 11), Fraction(1, 13)])
            component["closed_push_off_polyline"] = encode(push)
            component["push_off_cyclic_segment_successor"] = [1, 2, 3, 0]
        components.append(component)
    return {
        "schema": "t73_full_handle_diagram_input/v1",
        "purpose": "complete truth fixture; explicitly not the T73 diagram",
        "ambient": {
            "chart": "oriented_affine_Q3",
            "ambient_orientation": "standard_xyz",
            "projection_direction": ["0", "0", "1"],
            "projection_basis": [["1", "0", "0"], ["0", "1", "0"]],
            "height_direction": ["0", "0", "1"],
            "genericity_certificate": {
                "method": "exact_fraction_recomputation",
                "claimed": "PASS",
            },
        },
        "components": components,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(text, encoding="utf-8")
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != text:
            raise AssertionError("committed complete-diagram fixture is stale")
    print("T73_FULL_HANDLE_EXAMPLE=WRITTEN" if args.write else "T73_FULL_HANDLE_EXAMPLE=CHECKED")
    print(f"COMPONENTS={len(value['components'])}")


if __name__ == "__main__":
    main()
