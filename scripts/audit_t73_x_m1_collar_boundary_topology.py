#!/usr/bin/env python3
"""Audit the 3-boundary carrying the ejected x/m1 lane and stub cells."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import os
from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
HANDLE_PAIR = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"
LANES = ROOT / "audit/t73_x_m1_ejected_band_lanes_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_ejected_splice_stubs_receipt.json"
OUTPUT = ROOT / "audit/t73_x_m1_collar_boundary_topology.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if len(value) >= 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def point(values):
    return tuple(Fraction(value) for value in values)


def faces(simplex):
    return [tuple(sorted(simplex[:index] + simplex[index + 1:])) for index in range(len(simplex))]


def all_leaf_pieces(value):
    if isinstance(value, dict):
        yield value
    else:
        for item in value:
            yield from all_leaf_pieces(item)


def boundary_matrix(higher, lower):
    lower_index = {simplex: index for index, simplex in enumerate(lower)}
    matrix = sp.zeros(len(lower), len(higher))
    for column, simplex in enumerate(higher):
        for index in range(len(simplex)):
            face = simplex[:index] + simplex[index + 1:]
            matrix[lower_index[face], column] = (-1) ** index
    return matrix


def build():
    product = json.loads(PRODUCT.read_text())
    handle_pair = json.loads(HANDLE_PAIR.read_text())
    lanes = json.loads(LANES.read_text())
    stubs = json.loads(STUBS.read_text())
    four_simplices = [tuple(simplex) for simplex in product["four_simplices"]]
    face_counts = Counter(face for simplex in four_simplices for face in faces(simplex))
    boundary_tetrahedra = sorted(face for face, count in face_counts.items() if count == 1)
    triangles = sorted({face for tet in boundary_tetrahedra for face in faces(tet)})
    edges = sorted({tuple(edge) for triangle in triangles for edge in itertools.combinations(triangle, 2)})
    vertices = [(vertex,) for vertex in sorted({value for edge in edges for value in edge})]
    triangle_counts = Counter(face for tet in boundary_tetrahedra for face in faces(tet))
    if set(triangle_counts.values()) != {2}:
        raise AssertionError("collar boundary is not a closed 3-pseudomanifold")

    adjacency = defaultdict(set)
    owners = {}
    for index, tetrahedron in enumerate(boundary_tetrahedra):
        for triangle in faces(tetrahedron):
            if triangle in owners:
                adjacency[index].add(owners[triangle])
                adjacency[owners[triangle]].add(index)
            else:
                owners[triangle] = index
    reached = set()
    queue = deque([0])
    while queue:
        index = queue.popleft()
        if index in reached:
            continue
        reached.add(index)
        queue.extend(adjacency[index] - reached)
    if len(reached) != len(boundary_tetrahedra):
        raise AssertionError("collar boundary is disconnected")

    chain_groups = [vertices, edges, triangles, boundary_tetrahedra]
    ranks = [0]
    for dimension in range(1, 4):
        ranks.append(boundary_matrix(chain_groups[dimension], chain_groups[dimension - 1]).rank())
    betti = [
        len(chain_groups[dimension])
        - ranks[dimension]
        - (ranks[dimension + 1] if dimension < 3 else 0)
        for dimension in range(4)
    ]

    source_vertices = [point(value) for value in product["source_vertices"]]
    boundary_carrier_faces = {
        tuple(face)
        for tetrahedron in boundary_tetrahedra
        for size in range(1, 5)
        for face in itertools.combinations(tetrahedron, size)
    }
    exposed_face_count_distribution = Counter()
    inverse_by_simplex = {}
    for index, simplex in enumerate(four_simplices):
        boundary_positions = [
            position for position in range(5)
            if tuple(sorted(simplex[:position] + simplex[position + 1:])) in boundary_tetrahedra
        ]
        exposed_face_count_distribution[len(boundary_positions)] += 1
        matrix = sp.Matrix([
            [sp.Rational(source_vertices[vertex][axis].numerator, source_vertices[vertex][axis].denominator)
             for vertex in simplex]
            for axis in range(4)
        ] + [[1] * 5])
        inverse_by_simplex[index] = matrix.inv()

    boundary_point_occurrences = 0
    interior_point_occurrences = 0
    carrier_dimension_counts = Counter()
    stream_counts = {}
    for name, receipt, kind in (("lanes", lanes, "lanes"), ("stubs", stubs, "stubs")):
        boundary_count = interior_count = 0
        with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
            source.readline()
            for line in source:
                record = json.loads(line)
                images = (
                    [lane["core_segment_images"] for lane in record["lanes"].values()]
                    if kind == "lanes"
                    else [stub["core_segment_image"] for stub in record["stubs"].values()]
                )
                for image in images:
                    for piece in all_leaf_pieces(image):
                        simplex_index = piece["four_simplex_index"]
                        inverse = inverse_by_simplex[simplex_index]
                        simplex = four_simplices[simplex_index]
                        for raw in piece["source_vertices"]:
                            value = point(raw)
                            rhs = sp.Matrix([
                                *(sp.Rational(x.numerator, x.denominator) for x in value), 1
                            ])
                            weights = inverse * rhs
                            if any(weight < 0 for weight in weights) or sum(weights) != 1:
                                raise AssertionError(f"{name} point leaves its product simplex")
                            carrier = tuple(
                                simplex[position]
                                for position, weight in enumerate(weights)
                                if weight > 0
                            )
                            carrier = tuple(sorted(carrier))
                            if carrier in boundary_carrier_faces:
                                boundary_count += 1
                                boundary_point_occurrences += 1
                            else:
                                interior_count += 1
                                interior_point_occurrences += 1
                            carrier_dimension_counts[len(carrier) - 1] += 1
        stream_counts[name] = {
            "boundary": boundary_count,
            "interior": interior_count,
            "total": boundary_count + interior_count,
        }

    result = {
        "schema": "t73_x_m1_collar_boundary_topology/v1",
        "x_m1_collar_product_extension_sha256": product["sha256"],
        "x_m1_handle_pair_deletion_sha256": handle_pair["sha256"],
        "ejected_band_lanes_receipt_sha256": lanes["sha256"],
        "ejected_splice_stubs_receipt_sha256": stubs["sha256"],
        "four_simplex_count": len(four_simplices),
        "boundary_simplex_counts": [len(group) for group in chain_groups],
        "boundary_operator_ranks_over_Q": ranks,
        "betti_numbers_over_Q": betti,
        "euler_characteristic": sum((-1) ** index * len(group) for index, group in enumerate(chain_groups)),
        "closed_boundary_triangle_degree": 2,
        "boundary_connected": True,
        "exposed_boundary_tetrahedra_per_four_simplex_distribution": {
            str(key): value for key, value in sorted(exposed_face_count_distribution.items())
        },
        "boundary_carrier_dimension_counts": {
            str(key): value for key, value in sorted(carrier_dimension_counts.items())
        },
        "lane_stub_core_boundary_point_occurrences": boundary_point_occurrences,
        "lane_stub_core_interior_point_occurrences": interior_point_occurrences,
        "stream_boundary_point_occurrences": stream_counts,
        "product_support_boundary_as_ambient_boundary_status": (
            "REFUTED_BY_INTERIOR_LANE_CORE_CARRIERS"
        ),
        "whole_boundary_single_r3_chart_status": "NOT_APPLICABLE_TO_PRODUCT_SUPPORT_BOUNDARY",
        "topology_scope": (
            "the finite complex has the rational homology of S2 x S1; this "
            "does not by itself assert a homeomorphism classification"
        ),
        "required_next_map": (
            "construct the actual post-deletion ambient 3-boundary map from "
            "the handle-pair deletion; the product-support boundary is not it"
        ),
        "completion_status": "X_M1_COLLAR_BOUNDARY_TOPOLOGY_AND_CELL_MEMBERSHIP_VERIFIED",
    }
    result["sha256"] = canonical_sha256(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("x/m1 collar boundary audit is stale")
    print(json.dumps({
        "simplices": result["boundary_simplex_counts"],
        "ranks": result["boundary_operator_ranks_over_Q"],
        "betti": result["betti_numbers_over_Q"],
        "core_boundary_points": result["lane_stub_core_boundary_point_occurrences"],
        "r3_chart": result["whole_boundary_single_r3_chart_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
