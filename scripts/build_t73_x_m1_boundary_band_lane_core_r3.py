#!/usr/bin/env python3
"""Map the complete boundary-carried x-band lane into the cut R3 shell."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import os
from fractions import Fraction
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
CUT = ROOT / "geometry/t73_x_m1_support_generator_sphere_cut.json"
SHELL = ROOT / "geometry/t73_x_m1_support_cut_r3_shell.json"
TOPOLOGY = ROOT / "audit/t73_x_m1_collar_boundary_topology.json"
LANES = ROOT / "audit/t73_x_m1_ejected_band_lanes_receipt.json"
OUTPUT = ROOT / "geometry/t73_x_m1_boundary_band_lane_core_r3.json"


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


def build():
    product = json.loads(PRODUCT.read_text())
    cut = json.loads(CUT.read_text())
    shell = json.loads(SHELL.read_text())
    topology = json.loads(TOPOLOGY.read_text())
    lanes = json.loads(LANES.read_text())
    simplices = [tuple(value) for value in product["four_simplices"]]
    source_vertices = [point(value) for value in product["source_vertices"]]
    shell_vertices = [point(value) for value in shell["vertices"]]
    duplicate = dict(cut["cut_duplicate_vertex_map"])
    ac_tetrahedra = sorted(set(
        tuple(sorted(vertex - 32 if vertex >= 32 else vertex for vertex in tetrahedron))
        for tetrahedron in cut["cut_tetrahedra"]
        if any(vertex >= 32 for vertex in tetrahedron)
    ))
    inverses = []
    for simplex in simplices:
        matrix = sp.Matrix([
            [sp.Rational(source_vertices[vertex][axis].numerator, source_vertices[vertex][axis].denominator)
             for vertex in simplex]
            for axis in range(4)
        ] + [[1] * 5])
        inverses.append(matrix.inv())

    def weights(simplex_index, raw):
        value = point(raw)
        rhs = sp.Matrix([
            *(sp.Rational(coordinate.numerator, coordinate.denominator) for coordinate in value), 1
        ])
        return [Fraction(int(item.p), int(item.q)) for item in inverses[simplex_index] * rhs]

    boundary_pieces = []
    total_pieces = 0
    with gzip.open(resolve(lanes["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            for lane_name, lane in record["lanes"].items():
                for source_segment, group in enumerate(lane["core_segment_images"]):
                    for piece_index, piece in enumerate(group):
                        total_pieces += 1
                        simplex_index = piece["four_simplex_index"]
                        simplex = simplices[simplex_index]
                        endpoint_weights = [weights(simplex_index, raw) for raw in piece["source_vertices"]]
                        midpoint = [sum(pair) / 2 for pair in zip(*endpoint_weights)]
                        carrier = {
                            simplex[index] for index, weight in enumerate(midpoint) if weight > 0
                        }
                        candidates = [tetrahedron for tetrahedron in ac_tetrahedra if carrier <= set(tetrahedron)]
                        if not candidates:
                            continue
                        carrier_tetrahedron = min(candidates)
                        cut_carrier = sorted(duplicate.get(vertex, vertex) for vertex in carrier_tetrahedron)
                        mapped = []
                        for values in endpoint_weights:
                            coordinates = [Fraction(0), Fraction(0), Fraction(0)]
                            for local, weight in enumerate(values):
                                target = duplicate.get(simplex[local], simplex[local])
                                for axis in range(3):
                                    coordinates[axis] += weight * shell_vertices[target][axis]
                            mapped.append([str(value) for value in coordinates])
                        boundary_pieces.append({
                            "band_index": record["band_index"],
                            "component": record["component"],
                            "lane": lane_name,
                            "source_segment_index": source_segment,
                            "piece_index": piece_index,
                            "source_four_simplex_index": simplex_index,
                            "source_parameter_interval": piece["parameter_interval"],
                            "cut_carrier_tetrahedron": cut_carrier,
                            "r3_vertices": mapped,
                        })
    expected_identity = {(piece["band_index"], piece["component"], piece["lane"]) for piece in boundary_pieces}
    if expected_identity != {(0, "m_2", "positive_band_lane")}:
        raise AssertionError("boundary band-lane identity changed")
    for previous, following in zip(boundary_pieces, boundary_pieces[1:]):
        if previous["r3_vertices"][-1] != following["r3_vertices"][0]:
            raise AssertionError("boundary band-lane R3 pieces are discontinuous")
    assembled = [boundary_pieces[0]["r3_vertices"][0]] + [
        piece["r3_vertices"][1] for piece in boundary_pieces
    ]
    result = {
        "schema": "t73_x_m1_boundary_band_lane_core_r3/v1",
        "collar_product_sha256": product["sha256"],
        "support_generator_sphere_cut_sha256": cut["sha256"],
        "support_cut_r3_shell_sha256": shell["sha256"],
        "collar_boundary_topology_sha256": topology["sha256"],
        "ejected_band_lanes_receipt_sha256": lanes["sha256"],
        "total_core_piece_count": total_pieces,
        "boundary_core_piece_count": len(boundary_pieces),
        "interior_core_piece_count": total_pieces - len(boundary_pieces),
        "boundary_pieces": boundary_pieces,
        "complete_boundary_lane": {
            "band_index": 0,
            "component": "m_2",
            "lane": "positive_band_lane",
            "source_segment_count": 2,
            "r3_segment_count": len(boundary_pieces),
            "r3_vertices": assembled,
            "cut_side": "AC_to_C_A_copy",
        },
        "r3_continuity_check_count": len(boundary_pieces) - 1,
        "mapped_push_status": "OPEN",
        "interior_lane_extension_status": "OPEN_15151_PIECES",
        "completion_status": "COMPLETE_BOUNDARY_CARRIED_BAND_LANE_CORE_MAPPED_TO_R3",
        "verdict": "PASS_X_M1_BOUNDARY_BAND_LANE_CORE_R3",
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
        raise AssertionError("boundary band-lane R3 artifact is stale")
    print(json.dumps({
        "boundary_pieces": result["boundary_core_piece_count"],
        "interior_pieces": result["interior_core_piece_count"],
        "complete_lane": result["complete_boundary_lane"]["lane"],
        "verdict": result["verdict"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
