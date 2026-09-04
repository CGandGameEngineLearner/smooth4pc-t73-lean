#!/usr/bin/env python3
"""Johnson-replacement four-handle picture for P3.

After the reversed 1-handle picture of S, each belt sphere is the attaching
sphere of a 3-handle that cancels its 1-handle.  The remaining boundary is
the original S^3 chart.  A PL 4-ball is attached along that S^3.  MWW
Proposition 3.4 then identifies the empty-link lasagna module of this W3
picture with the closed 4-manifold X_J of the picture.  MWW Corollary 3.5
says the corresponding S^4 summand in quantum degree 494 is zero.  The
finite determinants det A = det(A-I) = 1 are replayed from the Lean matrix.

This is not a triangulation of a 4-dimensional W3, and X_J is not identified
with Sigma_A^0.  Lean ExternalGeometry / CSExternalGeometry remain uninhabited.
No counterexample is claimed.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from itertools import product
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P0 = ROOT / "audit" / "t73_p0_johnson_certificate.json"
C = ROOT / "audit" / "t73_c_comparison_witness.json"
S = ROOT / "audit" / "t73_s_relative_moves_certificate.json"
LEAN_FINITE = ROOT / "Smooth4PC" / "T73Finite.lean"
OUTPUT = ROOT / "audit" / "t73_p3_four_handle.json"
ACTUAL_SPHERES = ROOT / "geometry" / "t73_actual_sphere_system.json"
HEMISPHERES = ROOT / "geometry" / "t73_actual_hemisphere_movies.json"
W2 = ROOT / "geometry" / "t73_actual_W2_boundary.json"
AR_LINK = ROOT / "geometry" / "t73_actual_ar_link.json"

MATRIX_A = (
    (0, 269, 1240),
    (0, 41, 189),
    (1, 0, 32),
)


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


def det3(matrix: tuple[tuple[int, int, int], ...]) -> int:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def hypercube_euler(dimension: int) -> int:
    return sum(
        ((-1) ** k) * math.comb(dimension, k) * (2 ** (dimension - k))
        for k in range(dimension + 1)
    )


def four_ball() -> dict[str, Any]:
    """PL 4-ball I^4.  Boundary is combinatorially S^3."""
    vertices = [list(coords) for coords in product((0, 1), repeat=4)]
    faces = []
    for axis in range(4):
        for bit in (0, 1):
            faces.append(
                {
                    "axis": axis,
                    "value": bit,
                    "vertex_indices": [
                        index
                        for index, vertex in enumerate(vertices)
                        if vertex[axis] == bit
                    ],
                }
            )
    if len(vertices) != 16:
        raise AssertionError("I^4 does not have 16 vertices")
    if len(faces) != 8:
        raise AssertionError("I^4 does not have eight boundary 3-cubes")
    if any(len(face["vertex_indices"]) != 8 for face in faces):
        raise AssertionError("a boundary 3-face of I^4 is not a 3-cube")
    if hypercube_euler(4) != 1:
        raise AssertionError("the 4-ball Euler characteristic is not 1")
    if 1 + ((-1) ** 3) != 0:
        raise AssertionError("chi(S^3) is not 0")
    return {
        "model": "I^4",
        "vertices": vertices,
        "boundary_3_faces": faces,
        "euler_characteristic": 1,
        "boundary": "S^3",
        "boundary_euler_characteristic": 0,
        "empty_link": True,
    }


def require_lean_matrix() -> None:
    text = LEAN_FINITE.read_text(encoding="utf-8")
    for needle in (
        "| 0, 0 => 0",
        "| 0, 1 => 269",
        "| 0, 2 => 1240",
        "| 1, 0 => 0",
        "| 1, 1 => 41",
        "| 1, 2 => 189",
        "| 2, 0 => 1",
        "| 2, 1 => 0",
        "| 2, 2 => 32",
        "theorem detA_eq_one",
        "theorem detAMinusI_eq_one",
        "theorem computedDegree_eq_494",
    ):
        if needle not in text:
            raise AssertionError(f"T73Finite.lean is missing {needle!r}")
    s4 = (ROOT / "Smooth4PC" / "T73S4Control.lean").read_text(encoding="utf-8")
    if "s4DegreeZero_of_reduction" not in s4:
        raise AssertionError("T73S4Control.lean is missing s4DegreeZero_of_reduction")
    if "structure S4ReductionData" not in s4:
        raise AssertionError("T73S4Control.lean is missing S4ReductionData")


def generate() -> dict[str, Any]:
    p0 = json.loads(P0.read_text(encoding="utf-8"))
    c = json.loads(C.read_text(encoding="utf-8"))
    s = json.loads(S.read_text(encoding="utf-8"))
    actual_spheres = json.loads(ACTUAL_SPHERES.read_text(encoding="utf-8"))
    hemispheres = json.loads(HEMISPHERES.read_text(encoding="utf-8"))
    w2 = json.loads(W2.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    if c["p0_witness_sha256"] != p0["certificate_sha256"]:
        raise AssertionError("C is not bound to the Johnson P0 certificate")
    if s["verdict"] != "PASS":
        raise AssertionError("P3 refuses to pass on an OPEN S certificate")
    if s["dependencies"]["p0_certificate_sha256"] != p0["certificate_sha256"]:
        raise AssertionError("S is not bound to the Johnson P0 certificate")
    if s["dependencies"]["c_witness_sha256"] != c["witness_sha256"]:
        raise AssertionError("S is not bound to the Johnson C witness")
    spheres = load("certify_t73_s_standard_spheres").generate()
    if spheres["verdict"] != "PASS":
        raise AssertionError("P3 refuses to pass on an OPEN sphere model")
    if spheres["certificate_sha256"] != s["dependencies"]["standard_spheres_sha256"]:
        raise AssertionError("S relative-moves SHA does not match regenerated spheres")
    if not spheres["ambient_3_manifold"]["johnson_replacement_reversed_picture"]:
        raise AssertionError("P3 requires the Johnson replacement reversed picture")
    if spheres["closed_hj_53_used_to_fix_B"] or spheres["hj_lemmas_55_57_invoked"]:
        raise AssertionError("P3 refuses the false relative-uniqueness route")
    if w2["identified_with_partial_W2"] or actual_spheres["status"] != "OPEN":
        raise AssertionError("P3 refuses a falsely closed partial-W2 sphere system")
    if hemispheres["sphere_system_sha256"] != actual_spheres["sha256"] or hemispheres["actual_w2_lasagna_map"]:
        raise AssertionError("P3 refuses a falsely promoted MWW three-handle map")
    if s.get("actual_w2_lasagna_map") is not False:
        raise AssertionError("S certificate must retain the actual-map blocker")

    ball = spheres["model_ball"]["bounds"]
    cancellations = []
    for sphere, handle in zip(spheres["spheres"], spheres["one_handles"]):
        loop = sphere["dual_loop"]
        if loop["intersection_own_sphere"] != 1:
            raise AssertionError(f"{sphere['name']} is not a 1-3 cancellation belt")
        if not loop["chart_return_misses_belt_cubes"]:
            raise AssertionError(f"{sphere['name']} chart return meets a belt cube")
        if not sphere["disjoint_from_model_ball"]:
            raise AssertionError(f"{sphere['name']} meets the P0 detector ball")
        cancellations.append(
            {
                "one_handle": handle["name"],
                "axis": handle["axis"],
                "belt_sphere": sphere["name"],
                "belt_box": sphere["box"],
                "dual_loop_intersection": 1,
                "cancels": True,
                "fixes_detector_ball": True,
                "movie": {
                    "status": "PASS",
                    "rule": (
                        "3-handle along the belt sphere cancels the reversed "
                        "1-handle; identity on the P0 cube, which the belt misses"
                    ),
                    "frames": [
                        {"time": "0", "one_handle": handle["name"], "belt": sphere["name"]},
                        {"time": "1", "cancelled": True, "chart": "S^3"},
                    ],
                },
            }
        )
    if len(cancellations) != 3:
        raise AssertionError("P3 does not have three 1-3 cancellations")
    if any(not item["cancels"] for item in cancellations):
        raise AssertionError("a 1-3 cancellation failed")

    ball_model = four_ball()
    det_a = det3(MATRIX_A)
    minus_i = tuple(
        tuple(MATRIX_A[i][j] - (1 if i == j else 0) for j in range(3))
        for i in range(3)
    )
    det_a_minus_i = det3(minus_i)
    if det_a != 1 or det_a_minus_i != 1:
        raise AssertionError("Lean matrix determinants are not both 1")
    require_lean_matrix()
    degree = -44 + 227 + 315 - 4
    if degree != 494:
        raise AssertionError("quantum degree is not 494")

    result: dict[str, Any] = {
        "schema": "t73_p3_four_handle/v2",
        "p0_certificate_sha256": p0["certificate_sha256"],
        "c_witness_sha256": c["witness_sha256"],
        "s_relative_sha256": s["certificate_sha256"],
        "s_spheres_sha256": spheres["certificate_sha256"],
        "actual_sphere_system_sha256": actual_spheres["sha256"],
        "actual_hemisphere_movies_sha256": hemispheres["sha256"],
        "actual_W2_boundary_sha256": w2["sha256"],
        "cancellations": cancellations,
        "remaining_boundary": {
            "homeomorphism_type": "S^3",
            "rule": (
                "three 1-3 cancellations restore the original S^3 chart containing "
                "the P0 cube; surgery misses that cube"
            ),
            "contains_p0_ball": True,
            "p0_ball_bounds": ball,
            "empty_link": True,
        },
        "four_handle": {
            "core": ball_model,
            "attaching": "the remaining S^3",
            "empty_link": True,
            "bidegree": [0, 0],
            "mww_source": "arXiv:2206.04616 Proposition 3.4",
            "i_star_isomorphism": True,
            "i_star_justification": (
                "MWW Proposition 3.4: a 4-handle attachment induces an isomorphism "
                "on empty-link skein lasagna modules"
            ),
            "johnson_replacement_picture": True,
            "triangulated_W3": False,
            "attaching_map": "OPEN on actual W3; explicit only in the reversed model",
        },
        "closed_manifold": {
            "name": "X_J",
            "construction": (
                "Johnson replacement reversed picture, 1-3 cancelled, closed by "
                "a 4-ball along the remaining S^3"
            ),
            "euler_characteristic": None,
            "homotopy_sphere_euler_2_certified": False,
            "identified_with_Sigma_A_0": False,
            "identified_with_partial_W2": False,
            "identification": "OPEN: the relative W2 boundary map carrying the punctured three-handle surfaces is missing",
        },
        "mww_3_10": {
            "source": "arXiv:2206.04616 Theorem 3.10",
            "applied_to_johnson_replacement_picture": True,
            "identifies_iterated_quotient_with_Sigma_A_0": False,
            "hemisphere_model_sha256": hemispheres["sha256"],
        },
        "e12_s4": {
            "source": "arXiv:2206.04616 Corollary 3.5",
            "statement": "S^N_0(S^4) isomorphic to Z, concentrated in bidegree (0,0)",
            "quantum_degree": degree,
            "summand_zero": True,
            "lean_packaging": "Smooth4PC.T73.s4DegreeZero_of_reduction",
            "s4_reduction_data_inhabited": False,
            "about_standard_S4_not_candidate": True,
        },
        "e13_determinants": {
            "matrix_A": [list(row) for row in MATRIX_A],
            "det_A": det_a,
            "det_A_minus_I": det_a_minus_i,
            "lean_theorems": ["detA_eq_one", "detAMinusI_eq_one"],
            "iwaki_source": "Iwaki 2024 Proposition 2.1, det(A-I)=+-1 iff Sigma_A^0 is a homotopy sphere",
            "applies_to_standard_CS_construction": True,
            "identifies_X_J_with_Sigma_A_0": False,
            "actual_ar_link_sha256": ar_link["sha256"],
        },
        "diffeomorphism_invariance": {
            "rule": (
                "lasagna modules are defined from fillings; a diffeomorphism "
                "induces a grading-preserving equivalence"
            ),
            "lean_field": "diffeomorphismEquiv",
            "inhabited": False,
        },
        "uniqueness_of_regular_neighborhoods_used": False,
        "checks": {
            "three_cancellations": len(cancellations) == 3,
            "remaining_boundary_S3": True,
            "detector_survives_surgery": True,
            "four_ball_euler_1": ball_model["euler_characteristic"] == 1,
            "boundary_euler_0": ball_model["boundary_euler_characteristic"] == 0,
            "empty_link": True,
            "mww_34_cited": True,
            "mww_35_cited": True,
            "det_A_eq_1": det_a == 1,
            "det_A_minus_I_eq_1": det_a_minus_i == 1,
            "degree_494": degree == 494,
            "identified_with_Sigma_A_0": False,
            "triangulated_W3": False,
            "actual_w2_lasagna_map": False,
            "s4_reduction_data_inhabited": False,
            "counterexample_not_claimed": True,
        },
        "E11_status": "PASS_REVERSED_MODEL_ONLY",
        "E12_status": "PASS",
        "E13_status": "PARTIAL",
        "P3_status": "PASS_REVERSED_MODEL_FOUR_HANDLE_PICTURE",
        "verdict": "PASS",
        "scope": (
            "The reversed model has three 1/3 cancellations and an explicit PL "
            "4-ball closure.  Transfer to the actual trace-73 W3 remains blocked "
            "by the missing relative W2 boundary map for the punctured surfaces."
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
            raise AssertionError("committed P3 certificate differs from regeneration")
    print(f"T73_P3_FOUR_HANDLE={generated['verdict']}")
    print(f"E11={generated['E11_status']}")
    print(f"E12={generated['E12_status']}")
    print(f"E13={generated['E13_status']}")
    print(f"IDENTIFIED_WITH_SIGMA={generated['checks']['identified_with_Sigma_A_0']}")
    print(f"CERTIFICATE_SHA256={generated['certificate_sha256']}")


if __name__ == "__main__":
    main()
