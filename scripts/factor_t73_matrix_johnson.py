#!/usr/bin/env python3
"""Factor A using only determinant-one transvections alpha_ij."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
A = [[0, 269, 1240], [0, 41, 189], [1, 0, 32]]


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def add_op(target: int, source: int, coefficient: int):
    return {"kind": "add", "target": target, "source": source, "coefficient": coefficient}


def signed_swap_ops(first: int, second: int):
    # (a,b) -> (a+b,b) -> (a+b,-a) -> (b,-a).
    return [add_op(first, second, 1), add_op(second, first, -1), add_op(first, second, 1)]


def pair_negate_ops(first: int, second: int):
    return signed_swap_ops(first, second) + signed_swap_ops(first, second)


def apply(matrix: list[list[int]], operation: dict[str, Any]):
    out = [row[:] for row in matrix]
    target, source, coefficient = operation["target"], operation["source"], operation["coefficient"]
    out[target] = [out[target][j] + coefficient * out[source][j] for j in range(3)]
    return out


def apply_all(matrix, operations):
    out = [row[:] for row in matrix]
    for operation in operations:
        out = apply(out, operation)
    return out


def reduction_ops():
    matrix = [row[:] for row in A]
    operations = []

    def perform(ops):
        nonlocal matrix
        for operation in ops:
            matrix = apply(matrix, operation)
            operations.append(operation)

    for column in range(3):
        pivot = next((row for row in range(column, 3) if matrix[row][column]), None)
        if pivot is None:
            raise AssertionError("singular matrix")
        if pivot != column:
            perform(signed_swap_ops(column, pivot))
        for row in range(column + 1, 3):
            while matrix[row][column] != 0:
                coefficient = -(matrix[column][column] // matrix[row][column])
                if coefficient:
                    perform([add_op(column, row, coefficient)])
                perform(signed_swap_ops(column, row))
        if matrix[column][column] == -1:
            partner = column + 1 if column < 2 else None
            if partner is None:
                raise AssertionError("last pivot is negative despite determinant one")
            perform(pair_negate_ops(column, partner))
        if matrix[column][column] != 1:
            raise AssertionError(f"non-unit pivot in column {column}: {matrix}")
        for row in range(3):
            if row != column and matrix[row][column]:
                perform([add_op(row, column, -matrix[row][column])])
    identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    if matrix != identity:
        raise AssertionError(f"transvection reduction failed: {matrix}")
    return operations


def inverse(operation):
    return {**operation, "coefficient": -operation["coefficient"]}


def generate():
    reduction = reduction_ops()
    construction = [inverse(operation) for operation in reversed(reduction)]
    identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    if apply_all(identity, construction) != A:
        raise AssertionError("Johnson transvections do not reconstruct A")
    unit_moves = []
    for operation_index, operation in enumerate(construction):
        sign = 1 if operation["coefficient"] > 0 else -1
        for repetition in range(abs(operation["coefficient"])):
            unit_moves.append({
                "operation_index": operation_index,
                "repetition": repetition,
                "alpha_target": operation["source"],
                "alpha_prefix": operation["target"],
                "power": sign,
                "matrix_operation": operation,
            })
    result = {
        "schema": "t73_johnson_alpha_factorization/v1",
        "matrix_A": A,
        "reduction_transvections": reduction,
        "construction_transvections": construction,
        "unit_alpha_moves": unit_moves,
        "compressed_move_count": len(construction),
        "unit_alpha_move_count": len(unit_moves),
        "matrix_product_status": "PASS",
        "geometric_source": "Johnson alpha_ij: isotope the xi-xj square diagonal to follow xj then xi",
    }
    result["witness_sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.check:
        print("T73_JOHNSON_ALPHA_FACTORIZATION=PASS")
        print(f"COMPRESSED_MOVES={result['compressed_move_count']}")
        print(f"UNIT_ALPHA_MOVES={result['unit_alpha_move_count']}")
        print(f"WITNESS_SHA256={result['witness_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
