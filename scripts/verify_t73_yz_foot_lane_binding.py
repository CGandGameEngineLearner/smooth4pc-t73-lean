#!/usr/bin/env python3
"""Independently verify the Johnson y/z belt and Figure-2a foot bindings."""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_yz_foot_lane_binding.json"
FEET = ROOT / "geometry/t73_ar_foot_pairing_model.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
X_DELETION = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def matrix_apply(matrix, value):
    return tuple(
        sum(Fraction(entry) * coordinate for entry, coordinate in zip(row, value))
        for row in matrix
    )


def determinant3(matrix):
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def edge(first, second):
    return tuple(sorted((first, second)))


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    feet = json.loads(FEET.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    x_deletion = json.loads(X_DELETION.read_text(encoding="utf-8"))
    if data["completion_status"] != "YZ_JOHNSON_BASE_LANES_ACTUALLY_BOUND_HYBRID_Z_REPLACEMENTS_OPEN":
        raise AssertionError("y/z foot binding scope changed")
    if data["ar_foot_model_sha256"] != feet["sha256"] or data["johnson_spine_embedding_sha256"] != spine["sha256"] or data["post_x_m1_deletion_sha256"] != x_deletion["sha256"]:
        raise AssertionError("y/z foot binding has stale sources")
    foot_by_index = {item["handle_index"]: item for item in feet["feet"]}
    total_passages = 0
    reflection_checks = 0
    for handle in data["handles"]:
        foot = foot_by_index[handle["foot_handle_index"]]
        matrix = [[Fraction(value) for value in row] for row in foot["reflection_matrix"]]
        if determinant3(matrix) != -1:
            raise AssertionError("foot pairing is not orientation reversing")
        identity = [[Fraction(int(row == column)) for column in range(3)] for row in range(3)]
        square = [
            [sum(matrix[row][middle] * matrix[middle][column] for middle in range(3)) for column in range(3)]
            for row in range(3)
        ]
        if square != identity:
            raise AssertionError("foot reflection is not an involution")
        positive_center = point(foot["positive_center"])
        negative_center = point(foot["negative_center"])
        if matrix_apply(matrix, positive_center) != negative_center:
            raise AssertionError("foot reflection does not exchange centers")
        for tangent in [point(value) for value in handle["tangent_basis"]]:
            if matrix_apply(matrix, tangent) != tangent:
                raise AssertionError("declared foot tangent basis is not fixed")

        arcs = {
            item["arc_id"]: item
            for item in spine["handle_arcs"]
            if item["axis"] == handle["generator_axis"]
        }
        if set(arcs) != {item["arc_id"] for item in handle["passages"]}:
            raise AssertionError("foot passages do not cover the Johnson handle arcs")
        endpoint_pairs = set()
        for passage in handle["passages"]:
            arc = arcs[passage["arc_id"]]
            polyline = [point(value) for value in arc["lift_polyline"]]
            transverse_axes = [axis for axis in range(3) if axis != handle["generator_axis"]]
            expected_belt = tuple(polyline[1][axis] for axis in transverse_axes) + (Fraction(1),)
            if point(passage["belt_point"]) != expected_belt or passage["orientation"] != arc["sign"]:
                raise AssertionError("Johnson arc/belt point binding changed")
            positive = point(passage["positive_foot_endpoint"])
            negative = point(passage["negative_foot_endpoint"])
            if matrix_apply(matrix, positive) != negative:
                raise AssertionError("passage endpoints are not reflection paired")
            radius = Fraction(foot["radius"])
            if sum((positive[index] - positive_center[index]) ** 2 for index in range(3)) >= radius**2:
                raise AssertionError("positive passage endpoint left its foot disk")
            pair = (negative, positive)
            if pair in endpoint_pairs:
                raise AssertionError("two Johnson passages share a foot endpoint pair")
            endpoint_pairs.add(pair)
            reflection_checks += 1
        belt = handle["belt_sphere"]
        edge_counts = Counter(
            edge(triangle[index], triangle[(index + 1) % 3])
            for triangle in belt["triangles"]
            for index in range(3)
        )
        if len(belt["vertices"]) - len(edge_counts) + len(belt["triangles"]) != 2 or set(edge_counts.values()) != {2}:
            raise AssertionError("y/z cubical belt is not a triangulated sphere")
        total_passages += len(handle["passages"])
    if [item["passage_count"] for item in data["handles"]] != [230, 33]:
        raise AssertionError("y/z passage counts changed")
    if x_deletion["deletion"]["remaining_one_handles"] != ["y", "z"]:
        raise AssertionError("post-x-cancel handle inventory changed")
    return {
        "verdict": "PASS_YZ_JOHNSON_BASE_LANE_FOOT_BINDINGS",
        "handles": 2,
        "y_passages": 230,
        "z_passages": 33,
        "reflection_pair_checks": reflection_checks,
        "total_passages": total_passages,
        "scope": "BASE_JOHNSON_LANES_ONLY_HYBRID_Z_REPLACEMENTS_OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
