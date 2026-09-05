#!/usr/bin/env python3
"""Independently verify the first candidate framed band disk."""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SURFACE = ROOT / "geometry/t73_candidate_t_band0_surface.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def edge(first: int, second: int):
    return tuple(sorted((first, second)))


def triangle_nondegenerate(vertices, triangle) -> bool:
    origin, first, second = (vertices[index] for index in triangle)
    left = tuple(first[i] - origin[i] for i in range(4))
    right = tuple(second[i] - origin[i] for i in range(4))
    return any(
        left[j] * right[i] - left[i] * right[j] != 0
        for i in range(4) for j in range(i + 1, 4)
    )


def chain_edges(chain):
    return {edge(first, second) for first, second in zip(chain, chain[1:])}


def solve_square(matrix, rhs):
    augmented = [list(row) + [rhs[index]] for index, row in enumerate(matrix)]
    for column in range(len(matrix)):
        pivot = next((row for row in range(column, len(matrix)) if augmented[row][column]), None)
        if pivot is None:
            return None
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(len(matrix)):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [augmented[row][item] - factor * augmented[column][item] for item in range(len(matrix) + 1)]
    return [augmented[index][-1] for index in range(len(matrix))]


def solve_columns(columns, rhs):
    variable_count = len(columns)
    for axes in combinations(range(4), variable_count):
        matrix = [[columns[column][axis] for column in range(variable_count)] for axis in axes]
        solution = solve_square(matrix, [rhs[axis] for axis in axes])
        if solution is None:
            continue
        if all(sum(columns[column][axis] * solution[column] for column in range(variable_count)) == rhs[axis] for axis in range(4)):
            return solution
    return None


def point_in_triangle(value, triangle) -> bool:
    origin, first, second = triangle
    columns = [
        tuple(first[i] - origin[i] for i in range(4)),
        tuple(second[i] - origin[i] for i in range(4)),
    ]
    solution = solve_columns(columns, tuple(value[i] - origin[i] for i in range(4)))
    return solution is not None and solution[0] >= 0 and solution[1] >= 0 and sum(solution) <= 1


def segment_meets_triangle(segment, triangle) -> bool:
    start, end = segment
    origin, first, second = triangle
    columns = [
        tuple(end[i] - start[i] for i in range(4)),
        tuple(origin[i] - first[i] for i in range(4)),
        tuple(origin[i] - second[i] for i in range(4)),
    ]
    solution = solve_columns(columns, tuple(origin[i] - start[i] for i in range(4)))
    if solution is None:
        return False
    parameter, first_weight, second_weight = solution
    return 0 <= parameter <= 1 and first_weight >= 0 and second_weight >= 0 and first_weight + second_weight <= 1


def triangles_intersect(first, second):
    p, p1, p2 = first
    q, q1, q2 = second
    columns = [
        tuple(p1[i] - p[i] for i in range(4)),
        tuple(p2[i] - p[i] for i in range(4)),
        tuple(q[i] - q1[i] for i in range(4)),
        tuple(q[i] - q2[i] for i in range(4)),
    ]
    matrix = [[columns[column][row] for column in range(4)] for row in range(4)]
    solution = solve_square(matrix, tuple(q[i] - p[i] for i in range(4)))
    if solution is None:
        first_edges = [(first[i], first[(i + 1) % 3]) for i in range(3)]
        second_edges = [(second[i], second[(i + 1) % 3]) for i in range(3)]
        return (
            any(segment_meets_triangle(segment, second) for segment in first_edges)
            or any(segment_meets_triangle(segment, first) for segment in second_edges)
            or any(point_in_triangle(vertex, second) for vertex in first)
            or any(point_in_triangle(vertex, first) for vertex in second)
        )
    a, b, c, d = solution
    return a >= 0 and b >= 0 and a + b <= 1 and c >= 0 and d >= 0 and c + d <= 1


def verify() -> dict:
    data = json.loads(SURFACE.read_text(encoding="utf-8"))
    if data["completion_status"] != "CANDIDATE_FRAMED_BAND_DISK":
        raise AssertionError("candidate band-disk status changed")
    vertices = [point(value) for value in data["vertices"]]
    triangles = data["triangles"]
    if any(not triangle_nondegenerate(vertices, triangle) for triangle in triangles):
        raise AssertionError("candidate band disk has a degenerate triangle")
    edge_counts = Counter(
        edge(triangle[i], triangle[(i + 1) % 3])
        for triangle in triangles for i in range(3)
    )
    if set(edge_counts.values()) - {1, 2}:
        raise AssertionError("candidate band disk is not a triangle manifold")
    boundary_edges = {item for item, count in edge_counts.items() if count == 1}
    boundary = data["boundary"]
    expected_boundary = {
        edge(*boundary["source_attachment"]),
        edge(*boundary["target_attachment"]),
        *chain_edges(boundary["left_lane"]),
        *chain_edges(boundary["right_lane"]),
    }
    if boundary_edges != expected_boundary:
        raise AssertionError("candidate band-disk boundary decomposition changed")
    euler = len(vertices) - len(edge_counts) + len(triangles)
    if euler != 1:
        raise AssertionError("candidate band surface is not a disk")
    numeric = np.array([[float(value) for value in vertex] for vertex in vertices])
    exact_triangle_checks = 0
    for first_index, first_ids in enumerate(triangles):
        for second_index in range(first_index + 1, len(triangles)):
            second_ids = triangles[second_index]
            if set(first_ids) & set(second_ids):
                continue
            first_box = numeric[first_ids]
            second_box = numeric[second_ids]
            if np.any(first_box.max(axis=0) < second_box.min(axis=0)) or np.any(second_box.max(axis=0) < first_box.min(axis=0)):
                continue
            exact_triangle_checks += 1
            intersection = triangles_intersect(
                tuple(vertices[index] for index in first_ids),
                tuple(vertices[index] for index in second_ids),
            )
            if intersection:
                raise AssertionError(f"candidate band triangles {first_index},{second_index} intersect")
    normals = [point(value) for value in data["normal_field"]]
    push_vertices = [point(value) for value in data["push_off_vertices"]]
    if len(normals) != len(vertices) or len(push_vertices) != len(vertices):
        raise AssertionError("candidate band framing arrays have the wrong length")
    for vertex, normal, pushed in zip(vertices, normals, push_vertices):
        if not any(normal):
            raise AssertionError("candidate band disk has a zero normal")
        if tuple(vertex[i] + normal[i] for i in range(4)) != pushed:
            raise AssertionError("candidate band push-off is not vertex plus normal")
    return {
        "verdict": "PASS_CANDIDATE_FRAMED_BAND_DISK_LOCAL_EMBEDDEDNESS_ONLY",
        "vertices": len(vertices),
        "triangles": len(triangles),
        "boundary_edges": len(boundary_edges),
        "euler_characteristic": euler,
        "exact_triangle_checks": exact_triangle_checks,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
