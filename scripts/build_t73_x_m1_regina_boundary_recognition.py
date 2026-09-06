#!/usr/bin/env python3
"""Recognize the x/m1 support and standard boundaries with Regina."""

from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path

import regina


ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
HANDLE_PAIR = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"
OUTPUT = ROOT / "audit/t73_x_m1_regina_boundary_recognition.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def boundary_tetrahedra(four_simplices):
    counts = collections.Counter(
        tuple(sorted(simplex[:index] + simplex[index + 1:]))
        for simplex in four_simplices
        for index in range(5)
    )
    return sorted(face for face, count in counts.items() if count == 1)


def regina_triangulation(tetrahedra):
    triangulation = regina.Triangulation3()
    regina_tetrahedra = [triangulation.newTetrahedron() for _ in tetrahedra]
    face_owners = {}
    for tetrahedron_index, tetrahedron in enumerate(tetrahedra):
        for omitted in range(4):
            face = tuple(
                vertex for index, vertex in enumerate(tetrahedron) if index != omitted
            )
            face_owners.setdefault(face, []).append((tetrahedron_index, omitted))
    for face, owners in face_owners.items():
        if len(owners) != 2:
            raise AssertionError("boundary triangle does not have two owners")
        (first, first_face), (second, second_face) = owners
        if regina_tetrahedra[first].adjacentTetrahedron(first_face):
            continue
        permutation = [
            tetrahedra[second].index(vertex) if vertex in face else second_face
            for vertex in tetrahedra[first]
        ]
        regina_tetrahedra[first].join(
            first_face,
            regina_tetrahedra[second],
            regina.Perm4(*permutation),
        )
    return triangulation


def summary(triangulation):
    simplified = regina.Triangulation3(triangulation)
    simplified.intelligentSimplify()
    return {
        "tetrahedra": triangulation.size(),
        "valid": triangulation.isValid(),
        "closed": triangulation.isClosed(),
        "connected": triangulation.isConnected(),
        "orientable": triangulation.isOrientable(),
        "homology": str(triangulation.homology()),
        "is_sphere": triangulation.isSphere(),
        "iso_sig": triangulation.isoSig(),
        "simplified_tetrahedra": simplified.size(),
        "simplified_iso_sig": simplified.isoSig(),
        "simplified_homology": str(simplified.homology()),
        "simplified_is_sphere": simplified.isSphere(),
    }


def build():
    product = json.loads(PRODUCT.read_text())
    handle_pair = json.loads(HANDLE_PAIR.read_text())
    support_tetrahedra = boundary_tetrahedra(
        [tuple(value) for value in product["four_simplices"]]
    )
    standard_tetrahedra = boundary_tetrahedra(
        [tuple(value) for value in handle_pair["standard_pair"]["union_four_simplices"]]
    )
    support = regina_triangulation(support_tetrahedra)
    standard = regina_triangulation(standard_tetrahedra)
    support_summands = support.summands()
    reference_s2xs1 = regina.Example3.s2xs1()
    reference_s3 = regina.Example3.threeSphere()
    if len(support_summands) != 1:
        raise AssertionError("support boundary does not have one prime summand")
    result = {
        "schema": "t73_x_m1_regina_boundary_recognition/v1",
        "regina_version": regina.versionString(),
        "x_m1_collar_product_extension_sha256": product["sha256"],
        "x_m1_handle_pair_deletion_sha256": handle_pair["sha256"],
        "support_boundary": summary(support),
        "support_prime_summands": [
            {
                "tetrahedra": summand.size(),
                "iso_sig": summand.isoSig(),
                "homology": str(summand.homology()),
                "orientable": summand.isOrientable(),
            }
            for summand in support_summands
        ],
        "regina_reference_s2xs1": {
            "tetrahedra": reference_s2xs1.size(),
            "iso_sig": reference_s2xs1.isoSig(),
        },
        "support_prime_isomorphic_to_reference_s2xs1": (
            support_summands[0].isIsomorphicTo(reference_s2xs1) is not None
        ),
        "standard_boundary": summary(standard),
        "regina_reference_s3": {
            "tetrahedra": reference_s3.size(),
            "iso_sig": reference_s3.isoSig(),
        },
        "standard_simplification_matches_reference_s3": (
            summary(standard)["simplified_iso_sig"] == reference_s3.isoSig()
        ),
        "completion_status": "REGINA_RECOGNIZES_SUPPORT_S2XS1_AND_STANDARD_S3",
        "verdict": "PASS_X_M1_REGINA_BOUNDARY_RECOGNITION",
    }
    result["sha256"] = canonical_sha256(result)
    return result


if __name__ == "__main__":
    result = build()
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "verdict": result["verdict"],
        "regina": result["regina_version"],
        "support_prime": result["support_prime_summands"],
        "standard_simplified": result["standard_boundary"]["simplified_iso_sig"],
    }, sort_keys=True))
