#!/usr/bin/env python3
"""Independently replay all splice-stub core maps into the cut R3 shell."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from collections import Counter
from fractions import Fraction
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
CUT = ROOT / "geometry/t73_x_m1_support_generator_sphere_cut.json"
SHELL = ROOT / "geometry/t73_x_m1_support_cut_r3_shell.json"
STUBS = ROOT / "audit/t73_x_m1_ejected_splice_stubs_receipt.json"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest().upper()


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    return path


def point(values):
    return tuple(Fraction(value) for value in values)


def leaves(value):
    if isinstance(value, dict):
        yield value
    else:
        for item in value:
            yield from leaves(item)


def check_receipt():
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("splice-stub R3 receipt SHA mismatch")
    product = json.loads(PRODUCT.read_text())
    cut = json.loads(CUT.read_text())
    shell = json.loads(SHELL.read_text())
    stubs = json.loads(STUBS.read_text())
    bindings = {
        "collar_product_sha256": product["sha256"],
        "support_cut_sha256": cut["sha256"],
        "support_cut_r3_shell_sha256": shell["sha256"],
        "ejected_splice_stubs_receipt_sha256": stubs["sha256"],
    }
    if any(data[key] != value for key, value in bindings.items()):
        raise AssertionError("splice-stub R3 source binding changed")
    return data, product, cut, shell, stubs


def verify_full(check_cache_sha=False):
    data, product, cut, shell, stubs = check_receipt()
    output_path = resolve(data["cache_path"])
    source_path = resolve(stubs["cache_path"])
    if not output_path.is_file() or output_path.stat().st_size != data["cache_size"]:
        raise AssertionError("splice-stub R3 cache missing or resized")
    if check_cache_sha and file_sha256(output_path) != data["cache_sha256"]:
        raise AssertionError("splice-stub R3 cache SHA mismatch")
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

    def map_source_piece(piece):
        simplex_index = piece["four_simplex_index"]
        simplex = simplices[simplex_index]
        endpoint_weights = []
        for raw in piece["source_vertices"]:
            value = point(raw)
            rhs = sp.Matrix([
                *(sp.Rational(coordinate.numerator, coordinate.denominator) for coordinate in value), 1
            ])
            endpoint_weights.append([
                Fraction(int(item.p), int(item.q))
                for item in inverses[simplex_index] * rhs
            ])
        midpoint = [sum(pair) / 2 for pair in zip(*endpoint_weights)]
        carrier = {
            simplex[index] for index, weight in enumerate(midpoint) if weight > 0
        }
        candidates = [tetrahedron for tetrahedron in ac_tetrahedra if carrier <= set(tetrahedron)]
        if not candidates:
            raise AssertionError("source stub piece has no AC carrier")
        cut_carrier = sorted(duplicate.get(vertex, vertex) for vertex in min(candidates))
        mapped = []
        for weights in endpoint_weights:
            coordinates = [Fraction(0), Fraction(0), Fraction(0)]
            for local, weight in enumerate(weights):
                target = duplicate.get(simplex[local], simplex[local])
                for axis in range(3):
                    coordinates[axis] += weight * shell_vertices[target][axis]
            mapped.append([str(value) for value in coordinates])
        return {
            "source_four_simplex_index": simplex_index,
            "source_parameter_interval": piece["parameter_interval"],
            "cut_carrier_tetrahedron": cut_carrier,
            "r3_vertices": mapped,
        }

    digest = hashlib.sha256()
    records = pieces = endpoints = continuity = 0
    components = Counter()
    stub_counts = Counter()
    with gzip.open(output_path, "rt", encoding="utf-8") as output, gzip.open(source_path, "rt", encoding="utf-8") as source:
        output_header = output.readline()
        digest.update(output_header.encode())
        if json.loads(output_header)["cut_side"] != "AC_to_C_A_copy":
            raise AssertionError("splice-stub R3 cut side changed")
        source.readline()
        for source_line in source:
            output_line = output.readline()
            if not output_line:
                raise AssertionError("splice-stub R3 output ended early")
            source_record = json.loads(source_line)
            output_record = json.loads(output_line)
            digest.update(output_line.encode())
            if (output_record["band_index"], output_record["component"]) != (
                source_record["band_index"], source_record["component"]
            ):
                raise AssertionError("splice-stub R3 record identity changed")
            for name, source_stub in source_record["stubs"].items():
                expected = [map_source_piece(piece) for piece in leaves(source_stub["core_segment_image"])]
                saved = output_record["stubs"][name]
                if saved["pieces"] != expected:
                    raise AssertionError(f"splice-stub R3 mapping changed at band {source_record['band_index']}")
                for previous, following in zip(expected, expected[1:]):
                    if previous["r3_vertices"][-1] != following["r3_vertices"][0]:
                        raise AssertionError("replayed R3 stub is discontinuous")
                    continuity += 1
                pieces += len(expected)
                endpoints += 2 * len(expected)
                stub_counts[name] += len(expected)
            records += 1
            components[source_record["component"]] += 1
        if output.readline():
            raise AssertionError("unused splice-stub R3 output remains")
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("splice-stub R3 decompressed stream SHA mismatch")
    if (records, pieces, endpoints, continuity) != (1513, 10582, 21164, 4530):
        raise AssertionError("splice-stub R3 replay totals changed")
    if dict(sorted(components.items())) != data["component_counts"]:
        raise AssertionError("splice-stub R3 component counts changed")
    if dict(sorted(stub_counts.items())) != data["stub_piece_counts"]:
        raise AssertionError("splice-stub R3 type counts changed")
    if data["mapped_push_status"] != "OPEN_EXTEND_R3_SHELL_COLLAR_NORMAL":
        raise AssertionError("splice-stub push scope was overstated")
    return {
        "verdict": "PASS_X_M1_ALL_SPLICE_STUB_CORES_R3_FULL",
        "records_reconstructed": records,
        "core_pieces_reconstructed": pieces,
        "endpoint_occurrences_reconstructed": endpoints,
        "continuity_checks": continuity,
        "cut_side": "AC_to_C_A_copy",
        "cache_sha_checked": check_cache_sha,
        "mapped_push": "OPEN",
        "interior_band_lanes": "OPEN_15151_PIECES",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--check-cache-sha", action="store_true")
    args = parser.parse_args()
    if args.full:
        result = verify_full(args.check_cache_sha)
    else:
        check_receipt()
        result = {"verdict": "PASS_X_M1_SPLICE_STUB_CORES_R3_RECEIPT"}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
