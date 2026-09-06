#!/usr/bin/env python3
"""Derive the unique diagonal-only homology correction for the affine model.

This is an algebraic target for the next geometric construction.  It does not
assert that the corrected framings have already been realized by PL ribbons.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "audit/t73_affine_kirby_matrix_homology_obstruction.json"
OUTPUT = ROOT / "geometry/t73_kirby_homology_admissible_correction.json"
DUAL_COMPONENTS = ("r_xy", "r_yz", "r_zx")


def payload_sha256(value: dict) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def integer_matrix(matrix: sp.Matrix) -> list[list[int]]:
    return [[int(value) for value in row] for row in matrix.tolist()]


def build() -> dict:
    source = json.loads(SOURCE.read_text())
    current = sp.Matrix(source["dotted_surgery_matrix"])
    order = source["component_order"]

    # The first four components are dotted_y, dotted_z, m_2, m_3.
    # Their block is unimodular because the dotted-incidence block is.
    fixed_block = current[:4, :4]
    coupling = current[:4, 4:]
    current_dual_block = current[4:, 4:]
    if fixed_block.det() not in (-1, 1):
        raise AssertionError("the fixed four-component block is not unimodular")

    fixed_inverse_times_coupling = fixed_block.inv() * coupling
    current_schur = (
        current_dual_block
        - coupling.T * fixed_inverse_times_coupling
    )

    # Keep every off-diagonal linking and both m_i self-linkings fixed.  With
    # this restriction, nullity three forces the entire Schur complement to
    # vanish, hence all three dual diagonal entries must be zero.
    candidate = current.copy()
    corrections: dict[str, int] = {}
    for component in DUAL_COMPONENTS:
        index = order.index(component)
        corrections[component] = -int(candidate[index, index])
        candidate[index, index] = 0

    candidate_dual_block = candidate[4:, 4:]
    candidate_schur = (
        candidate_dual_block
        - coupling.T * fixed_inverse_times_coupling
    )

    # This integral basis change exhibits a unimodular four-block plus three
    # zero rows/columns, and its last three columns give a Z-basis of ker(M).
    transform = sp.eye(7)
    transform[:4, 4:] = -fixed_inverse_times_coupling
    reduced = transform.T * candidate * transform
    kernel_basis = [transform[:, index] for index in range(4, 7)]
    smith = smith_normal_form(candidate, domain=ZZ)

    result = {
        "schema": "t73_kirby_homology_admissible_correction/v1",
        "source_obstruction_sha256": source["sha256"],
        "component_order": order,
        "allowed_change_scope": (
            "dual-component diagonal framings only; every core, dotted "
            "incidence, pairwise linking, and m_2/m_3 diagonal is fixed"
        ),
        "fixed_four_block_determinant": int(fixed_block.det()),
        "fixed_dotted_incidence_determinant": int(
            sp.Matrix(current[:2, 2:4]).det()
        ),
        "current_schur_complement": integer_matrix(current_schur),
        "required_framing_corrections": corrections,
        "candidate_integer_framings": {
            name: int(candidate[index, index])
            for index, name in enumerate(order[2:], start=2)
        },
        "candidate_dotted_surgery_matrix": integer_matrix(candidate),
        "candidate_schur_complement": integer_matrix(candidate_schur),
        "unimodular_congruence_transform": integer_matrix(transform),
        "congruence_reduced_matrix": integer_matrix(reduced),
        "integer_kernel_basis": [
            [int(value) for value in vector] for vector in kernel_basis
        ],
        "candidate_rank": int(candidate.rank()),
        "candidate_smith_diagonal": [int(value) for value in smith.diagonal()],
        "candidate_boundary_h1": "Z^3",
        "uniqueness_statement": (
            "under the declared diagonal-only change scope, nullity three "
            "uniquely forces r_xy=r_yz=r_zx=0"
        ),
        "geometric_realization_status": "CANDIDATE_UNVERIFIED",
        "required_next_witness": (
            "construct disjoint source-relative framing ribbons carrying "
            "+1,+1,+3 twists and replay their exact self-linkings"
        ),
        "completion_status": (
            "UNIQUE_HOMOLOGY_ADMISSIBLE_DIAGONAL_CORRECTION_DERIVED"
        ),
    }
    result["sha256"] = payload_sha256(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()

    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("homology-admissible correction artifact is stale")
    print(
        json.dumps(
            {
                "corrections": result["required_framing_corrections"],
                "rank": result["candidate_rank"],
                "smith": result["candidate_smith_diagonal"],
                "status": result["geometric_realization_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
