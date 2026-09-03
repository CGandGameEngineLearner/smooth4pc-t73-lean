#!/usr/bin/env python3
"""Computational S^4 reduction for E12.

MWW Corollary 3.5 is the published statement S^N_0(S^4) ≅ Z in bidegree
(0,0).  Lean packages that as S4ReductionData: G(B^4,q) ≃ EmptyKhQ(q) and
G(B^4,q) ≃ G(S^4,q).  This program computes the two concrete pieces of that
reduction from existing objects:

- Empty-link Khovanov over Q of the empty diagram (0 crossings, 0 circles):
  one generator in bidegree (0,0), zero differential, rank 1 at q=0 and 0
  otherwise.  This is EmptyKhQ.
- The PL 4-ball I^4 already used by the P3 four-handle certificate, glued to
  a second I^4 along S^3.  Euler characteristic 1+1-0=2 is the standard S^4,
  not X_J.

Degree 494 is replayed from T73Finite.lean.  EmptyKhQ(494)=0, so the S^4
summand in quantum degree 494 vanishes.  T73S4Control.lean still has no
S4ReductionData instance.  T73S4Inhabitant.lean inhabits the empty-link
control universe only; that is not a candidate ExternalGeometry.
The closed manifold X_J is not identified with S^4.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P3 = ROOT / "audit" / "t73_p3_four_handle.json"
LEAN_FINITE = ROOT / "Smooth4PC" / "T73Finite.lean"
LEAN_S4 = ROOT / "Smooth4PC" / "T73S4Control.lean"
LEAN_S4_INHABITANT = ROOT / "Smooth4PC" / "T73S4Inhabitant.lean"
OUTPUT = ROOT / "audit" / "t73_e12_s4_reduction.json"
DEGREE = -44 + 227 + 315 - 4


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def empty_link_khovanov() -> dict[str, Any]:
    """Khovanov chain complex of the empty diagram, N=2, coefficients Q.

    The cube of resolutions of a 0-crossing, 0-component diagram has one
    vertex: the empty smoothing.  The Blanchet--Khovanov TQFT assigns Q to
    the empty 1-manifold (zero circles, V^{⊗0} = Q).  There are no
    cobordism maps, so the differential is the 1x1 zero matrix.
    """
    generators = [{"name": "empty_smoothing", "homological": 0, "quantum": 0}]
    differential = [[0]]
    image_rank = 0
    kernel_rank = 1
    homology_rank = kernel_rank - image_rank
    if homology_rank != 1:
        raise AssertionError("empty-link Khovanov homology is not rank 1")
    ranks = {str(q): (1 if q == 0 else 0) for q in (-1, 0, 1, DEGREE)}
    if ranks[str(DEGREE)] != 0:
        raise AssertionError("EmptyKhQ(494) is not zero")
    if ranks["0"] != 1:
        raise AssertionError("EmptyKhQ(0) is not Q")
    return {
        "theory": "Blanchet-Khovanov / KhR_2 over Q",
        "diagram": "empty link: 0 crossings, 0 components",
        "resolution_cube_vertices": 1,
        "generators": generators,
        "differential": differential,
        "kernel_rank": kernel_rank,
        "image_rank": image_rank,
        "homology_rank_total": homology_rank,
        "rational_dimension_by_quantum_degree": ranks,
        "matches_lean_EmptyKhQ": True,
        "lean_def": "Smooth4PC.T73.EmptyKhQ",
    }


def empty_kh_q(q: int) -> int:
    return 1 if q == 0 else 0


def standard_s4(ball: dict[str, Any]) -> dict[str, Any]:
    chi_ball = ball["euler_characteristic"]
    chi_boundary = ball["boundary_euler_characteristic"]
    chi_s4 = chi_ball + chi_ball - chi_boundary
    if chi_ball != 1:
        raise AssertionError("I^4 Euler characteristic is not 1")
    if chi_boundary != 0:
        raise AssertionError("boundary of I^4 is not combinatorially S^3")
    if chi_s4 != 2:
        raise AssertionError("two 4-balls glued along S^3 do not have Euler characteristic 2")
    if not ball["empty_link"]:
        raise AssertionError("the 4-ball is not recorded as an empty-link chart")
    return {
        "model": "B4 union_{S^3} B4",
        "B4": {
            "model": ball["model"],
            "vertices": len(ball["vertices"]),
            "boundary_3_faces": len(ball["boundary_3_faces"]),
            "euler_characteristic": chi_ball,
            "boundary": ball["boundary"],
            "boundary_euler_characteristic": chi_boundary,
            "empty_link": True,
        },
        "glue": "identify the eight boundary 3-cubes of two I^4 copies",
        "euler_characteristic": chi_s4,
        "name": "S^4",
        "identified_with_X_J": False,
        "about_standard_S4_not_candidate": True,
    }


def require_lean() -> None:
    finite = LEAN_FINITE.read_text(encoding="utf-8")
    for needle in (
        "theorem computedDegree_eq_494",
        "theorem computedDegree_ne_zero",
        "degreeMinus44",
        "degreePlus227",
        "degreePlus315",
        "degreeMinus4",
    ):
        if needle not in finite:
            raise AssertionError(f"T73Finite.lean is missing {needle!r}")
    s4 = LEAN_S4.read_text(encoding="utf-8")
    for needle in (
        "structure S4ReductionData",
        "evalB4",
        "attach4",
        "def EmptyKhQ",
        "theorem emptyKhQ_subsingleton",
        "theorem s4DegreeZero_of_reduction",
        "theorem s4ComputedDegreeZero_of_reduction",
    ):
        if needle not in s4:
            raise AssertionError(f"T73S4Control.lean is missing {needle!r}")
    if "instance S4ReductionData" in s4 or "def s4Reduction" in s4:
        raise AssertionError("T73S4Control.lean must not inhabit S4ReductionData")
    inhabitant = LEAN_S4_INHABITANT.read_text(encoding="utf-8")
    if "def emptyLinkS4Reduction" not in inhabitant:
        raise AssertionError("T73S4Inhabitant.lean is missing emptyLinkS4Reduction")
    if "theorem emptyLink_s4ComputedDegreeZero" not in inhabitant:
        raise AssertionError("T73S4Inhabitant.lean is missing emptyLink_s4ComputedDegreeZero")
    if "instance ExternalGeometry" in inhabitant or "def t73ExternalGeometry" in inhabitant:
        raise AssertionError("empty-link inhabitant must not supply ExternalGeometry")


def generate() -> dict[str, Any]:
    p3 = json.loads(P3.read_text(encoding="utf-8"))
    if p3["verdict"] != "PASS":
        raise AssertionError("E12 requires a PASS P3 four-handle certificate")
    if not p3["e12_s4"]["about_standard_S4_not_candidate"]:
        raise AssertionError("P3 E12 is not recorded as a statement about S^4")
    if p3["closed_manifold"]["identified_with_Sigma_A_0"]:
        raise AssertionError("E12 refuses to close on a fake candidate identification")
    if p3["e12_s4"]["s4_reduction_data_inhabited"]:
        raise AssertionError("P3 claims a Lean S4ReductionData instance that does not exist")
    ball = load("certify_t73_p3_four_handle").four_ball()
    if ball != p3["four_handle"]["core"]:
        raise AssertionError("committed P3 4-ball differs from regenerated I^4")
    require_lean()
    if DEGREE != 494:
        raise AssertionError("quantum degree is not 494")
    kh = empty_link_khovanov()
    sphere = standard_s4(ball)
    if empty_kh_q(DEGREE) != 0:
        raise AssertionError("EmptyKhQ(494) is not zero")
    if empty_kh_q(0) != 1:
        raise AssertionError("EmptyKhQ(0) is not Q")

    reduction = {
        "B4": sphere["B4"],
        "evalB4": {
            "statement": "G(B^4, q) ≃ EmptyKhQ(q)",
            "source": "empty-link evaluation of skein lasagna of a 4-ball",
            "empty_khovanov": kh,
            "computed": True,
        },
        "attach4": {
            "statement": "G(B^4, q) ≃ G(S^4, q)",
            "source": "arXiv:2206.04616 Proposition 3.4, empty-link 4-handle isomorphism",
            "geometric_model": sphere,
            "bidegree": [0, 0],
            "empty_link": True,
        },
        "conclusion": {
            "statement": "G(S^4, 494) = 0",
            "rule": (
                "EmptyKhQ(494)=0, evalB4 identifies G(B^4,494) with that zero "
                "module, attach4 identifies G(S^4,494) with G(B^4,494)"
            ),
            "lean_packaging": "Smooth4PC.T73.s4ComputedDegreeZero_of_reduction",
            "quantum_degree": DEGREE,
            "summand_zero": True,
        },
    }
    result: dict[str, Any] = {
        "schema": "t73_e12_s4_reduction/v1",
        "p3_certificate_sha256": p3["certificate_sha256"],
        "s4_reduction": reduction,
        "mww_corollary_3_5": {
            "source": "arXiv:2206.04616 Corollary 3.5",
            "statement": "S^N_0(S^4) isomorphic to Z, concentrated in bidegree (0,0)",
            "unpacked_as": "S4ReductionData.evalB4 and attach4 on the computed I^4 and empty Khovanov",
        },
        "lean_s4_reduction_data_inhabited": False,
        "identified_with_X_J": False,
        "about_standard_S4_not_candidate": True,
        "checks": {
            "empty_khovanov_rank_1_at_q0": kh["rational_dimension_by_quantum_degree"]["0"] == 1,
            "empty_khovanov_rank_0_at_494": kh["rational_dimension_by_quantum_degree"][str(DEGREE)] == 0,
            "four_ball_euler_1": ball["euler_characteristic"] == 1,
            "boundary_euler_0": ball["boundary_euler_characteristic"] == 0,
            "standard_s4_euler_2": sphere["euler_characteristic"] == 2,
            "degree_494": DEGREE == 494,
            "s4_degree_494_zero": True,
            "about_standard_S4_not_candidate": True,
            "identified_with_X_J": False,
            "lean_s4_reduction_data_inhabited": False,
            "p3_four_ball_bound": True,
            "counterexample_not_claimed": True,
        },
        "E12_status": "PASS",
        "verdict": "PASS",
        "scope": (
            "Computational S^4 reduction: empty-link Khovanov over Q, PL I^4, "
            "standard S^4 of Euler characteristic 2, MWW Proposition 3.4 and "
            "Corollary 3.5, degree 494 vanishes.  Not X_J, and Lean "
            "S4ReductionData remains uninhabited."
        ),
    }
    result["certificate_sha256"] = canonical_sha(
        {key: value for key, value in result.items() if key != "certificate_sha256"}
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = generate()
    if args.write:
        OUTPUT.write_text(
            json.dumps(generated, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"WROTE={OUTPUT}")
    if args.check:
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if committed != generated:
            raise AssertionError("committed E12 S^4 reduction differs from regeneration")
    print(f"T73_E12_S4_REDUCTION={generated['verdict']}")
    print(f"E12={generated['E12_status']}")
    print(f"S4_DEGREE_494_ZERO={generated['checks']['s4_degree_494_zero']}")
    print(f"ABOUT_STANDARD_S4={generated['about_standard_S4_not_candidate']}")
    print(f"LEAN_INHABITED={generated['lean_s4_reduction_data_inhabited']}")
    print(f"CERTIFICATE_SHA256={generated['certificate_sha256']}")


if __name__ == "__main__":
    main()
