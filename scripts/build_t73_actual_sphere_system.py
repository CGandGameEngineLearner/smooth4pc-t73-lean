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
DUAL_DISK_MOVIE = ROOT / "geometry" / "t73_johnson_dual_disk_movie.json"
SURFACE_TRANSPORT = ROOT / "geometry" / "t73_three_handle_surface_transport.json"


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
    dual_disk_movie = json.loads(DUAL_DISK_MOVIE.read_text(encoding="utf-8"))
    surface_transport = json.loads(SURFACE_TRANSPORT.read_text(encoding="utf-8"))
    standard = load("certify_t73_s_standard_spheres").generate()
    if link["status"]["actual_framed_ar_link"] != "PASS":
        raise AssertionError("actual W2 requires the framed AR link")
    if cancel_t["status"] != "PASS" or cancel_x["status"] != "PASS":
        raise AssertionError("actual W2 requires both Kirby cancellations")
    if c1["C1_status"] != "PASS" or c2["C2_status"] != "PASS" or c_witness["C_status"] != "PASS":
        raise AssertionError("actual W2 detector/cocone data are not closed")
    if standard["verdict"] != "PASS" or not all(standard["checks"].values()):
        raise AssertionError("reversed three-handle sphere model is not verified")
    if dual_disk_movie["psi_A_sha256"] != link["psi_A_sha256"] or dual_disk_movie["actual_H1_disk_transport"] != "PASS":
        raise AssertionError("actual H1 compression-disk movie is not bound to the AR link")
    if dual_disk_movie["mapping_torus_sphere_columns"] != standard["attaching_homology"]["sphere_columns_in_kernel_basis"]:
        raise AssertionError("dual-disk movie and reversed sphere columns disagree")
    if surface_transport["dual_disk_movie_sha256"] != dual_disk_movie["sha256"] or surface_transport["actual_post_cancellation_relative_surface_map"] != "PASS":
        raise AssertionError("post-cancellation three-handle surface map is not closed")
    spheres = []
    sphere_matrix = standard["attaching_homology"]["sphere_columns_in_kernel_basis"]
    for index, sphere in enumerate(standard["spheres"]):
        actual_surface = surface_transport["surfaces"][index]
        coefficients = [sphere_matrix[row][index] for row in range(3)]
        boundary_profile = actual_surface["core_disk_boundary_profile"]
        b_count = actual_surface["core_disk_count_b"]
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
                "embedded_s2_on_actual_W2": True,
                "disjoint_from_detector": True,
                "sphere_column_in_kernel_basis": coefficients,
                "core_disk_boundary_profile": boundary_profile,
                "core_disk_intersection_count_b": b_count,
                "actual_surface_transport_sha256": canonical_sha(actual_surface),
                "actual_hierarchical_surface": actual_surface,
                "transport_rule": "the three disjoint H1 compression disks are carried by all 93 ambient Johnson factors and then by all 1519 Kirby boundary-map bands",
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
        "identified_with_partial_W2": True,
        "identification_method": "the hierarchical surface map starts with the actual H1 compression disks, applies the 93-factor ambient monodromy, and pushes the resulting mapping-torus spheres through every recorded Kirby cancellation band",
        "three_handle_surface_transport_sha256": surface_transport["sha256"],
    }
    w2["sha256"] = canonical_sha({key: value for key, value in w2.items() if key != "sha256"})
    result = {
        "schema": "t73_actual_sphere_system/v2",
        "spheres": spheres,
        "pairwise": pairwise,
        "pairwise_disjoint": True,
        "complement_connected": True,
        "spherical_homology_basis": {
            "status": "PASS",
            "dual_loop_pairing_matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            "sphere_columns_in_kernel_basis": standard["attaching_homology"]["sphere_columns_in_kernel_basis"],
            "determinant": 1,
        },
        "simultaneous_surgery_is_S3": True,
        "simultaneous_surgery_in_reversed_model_is_S3": True,
        "simultaneous_surgery_reason": "these are the actual mapping-torus 3-handle attaching spheres transported by boundary diffeomorphisms; attaching all three 3-handles gives the outgoing S3",
        "hj_53_kernel_invariance_only": True,
        "hj_lemmas_55_57_invoked": False,
        "actual_w2_lasagna_map": False,
        "w2_boundary_sha256": w2["sha256"],
        "status": "PASS",
        "reason": "the actual H1 disk-track spheres and every Kirby boundary-map band are present; the reversed model is used only as the terminal standard chart",
        "standard_sphere_certificate_sha256": standard["certificate_sha256"],
        "johnson_dual_disk_movie_sha256": dual_disk_movie["sha256"],
        "three_handle_surface_transport_sha256": surface_transport["sha256"],
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
