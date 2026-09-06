#!/usr/bin/env python3
"""Independently verify the homology-admissible correction candidate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "audit/t73_affine_kirby_matrix_homology_obstruction.json"
CANDIDATE = ROOT / "geometry/t73_kirby_homology_admissible_correction.json"


def payload_sha256(value: dict) -> str:
    unsigned = {key: item for key, item in value.items() if key != "sha256"}
    encoded = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def verify() -> dict:
    source = json.loads(SOURCE.read_text())
    data = json.loads(CANDIDATE.read_text())
    if data["source_obstruction_sha256"] != source["sha256"]:
        raise AssertionError("candidate is not bound to the current obstruction")
    if data["sha256"] != payload_sha256(data):
        raise AssertionError("candidate payload SHA mismatch")

    original = sp.Matrix(source["dotted_surgery_matrix"])
    candidate = sp.Matrix(data["candidate_dotted_surgery_matrix"])
    if original.shape != (7, 7) or candidate.shape != (7, 7):
        raise AssertionError("unexpected Kirby matrix shape")
    if original != original.T or candidate != candidate.T:
        raise AssertionError("Kirby matrix is not symmetric")

    # Independently enforce the declared scope: precisely three diagonal cells
    # may change, and their values must be zero.
    dual_indices = (4, 5, 6)
    for row in range(7):
        for column in range(7):
            if row == column and row in dual_indices:
                if candidate[row, column] != 0:
                    raise AssertionError("dual framing is not zero")
            elif candidate[row, column] != original[row, column]:
                raise AssertionError("entry outside diagonal-only scope changed")

    fixed_block = original[:4, :4]
    coupling = original[:4, 4:]
    if fixed_block.det() != 1:
        raise AssertionError("expected fixed unimodular block determinant +1")
    if sp.Matrix(original[:2, 2:4]).det() != -1:
        raise AssertionError("expected dotted-incidence determinant -1")

    schur = candidate[4:, 4:] - coupling.T * fixed_block.inv() * coupling
    if schur != sp.zeros(3):
        raise AssertionError("candidate Schur complement is nonzero")

    transform = sp.Matrix(data["unimodular_congruence_transform"])
    if abs(int(transform.det())) != 1:
        raise AssertionError("congruence transform is not unimodular")
    reduced = transform.T * candidate * transform
    if reduced != sp.Matrix(data["congruence_reduced_matrix"]):
        raise AssertionError("claimed congruence reduction is wrong")
    if reduced[:4, :4] != fixed_block or reduced[4:, :] != sp.zeros(3, 7):
        raise AssertionError("reduced matrix is not a four-block plus zero block")

    kernel = sp.Matrix.hstack(
        *(sp.Matrix(vector) for vector in data["integer_kernel_basis"])
    )
    if kernel.rank() != 3 or candidate * kernel != sp.zeros(7, 3):
        raise AssertionError("integer kernel basis is invalid")

    smith = [int(value) for value in smith_normal_form(candidate, domain=ZZ).diagonal()]
    if candidate.rank() != 4 or smith != [1, 1, 1, 1, 0, 0, 0]:
        raise AssertionError("candidate does not present torsion-free rank-three H1")
    if data["required_framing_corrections"] != {
        "r_xy": 1,
        "r_yz": 1,
        "r_zx": 3,
    }:
        raise AssertionError("unexpected geometric twist target")
    if data["geometric_realization_status"] != "CANDIDATE_UNVERIFIED":
        raise AssertionError("algebraic candidate was overstated as geometry")

    return {
        "verdict": "PASS_UNIQUE_HOMOLOGY_ADMISSIBLE_DIAGONAL_CORRECTION",
        "required_framing_corrections": data["required_framing_corrections"],
        "rank": 4,
        "smith_diagonal": smith,
        "boundary_h1": "Z^3",
        "geometric_realization": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
