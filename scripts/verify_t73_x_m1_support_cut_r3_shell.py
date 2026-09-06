#!/usr/bin/env python3
"""Verify the exact R3 cubical-shell realization of the support cut."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_support_cut_r3_shell.json"
CUT = ROOT / "geometry/t73_x_m1_support_generator_sphere_cut.json"
REGINA = ROOT / "audit/t73_x_m1_support_generator_sphere_cut_regina_verification.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def det(a, b, c, d):
    rows = [[b[i] - a[i], c[i] - a[i], d[i] - a[i]] for i in range(3)]
    return (
        rows[0][0] * (rows[1][1] * rows[2][2] - rows[1][2] * rows[2][1])
        - rows[0][1] * (rows[1][0] * rows[2][2] - rows[1][2] * rows[2][0])
        + rows[0][2] * (rows[1][0] * rows[2][1] - rows[1][1] * rows[2][0])
    )


def verify():
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("support-cut R3 shell payload SHA mismatch")
    cut = json.loads(CUT.read_text())
    regina = json.loads(REGINA.read_text())
    if data["support_generator_sphere_cut_sha256"] != cut["sha256"]:
        raise AssertionError("support-cut shell cut binding changed")
    if data["support_cut_regina_verification_sha256"] != regina["sha256"]:
        raise AssertionError("support-cut shell Regina binding changed")
    vertices = [tuple(Fraction(value) for value in point) for point in data["vertices"]]
    tetrahedra = [tuple(value) for value in data["tetrahedra"]]
    if len(vertices) != 40 or tetrahedra != [tuple(value) for value in cut["cut_tetrahedra"]]:
        raise AssertionError("support-cut shell incidence changed")
    determinants = [det(*(vertices[index] for index in tetrahedron)) for tetrahedron in tetrahedra]
    if any(value == 0 for value in determinants):
        raise AssertionError("support-cut R3 tetrahedron degenerated")
    if sum(abs(value) for value in determinants) / 6 != 992:
        raise AssertionError("support-cut R3 exact volume changed")
    face_counts = Counter(
        tuple(sorted(face))
        for tetrahedron in tetrahedra
        for face in itertools.combinations(tetrahedron, 3)
    )
    boundary = [face for face, count in face_counts.items() if count == 1]
    if len(boundary) != 24 or set(face_counts.values()) != {1, 2}:
        raise AssertionError("support-cut shell boundary incidence changed")
    if data["recognized_topological_type"] != "S2 x I":
        raise AssertionError("support-cut R3 shell topology changed")
    return {
        "verdict": "PASS_X_M1_SUPPORT_CUT_EXACT_R3_SHELL",
        "vertices": 40,
        "tetrahedra": 144,
        "nonzero_exact_determinants": 144,
        "exact_volume": "992",
        "boundary_spheres": 2,
        "recognized_type": "S2 x I",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
