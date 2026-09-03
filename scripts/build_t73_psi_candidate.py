#!/usr/bin/env python3
"""Audit the linear/Nielsen candidate for the required AR map psi_A.

The linear torus map phi_A is explicit, but P0 needs a map isotopic to it that
is fixed on the section ball and preserves the AR Heegaard handlebodies.  This
program identifies exactly which of those properties are not supplied by the
linear/Nielsen data.
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


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [[sum(left[i][k] * right[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def matvec(matrix: list[list[int]], vector: list[int]) -> list[int]:
    return [sum(matrix[i][j] * vector[j] for j in range(3)) for i in range(3)]


def operation_matrix(factor_module: Any, operation: dict[str, Any]) -> list[list[int]]:
    return factor_module.apply(factor_module.identity(), operation)


def mod_period(vector: list[int], period: int = 4) -> list[int]:
    return [((value + 2) % period) - 2 for value in vector]


def coordinate_axis_image(matrix: list[list[int]], axis: int) -> list[int]:
    return [matrix[row][axis] for row in range(3)]


def is_signed_axis(vector: list[int]) -> bool:
    return sum(value != 0 for value in vector) == 1 and sum(abs(value) for value in vector) == 1


def generate() -> dict[str, Any]:
    factor = load("factor_t73_matrix_nielsen")
    torus = load("build_t73_ar_torus")
    factorization = factor.generate()
    torus_model = torus.generate()
    matrices = [operation_matrix(factor, op) for op in factorization["construction_operations"]]
    product = factor.identity()
    records = []
    for index, (operation, matrix) in enumerate(zip(factorization["construction_operations"], matrices)):
        product = matmul(matrix, product)
        axis_images = [coordinate_axis_image(matrix, axis) for axis in range(3)]
        records.append({
            "index": index,
            "operation": operation,
            "linear_lift_matrix": matrix,
            "coordinate_axis_images": axis_images,
            "preserves_coordinate_spine_setwise": all(is_signed_axis(v) for v in axis_images),
            "partial_product": product,
        })
    if product != factor.A:
        raise AssertionError("factor matrices do not compose to A")

    q = [-1, -1, -1]
    qbar = [1, 1, 1]
    phi_q = mod_period(matvec(factor.A, q))
    phi_qbar = mod_period(matvec(factor.A, qbar))
    fixed_section_arc = phi_q == q and phi_qbar == qbar
    all_spine_preserving = all(record["preserves_coordinate_spine_setwise"] for record in records)
    result: dict[str, Any] = {
        "schema": "t73_psi_candidate_audit/v1",
        "torus_model_sha256": torus_model["model_sha256"],
        "factorization_sha256": factorization["witness_sha256"],
        "matrix_A": factor.A,
        "factor_records": records,
        "linear_phi_A": {
            "Q_image_mod_period": phi_q,
            "Qbar_image_mod_period": phi_qbar,
            "fixes_section_arc_endpoints": fixed_section_arc,
        },
        "all_linear_factors_preserve_coordinate_spine_setwise": all_spine_preserving,
        "psi_A_status": "PASS" if fixed_section_arc and all_spine_preserving else "OPEN",
        "missing_geometric_data": [
            "relative PL isotopy from phi_A to a map fixed on the section ball",
            "simplex-by-simplex extension preserving H_B and H_D",
            "transport of product-annulus normal fields through that isotopy",
        ],
        "interpretation": "Failure here does not falsify AR existence; it proves that the linear/Nielsen data alone are not the required psi_A.",
    }
    result["audit_sha256"] = canonical_sha(result)
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
        print("T73_PSI_CANDIDATE_AUDIT=PASS")
        print(f"PSI_A_STATUS={result['psi_A_status']}")
        print(f"AUDIT_SHA256={result['audit_sha256']}")
    elif not args.output:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
