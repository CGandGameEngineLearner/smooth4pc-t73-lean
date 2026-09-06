#!/usr/bin/env python3
"""Independently check collar-support topology and lane/stub carrier counts."""

from __future__ import annotations

import gzip
import hashlib
import itertools
import json
import os
from collections import Counter
from fractions import Fraction
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_collar_boundary_topology.json"
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
LANES = ROOT / "audit/t73_x_m1_ejected_band_lanes_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_ejected_splice_stubs_receipt.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    return path


def faces(simplex):
    return [tuple(sorted(simplex[:index] + simplex[index + 1:])) for index in range(len(simplex))]


def boundary_rank(higher, lower):
    index = {simplex: row for row, simplex in enumerate(lower)}
    matrix = sp.zeros(len(lower), len(higher))
    for column, simplex in enumerate(higher):
        for omitted in range(len(simplex)):
            matrix[index[simplex[:omitted] + simplex[omitted + 1:]], column] = (-1) ** omitted
    return matrix.rank()


def leaves(value):
    if isinstance(value, dict):
        yield value
    else:
        for item in value:
            yield from leaves(item)


def direct_outer_shell_count(receipt, kind):
    total = outer = 0
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            images = (
                [value["core_segment_images"] for value in record["lanes"].values()]
                if kind == "lanes"
                else [value["core_segment_image"] for value in record["stubs"].values()]
            )
            for image in images:
                for piece in leaves(image):
                    for raw in piece["target_vertices"]:
                        value = [Fraction(coordinate) for coordinate in raw]
                        total += 1
                        if max(abs(coordinate) for coordinate in value[1:]) == Fraction(3, 2):
                            outer += 1
    return total, outer


def verify():
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("collar-boundary topology payload SHA mismatch")
    product = json.loads(PRODUCT.read_text())
    lanes = json.loads(LANES.read_text())
    stubs = json.loads(STUBS.read_text())
    if data["x_m1_collar_product_extension_sha256"] != product["sha256"]:
        raise AssertionError("collar-boundary product binding changed")

    four = [tuple(simplex) for simplex in product["four_simplices"]]
    facet_counts = Counter(face for simplex in four for face in faces(simplex))
    tetrahedra = sorted(face for face, count in facet_counts.items() if count == 1)
    triangles = sorted({face for tetrahedron in tetrahedra for face in faces(tetrahedron)})
    edges = sorted({tuple(edge) for triangle in triangles for edge in itertools.combinations(triangle, 2)})
    vertices = [(value,) for value in sorted({vertex for edge in edges for vertex in edge})]
    groups = [vertices, edges, triangles, tetrahedra]
    ranks = [0] + [boundary_rank(groups[index], groups[index - 1]) for index in range(1, 4)]
    betti = [len(groups[index]) - ranks[index] - (ranks[index + 1] if index < 3 else 0) for index in range(4)]
    if [len(group) for group in groups] != [32, 176, 288, 144]:
        raise AssertionError("collar-support boundary inventory changed")
    if ranks != [0, 31, 144, 143] or betti != [1, 1, 1, 1]:
        raise AssertionError("collar-support boundary homology changed")

    lane_total, lane_outer = direct_outer_shell_count(lanes, "lanes")
    stub_total, stub_outer = direct_outer_shell_count(stubs, "stubs")
    if (lane_total, lane_outer, stub_total, stub_outer) != (30316, 6064, 21164, 21164):
        raise AssertionError("direct target-shell membership counts changed")
    if data["lane_stub_core_boundary_point_occurrences"] != lane_outer + stub_outer:
        raise AssertionError("barycentric and direct boundary counts disagree")
    if data["lane_stub_core_interior_point_occurrences"] != lane_total - lane_outer:
        raise AssertionError("barycentric and direct interior counts disagree")
    if data["product_support_boundary_as_ambient_boundary_status"] != "REFUTED_BY_INTERIOR_LANE_CORE_CARRIERS":
        raise AssertionError("support boundary was overstated as ambient boundary")
    return {
        "verdict": "PASS_X_M1_COLLAR_SUPPORT_BOUNDARY_TOPOLOGY_AUDIT",
        "boundary_simplex_counts": [32, 176, 288, 144],
        "betti_numbers_over_Q": [1, 1, 1, 1],
        "boundary_core_point_occurrences": lane_outer + stub_outer,
        "interior_lane_core_point_occurrences": lane_total - lane_outer,
        "product_support_is_ambient_boundary": False,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
