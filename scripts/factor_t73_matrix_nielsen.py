#!/usr/bin/env python3
"""Factor the trace-73 matrix into exact elementary row/Nielsen moves."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
A = [[0, 269, 1240], [0, 41, 189], [1, 0, 32]]


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def identity() -> list[list[int]]:
    return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def apply(matrix: list[list[int]], op: dict[str, Any]) -> list[list[int]]:
    out = [row[:] for row in matrix]
    if op["kind"] == "swap":
        i, j = op["rows"]
        out[i], out[j] = out[j], out[i]
    elif op["kind"] == "add":
        target, source, coefficient = op["target"], op["source"], op["coefficient"]
        out[target] = [out[target][j] + coefficient * out[source][j] for j in range(3)]
    elif op["kind"] == "negate":
        row = op["row"]
        out[row] = [-x for x in out[row]]
    else:
        raise AssertionError(f"unknown operation {op}")
    return out


def inverse(op: dict[str, Any]) -> dict[str, Any]:
    if op["kind"] == "add":
        return {**op, "coefficient": -op["coefficient"]}
    return dict(op)


def reduction() -> list[dict[str, Any]]:
    matrix = [row[:] for row in A]
    operations: list[dict[str, Any]] = []
    for column in range(3):
        pivot = next((row for row in range(column, 3) if matrix[row][column] != 0), None)
        if pivot is None:
            raise AssertionError("singular matrix")
        if pivot != column:
            op = {"kind": "swap", "rows": [column, pivot]}
            matrix = apply(matrix, op)
            operations.append(op)
        for row in range(column + 1, 3):
            while matrix[row][column] != 0:
                coefficient = -(matrix[column][column] // matrix[row][column])
                if coefficient:
                    op = {"kind": "add", "target": column, "source": row, "coefficient": coefficient}
                    matrix = apply(matrix, op)
                    operations.append(op)
                op = {"kind": "swap", "rows": [column, row]}
                matrix = apply(matrix, op)
                operations.append(op)
        if matrix[column][column] == -1:
            op = {"kind": "negate", "row": column}
            matrix = apply(matrix, op)
            operations.append(op)
        if matrix[column][column] != 1:
            raise AssertionError(f"column {column} pivot is not a unit")
        for row in range(3):
            if row == column or matrix[row][column] == 0:
                continue
            op = {"kind": "add", "target": row, "source": column, "coefficient": -matrix[row][column]}
            matrix = apply(matrix, op)
            operations.append(op)
    if matrix != identity():
        raise AssertionError(f"integer reduction did not reach identity: {matrix}")
    return operations


def generate() -> dict[str, Any]:
    reduce_ops = reduction()
    construction_ops = [inverse(op) for op in reversed(reduce_ops)]
    matrix = identity()
    states = [matrix]
    for op in construction_ops:
        matrix = apply(matrix, op)
        states.append(matrix)
    if matrix != A:
        raise AssertionError("Nielsen construction does not reproduce A")
    witness: dict[str, Any] = {
        "schema": "t73_matrix_nielsen_factorization/v1",
        "matrix_A": A,
        "reduction_operations": reduce_ops,
        "construction_operations": construction_ops,
        "construction_states": states,
        "operation_count": len(construction_ops),
        "product_check": "PASS",
        "geometric_scope": "algebraic Nielsen candidate only; each operation still needs a handlebody-preserving PL local model",
    }
    witness["witness_sha256"] = canonical_sha(witness)
    return witness


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    generated = generate()
    if args.output:
        args.output.write_text(json.dumps(generated, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        print("T73_MATRIX_NIELSEN_FACTORIZATION=PASS")
        print(f"OPERATIONS={generated['operation_count']}")
        print(f"WITNESS_SHA256={generated['witness_sha256']}")
        return
    if not args.output:
        print(json.dumps(generated, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
