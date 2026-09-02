#!/usr/bin/env python3
"""Factor the T73 sphere-coordinate matrix into geometric Nielsen moves."""

from __future__ import annotations

import hashlib
import json
from typing import Any


SPHERE_COLUMNS = [
    [-1311, -189, 41],
    [8608, 1241, -269],
    [-1, 0, 1],
]


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def identity(size: int) -> list[list[int]]:
    return [[int(row == column) for column in range(size)] for row in range(size)]


def apply(matrix: list[list[int]], operation: dict[str, int | str]) -> None:
    kind = operation["kind"]
    if kind == "swap":
        left = int(operation["left"])
        right = int(operation["right"])
        matrix[left], matrix[right] = matrix[right], matrix[left]
    elif kind == "negate":
        row = int(operation["row"])
        matrix[row] = [-value for value in matrix[row]]
    elif kind == "add":
        target = int(operation["target"])
        source = int(operation["source"])
        multiple = int(operation["multiple"])
        matrix[target] = [
            value + multiple * addend
            for value, addend in zip(matrix[target], matrix[source])
        ]
    else:
        raise ValueError(f"unknown operation: {kind}")


def inverse_operation(operation: dict[str, int | str]) -> dict[str, int | str]:
    if operation["kind"] in ("swap", "negate"):
        return dict(operation)
    result = dict(operation)
    result["multiple"] = -int(result["multiple"])
    return result


def reduction_operations(matrix: list[list[int]]) -> list[dict[str, int | str]]:
    work = [row[:] for row in matrix]
    size = len(work)
    operations: list[dict[str, int | str]] = []

    def record(operation: dict[str, int | str]) -> None:
        apply(work, operation)
        operations.append(operation)

    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            raise ValueError("matrix is singular")
        if pivot != column:
            record({"kind": "swap", "left": column, "right": pivot})

        for row in range(column + 1, size):
            while work[row][column] != 0:
                a = work[column][column]
                b = work[row][column]
                quotient = a // b
                if quotient:
                    record(
                        {
                            "kind": "add",
                            "target": column,
                            "source": row,
                            "multiple": -quotient,
                        }
                    )
                record({"kind": "swap", "left": column, "right": row})

        if work[column][column] == -1:
            record({"kind": "negate", "row": column})
        if work[column][column] != 1:
            raise ValueError("matrix is not unimodular")

        for row in range(size):
            if row == column:
                continue
            coefficient = work[row][column]
            if coefficient:
                record(
                    {
                        "kind": "add",
                        "target": row,
                        "source": column,
                        "multiple": -coefficient,
                    }
                )

    if work != identity(size):
        raise AssertionError(f"integer reduction did not reach identity: {work}")
    return operations


def generate_ledger() -> dict[str, Any]:
    reduction = reduction_operations(SPHERE_COLUMNS)
    reconstruction = [inverse_operation(operation) for operation in reversed(reduction)]

    check = identity(3)
    for operation in reconstruction:
        apply(check, operation)
    if check != SPHERE_COLUMNS:
        raise AssertionError("reverse Nielsen program does not reconstruct C")

    ledger = {
        "schema": "t73_sphere_basis_nielsen_ledger/v1",
        "sphere_coordinate_matrix": SPHERE_COLUMNS,
        "determinant": 1,
        "reduction_to_identity": reduction,
        "construction_from_standard_basis": reconstruction,
        "operation_count": len(reconstruction),
        "geometric_dictionary": {
            "swap": "permute two standard nonseparating spheres/dual 1-handles",
            "negate": "reverse the orientation of one sphere",
            "add": "sphere slide; add the stated multiple of the source class",
        },
        "ambient": "#^3(S^1 x S^2), away from a chosen detector collar",
        "consequence": (
            "images of the standard sphere system are embedded, framed, "
            "pairwise disjoint and have the displayed coordinate columns"
        ),
    }
    ledger["ledger_sha256"] = canonical_sha(ledger)
    return ledger


def main() -> None:
    print(json.dumps(generate_ledger(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
