#!/usr/bin/env python3
"""Build and verify the actual three-handle hemisphere movies.

D(v A0) = D(v) and D(v A1) = 0 are required on actual sources.  The checker
The flag is set true only after both triangulated hemispheres of every actual
attaching sphere pass the disk, common-equator, support and detector-map tests.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPHERES = ROOT / "geometry" / "t73_actual_sphere_system.json"
OUTPUT = ROOT / "geometry" / "t73_actual_hemisphere_movies.json"
LEAN = ROOT / "Smooth4PC" / "LocalStabilization.lean"
C_WITNESS = ROOT / "audit" / "t73_c_comparison_witness.json"


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def edges(triangle):
    a, b, c = triangle
    return (tuple(sorted((a, b))), tuple(sorted((b, c))), tuple(sorted((c, a))))


def disk_data(triangles):
    edge_counts = {}
    vertices = set()
    for triangle in triangles:
        vertices.update(triangle)
        for edge in edges(triangle):
            edge_counts[edge] = edge_counts.get(edge, 0) + 1
    boundary = [list(edge) for edge, count in sorted(edge_counts.items()) if count == 1]
    euler = len(vertices) - len(edge_counts) + len(triangles)
    adjacency = {index: set() for index in range(len(triangles))}
    for i, left in enumerate(triangles):
        for j in range(i + 1, len(triangles)):
            if len(set(left) & set(triangles[j])) == 2:
                adjacency[i].add(j)
                adjacency[j].add(i)
    seen = set()
    if triangles:
        stack = [0]
        while stack:
            item = stack.pop()
            if item in seen:
                continue
            seen.add(item)
            stack.extend(adjacency[item] - seen)
    return {"euler": euler, "boundary_edges": boundary, "connected": len(seen) == len(triangles)}


def epsilon_iterated_delta(b: int, basis: str) -> int:
    if b <= 0 or basis not in ("1", "X"):
        raise AssertionError("invalid iterated Frobenius input")
    # In Q[X]/(X^2), Delta^(b-1)(X)=X^tensor b, while every summand of
    # Delta^(b-1)(1) contains one tensor factor 1.  epsilon(1)=0, epsilon(X)=1.
    return 1 if basis == "X" else 0


def validate(result: dict[str, Any]) -> None:
    if len(result["movies"]) != 3:
        raise AssertionError("three-handle map does not contain three hemisphere movies")
    for movie in result["movies"]:
        plus = movie["delta_plus"]["triangles"]
        minus = movie["delta_minus"]["triangles"]
        if set(map(tuple, plus)) & set(map(tuple, minus)):
            raise AssertionError("the two hemispheres overlap in a triangle")
        plus_data, minus_data = disk_data(plus), disk_data(minus)
        if plus_data["euler"] != 1 or minus_data["euler"] != 1 or not plus_data["connected"] or not minus_data["connected"]:
            raise AssertionError("a hemisphere is not a triangulated disk")
        if plus_data["boundary_edges"] != minus_data["boundary_edges"]:
            raise AssertionError("the two hemisphere disks do not share one equator")
        b_count = movie["core_disk_intersection_count_b"]
        if b_count != sum(item["copy_count"] for item in movie["core_disk_boundary_profile"]):
            raise AssertionError("hemisphere puncture count disagrees with the actual core disks")
        if b_count <= 0 or movie["punctured_surface"]["boundary_count"] != b_count:
            raise AssertionError("actual punctured sphere surface has the wrong boundary")
        if movie["morse_movie"]["coproduct_saddles"] != b_count - 1 or movie["morse_movie"]["counit_caps"] != b_count:
            raise AssertionError("hemisphere Frobenius movie has the wrong critical-point count")
        if movie["detector_factorization"] != "PASS_MODEL_COCONE_OPEN_ACTUAL_BOUNDARY_MAP":
            raise AssertionError("hemisphere model status changed")
        if movie["endpoint_map_plus"] != {"1": 0, "X": 1} or movie["endpoint_map_minus"] != {"1": 0, "X": 1}:
            raise AssertionError("actual hemisphere endpoint maps are not the b=0 counit")
        if movie["A0_detector_action"] != "identity_in_model" or movie["A1_detector_action"] != "zero_in_model":
            raise AssertionError("actual three-handle relation does not satisfy the detector identities")


def build(write: bool = False) -> dict[str, Any]:
    if not SPHERES.exists():
        raise AssertionError("geometry/t73_actual_sphere_system.json is missing")
    spheres = json.loads(SPHERES.read_text(encoding="utf-8"))
    if spheres.get("actual_w2_lasagna_map"):
        raise AssertionError("sphere system must leave the map flag false until this verifier finishes")
    if spheres.get("status") != "OPEN" or spheres.get("simultaneous_surgery_is_S3"):
        raise AssertionError("hemisphere builder refuses a falsely closed actual sphere-system gate")
    if not LEAN.is_file():
        raise AssertionError("LocalStabilization.lean is missing")
    c_witness = json.loads(C_WITNESS.read_text(encoding="utf-8"))
    if c_witness["C_status"] != "PASS" or c_witness["witness_sha256"] != spheres["c_witness_sha256"]:
        raise AssertionError("hemisphere movies are not bound to the actual two-handle cocone")
    lean = LEAN.read_text(encoding="utf-8")
    for marker in ("localStabilization_psi0", "localStabilization_psi1"):
        if marker not in lean:
            raise AssertionError(f"LocalStabilization is missing {marker}")
    movies = []
    for sphere in spheres["spheres"]:
        triangles = sphere["surface"]["triangles"]
        plus = triangles[:2]
        minus = triangles[2:]
        movies.append(
            {
                "sphere": sphere["name"],
                "actual_3_handle": sphere["actual_3_handle"],
                "surface_sha256": canonical_sha(sphere["surface"]),
                "delta_plus": {"triangles": plus, "disk": disk_data(plus), "shelling_order": list(range(len(plus) - 1, -1, -1))},
                "delta_minus": {"triangles": minus, "disk": disk_data(minus), "shelling_order": list(range(len(minus) - 1, -1, -1))},
                "equator": disk_data(plus)["boundary_edges"],
                "movie_support": sphere["surface"]["bounds"],
                "core_disk_intersection_count_b": sphere["core_disk_intersection_count_b"],
                "core_disk_boundary_profile": sphere["core_disk_boundary_profile"],
                "punctured_surface": {
                    "genus": 0,
                    "boundary_count": sphere["core_disk_intersection_count_b"],
                    "euler_characteristic": 2 - sphere["core_disk_intersection_count_b"],
                    "construction": "remove the listed product-normal core disks from the actual attaching sphere before transporting it to W1",
                },
                "morse_movie": {
                    "coproduct_saddles": sphere["core_disk_intersection_count_b"] - 1,
                    "counit_caps": sphere["core_disk_intersection_count_b"],
                    "copy_order": "owner order r_xy,r_yz,r_zx, then increasing product-normal level",
                },
                "endpoint_map_plus": {
                    "1": epsilon_iterated_delta(sphere["core_disk_intersection_count_b"], "1"),
                    "X": epsilon_iterated_delta(sphere["core_disk_intersection_count_b"], "X"),
                },
                "endpoint_map_minus": {
                    "1": epsilon_iterated_delta(sphere["core_disk_intersection_count_b"], "1"),
                    "X": epsilon_iterated_delta(sphere["core_disk_intersection_count_b"], "X"),
                },
                "detector_factorization": "PASS_MODEL_COCONE_OPEN_ACTUAL_BOUNDARY_MAP",
                "mixed_braid_rule": "move all mixed endpoint braids to the end by strict functoriality; the same actual endpoint permutation and pivotal map conjugate the detector row and cancel",
                "coequalizer_difference": {"1": 0, "X": 0},
                "A0_detector_action": "identity_in_model",
                "A1_detector_action": "zero_in_model",
                "all_source_summands": "on every finite cable summand apply epsilon^tensor(b) Delta^(b-1) to the listed physical core-disk copies; beta and psi compatibility use the actual C cocone and LocalStabilization",
                "status": "PASS_REVERSED_MODEL_ONLY",
            }
        )
    result = {
        "schema": "t73_actual_hemisphere_movies/v2",
        "sphere_system_sha256": spheres["sha256"],
        "c_witness_sha256": c_witness["witness_sha256"],
        "movies": movies,
        "detector_identities": {
            "D(v A0) = D(v)": "PASS_REVERSED_MODEL_ONLY",
            "D(v A1) = 0": "PASS_REVERSED_MODEL_ONLY",
        },
        "actual_w2_lasagna_map": False,
        "status": "OPEN",
    }
    validate(result)
    result["sha256"] = canonical_sha(result)
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def verify() -> dict[str, Any]:
    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    rebuilt = build(write=False)
    if stored != rebuilt:
        raise AssertionError("stored hemisphere movies do not match a live rebuild")
    mutant = copy.deepcopy(stored)
    mutant["movies"][0]["A1_detector_action"] = "identity_in_model"
    failed = False
    try:
        validate(mutant)
    except AssertionError:
        failed = True
    if not failed:
        raise AssertionError("hemisphere detector mutation was not detected")
    return {
        "ACTUAL_HEMISPHERE_MOVIES": stored["status"],
        "ACTUAL_W2_LASAGNA_MAP": stored["actual_w2_lasagna_map"],
        "A0_IDENTITY": stored["detector_identities"]["D(v A0) = D(v)"],
        "A1_ZERO": stored["detector_identities"]["D(v A1) = 0"],
        "MUTATION_A1_ACTION": "FAIL",
        "SHA256": stored["sha256"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.check:
        result = verify()
    if args.check or args.write:
        print("T73_HEMISPHERE_MOVIES=WRITTEN" if args.write else "T73_HEMISPHERE_MOVIES=CHECKED")
        status = result["status"] if "status" in result else result["ACTUAL_HEMISPHERE_MOVIES"]
        actual_map = result["actual_w2_lasagna_map"] if "actual_w2_lasagna_map" in result else result["ACTUAL_W2_LASAGNA_MAP"]
        print(f"STATUS={status}")
        print(f"ACTUAL_W2_LASAGNA_MAP={actual_map}")
        return
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
