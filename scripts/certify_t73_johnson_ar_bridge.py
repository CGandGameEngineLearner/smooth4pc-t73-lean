#!/usr/bin/env python3
"""Certified simplicial map of Johnson's T^3 onto the AR coordinate torus.

Johnson, Pacific J. Math. 253 (2011), defines the genus-three splitting of
T^3 = R^3/Z^3 as the Euclidean Voronoi pair of the spines K1 (the three
coordinate circles through 0) and K2 (the same circles translated by
(1/2,1/2,1/2)).  Aitchison--Rubinstein use period-two coordinate spines
through Q = (-1/2,-1/2,-1/2) and Qbar = (1/2,1/2,1/2) on R^3/(2Z)^3.

This program exhibits an orientation-preserving affine map on Freudenthal
triangulations that carries every 1-simplex of those spines onto the
corresponding AR spine.  It also records the algebraic identity that this
map is a similarity, so it carries Johnson's Voronoi handlebodies onto the
Voronoi cells of the image spines.

The committed 384-tetrahedron Freudenthal torus now carries an explicit
discrete-Voronoi Heegaard pair of those spines, and the same assignment on
the period-4 Johnson mesh is carried onto that pair by T(v)=v-(1,1,1).
Uniqueness of regular neighborhoods is not used.  The Euclidean Voronoi
surface is not a subcomplex; that mapping-torus identification is a
separate remark, not the Johnson-replacement P0a object.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from typing import Any
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_spine_stars():
    path = ROOT / "scripts" / "certify_t73_spine_star_handlebodies.py"
    spec = importlib.util.spec_from_file_location("spine_stars", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def add(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def det3(rows: list[list[int]]) -> int:
    return (
        rows[0][0] * (rows[1][1] * rows[2][2] - rows[1][2] * rows[2][1])
        - rows[0][1] * (rows[1][0] * rows[2][2] - rows[1][2] * rows[2][0])
        + rows[0][2] * (rows[1][0] * rows[2][1] - rows[1][1] * rows[2][0])
    )


def tet_volume6(tet: list[tuple[int, int, int]]) -> int:
    base = tet[0]
    rows = [[tet[i][j] - base[j] for j in range(3)] for i in range(1, 4)]
    return det3(rows)


def scaled_map(point: tuple[int, int, int]) -> tuple[int, int, int]:
    """Integer model of S(u)=2u-(1/2,1/2,1/2) after the uniform scale u |-> 2u."""
    return (2 * point[0] - 1, 2 * point[1] - 1, 2 * point[2] - 1)


def original_map(point: tuple[Fraction, Fraction, Fraction]) -> tuple[Fraction, Fraction, Fraction]:
    return (
        2 * point[0] - Fraction(1, 2),
        2 * point[1] - Fraction(1, 2),
        2 * point[2] - Fraction(1, 2),
    )


def freudenthal_cube(origin: tuple[int, int, int]) -> list[list[tuple[int, int, int]]]:
    axes = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    tetrahedra = []
    for permutation in itertools.permutations(range(3)):
        v0 = origin
        v1 = add(v0, axes[permutation[0]])
        v2 = add(v1, axes[permutation[1]])
        v3 = add(v2, axes[permutation[2]])
        tetrahedra.append([v0, v1, v2, v3])
    return tetrahedra


def spine_edges(base: tuple[int, int, int], period: int) -> list[dict[str, Any]]:
    edges = []
    for axis in range(3):
        point = list(base)
        for step in range(period):
            start = tuple(point)
            point[axis] += 1
            end = tuple(point)
            edges.append({"axis": axis, "start": list(start), "end": list(end)})
        if tuple(point)[axis] - base[axis] != period:
            raise AssertionError("spine period is incomplete")
    return edges


def on_axis_circle(point: tuple[int, int, int], base: tuple[int, int, int], axis: int) -> bool:
    return all(point[i] == base[i] for i in range(3) if i != axis)


def generate():
    johnson_tets = []
    for origin in itertools.product(range(0, 2), repeat=3):
        johnson_tets.extend(freudenthal_cube(tuple(origin)))
    if len(johnson_tets) != 48:
        raise AssertionError("unexpected Johnson Freudenthal count")
    if any(tet_volume6(tet) == 0 for tet in johnson_tets):
        raise AssertionError("Johnson tetrahedron is degenerate")

    image_tets = [[scaled_map(vertex) for vertex in tet] for tet in johnson_tets]
    if any(tet_volume6(tet) != 8 * tet_volume6(source) for source, tet in zip(johnson_tets, image_tets)):
        raise AssertionError("image volumes are not scaled by det=8")
    if any(tet_volume6(source) * tet_volume6(image) <= 0 for source, image in zip(johnson_tets, image_tets)):
        raise AssertionError("simplicial map reverses a tetrahedron")

    displacement_checks = []
    origin = (0, 0, 0)
    for axis, unit in enumerate(((1, 0, 0), (0, 1, 0), (0, 0, 1))):
        image_unit = tuple(scaled_map(unit)[i] - scaled_map(origin)[i] for i in range(3))
        expected = (2 if i == axis else 0 for i in range(3))
        if image_unit != tuple(expected):
            raise AssertionError("linear part is not 2I")
        period_image = tuple(
            scaled_map(tuple(2 if i == axis else 0 for i in range(3)))[j] - scaled_map(origin)[j]
            for j in range(3)
        )
        if period_image != tuple(4 if i == axis else 0 for i in range(3)):
            raise AssertionError("period-1 lattice is not carried onto the period-2 lattice")
        displacement_checks.append(
            {
                "axis": axis,
                "scaled_unit_image": list(image_unit),
                "scaled_period_image": list(period_image),
            }
        )

    k1_edges = spine_edges((0, 0, 0), period=2)
    k2_edges = spine_edges((1, 1, 1), period=2)
    ar_q = (-1, -1, -1)
    ar_qbar = (1, 1, 1)
    mapped_k1 = []
    mapped_k2 = []
    for edge in k1_edges:
        start = scaled_map(tuple(edge["start"]))
        end = scaled_map(tuple(edge["end"]))
        if not on_axis_circle(start, ar_q, edge["axis"]) or not on_axis_circle(end, ar_q, edge["axis"]):
            raise AssertionError("a K1 edge does not land on the AR L_B circle")
        mapped_k1.append({"axis": edge["axis"], "start": list(start), "end": list(end)})
    for edge in k2_edges:
        start = scaled_map(tuple(edge["start"]))
        end = scaled_map(tuple(edge["end"]))
        if not on_axis_circle(start, ar_qbar, edge["axis"]) or not on_axis_circle(end, ar_qbar, edge["axis"]):
            raise AssertionError("a K2 edge does not land on the AR L_D circle")
        mapped_k2.append({"axis": edge["axis"], "start": list(start), "end": list(end)})

    # Recorded uniform radius from the 93-step inverse-basis bound.
    protected_radius = Fraction(1, 196104)
    image_radius = 2 * protected_radius
    # Distance from Q to the dual spine L_D is sqrt(2) in original AR coordinates.
    if image_radius * image_radius >= 2:
        raise AssertionError("image protected ball meets the dual AR spine")

    cube_half = Fraction(1, 400000)
    if 3 * cube_half * cube_half >= protected_radius * protected_radius:
        raise AssertionError("PL core cube is not inside the Johnson protected ball")
    cube_vertices = [
        [sign0 * cube_half, sign1 * cube_half, sign2 * cube_half]
        for sign0, sign1, sign2 in itertools.product((-1, 1), repeat=3)
    ]
    cube_images = [list(original_map(tuple(vertex))) for vertex in cube_vertices]
    stars = load_spine_stars().generate()
    origin_frac = (Fraction(0), Fraction(0), Fraction(0))
    q_original = original_map(origin_frac)
    if q_original != (Fraction(-1, 2), Fraction(-1, 2), Fraction(-1, 2)):
        raise AssertionError("origin is not sent to AR vertex Q")
    half = original_map((Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)))
    if half != (Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)):
        raise AssertionError("Johnson dual vertex is not sent to AR vertex Qbar")

    tet_digest = canonical_sha(
        {
            "johnson_tets": [[list(v) for v in tet] for tet in johnson_tets],
            "image_tets": [[list(v) for v in tet] for tet in image_tets],
        }
    )
    result: dict[str, Any] = {
        "schema": "t73_johnson_ar_pl_bridge/v2",
        "formula_original": "S(u)=2u-(1/2,1/2,1/2)",
        "formula_scaled": "T(u)=2u-(1,1,1) on the uniform scale u |-> 2u",
        "johnson_period_scaled": 2,
        "ar_period_scaled": 4,
        "linear_determinant": 8,
        "orientation_preserving": True,
        "K1_vertex_image": ["-1/2", "-1/2", "-1/2"],
        "K2_vertex_image": ["1/2", "1/2", "1/2"],
        "expected_LB_vertex": ["-1/2", "-1/2", "-1/2"],
        "expected_LD_vertex": ["1/2", "1/2", "1/2"],
        "axis_images": displacement_checks,
        "johnson_spine_edges_scaled": k1_edges + k2_edges,
        "ar_spine_edge_images_scaled": mapped_k1 + mapped_k2,
        "johnson_tetrahedron_count": len(johnson_tets),
        "image_tetrahedron_count": len(image_tets),
        "tetrahedra_sha256": tet_digest,
        "spine_one_complex_map": "PASS",
        "ambient_simplicial_map": "PASS",
        "johnson_voronoi_to_image_spine_voronoi": (
            "ALGEBRAIC_SIMILARITY_ONLY: ||S(p)-S(q)||=2||p-q|| on R^3 and "
            "S(Z^3)+(1/2,1/2,1/2)=(2Z)^3, so torus distances scale by 2 and "
            "Johnson Voronoi cells map onto Voronoi cells of the image spines. "
            "This does not identify AR mapping-torus handlebodies."
        ),
        "ar_handlebody_as_certified_complex": stars["ar_handlebody_as_certified_complex"],
        "spine_star_complex_status": stars["star_complex_status"],
        "spine_star_certificate_sha256": stars["certificate_sha256"],
        "spine_star_L_B_tetrahedra": stars["star_L_B_tetrahedron_count"],
        "spine_star_L_D_tetrahedra": stars["star_L_D_tetrahedron_count"],
        "handlebody_L_B_tetrahedra": stars["handlebody_L_B_tetrahedron_count"],
        "handlebody_L_D_tetrahedra": stars["handlebody_L_D_tetrahedron_count"],
        "equatorial_tets_unsplit": stars["equatorial_tets_touching_both_stars"],
        "spine_stars_fill_torus": stars["fills_torus"],
        "s_maps_johnson_pair_onto_ar_pair": stars["s_maps_johnson_pair_onto_ar_pair"],
        "interface_triangle_count": stars["interface_triangle_count"],
        "euclidean_voronoi_surface_as_subcomplex": stars["euclidean_voronoi_surface_as_subcomplex"],
        "mapping_torus_handlebody_identification": stars["mapping_torus_handlebody_identification"],
        "uniqueness_of_regular_neighborhoods_used": False,
        "protected_ball_center_original": ["-1/2", "-1/2", "-1/2"],
        "johnson_protected_ball_radius": str(protected_radius),
        "image_protected_ball_radius": str(image_radius),
        "protected_metric_ball_map": (
            "S sends the Euclidean ball of the recorded Johnson radius about 0 "
            "to the Euclidean ball of twice that radius about Q"
        ),
        "protected_pl_core_cube_half_side": str(cube_half),
        "protected_pl_core_vertices": [[str(x) for x in vertex] for vertex in cube_vertices],
        "protected_pl_core_images": [[str(x) for x in vertex] for vertex in cube_images],
        "heegaard_handlebody_complex": stars["heegaard_handlebody_complex"],
        "obstruction": stars["obstruction"],
        "p0a_status": stars["p0a_status"],
        "bridge_status": "PASS",
    }
    result["bridge_sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.check:
        print("T73_JOHNSON_AR_BRIDGE=PASS")
        print(f"P0A_STATUS={result['p0a_status']}")
        print(f"SPINE_ONE_COMPLEX_MAP={result['spine_one_complex_map']}")
        print(f"AMBIENT_SIMPLICIAL_MAP={result['ambient_simplicial_map']}")
        print(f"STAR_COMPLEX={result['spine_star_complex_status']}")
        print(f"HEEGAARD_COMPLEX={result['heegaard_handlebody_complex']}")
        print(f"AR_HANDLEBODY_COMPLEX={result['ar_handlebody_as_certified_complex']}")
        print(f"S_MAPS_PAIR={result['s_maps_johnson_pair_onto_ar_pair']}")
        print(f"FILLS_TORUS={result['spine_stars_fill_torus']}")
        print(f"EQUATORIAL_UNSPLIT={result['equatorial_tets_unsplit']}")
        print(f"K1_TO_LB={result['K1_vertex_image']}")
        print(f"K2_TO_LD={result['K2_vertex_image']}")
        print(f"BRIDGE_STATUS={result['bridge_status']}")
        print(f"BRIDGE_SHA256={result['bridge_sha256']}")
        print(f"OBSTRUCTION={result['obstruction']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
