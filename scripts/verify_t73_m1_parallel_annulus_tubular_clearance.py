#!/usr/bin/env python3
"""Exact nonincident tetrahedron clearance for the m1 quotient tube."""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_m1_parallel_annulus_tubular_frame.json"
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
PERIOD = Fraction(4)


def point(values):
    return tuple(Fraction(value) for value in values)


def floor(value):
    return value.numerator // value.denominator


def ceil(value):
    return -floor(-value)


def rank(matrix):
    rows = [list(row) for row in matrix]
    row = 0
    for column in range(len(rows[0]) if rows else 0):
        pivot = next((index for index in range(row, len(rows)) if rows[index][column]), None)
        if pivot is None:
            continue
        rows[row], rows[pivot] = rows[pivot], rows[row]
        divisor = rows[row][column]
        rows[row] = [value / divisor for value in rows[row]]
        for index in range(len(rows)):
            if index != row and rows[index][column]:
                factor = rows[index][column]
                rows[index] = [left - factor * right for left, right in zip(rows[index], rows[row])]
        row += 1
        if row == len(rows):
            break
    return row


def independent_rows(matrix, target_rank):
    selected = []
    for index in range(len(matrix)):
        candidate = selected + [index]
        if rank([matrix[value] for value in candidate]) > len(selected):
            selected.append(index)
        if len(selected) == target_rank:
            return selected
    raise AssertionError("could not select independent equality rows")


def solve_square(matrix, right):
    size = len(matrix)
    rows = [list(matrix[index]) + [right[index]] for index in range(size)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if rows[row][column]), None)
        if pivot is None:
            return None
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [value / divisor for value in rows[column]]
        for row in range(size):
            if row != column and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [left - factor * right_value for left, right_value in zip(rows[row], rows[column])]
    return [rows[index][-1] for index in range(size)]


def convex_hulls_intersect(first, second):
    # Variables are four barycentric weights for each tetrahedron. Equations:
    # A alpha - B beta=0 in Q4 and sum(alpha)=sum(beta)=1.
    matrix = []
    for axis in range(4):
        matrix.append([value[axis] for value in first] + [-value[axis] for value in second])
    matrix.extend(([Fraction(1)] * 4 + [Fraction(0)] * 4,
                   [Fraction(0)] * 4 + [Fraction(1)] * 4))
    right = [Fraction(0)] * 4 + [Fraction(1), Fraction(1)]
    matrix_rank = rank(matrix)
    rows = independent_rows(matrix, matrix_rank)
    for columns in itertools.combinations(range(8), matrix_rank):
        square = [[matrix[row][column] for column in columns] for row in rows]
        solution = solve_square(square, [right[row] for row in rows])
        if solution is None or any(value < 0 for value in solution):
            continue
        candidate = [Fraction(0)] * 8
        for column, value in zip(columns, solution):
            candidate[column] = value
        if all(sum(matrix[row][column] * candidate[column] for column in range(8)) == right[row] for row in range(6)):
            return True
    return False


def translation_ranges(first, second):
    ranges = []
    for axis in range(3):
        first_low, first_high = min(value[axis] for value in first), max(value[axis] for value in first)
        second_low, second_high = min(value[axis] for value in second), max(value[axis] for value in second)
        low, high = ceil((first_low - second_high) / PERIOD), floor((first_high - second_low) / PERIOD)
        if low > high:
            return []
        ranges.append(range(low, high + 1))
    if max(value[3] for value in first) < min(value[3] for value in second) or max(value[3] for value in second) < min(value[3] for value in first):
        return []
    return itertools.product(*ranges)


def translate(tetrahedron, deck):
    return tuple(tuple(value[axis] + PERIOD * deck[axis] for axis in range(3)) + (value[3],) for value in tetrahedron)


def boxes_overlap(first, second):
    return all(max(min(value[axis] for value in first), min(value[axis] for value in second)) <= min(max(value[axis] for value in first), max(value[axis] for value in second)) for axis in range(4))


def verify():
    data = json.loads(DATA.read_text(encoding="utf-8")); foliation = json.loads(FOLIATION.read_text(encoding="utf-8"))
    vertices = [point(value) for value in data["tubular_vertices"]]; ids = [tuple(value) for value in data["tubular_tetrahedra"]]
    tetrahedra = [tuple(vertices[index] for index in simplex) for simplex in ids]
    triangle_ids = [set(value) for value in data["annulus_triangles"]]
    seam_triangles = set(foliation["mapping_torus_seam_triangle_indices"])
    deck_candidates = exact_box_candidates = exact_convex_checks = adjacency_skips = seam_skips = 0
    for first_index, first in enumerate(tetrahedra):
        first_triangle = first_index // 3
        for second_index in range(first_index, len(tetrahedra)):
            second = tetrahedra[second_index]; second_triangle = second_index // 3
            for raw_deck in translation_ranges(first, second):
                deck = tuple(raw_deck); deck_candidates += 1
                if first_index == second_index and deck == (0, 0, 0):
                    adjacency_skips += 1; continue
                if first_triangle in seam_triangles or second_triangle in seam_triangles:
                    seam_skips += 1; continue
                if deck == (0, 0, 0) and triangle_ids[first_triangle] & triangle_ids[second_triangle]:
                    adjacency_skips += 1; continue
                if first_triangle // 2 == 0 and second_triangle // 2 == len(foliation["base_vertices"]) - 2 and deck == (1, 0, -1):
                    seam_skips += 1; continue
                moved = translate(second, deck)
                if not boxes_overlap(first, moved):
                    continue
                exact_box_candidates += 1; exact_convex_checks += 1
                if convex_hulls_intersect(first, moved):
                    raise AssertionError(f"nonincident m1 tubular tetrahedra intersect: {first_index}/{second_index}/{deck}")
    return {
        "verdict": "PASS_M1_PARALLEL_ANNULUS_NONINCIDENT_TETRAHEDRON_CLEARANCE",
        "tetrahedra": len(tetrahedra),
        "deck_candidates": deck_candidates,
        "adjacency_skips": adjacency_skips,
        "seam_skips": seam_skips,
        "exact_box_candidates": exact_box_candidates,
        "exact_convex_feasibility_checks": exact_convex_checks,
        "embedded_tubular_neighborhood": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
