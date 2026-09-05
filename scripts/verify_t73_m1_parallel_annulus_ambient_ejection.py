#!/usr/bin/env python3
"""Verify local cells of the compactly supported m1 annulus ejection."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_m1_parallel_annulus_ambient_ejection.json"
FRAME = ROOT / "geometry/t73_m1_parallel_annulus_tubular_frame.json"
CLEARANCE = ROOT / "audit/t73_m1_parallel_annulus_tubular_clearance_receipt.json"


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def determinant3(vectors, axes):
    matrix = [[vector[axis] for vector in vectors] for axis in axes]
    return matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]) - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0]) + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])


def verify():
    data = json.loads(DATA.read_text(encoding="utf-8")); frame = json.loads(FRAME.read_text(encoding="utf-8")); clearance = json.loads(CLEARANCE.read_text(encoding="utf-8"))
    if data["sha256"] != canonical_sha({key: value for key, value in data.items() if key != "sha256"}) or data["m1_parallel_annulus_tubular_frame_sha256"] != frame["sha256"] or data["m1_parallel_annulus_tubular_clearance_receipt_sha256"] != clearance["sha256"]:
        raise AssertionError("m1 ambient-ejection hashes changed")
    source = [point(value) for value in data["source_vertices"]]; target = [point(value) for value in data["target_vertex_images"]]; tetrahedra = data["tetrahedra"]
    if len(source) != 210 or len(target) != 210 or len(tetrahedra) != 408:
        raise AssertionError("m1 ambient-ejection cell counts changed")
    layer = 70
    if source[:layer] != target[:layer] or source[2 * layer:] != target[2 * layer:]:
        raise AssertionError("ambient-ejection support boundary is not fixed")
    displacement = point(data["outward_displacement"])
    if any(target[layer + index] != tuple(source[layer + index][axis] + displacement[axis] for axis in range(4)) for index in range(layer)):
        raise AssertionError("central annulus is not ejected by one outward level")
    ratios = Counter()
    for tetrahedron_index, tetrahedron in enumerate(tetrahedra):
        source_origin, target_origin = source[tetrahedron[0]], target[tetrahedron[0]]
        source_vectors = [tuple(source[index][axis] - source_origin[axis] for axis in range(4)) for index in tetrahedron[1:]]
        target_vectors = [tuple(target[index][axis] - target_origin[axis] for axis in range(4)) for index in tetrahedron[1:]]
        ratio = None
        for axes in combinations(range(4), 3):
            before = determinant3(source_vectors, axes)
            if before:
                after = determinant3(target_vectors, axes); ratio = after / before; break
        expected = Fraction(2) if tetrahedron_index < 204 else Fraction(1, 2)
        if ratio != expected or ratio <= 0:
            raise AssertionError("ambient-ejection tetrahedron reverses or has wrong slope")
        ratios[str(ratio)] += 1
    faces = Counter(tuple(sorted(face)) for tetrahedron in tetrahedra for face in combinations(tetrahedron, 3))
    if max(faces.values()) != 2 or any(count not in (1, 2) for count in faces.values()):
        raise AssertionError("ambient-ejection cells are not a pseudomanifold")
    if data["completion_status"] != "M1_PARALLEL_ANNULUS_AMBIENT_EJECTION_LOCAL_CELLS_CONSTRUCTED" or data["support_clearance_status"] != "OPEN_EXTENDED_MINUS1_TO2_TUBE_CLEARANCE":
        raise AssertionError("ambient-ejection scope changed")
    return {"verdict": "PASS_M1_PARALLEL_ANNULUS_AMBIENT_EJECTION_LOCAL_CELLS", "vertices": 210, "tetrahedra": 408, "slope_counts": dict(ratios), "fixed_boundary_vertices": 140, "moved_annulus_vertices": 70, "support_clearance_status": data["support_clearance_status"]}


if __name__ == "__main__": print(json.dumps(verify(), sort_keys=True))
