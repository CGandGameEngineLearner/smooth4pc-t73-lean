#!/usr/bin/env python3
"""Build a rational one-sided PL tubular frame of the full m1 parallel annulus."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
OUTPUT = ROOT / "geometry/t73_m1_parallel_annulus_tubular_frame.json"


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def determinant3(first, second, third, axes):
    matrix = [[value[axis] for value in (first, second, third)] for axis in axes]
    return (matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
            - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
            + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]))


def choose_outward(base, normals):
    for candidate in itertools.product(range(-3, 4), repeat=4):
        if not any(candidate):
            continue
        certificates = []
        for index in range(len(base) - 1):
            tangent = tuple(base[index + 1][axis] - base[index][axis] for axis in range(4))
            found = None
            for axes in itertools.combinations(range(4), 3):
                first = determinant3(tangent, normals[index], candidate, axes)
                second = determinant3(tangent, normals[index + 1], candidate, axes)
                if first and second and first * second > 0:
                    found = {"segment": index, "coordinate_minor": list(axes), "start_determinant": str(first), "end_determinant": str(second)}
                    break
            if found is None:
                break
            certificates.append(found)
        if len(certificates) == len(base) - 1:
            return tuple(Fraction(value) for value in candidate), certificates
    raise AssertionError("no small integer outward vector is transverse along m1")


def build():
    foliation = json.loads(FOLIATION.read_text(encoding="utf-8")); product = json.loads(PRODUCT.read_text(encoding="utf-8"))
    base = [point(value) for value in foliation["base_vertices"]]; normals = [point(value) for value in foliation["unit_normal_field"]]; outer = [point(value) for value in foliation["outer_vertices"]]
    outward, certificates = choose_outward(base, normals)
    epsilon = Fraction(foliation["unit_normal_field"][2][1]) / 1000
    displacement = tuple(epsilon * value for value in outward)
    source_vertices = base + outer
    pushed_vertices = [tuple(value[axis] + displacement[axis] for axis in range(4)) for value in source_vertices]
    vertices = source_vertices + pushed_vertices; offset = len(source_vertices)
    tetrahedra = []
    for triangle in foliation["triangles"]:
        a, b, c = sorted(triangle)
        tetrahedra.extend(((a, b, c, c + offset), (a, b, b + offset, c + offset), (a, a + offset, b + offset, c + offset)))
    result = {
        "schema": "t73_m1_parallel_annulus_tubular_frame/v1",
        "m1_parallel_foliation_sha256": foliation["sha256"],
        "x_m1_collar_product_extension_sha256": product["sha256"],
        "outward_integer_vector": encode(outward),
        "outward_scale": str(epsilon),
        "outward_displacement": encode(displacement),
        "segment_transversality_certificates": certificates,
        "source_annulus_vertices": [encode(value) for value in source_vertices],
        "pushed_annulus_vertices": [encode(value) for value in pushed_vertices],
        "annulus_triangles": foliation["triangles"],
        "tubular_vertices": [encode(value) for value in vertices],
        "tubular_tetrahedra": [list(value) for value in tetrahedra],
        "source_vertex_count": len(source_vertices),
        "tubular_vertex_count": len(vertices),
        "annulus_triangle_count": len(foliation["triangles"]),
        "tubular_tetrahedron_count": len(tetrahedra),
        "mapping_torus_seam_deck": [-1, 0, 1, 0],
        "completion_status": "M1_PARALLEL_ANNULUS_LOCAL_TUBULAR_FRAME_CONSTRUCTED",
        "nonlocal_tetrahedron_clearance_status": "OPEN_EXACT_NONINCIDENT_CELL_CHECK",
    }
    result["sha256"] = canonical_sha(result); return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args(); result = build()
    if args.write: OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result: raise AssertionError("m1 tubular frame is stale")
    print(f"T73_M1_TUBULAR_FRAME={result['completion_status']}")


if __name__ == "__main__": main()
