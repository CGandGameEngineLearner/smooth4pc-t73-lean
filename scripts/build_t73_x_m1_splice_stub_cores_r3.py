#!/usr/bin/env python3
"""Map every ejected splice-stub core piece into the exact cut R3 shell."""

from __future__ import annotations

import argparse
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
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
CUT = ROOT / "geometry/t73_x_m1_support_generator_sphere_cut.json"
SHELL = ROOT / "geometry/t73_x_m1_support_cut_r3_shell.json"
STUBS = ROOT / "audit/t73_x_m1_ejected_splice_stubs_receipt.json"
COMPLETE = ROOT / "audit/t73_x_m1_complete_explicit_replacement_images_verification.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_m1_splice_stub_cores_r3.jsonl.gz"


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
    if len(value) >= 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def point(values):
    return tuple(Fraction(value) for value in values)


def leaves(value):
    if isinstance(value, dict):
        yield value
    else:
        for item in value:
            yield from leaves(item)


def build(output_path):
    product = json.loads(PRODUCT.read_text())
    cut = json.loads(CUT.read_text())
    shell = json.loads(SHELL.read_text())
    stubs = json.loads(STUBS.read_text())
    complete = json.loads(COMPLETE.read_text())
    four_simplices = [tuple(value) for value in product["four_simplices"]]
    source_vertices = [point(value) for value in product["source_vertices"]]
    shell_vertices = [point(value) for value in shell["vertices"]]
    original_boundary = [
        tuple(value) for value in cut["cut_tetrahedra"]
        if not any(vertex >= 32 for vertex in value)
    ]
    ac_boundary = [
        tuple(sorted(vertex - 32 if vertex >= 32 else vertex for vertex in value))
        for value in cut["cut_tetrahedra"]
        if any(vertex >= 32 for vertex in value)
    ]
    ac_boundary = sorted(set(ac_boundary))
    if len(ac_boundary) != 36:
        raise AssertionError("cut AC boundary tetrahedron inventory changed")
    duplicate = dict(cut["cut_duplicate_vertex_map"])

    inverses = []
    for simplex in four_simplices:
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
        return [
            Fraction(int(item.p), int(item.q))
            for item in inverses[simplex_index] * rhs
        ]

    def map_piece(piece):
        simplex_index = piece["four_simplex_index"]
        simplex = four_simplices[simplex_index]
        endpoint_weights = [weights(simplex_index, raw) for raw in piece["source_vertices"]]
        midpoint = [sum(values) / 2 for values in zip(*endpoint_weights)]
        carrier = tuple(sorted(
            simplex[index] for index, weight in enumerate(midpoint) if weight > 0
        ))
        candidates = [tetrahedron for tetrahedron in ac_boundary if set(carrier) <= set(tetrahedron)]
        if not candidates:
            raise AssertionError("splice-stub piece is not on the AC boundary side")
        carrier_tetrahedron = min(candidates)
        cut_carrier = tuple(sorted(duplicate.get(vertex, vertex) for vertex in carrier_tetrahedron))
        mapped = []
        for values in endpoint_weights:
            coordinates = [Fraction(0), Fraction(0), Fraction(0)]
            for local_index, weight in enumerate(values):
                target_vertex = duplicate.get(simplex[local_index], simplex[local_index])
                for axis in range(3):
                    coordinates[axis] += weight * shell_vertices[target_vertex][axis]
            mapped.append([str(value) for value in coordinates])
        return {
            "source_four_simplex_index": simplex_index,
            "source_parameter_interval": piece["parameter_interval"],
            "cut_carrier_tetrahedron": list(cut_carrier),
            "r3_vertices": mapped,
        }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_splice_stub_cores_r3/v1",
        "collar_product_sha256": product["sha256"],
        "support_cut_sha256": cut["sha256"],
        "support_cut_r3_shell_sha256": shell["sha256"],
        "ejected_splice_stubs_receipt_sha256": stubs["sha256"],
        "complete_replacement_verification_sha256": complete["sha256"],
        "cut_side": "AC_to_C_A_copy",
    }
    records = pieces = endpoint_occurrences = continuity_checks = 0
    component_counts = Counter()
    stub_counts = Counter()
    with gzip.open(resolve(stubs["cache_path"]), "rt", encoding="utf-8") as source, output_path.open("wb") as raw_output:
        source.readline()
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            encoded = (canonical(header) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            for line in source:
                record = json.loads(line)
                mapped_stubs = {}
                for stub_name, stub in record["stubs"].items():
                    mapped_pieces = [map_piece(piece) for piece in leaves(stub["core_segment_image"])]
                    for previous, following in zip(mapped_pieces, mapped_pieces[1:]):
                        if previous["r3_vertices"][-1] != following["r3_vertices"][0]:
                            raise AssertionError("mapped splice-stub R3 pieces are discontinuous")
                        continuity_checks += 1
                    mapped_stubs[stub_name] = {
                        "pieces": mapped_pieces,
                        "piece_count": len(mapped_pieces),
                        "start_r3": mapped_pieces[0]["r3_vertices"][0],
                        "end_r3": mapped_pieces[-1]["r3_vertices"][-1],
                    }
                    pieces += len(mapped_pieces)
                    endpoint_occurrences += 2 * len(mapped_pieces)
                    stub_counts[stub_name] += len(mapped_pieces)
                output_record = {
                    "record": "splice_stub_cores_r3",
                    "band_index": record["band_index"],
                    "component": record["component"],
                    "stubs": mapped_stubs,
                    "piece_count": sum(value["piece_count"] for value in mapped_stubs.values()),
                    "relative_map_status": "EXACT_AC_BOUNDARY_BARYCENTRIC_MAP",
                }
                encoded = (canonical(output_record) + "\n").encode()
                output.write(encoded)
                digest.update(encoded)
                records += 1
                component_counts[record["component"]] += 1

    receipt = {
        "schema": "t73_x_m1_splice_stub_cores_r3_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha256(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha256(Path(__file__)),
        "collar_product_sha256": product["sha256"],
        "support_cut_sha256": cut["sha256"],
        "support_cut_r3_shell_sha256": shell["sha256"],
        "ejected_splice_stubs_receipt_sha256": stubs["sha256"],
        "complete_replacement_verification_sha256": complete["sha256"],
        "record_count": records,
        "component_counts": dict(sorted(component_counts.items())),
        "stub_piece_counts": dict(sorted(stub_counts.items())),
        "mapped_core_piece_count": pieces,
        "mapped_core_endpoint_occurrences": endpoint_occurrences,
        "r3_piece_continuity_checks": continuity_checks,
        "cut_side": "AC_to_C_A_copy",
        "mapped_push_status": "OPEN_EXTEND_R3_SHELL_COLLAR_NORMAL",
        "interior_band_lane_status": "OPEN_15151_PIECES",
        "completion_status": "ALL_SPLICE_STUB_CORES_MAPPED_TO_SUPPORT_CUT_R3_SHELL",
        "verdict": "PASS_X_M1_ALL_SPLICE_STUB_CORES_R3",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(os.environ.get("T73_X_M1_STUB_CORES_R3_CACHE", DEFAULT_OUTPUT))
    receipt = build(output)
    print(json.dumps({
        "verdict": receipt["verdict"],
        "records": receipt["record_count"],
        "pieces": receipt["mapped_core_piece_count"],
        "continuity": receipt["r3_piece_continuity_checks"],
        "bytes": receipt["cache_size"],
        "push": receipt["mapped_push_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
