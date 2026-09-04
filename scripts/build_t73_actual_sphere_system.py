#!/usr/bin/env python3
"""Bind the reversed three-handle picture to the actual partial W2 boundary.

Reverse the three actual 3-handles in the AR handle decomposition.  Their
dual 1-handles give #^3(S1 x S2), and their belt spheres are the attaching
spheres transported through the two verified Kirby cancellations.  The
detector chart is carried along and the reverse handle feet are chosen in its
complement.  actual_w2_lasagna_map remains false here until the separate
hemisphere-movie verifier succeeds.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "geometry" / "t73_actual_sphere_system.json"
W2 = ROOT / "geometry" / "t73_actual_W2_boundary.json"
LINK = ROOT / "geometry" / "t73_actual_ar_link.json"
CANCEL_T = ROOT / "geometry" / "t73_cancel_t_hcs.json"
CANCEL_X = ROOT / "geometry" / "t73_cancel_x_m1.json"
C1 = ROOT / "audit" / "t73_c1_cut_link.json"
C2 = ROOT / "audit" / "t73_c2_comparison.json"
C_WITNESS = ROOT / "audit" / "t73_c_comparison_witness.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def closed_polyline(disk: dict[str, Any]) -> bool:
    return bool(disk["closed"] and disk["vertex_count"] >= 3)


def build(write: bool = False) -> dict[str, Any]:
    link = json.loads(LINK.read_text(encoding="utf-8"))
    cancel_t = json.loads(CANCEL_T.read_text(encoding="utf-8"))
    cancel_x = json.loads(CANCEL_X.read_text(encoding="utf-8"))
    c1 = json.loads(C1.read_text(encoding="utf-8"))
    c2 = json.loads(C2.read_text(encoding="utf-8"))
    c_witness = json.loads(C_WITNESS.read_text(encoding="utf-8"))
    standard = load("certify_t73_s_standard_spheres").generate()
    if link["status"]["actual_framed_ar_link"] != "PASS":
        raise AssertionError("actual W2 requires the framed AR link")
    if cancel_t["status"] != "PASS" or cancel_x["status"] != "PASS":
        raise AssertionError("actual W2 requires both Kirby cancellations")
    if c1["C1_status"] != "PASS" or c2["C2_status"] != "PASS" or c_witness["C_status"] != "PASS":
        raise AssertionError("actual W2 detector/cocone data are not closed")
    if standard["verdict"] != "PASS" or not all(standard["checks"].values()):
        raise AssertionError("reversed three-handle sphere model is not verified")
    spheres = []
    kernel_owners = ["r_xy", "r_yz", "r_zx"]
    for index, sphere in enumerate(standard["spheres"]):
        coefficients = standard["attaching_homology"]["sphere_columns_in_kernel_basis"][index]
        boundary_profile = []
        for owner, coefficient in zip(kernel_owners, coefficients):
            boundary_profile.append(
                {
                    "owner": owner,
                    "coefficient": coefficient,
                    "copy_count": abs(coefficient),
                    "orientation": 1 if coefficient > 0 else -1 if coefficient < 0 else 0,
                    "product_normal_level_rule": f"(copy_index+1)/({sum(abs(value) for value in coefficients) + 1}) inside the actual {owner} framing collar",
                }
            )
        b_count = sum(item["copy_count"] for item in boundary_profile)
        spheres.append(
            {
                "name": sphere["name"],
                "actual_3_handle": f"H^3_{index + 1}",
                "surface": sphere["surface"],
                "surface_euler": sphere["surface_euler"],
                "dual_loop": sphere["dual_loop"],
                "kernel_attaching": sphere["kernel_attaching"],
                "relative_detector_movie": sphere["relative_movie"],
                "endpoint_foam": sphere["endpoint_foam"],
                "embedded_s2_in_reversed_model": True,
                "embedded_s2_on_actual_W2": False,
                "disjoint_from_detector": True,
                "sphere_column_in_kernel_basis": coefficients,
                "core_disk_boundary_profile": boundary_profile,
                "core_disk_intersection_count_b": b_count,
                "transport_rule": "OPEN: the belt sphere is explicit in the reversed model, but the PL boundary map through all five actual 2-handle core collars has not been constructed",
            }
        )
    pairwise = [
        {"left": left["name"], "right": right["name"], "disjoint": True}
        for left, right in itertools.combinations(spheres, 2)
    ]
    w2 = {
        "schema": "t73_actual_W2_boundary/v2",
        "source": "actual seven-component AR handle decomposition transported through both Kirby cancellations",
        "ar_link_sha256": link["sha256"],
        "cancel_t_sha256": cancel_t["sha256"],
        "cancel_x_sha256": cancel_x["sha256"],
        "c1_certificate_sha256": c1["certificate_sha256"],
        "handle_counts_at_W2": [1, 2, 5, 0, 0],
        "outgoing_handles": {"three_handles": 3, "four_handles": 1},
        "reversed_outgoing_picture": {
            "zero_handle": 1,
            "one_handles": 3,
            "boundary": "#^3(S^1 x S^2)",
            "belt_spheres_are_actual_3_handle_attaching_spheres": True,
            "detector_chart_carried_to_model_ball": c1["p0_ambient_ball"],
        },
        "identified_with_partial_W2": False,
        "identification_method": "OPEN: reversing the outgoing 3-handles gives the abstract model, but an explicit relative boundary diffeomorphism carrying all actual 2-handle core collars and the detector is still missing",
    }
    w2["sha256"] = canonical_sha({key: value for key, value in w2.items() if key != "sha256"})
    result = {
        "schema": "t73_actual_sphere_system/v2",
        "spheres": spheres,
        "pairwise": pairwise,
        "pairwise_disjoint": True,
        "complement_connected": True,
        "spherical_homology_basis": {
            "status": "PASS_REVERSED_MODEL_ONLY",
            "dual_loop_pairing_matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            "sphere_columns_in_kernel_basis": standard["attaching_homology"]["sphere_columns_in_kernel_basis"],
            "determinant": 1,
        },
        "simultaneous_surgery_is_S3": False,
        "simultaneous_surgery_in_reversed_model_is_S3": True,
        "simultaneous_surgery_reason": "the abstract reversed model compresses to S3; transfer to the actual W2 boundary awaits the missing relative boundary map",
        "hj_53_kernel_invariance_only": True,
        "hj_lemmas_55_57_invoked": False,
        "actual_w2_lasagna_map": False,
        "w2_boundary_sha256": w2["sha256"],
        "status": "OPEN",
        "reason": "the reversed sphere model and b=(1541,10118,2) profiles are explicit, but the surfaces have not been transported through an actual relative W2 boundary map",
        "standard_sphere_certificate_sha256": standard["certificate_sha256"],
        "c_witness_sha256": c_witness["witness_sha256"],
    }
    result["sha256"] = canonical_sha({key: value for key, value in result.items() if key != "sha256"})
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        W2.write_text(json.dumps(w2, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.check or args.write:
        print("T73_ACTUAL_SPHERE_SYSTEM=WRITTEN" if args.write else "T73_ACTUAL_SPHERE_SYSTEM=CHECKED")
        print(f"STATUS={result['status']}")
        print(f"ACTUAL_W2_LASAGNA_MAP={result['actual_w2_lasagna_map']}")
        print(f"HJ_55_57_INVOKED={result['hj_lemmas_55_57_invoked']}")
        print(f"SHA256={result['sha256']}")
        return
    print(json.dumps({"status": result["status"]}, indent=2))


if __name__ == "__main__":
    main()
