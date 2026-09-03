#!/usr/bin/env python3
"""Generate the paired Heegaard Nielsen movie induced by the A factorization.

For each elementary action M on the H_B spine, the dual H_D action is
(M^{-1})^T.  The script verifies the perfect intersection pairing after each
step.  It is a combinatorial handle-slide movie; explicit PL support balls and
bands remain a separate gate.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


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


def transpose(m: list[list[int]]) -> list[list[int]]:
    return [[m[j][i] for j in range(3)] for i in range(3)]


def matmul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def det3(m: list[list[int]]) -> int:
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def inverse3(m: list[list[int]]) -> list[list[int]]:
    determinant = det3(m)
    if determinant not in (-1, 1):
        raise AssertionError("elementary factor is not unimodular")
    cofactors = []
    for i in range(3):
        row = []
        for j in range(3):
            rows = [r for r in range(3) if r != i]
            cols = [c for c in range(3) if c != j]
            minor = m[rows[0]][cols[0]] * m[rows[1]][cols[1]] - m[rows[0]][cols[1]] * m[rows[1]][cols[0]]
            row.append(((-1) ** (i + j)) * minor)
        cofactors.append(row)
    adjugate = transpose(cofactors)
    return [[entry // determinant for entry in row] for row in adjugate]


def generate() -> dict[str, Any]:
    factor = load("factor_t73_matrix_nielsen")
    factorization = factor.generate()
    identity = factor.identity()
    b_total = identity
    d_total = identity
    movie = []
    for index, operation in enumerate(factorization["construction_operations"]):
        b_factor = factor.apply(identity, operation)
        d_factor = transpose(inverse3(b_factor))
        b_total = matmul(b_factor, b_total)
        d_total = matmul(d_factor, d_total)
        pairing = matmul(transpose(d_total), b_total)
        if pairing != identity:
            raise AssertionError(f"dual pairing failed at Nielsen move {index}")
        movie.append({
            "index": index,
            "B_move": operation,
            "B_factor": b_factor,
            "D_dual_factor": d_factor,
            "B_partial": b_total,
            "D_partial": d_total,
            "intersection_pairing": pairing,
            "pl_support_status": "OPEN",
        })
    if b_total != factor.A:
        raise AssertionError("paired movie does not induce A on H_B")
    result: dict[str, Any] = {
        "schema": "t73_heegaard_nielsen_movie/v1",
        "matrix_A": factor.A,
        "move_count": len(movie),
        "moves": movie,
        "final_B_action": b_total,
        "final_D_action": d_total,
        "all_intersection_pairings_identity": True,
        "combinatorial_status": "PASS",
        "pl_realization_status": "OPEN: support balls, slide bands, and relative section-ball isotopies not yet parameterized",
    }
    result["movie_sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = generate()
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check:
        print("T73_HEEGAARD_NIELSEN_MOVIE=PASS")
        print(f"MOVES={result['move_count']}")
        print(f"PL_REALIZATION_STATUS={result['pl_realization_status']}")
        print(f"MOVIE_SHA256={result['movie_sha256']}")
    elif not args.output:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
