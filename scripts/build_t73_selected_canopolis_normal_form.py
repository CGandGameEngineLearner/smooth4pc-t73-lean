#!/usr/bin/env python3
"""Build the complete rational target template for the selected C state.

This is a target canopolis template, not a claimed relative isotopy from the
actual AR coefficient exterior. Each representable closure has 88 active
Y--Z arcs and 227 boundary-parallel Z--Z arcs. The latter have two Z endpoints
each, so the four insertion balls carry 88, 542, 542, and 88 endpoints.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PRIMITIVES = ROOT / "geometry" / "t73_all_owner_product_primitives.json"
COLLAR = ROOT / "geometry" / "t73_p0_marked_vertical_collar.json"
OUTPUT = ROOT / "geometry" / "t73_selected_canopolis_normal_form.json"
DELTA = Fraction(1, 10**7)


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def encode(point) -> list[str]:
    return [str(Fraction(value)) for value in point]


def add(a, b):
    return tuple(a[index] + b[index] for index in range(3))


def endpoint_grid(count: int) -> list[tuple[Fraction, Fraction]]:
    """A common exact grid; its first 88 points are the active lanes."""
    columns = math.isqrt(count)
    if columns * columns < count:
        columns += 1
    rows = (count + columns - 1) // columns
    return [
        (
            Fraction(-9, 10)
            + Fraction(9, 5) * Fraction(index % columns + 1, columns + 1),
            Fraction(-9, 10)
            + Fraction(9, 5) * Fraction(index // columns + 1, rows + 1),
        )
        for index in range(count)
    ]


def box(name, lower, upper, closure, variable, face_x, endpoint_count):
    return {
        "name": name,
        "lower": encode(lower),
        "upper": encode(upper),
        "closure": closure,
        "variable": variable,
        "parametrized": True,
        "designated_face_axis": "x",
        "designated_face_value": str(Fraction(face_x)),
        "endpoint_count": endpoint_count,
        "endpoints": [],
    }


def endpoint(ball, index, point, role, primitive_id, side):
    endpoint_id = f"{side}:{ball['name']}:endpoint:{index}"
    record = {
        "endpoint_id": endpoint_id,
        "index": index,
        "role": role,
        "primitive_id": primitive_id,
        "point": encode(point),
        "positive_push_off_point": encode(add(point, (0, 0, DELTA))),
    }
    ball["endpoints"].append(record)
    return record


def framed_strand(side, index, primitive, endpoint_records, vertices):
    pushed = [add(point, (0, 0, DELTA)) for point in vertices]
    endpoint_records[0]["oriented_incidence"] = "initial"
    endpoint_records[1]["oriented_incidence"] = "terminal"
    return {
        "index": index,
        "side": side,
        "role": primitive["role"],
        "primitive_id": primitive["primitive_id"],
        "owner": primitive["owner"],
        "source_ids": primitive["source_ids"],
        "is_cyclic_m2_connector": primitive["is_cyclic_m2_connector"],
        "endpoint_ids": [item["endpoint_id"] for item in endpoint_records],
        "orientation": {
            "direction": "listed_vertex_order",
            "from_endpoint_id": endpoint_records[0]["endpoint_id"],
            "to_endpoint_id": endpoint_records[1]["endpoint_id"],
            "ribbon_side": primitive["ribbon_side"],
        },
        "centerline": [encode(point) for point in vertices],
        "product_normal": ["0", "0", str(DELTA)],
        "positive_push_off": [encode(point) for point in pushed],
        "relative_twist": 0,
    }


def build_closure(side, y_ball, z_ball, primitives):
    grid = endpoint_grid(542)
    y_x = Fraction(y_ball["designated_face_value"])
    z_x = Fraction(z_ball["designated_face_value"])
    y_points = [(y_x, y, z) for y, z in grid[:88]]
    z_points = [(z_x, y, z) for y, z in grid]
    records = []

    for index, primitive in enumerate(primitives[:88]):
        y_endpoint = endpoint(
            y_ball, index, y_points[index], "active_y", primitive["primitive_id"], side
        )
        z_endpoint = endpoint(
            z_ball, index, z_points[index], "active_z", primitive["primitive_id"], side
        )
        if side == "left":
            ends, vertices = [y_endpoint, z_endpoint], [y_points[index], z_points[index]]
        else:
            ends, vertices = [z_endpoint, y_endpoint], [z_points[index], y_points[index]]
        records.append(framed_strand(side, index, primitive, ends, vertices))

    direction = Fraction(-1) if side == "left" else Fraction(1)
    for residual_index, primitive in enumerate(primitives[88:]):
        first_index = 88 + 2 * residual_index
        second_index = first_index + 1
        first_point, second_point = z_points[first_index], z_points[second_index]
        first = endpoint(
            z_ball,
            first_index,
            first_point,
            "residual_z_start",
            primitive["primitive_id"],
            side,
        )
        second = endpoint(
            z_ball,
            second_index,
            second_point,
            "residual_z_end",
            primitive["primitive_id"],
            side,
        )
        depth = z_x + direction * (
            Fraction(1, 4) + Fraction(residual_index + 1, 1000)
        )
        vertices = [
            first_point,
            (depth, first_point[1], first_point[2]),
            (depth, second_point[1], second_point[2]),
            second_point,
        ]
        records.append(
            framed_strand(
                side, 88 + residual_index, primitive, [first, second], vertices
            )
        )
    return records


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
        for ribbon_side in ("negative_boundary", "positive_boundary"):
            primitives.append(
                {
                    "role": "active_yz_corridor",
                    "primitive_id": f"{pair['primitive_id']}:{ribbon_side}",
                    "base_primitive_id": pair["primitive_id"],
                    "ribbon_side": ribbon_side,
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
                "base_primitive_id": leftover["primitive_id"],
                "ribbon_side": "z_identity",
                "owner": leftover["owner"],
                "source_ids": [leftover["z_source_id"]],
                "is_cyclic_m2_connector": False,
                "connector_kind": "boundary_parallel_z_identity",
                "relative_twist": 0,
            }
        )

    insertion_balls = [
        box(
            "Y_source", (-8, -1, -1), (-7, 1, 1), "left_closure", "T", -7, 88
        ),
        box(
            "Z_target",
            (-3, -1, -1),
            (-2, 1, 1),
            "left_closure",
            "Z_prime",
            -3,
            542,
        ),
        box(
            "Z_source", (2, -1, -1), (3, 1, 1), "right_closure", "Z", 3, 542
        ),
        box(
            "Y_target",
            (7, -1, -1),
            (8, 1, 1),
            "right_closure",
            "T_prime",
            7,
            88,
        ),
    ]
    by_name = {item["name"]: item for item in insertion_balls}
    left = build_closure(
        "left", by_name["Y_source"], by_name["Z_target"], primitives
    )
    right = build_closure(
        "right", by_name["Y_target"], by_name["Z_source"], primitives
    )
    result = {
        "schema": "t73_selected_canopolis_normal_form/v2",
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
        "insertion_balls": insertion_balls,
        "endpoint_counts_per_insertion_ball": {
            item["name"]: len(item["endpoints"]) for item in insertion_balls
        },
        "total_boundary_endpoint_count": sum(
            len(item["endpoints"]) for item in insertion_balls
        ),
        "primitive_count": 315,
        "active_corridor_count_per_closure": 88,
        "added_z_arc_count_per_closure": 227,
        "target_strand_count": 630,
        "primitives": primitives,
        "left_closure_strands": left,
        "right_closure_strands": right,
        "canopolis_operation": {
            "name": "J",
            "source": "C_44",
            "target": "C_271",
            "rule": "retain both boundary sides of 44 active ribbons and adjoin 227 boundary-parallel z identity arcs",
        },
        "two_representable_pattern": {
            "left": "Hom_z(J B T, Z_prime)",
            "right": "Hom_z(Z, J B T_prime)",
            "split_union_as_abstract_target_template": True,
            "relative_source_isotopy_claimed": False,
        },
        "cyclic_connector": {
            "owner": "m_2",
            "y_source_id": "m_2:C_i",
            "z_source_id": "c1:letter:0",
            "primitive_indices": [
                index
                for index, primitive in enumerate(primitives)
                if primitive["is_cyclic_m2_connector"]
            ],
        },
        "product_normal": ["0", "0", str(DELTA)],
        "contains_braid_word": False,
        "scope": (
            "complete candidate target template only; the eight wrong-side source "
            "connectors forbid interpreting it as a literal relative ambient-isotopy target"
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
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"WROTE={OUTPUT}")
    print("T73_SELECTED_CANOPOLIS_NORMAL_FORM=BUILT")
    print(f"ENDPOINTS={result['endpoint_counts_per_insertion_ball']}")
    print(f"STRANDS={result['target_strand_count']}")
    print(f"CYCLIC_PRIMITIVES={result['cyclic_connector']['primitive_indices']}")
    print(f"SHA256={result['sha256']}")


if __name__ == "__main__":
    main()
