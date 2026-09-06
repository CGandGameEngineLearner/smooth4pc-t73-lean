#!/usr/bin/env python3
"""Small exact-rational convex-simplex predicates used by T73 verifiers."""

from __future__ import annotations

import itertools
from fractions import Fraction


def solve_square(matrix, right):
    size = len(matrix)
    rows = [
        [Fraction(value) for value in matrix[index]] + [Fraction(right[index])]
        for index in range(size)
    ]
    for column in range(size):
        pivot = next((row for row in range(column, size) if rows[row][column]), None)
        if pivot is None:
            return None
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


def affine_parameterization(first, second):
    columns = [
        tuple(first[index][axis] - first[0][axis] for axis in range(4))
        for index in (1, 2, 3)
    ] + [
        tuple(second[0][axis] - second[index][axis] for axis in range(4))
        for index in (1, 2, 3)
    ]
    right = tuple(second[0][axis] - first[0][axis] for axis in range(4))
    rows = [
        [Fraction(columns[column][row]) for column in range(6)] + [Fraction(right[row])]
        for row in range(4)
    ]
    pivots = []
    pivot_row = 0
    for column in range(6):
        pivot = next((row for row in range(pivot_row, 4) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        divisor = rows[pivot_row][column]
        rows[pivot_row] = [value / divisor for value in rows[pivot_row]]
        for row in range(4):
            if row == pivot_row or not rows[row][column]:
                continue
            multiplier = rows[row][column]
            rows[row] = [
                rows[row][index] - multiplier * rows[pivot_row][index]
                for index in range(7)
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == 4:
            break
    if any(
        not any(rows[row][column] for column in range(6)) and rows[row][6]
        for row in range(pivot_row, 4)
    ):
        return None
    free = [column for column in range(6) if column not in pivots]
    expressions = []
    for column in range(6):
        if column in free:
            coefficients = [Fraction(0)] * len(free)
            coefficients[free.index(column)] = Fraction(1)
            expressions.append((Fraction(0), coefficients))
        else:
            row = pivots.index(column)
            expressions.append(
                (rows[row][6], [-rows[row][free_column] for free_column in free])
            )
    return pivot_row, expressions


def tetrahedron_intersection_witness(first, second):
    parameterization = affine_parameterization(first, second)
    if parameterization is None:
        return None
    rank, expressions = parameterization
    dimension = 6 - rank
    constraints = list(expressions)
    for group in ((0, 1, 2), (3, 4, 5)):
        constraints.append(
            (
                Fraction(1)
                - sum((expressions[index][0] for index in group), Fraction(0)),
                [
                    -sum(
                        (expressions[index][1][axis] for index in group),
                        Fraction(0),
                    )
                    for axis in range(dimension)
                ],
            )
        )
    for active in itertools.combinations(range(8), dimension):
        free_values = solve_square(
            [constraints[index][1] for index in active],
            [-constraints[index][0] for index in active],
        )
        if free_values is None:
            continue
        if not all(
            constant
            + sum(
                (coefficient[axis] * free_values[axis] for axis in range(dimension)),
                Fraction(0),
            )
            >= 0
            for constant, coefficient in constraints
        ):
            continue
        parameters = [
            constant
            + sum(
                (coefficient[axis] * free_values[axis] for axis in range(dimension)),
                Fraction(0),
            )
            for constant, coefficient in expressions
        ]
        first_barycentric = [1 - sum(parameters[:3]), *parameters[:3]]
        second_barycentric = [1 - sum(parameters[3:]), *parameters[3:]]
        point = tuple(
            sum(first[index][axis] * first_barycentric[index] for index in range(4))
            for axis in range(4)
        )
        return {
            "affine_rank": rank,
            "free_dimension": dimension,
            "active_constraints": active,
            "first_barycentric": first_barycentric,
            "second_barycentric": second_barycentric,
            "point": point,
        }
    return None


def tetrahedra_intersect(first, second):
    return tetrahedron_intersection_witness(first, second) is not None
