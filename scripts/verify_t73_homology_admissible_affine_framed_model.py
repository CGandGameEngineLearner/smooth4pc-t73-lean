#!/usr/bin/env python3
"""Verify the aggregate homology-admissible affine framed candidate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_homology_admissible_affine_framed_model.json"
CORRECTION = ROOT / "geometry/t73_kirby_homology_admissible_correction.json"
TWISTS = ROOT / "geometry/t73_dual_zero_framing_twist_ribbons.json"
CLEARANCE = ROOT / "audit/t73_dual_zero_framing_twist_global_clearance.json"
PAIRWISE = ROOT / "audit/t73_pairwise_core_linking_full_verification.json"
DOTTED = ROOT / "geometry/t73_actual_dotted_s3_passage_cells.json"


def canonical_sha256(value: dict) -> str:
    unsigned = {key: item for key, item in value.items() if key != "sha256"}
    encoded = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def verify() -> dict:
    data = json.loads(DATA.read_text())
    correction = json.loads(CORRECTION.read_text())
    twists = json.loads(TWISTS.read_text())
    clearance = json.loads(CLEARANCE.read_text())
    pairwise = json.loads(PAIRWISE.read_text())
    dotted = json.loads(DOTTED.read_text())
    if data["sha256"] != canonical_sha256(data):
        raise AssertionError("aggregate affine framed payload SHA mismatch")
    bindings = {
        "homology_correction_sha256": correction["sha256"],
        "dual_twist_ribbons_sha256": twists["sha256"],
        "dual_twist_global_clearance_sha256": clearance["sha256"],
        "pairwise_core_linking_full_verification_sha256": pairwise["sha256"],
        "actual_dotted_passage_cells_sha256": dotted["sha256"],
    }
    if any(data[key] != value for key, value in bindings.items()):
        raise AssertionError("aggregate affine framed source binding changed")
    if clearance["full_result"]["embedded_and_disjoint_from_retained_model"] is not True:
        raise AssertionError("twist patches are not globally clear")

    expected_framings = {
        "m_2": -156621,
        "m_3": -3338112,
        "r_xy": 0,
        "r_yz": 0,
        "r_zx": 0,
    }
    if data["integer_framings"] != expected_framings:
        raise AssertionError("corrected affine framings changed")
    for component in twists["components"]:
        if component["integer_self_linking"] != expected_framings[component["component"]]:
            raise AssertionError("twist geometry disagrees with aggregate framing")

    matrix = sp.Matrix(data["dotted_surgery_matrix"])
    if matrix != sp.Matrix(correction["candidate_dotted_surgery_matrix"]):
        raise AssertionError("aggregate matrix changed")
    smith = [int(value) for value in smith_normal_form(matrix, domain=ZZ).diagonal()]
    kernel = sp.Matrix.hstack(
        *(sp.Matrix(vector) for vector in data["integer_kernel_basis"])
    )
    if matrix.rank() != 4 or matrix * kernel != sp.zeros(7, 3) or kernel.rank() != 3:
        raise AssertionError("aggregate matrix does not have the claimed kernel")
    if smith != [1, 1, 1, 1, 0, 0, 0]:
        raise AssertionError("aggregate boundary H1 is not torsion-free rank three")
    if data["actual_t73_relative_equivalence_status"] != "OPEN":
        raise AssertionError("candidate was overstated as actual T73 input")

    return {
        "verdict": "PASS_HOMOLOGY_ADMISSIBLE_AFFINE_FRAMED_MODEL_ONLY",
        "rank": 4,
        "nullity": 3,
        "smith_diagonal": smith,
        "boundary_h1": "Z^3",
        "globally_clear_dual_twist_ribbons": True,
        "actual_t73_relative_equivalence": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
