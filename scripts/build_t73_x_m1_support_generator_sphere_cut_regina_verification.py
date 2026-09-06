#!/usr/bin/env python3
"""Use Regina to recognize the cut support as S2 x I."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import regina


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_support_generator_sphere_cut.json"
VERIFIER = ROOT / "scripts/verify_t73_x_m1_support_generator_sphere_cut.py"
OUTPUT = ROOT / "audit/t73_x_m1_support_generator_sphere_cut_regina_verification.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def triangulation(tetrahedra):
    result = regina.Triangulation3()
    regina_tetrahedra = [result.newTetrahedron() for _ in tetrahedra]
    owners = {}
    for tetrahedron_index, tetrahedron in enumerate(tetrahedra):
        for omitted in range(4):
            face = tuple(vertex for index, vertex in enumerate(tetrahedron) if index != omitted)
            owners.setdefault(face, []).append((tetrahedron_index, omitted))
    for face, records in owners.items():
        if len(records) == 1:
            continue
        if len(records) != 2:
            raise AssertionError("triangular face has invalid degree")
        (first, first_face), (second, second_face) = records
        if regina_tetrahedra[first].adjacentTetrahedron(first_face):
            continue
        permutation = [
            tetrahedra[second].index(vertex) if vertex in face else second_face
            for vertex in tetrahedra[first]
        ]
        regina_tetrahedra[first].join(
            first_face, regina_tetrahedra[second], regina.Perm4(*permutation)
        )
    return result


def main():
    data = json.loads(DATA.read_text())
    cut = triangulation([tuple(value) for value in data["cut_tetrahedra"]])
    capped = triangulation([tuple(value) for value in data["capped_tetrahedra"]])
    simplified = regina.Triangulation3(capped)
    simplified.intelligentSimplify()
    reference_s3 = regina.Example3.threeSphere()
    result = {
        "schema": "t73_x_m1_support_generator_sphere_cut_regina_verification/v1",
        "support_generator_sphere_cut_sha256": data["sha256"],
        "combinatorial_verifier_path": str(VERIFIER.relative_to(ROOT)).replace("\\", "/"),
        "combinatorial_verifier_sha256": hashlib.sha256(VERIFIER.read_bytes()).hexdigest().upper(),
        "regina_version": regina.versionString(),
        "cut": {
            "tetrahedra": cut.size(),
            "valid": cut.isValid(),
            "connected": cut.isConnected(),
            "orientable": cut.isOrientable(),
            "closed": cut.isClosed(),
            "boundary_components": cut.countBoundaryComponents(),
            "has_two_sphere_boundary_components": cut.hasTwoSphereBoundaryComponents(),
            "homology_h1": str(cut.homology()),
            "relative_homology_h1": str(cut.homologyRel()),
            "iso_sig": cut.isoSig(),
        },
        "capped": {
            "tetrahedra": capped.size(),
            "valid": capped.isValid(),
            "closed": capped.isClosed(),
            "connected": capped.isConnected(),
            "orientable": capped.isOrientable(),
            "homology": str(capped.homology()),
            "is_sphere": capped.isSphere(),
            "iso_sig": capped.isoSig(),
            "simplified_tetrahedra": simplified.size(),
            "simplified_iso_sig": simplified.isoSig(),
            "reference_s3_iso_sig": reference_s3.isoSig(),
        },
        "cut_recognized_type": "S2 x I",
        "recognition_argument": (
            "the connected cut has exactly two S2 boundary components, and "
            "coning both boundary spheres produces Regina-recognized S3; "
            "removing the two cap balls from S3 gives S2 x I"
        ),
        "verdict": "PASS_X_M1_SUPPORT_CUT_IS_S2_X_I_REGINA",
    }
    if not (
        result["cut"]["valid"]
        and result["cut"]["connected"]
        and result["cut"]["boundary_components"] == 2
        and result["cut"]["has_two_sphere_boundary_components"]
        and result["capped"]["valid"]
        and result["capped"]["is_sphere"]
        and result["capped"]["simplified_iso_sig"] == reference_s3.isoSig()
    ):
        raise AssertionError("Regina support-cut recognition failed")
    result["sha256"] = canonical_sha256(result)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "verdict": result["verdict"],
        "regina": result["regina_version"],
        "cut_boundary_components": result["cut"]["boundary_components"],
        "capped_sphere": result["capped"]["is_sphere"],
        "capped_simplified": result["capped"]["simplified_iso_sig"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
