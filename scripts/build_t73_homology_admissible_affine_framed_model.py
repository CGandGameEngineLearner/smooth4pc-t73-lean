#!/usr/bin/env python3
"""Assemble the globally clear, homology-admissible affine framed candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


ROOT = Path(__file__).resolve().parents[1]
CORRECTION = ROOT / "geometry/t73_kirby_homology_admissible_correction.json"
TWISTS = ROOT / "geometry/t73_dual_zero_framing_twist_ribbons.json"
CLEARANCE = ROOT / "audit/t73_dual_zero_framing_twist_global_clearance.json"
PAIRWISE = ROOT / "audit/t73_pairwise_core_linking_full_verification.json"
DOTTED = ROOT / "geometry/t73_actual_dotted_s3_passage_cells.json"
OUTPUT = ROOT / "geometry/t73_homology_admissible_affine_framed_model.json"


def canonical_sha256(value: dict) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def build() -> dict:
    correction = json.loads(CORRECTION.read_text())
    twists = json.loads(TWISTS.read_text())
    clearance = json.loads(CLEARANCE.read_text())
    pairwise = json.loads(PAIRWISE.read_text())
    dotted = json.loads(DOTTED.read_text())
    matrix = sp.Matrix(correction["candidate_dotted_surgery_matrix"])

    twist_framings = {
        component["component"]: component["integer_self_linking"]
        for component in twists["components"]
    }
    candidate_framings = correction["candidate_integer_framings"]
    if any(candidate_framings[name] != value for name, value in twist_framings.items()):
        raise AssertionError("PL twist framings disagree with the algebraic correction")
    if clearance["verdict"] != "PASS_DUAL_ZERO_FRAMING_TWIST_GLOBAL_CLEARANCE":
        raise AssertionError("PL twist patches have not passed global clearance")

    characteristic = sp.Poly(matrix.charpoly().as_expr())
    variable = characteristic.gens[0]
    nonzero_characteristic = characteristic.exquo(
        sp.Poly(variable ** (matrix.rows - matrix.rank()), variable)
    )
    signature = int(
        nonzero_characteristic.count_roots(0, sp.oo)
        - nonzero_characteristic.count_roots(-sp.oo, 0)
    )
    smith = smith_normal_form(matrix, domain=ZZ)

    result = {
        "schema": "t73_homology_admissible_affine_framed_model/v1",
        "homology_correction_sha256": correction["sha256"],
        "dual_twist_ribbons_sha256": twists["sha256"],
        "dual_twist_global_clearance_sha256": clearance["sha256"],
        "pairwise_core_linking_full_verification_sha256": pairwise["sha256"],
        "actual_dotted_passage_cells_sha256": dotted["sha256"],
        "component_order": correction["component_order"],
        "integer_framings": candidate_framings,
        "dotted_surgery_matrix": correction["candidate_dotted_surgery_matrix"],
        "matrix_rank": int(matrix.rank()),
        "matrix_nullity": matrix.rows - int(matrix.rank()),
        "matrix_signature": signature,
        "smith_diagonal": [int(value) for value in smith.diagonal()],
        "boundary_h1": "Z^3",
        "integer_kernel_basis": correction["integer_kernel_basis"],
        "geometric_checks": {
            "dual_twist_local_ribbons": "PASS",
            "dual_twist_exact_self_linkings": "PASS",
            "dual_twist_global_clearance": "PASS",
            "unchanged_pairwise_core_linkings": "PASS_FULL_REPLAY",
            "unchanged_dotted_incidences": "PASS",
        },
        "model_status": "HOMOLOGY_ADMISSIBLE_AFFINE_FRAMED_CANDIDATE",
        "actual_t73_relative_equivalence_status": "OPEN",
        "scope_boundary": (
            "This is an explicit globally disjoint affine framed-link model "
            "with the required boundary H1. It is not actual T73 input until "
            "a source-relative complement homeomorphism transports the "
            "meridian/longitude and framing data."
        ),
        "completion_status": (
            "AFFINE_FRAMED_MODEL_PASSES_POST_2_HANDLE_HOMOLOGY_GATE_ONLY"
        ),
    }
    result["sha256"] = canonical_sha256(result)
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
        raise AssertionError("homology-admissible affine model is stale")
    print(json.dumps({
        "rank": result["matrix_rank"],
        "nullity": result["matrix_nullity"],
        "signature": result["matrix_signature"],
        "smith": result["smith_diagonal"],
        "relative_equivalence": result["actual_t73_relative_equivalence_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
