#!/usr/bin/env python3
"""Build a rational four-box normal form for the selected 44+227 pattern."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PRIMITIVES = ROOT / "geometry" / "t73_all_owner_product_primitives.json"
COLLAR = ROOT / "geometry" / "t73_p0_marked_vertical_collar.json"
OUTPUT = ROOT / "geometry" / "t73_selected_canopolis_normal_form.json"
DELTA = Fraction(1, 10000)


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def encode(point) -> list[str]:
    return [str(Fraction(value)) for value in point]


def lane_point(index: int) -> tuple[Fraction, Fraction]:
    column, row = index % 16, index // 16
    return Fraction(2 * column - 15, 18), Fraction(row - 8, 10)


def box(name, lower, upper, closure, variable):
    return {
        "name": name,
        "lower": encode(lower),
        "upper": encode(upper),
        "closure": closure,
        "variable": variable,
        "parametrized": True,
    }


def strand(side, index, source_x, target_x, primitive):
    y, z = lane_point(index)
    start, end = (source_x, y, z), (target_x, y, z)
    return {
        "index": index,
        "side": side,
        "role": primitive["role"],
        "primitive_id": primitive["primitive_id"],
        "owner": primitive["owner"],
        "source_ids": primitive["source_ids"],
        "is_cyclic_m2_connector": primitive["is_cyclic_m2_connector"],
        "centerline": [encode(start), encode(end)],
        "product_normal": ["0", str(DELTA), "0"],
        "positive_push_off": [
            encode((source_x, y + DELTA, z)),
            encode((target_x, y + DELTA, z)),
        ],
        "relative_twist": 0,
    }


def build() -> dict[str, Any]:
    all_owner = json.loads(PRIMITIVES.read_text(encoding="utf-8"))
    collar = json.loads(COLLAR.read_text(encoding="utf-8"))
    pairs = (
        all_owner["primitive_geometry"]["r_xy"]["product_rectangles"]
        + all_owner["primitive_geometry"]["m_2"]["product_rectangles"]
    )
    leftovers = (
        all_owner["primitive_geometry"]["r_xy"]["leftover_z_circles"]
        + all_owner["primitive_geometry"]["m_2"]["leftover_z_circles"]
    )
    if len(pairs) != 44 or len(leftovers) != 227:
        raise AssertionError("selected primitive counts are not 44 plus 227")
    primitives = []
    for pair in pairs:
        primitives.append(
            {
                "role": "active_yz_corridor",
                "primitive_id": pair["primitive_id"],
                "owner": pair["owner"],
                "source_ids": [pair["y_source_id"], pair["z_source_id"]],
                "is_cyclic_m2_connector": (
                    pair["owner"] == "m_2"
                    and pair["y_source_id"] == "m_2:C_i"
                    and pair["z_source_id"] == "c1:letter:0"
                ),
                "connector_kind": pair["connector"]["kind"],
                "relative_twist": pair["product_framing"]["relative_twist"],
            }
        )
    for leftover in leftovers:
        primitives.append(
            {
                "role": "added_z_arc",
                "primitive_id": leftover["primitive_id"],
                "owner": leftover["owner"],
                "source_ids": [leftover["z_source_id"]],
                "is_cyclic_m2_connector": False,
                "connector_kind": "boundary_parallel_z_identity",
                "relative_twist": 0,
            }
        )
    left = [
        strand("left", index, Fraction(-7), Fraction(-3), primitive)
        for index, primitive in enumerate(primitives)
    ]
    right = [
        strand("right", index, Fraction(3), Fraction(7), primitive)
        for index, primitive in enumerate(primitives)
    ]
    result = {
        "schema": "t73_selected_canopolis_normal_form/v1",
        "dependencies": {
            "all_owner_primitives_sha256": all_owner["sha256"],
            "marked_vertical_collar_sha256": collar["sha256"],
        },
        "ambient": {
            "model": "R3 compactified to S3",
            "outer_chart": {
                "lower": ["-10", "-3", "-3"],
                "upper": ["10", "3", "3"],
            },
        },
        "closure_balls": [
            {
                "name": "left_closure",
                "lower": ["-9", "-2", "-2"],
                "upper": ["-1", "2", "2"],
                "boundary_is_separating_sphere": True,
            },
            {
                "name": "right_closure",
                "lower": ["1", "-2", "-2"],
                "upper": ["9", "2", "2"],
                "boundary_is_separating_sphere": True,
            },
        ],
        "insertion_balls": [
            box("Y_source", (-8, -1, -1), (-7, 1, 1), "left_closure", "T"),
            box("Z_target", (-3, -1, -1), (-2, 1, 1), "left_closure", "Z_prime"),
            box("Z_source", (2, -1, -1), (3, 1, 1), "right_closure", "Z"),
            box("Y_target", (7, -1, -1), (8, 1, 1), "right_closure", "T_prime"),
        ],
        "primitive_count": 271,
        "active_corridor_count": 44,
        "added_z_arc_count": 227,
        "primitives": primitives,
        "left_closure_strands": left,
        "right_closure_strands": right,
        "canopolis_operation": {
            "name": "J",
            "source": "C_44",
            "target": "C_271",
            "rule": "retain 44 active wickets and adjoin 227 boundary-parallel z identity arcs",
        },
        "two_representable_pattern": {
            "left": "Hom_z(J B T, Z_prime)",
            "right": "Hom_z(Z, J B T_prime)",
            "split_union": True,
            "relative_to_all_four_insertion_balls": True,
        },
        "cyclic_connector": {
            "owner": "m_2",
            "y_source_id": "m_2:C_i",
            "z_source_id": "c1:letter:0",
            "private_lane": next(
                index
                for index, primitive in enumerate(primitives)
                if primitive["is_cyclic_m2_connector"]
            ),
        },
        "product_normal": ["0", str(DELTA), "0"],
        "contains_braid_word": False,
        "scope": (
            "candidate selected-state target normal form only; no relative "
            "ambient isotopy from the actual coefficient exterior is asserted"
        ),
    }
    result["sha256"] = canonical_sha(
        {key: value for key, value in result.items() if key != "sha256"}
    )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"WROTE={OUTPUT}")
    print("T73_SELECTED_CANOPOLIS_NORMAL_FORM=BUILT")
    print(f"ACTIVE={result['active_corridor_count']}")
    print(f"ADDED_Z={result['added_z_arc_count']}")
    print(f"CYCLIC_LANE={result['cyclic_connector']['private_lane']}")
    print(f"SHA256={result['sha256']}")


if __name__ == "__main__":
    main()
