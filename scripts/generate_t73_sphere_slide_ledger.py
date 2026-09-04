#!/usr/bin/env python3
"""Factor the T73 sphere-coordinate matrix into geometric Nielsen moves."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PSI = ROOT / "geometry" / "t73_psi_A.json"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def identity(size: int) -> list[list[int]]:
    return [[int(row == column) for column in range(size)] for row in range(size)]


def det3(matrix: list[list[int]]) -> int:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def inverse_transpose_unimodular(matrix: list[list[int]]) -> list[list[int]]:
    det = det3(matrix)
    if det != 1:
        raise AssertionError("psi_A homology matrix is not orientation-unimodular")
    a = matrix
    # Cofactor matrix is A^{-T} when det(A)=1.
    return [
        [a[1][1] * a[2][2] - a[1][2] * a[2][1], -(a[1][0] * a[2][2] - a[1][2] * a[2][0]), a[1][0] * a[2][1] - a[1][1] * a[2][0]],
        [-(a[0][1] * a[2][2] - a[0][2] * a[2][1]), a[0][0] * a[2][2] - a[0][2] * a[2][0], -(a[0][0] * a[2][1] - a[0][1] * a[2][0])],
        [a[0][1] * a[1][2] - a[0][2] * a[1][1], -(a[0][0] * a[1][2] - a[0][2] * a[1][0]), a[0][0] * a[1][1] - a[0][1] * a[1][0]],
    ]


def derive_sphere_columns(matrix_a: list[list[int]]) -> tuple[list[list[int]], list[list[int]]]:
    wedge2_a = inverse_transpose_unimodular(matrix_a)
    columns = [
        [int(i == j) - wedge2_a[i][j] for j in range(3)]
        for i in range(3)
    ]
    return wedge2_a, columns


# Compatibility name for downstream tests and ledgers; its value is derived
# from the committed actual psi_A matrix rather than frozen literal entries.
_INITIAL_PSI = json.loads(PSI.read_text(encoding="utf-8"))
_INITIAL_WEDGE2, SPHERE_COLUMNS = derive_sphere_columns(_INITIAL_PSI["matrix_A"])


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
    psi = json.loads(PSI.read_text(encoding="utf-8"))
    matrix_a = psi["matrix_A"]
    wedge2_a, sphere_columns = derive_sphere_columns(matrix_a)
    if det3(sphere_columns) != 1:
        raise AssertionError("I-wedge^2(A) is not unimodular")
    reduction = reduction_operations(sphere_columns)
    reconstruction = [inverse_operation(operation) for operation in reversed(reduction)]

    check = identity(3)
    for operation in reconstruction:
        apply(check, operation)
    if check != sphere_columns:
        raise AssertionError("reverse Nielsen program does not reconstruct C")

    ledger = {
        "schema": "t73_sphere_basis_nielsen_ledger/v1",
        "psi_A_sha256": psi["sha256"],
        "matrix_A": matrix_a,
        "wedge2_A_equals_A_inverse_transpose": wedge2_a,
        "sphere_coordinate_rule": "I - wedge^2(A)",
        "sphere_coordinate_matrix": sphere_columns,
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
