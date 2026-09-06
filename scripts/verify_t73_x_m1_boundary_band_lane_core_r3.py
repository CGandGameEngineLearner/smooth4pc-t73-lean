#!/usr/bin/env python3
"""Independently verify the complete boundary-carried band lane in R3."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_boundary_band_lane_core_r3.json"
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
CUT = ROOT / "geometry/t73_x_m1_support_generator_sphere_cut.json"
SHELL = ROOT / "geometry/t73_x_m1_support_cut_r3_shell.json"
LANES = ROOT / "audit/t73_x_m1_ejected_band_lanes_receipt.json"


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


def point(values):
    return tuple(Fraction(value) for value in values)


def verify():
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("boundary lane R3 payload SHA mismatch")
    product = json.loads(PRODUCT.read_text())
    cut = json.loads(CUT.read_text())
    shell = json.loads(SHELL.read_text())
    lanes = json.loads(LANES.read_text())
    bindings = {
        "collar_product_sha256": product["sha256"],
        "support_generator_sphere_cut_sha256": cut["sha256"],
        "support_cut_r3_shell_sha256": shell["sha256"],
        "ejected_band_lanes_receipt_sha256": lanes["sha256"],
    }
    if any(data[key] != value for key, value in bindings.items()):
        raise AssertionError("boundary lane R3 source binding changed")

    # A distinct direct test finds boundary pieces from target coordinates:
    # the entire open segment lies on the exposed outer cubical shell.
    boundary_sources = {}
    total = 0
    with gzip.open(resolve(lanes["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            for lane_name, lane in record["lanes"].items():
                for segment_index, group in enumerate(lane["core_segment_images"]):
                    for piece_index, piece in enumerate(group):
                        total += 1
                        endpoints = [point(value) for value in piece["target_vertices"]]
                        midpoint = tuple(sum(pair) / 2 for pair in zip(*endpoints))
                        if max(abs(value) for value in midpoint[1:]) == Fraction(3, 2):
                            key = (record["band_index"], record["component"], lane_name, segment_index, piece_index)
                            boundary_sources[key] = piece
    if total != 15158 or len(boundary_sources) != 7:
        raise AssertionError("direct boundary lane-piece inventory changed")

    simplices = [tuple(value) for value in product["four_simplices"]]
    source_vertices = [point(value) for value in product["source_vertices"]]
    shell_vertices = [point(value) for value in shell["vertices"]]
    duplicate = dict(cut["cut_duplicate_vertex_map"])
    replayed_vertices = []
    for index, saved in enumerate(data["boundary_pieces"]):
        key = (
            saved["band_index"], saved["component"], saved["lane"],
            saved["source_segment_index"], saved["piece_index"],
        )
        if key not in boundary_sources:
            raise AssertionError("saved boundary lane piece is absent from direct scan")
        source_piece = boundary_sources[key]
        if (
            saved["source_four_simplex_index"] != source_piece["four_simplex_index"]
            or saved["source_parameter_interval"] != source_piece["parameter_interval"]
        ):
            raise AssertionError("boundary lane source provenance changed")
        simplex = simplices[source_piece["four_simplex_index"]]
        matrix = sp.Matrix([
            [sp.Rational(source_vertices[vertex][axis].numerator, source_vertices[vertex][axis].denominator)
             for vertex in simplex]
            for axis in range(4)
        ] + [[1] * 5])
        mapped = []
        for raw in source_piece["source_vertices"]:
            value = point(raw)
            rhs = sp.Matrix([
                *(sp.Rational(item.numerator, item.denominator) for item in value), 1
            ])
            weights = matrix.gauss_jordan_solve(rhs)[0]
            coordinates = []
            for axis in range(3):
                coordinate = sum(
                    weights[local] * sp.Rational(
                        shell_vertices[duplicate.get(vertex, vertex)][axis].numerator,
                        shell_vertices[duplicate.get(vertex, vertex)][axis].denominator,
                    )
                    for local, vertex in enumerate(simplex)
                )
                coordinates.append(str(Fraction(int(coordinate.p), int(coordinate.q))))
            mapped.append(coordinates)
        if mapped != saved["r3_vertices"]:
            raise AssertionError("boundary lane R3 barycentric image changed")
        if index and replayed_vertices[-1] != mapped[0]:
            raise AssertionError("boundary lane R3 pieces are discontinuous")
        if not replayed_vertices:
            replayed_vertices.append(mapped[0])
        replayed_vertices.append(mapped[1])
    if replayed_vertices != data["complete_boundary_lane"]["r3_vertices"]:
        raise AssertionError("assembled boundary lane changed")
    if data["interior_core_piece_count"] != 15151 or data["mapped_push_status"] != "OPEN":
        raise AssertionError("boundary lane scope was overstated")
    return {
        "verdict": "PASS_X_M1_BOUNDARY_BAND_LANE_CORE_R3_FULL",
        "total_lane_core_pieces_scanned": total,
        "mapped_boundary_pieces": len(boundary_sources),
        "interior_pieces": total - len(boundary_sources),
        "complete_lane": "band0/positive_band_lane",
        "r3_continuity_checks": 6,
        "mapped_push": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
