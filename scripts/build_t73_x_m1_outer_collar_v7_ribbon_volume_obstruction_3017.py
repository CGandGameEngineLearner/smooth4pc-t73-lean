#!/usr/bin/env python3
"""Save an exact nonincident tetrahedron intersection in ribbon volume 3017."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOLUME = ROOT / "geometry/t73_x_m1_outer_collar_v7_ribbon_volume_3017.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v7_ribbon_volume_obstruction_3017.json"
TRANSITION = 7
TETRAHEDRA = (15, 22)


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def solve_square(matrix, right):
    size = len(matrix)
    rows = [
        [Fraction(value) for value in matrix[index]] + [Fraction(right[index])]
        for index in range(size)
    ]
    for column in range(size):
        pivot = next((row for row in range(column, size) if rows[row][column]), None)
        if pivot is None:
            raise AssertionError("obstruction active system is singular")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [value / divisor for value in rows[column]]
        for row in range(size):
            if row == column or not rows[row][column]:
                continue
            multiplier = rows[row][column]
            rows[row] = [
                rows[row][index] - multiplier * rows[column][index]
                for index in range(size + 1)
            ]
    return [rows[index][-1] for index in range(size)]


def build():
    volume = json.loads(VOLUME.read_text())
    payload = {key: value for key, value in volume.items() if key != "sha256"}
    if (
        volume["sha256"] != canonical_sha(payload)
        or volume["r4_volume_self_clearance_status"] != "OPEN"
    ):
        raise AssertionError("ribbon-volume obstruction input is stale or overclaimed")
    record = volume["transition_volumes"][TRANSITION]
    vertices = [point(value) for value in record["spacetime_vertices"]]
    first_ids, second_ids = (record["tetrahedra"][index] for index in TETRAHEDRA)
    if set(first_ids) & set(second_ids):
        raise AssertionError("claimed obstruction tetrahedra are incident")
    first = [vertices[index] for index in first_ids]
    second = [vertices[index] for index in second_ids]
    columns = [
        tuple(first[index][axis] - first[0][axis] for axis in range(4))
        for index in (1, 2, 3)
    ] + [
        tuple(second[0][axis] - second[index][axis] for axis in range(4))
        for index in (1, 2, 3)
    ]
    matrix = [[columns[column][row] for column in range(6)] for row in range(4)]
    right = [second[0][axis] - first[0][axis] for axis in range(4)]
    matrix.extend(
        (
            [
                Fraction(0),
                Fraction(1),
                Fraction(0),
                Fraction(0),
                Fraction(0),
                Fraction(0),
            ],
            [
                Fraction(0),
                Fraction(0),
                Fraction(0),
                Fraction(0),
                Fraction(1),
                Fraction(0),
            ],
        )
    )
    right.extend((Fraction(0), Fraction(0)))
    parameters = solve_square(matrix, right)
    first_barycentric = [1 - sum(parameters[:3]), *parameters[:3]]
    second_barycentric = [1 - sum(parameters[3:]), *parameters[3:]]
    if any(value < 0 for value in first_barycentric + second_barycentric):
        raise AssertionError("obstruction barycentric coordinates are not feasible")
    first_point = tuple(
        sum(first[index][axis] * first_barycentric[index] for index in range(4))
        for axis in range(4)
    )
    second_point = tuple(
        sum(second[index][axis] * second_barycentric[index] for index in range(4))
        for axis in range(4)
    )
    if first_point != second_point:
        raise AssertionError("obstruction barycentric points differ")
    result = {
        "schema": "t73_x_m1_outer_collar_v7_ribbon_volume_obstruction/v1",
        "ribbon_volume_sha256": volume["sha256"],
        "interface_index": 3017,
        "transition_index": TRANSITION,
        "tetrahedron_indices": list(TETRAHEDRA),
        "first_tetrahedron_vertex_indices": first_ids,
        "second_tetrahedron_vertex_indices": second_ids,
        "shared_vertex_count": 0,
        "active_constraint_indices": [1, 4],
        "first_barycentric_coordinates": [str(value) for value in first_barycentric],
        "second_barycentric_coordinates": [str(value) for value in second_barycentric],
        "intersection_point": [str(value) for value in first_point],
        "intersection_kind": "NONINCIDENT_R4_TETRAHEDRON_INTERSECTION",
        "normal_field_status": "RETAINED",
        "framed_one_skeleton_status": "RETAINED",
        "ribbon_volume_status": "CANDIDATE_REFUTED",
        "required_repair": "RETRIANGULATE_OR_REFINE_TRANSITION_7_RIBBON_VOLUME",
        "verdict": "REFUTED_X_M1_OUTER_COLLAR_V7_RIBBON_VOLUME_3017",
    }
    result["sha256"] = canonical_sha(result)
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
        raise AssertionError("ribbon-volume obstruction 3017 is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "transition": result["transition_index"],
                "tetrahedra": result["tetrahedron_indices"],
                "shared_vertices": result["shared_vertex_count"],
                "repair": result["required_repair"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
