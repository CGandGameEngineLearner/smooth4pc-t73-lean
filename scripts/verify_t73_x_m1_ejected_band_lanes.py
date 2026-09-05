#!/usr/bin/env python3
"""Verify receipt or every exact piecewise-affine ejected band-lane image."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "audit/t73_x_m1_ejected_band_lanes_receipt.json"
BUILDER = ROOT / "scripts/build_t73_x_m1_ejected_band_lanes.py"
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
POST_X = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"

sys.set_int_max_str_digits(0)


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def invert(matrix):
    size = len(matrix); rows = [list(row) + [Fraction(int(i == j)) for j in range(size)] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next(row for row in range(column, size) if rows[row][column]); rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]; rows[column] = [value / divisor for value in rows[column]]
        for row in range(size):
            if row != column and rows[row][column]:
                factor = rows[row][column]; rows[row] = [left - factor * right for left, right in zip(rows[row], rows[column])]
    return [row[size:] for row in rows]


def charts(vertices, simplices):
    result = []
    for simplex in simplices:
        values = [vertices[index] for index in simplex]; origin = values[0]
        matrix = [[values[column + 1][row] - origin[row] for column in range(4)] for row in range(4)]
        result.append((simplex, origin, invert(matrix)))
    return result


def barycentric(chart, value):
    _, origin, inverse = chart; delta = [value[index] - origin[index] for index in range(4)]
    tail = [sum(inverse[row][column] * delta[column] for column in range(4)) for row in range(4)]
    return (1 - sum(tail), *tail)


def image(chart, targets, value):
    weights = barycentric(chart, value); simplex = chart[0]
    return tuple(sum(weights[index] * targets[simplex[index]][axis] for index in range(5)) for axis in range(4))


def interpolate(start, end, parameter):
    return tuple(start[index] + parameter * (end[index] - start[index]) for index in range(4))


def resolve_path(value):
    path = Path(value)
    if path.exists() or len(value) < 3 or value[1:3] not in (":\\", ":/"):
        return path
    return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")


def check_receipt():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8")); product = json.loads(PRODUCT.read_text(encoding="utf-8")); post_x = json.loads(POST_X.read_text(encoding="utf-8"))
    checks = {
        "payload": receipt["sha256"] == canonical_sha({key: value for key, value in receipt.items() if key != "sha256"}),
        "builder": receipt["builder_sha256"] == file_sha(BUILDER),
        "sources": receipt["product_extension_sha256"] == product["sha256"] and receipt["post_x_receipt_sha256"] == post_x["sha256"],
        "counts": receipt["band_count"] == 1513 and receipt["source_core_and_push_segment_count"] == 12104 and receipt["piecewise_affine_image_segment_count"] == 30144,
        "verdict": receipt["verdict"] == "PASS_X_M1_EXACT_PIECEWISE_AFFINE_BAND_LANE_IMAGES",
    }
    if not all(checks.values()):
        raise AssertionError(f"ejected band-lane receipt failed: {checks}")
    return receipt, checks


def verify_full(input_cache=None, check_cache_sha=False):
    receipt, fast_checks = check_receipt(); product = json.loads(PRODUCT.read_text(encoding="utf-8")); post_x = json.loads(POST_X.read_text(encoding="utf-8"))
    output_cache = resolve_path(receipt["cache_path"]); input_cache = input_cache or resolve_path(post_x["cache_path"])
    if check_cache_sha and file_sha(output_cache) != receipt["cache_sha256"]:
        raise AssertionError("ejected band-lane cache SHA changed")
    source_vertices = [point(value) for value in product["source_vertices"]]; targets = [point(value) for value in product["target_vertex_images"]]
    simplex_charts = charts(source_vertices, product["four_simplices"]); uniform = point(product["exteriorized_uniform_push_vector"])
    source_segments = image_segments = continuity_checks = 0
    with gzip.open(input_cache, "rt", encoding="utf-8") as source_file, gzip.open(output_cache, "rt", encoding="utf-8") as image_file:
        source_header, image_header = json.loads(next(source_file)), json.loads(next(image_file))
        if image_header != {"record": "header", "schema": "t73_x_m1_ejected_band_lanes/v1", "product_extension_sha256": product["sha256"], "post_x_receipt_sha256": post_x["sha256"]}:
            raise AssertionError("ejected cache header changed")
        for expected_band, (source_line, image_line) in enumerate(zip(source_file, image_file)):
            source_cell, record = json.loads(source_line), json.loads(image_line)
            if source_cell["band_index"] != expected_band or record["band_index"] != expected_band or record["component"] != source_cell["component"]:
                raise AssertionError("ejected band order/provenance changed")
            for lane_name in ("negative_band_lane", "positive_band_lane"):
                core = [point(value) for value in source_cell[lane_name]["vertices"]]
                push = [tuple(value[axis] + uniform[axis] for axis in range(4)) for value in core]
                for original, stored in ((core, record["lanes"][lane_name]["core_segment_images"]), (push, record["lanes"][lane_name]["outward_push_segment_images"])):
                    if len(stored) != 2:
                        raise AssertionError("ejected source segment list changed")
                    for (start, end), pieces in zip(zip(original, original[1:]), stored):
                        previous_end = None
                        for piece_index, piece in enumerate(pieces):
                            first, second = map(Fraction, piece["parameter_interval"]); chart = simplex_charts[piece["four_simplex_index"]]
                            expected_source = [interpolate(start, end, first), interpolate(start, end, second)]
                            stored_source = [point(value) for value in piece["source_vertices"]]; stored_target = [point(value) for value in piece["target_vertices"]]
                            if stored_source != expected_source or stored_target != [image(chart, targets, value) for value in expected_source]:
                                raise AssertionError("piecewise-affine lane image changed")
                            if any(weight < 0 for value in expected_source for weight in barycentric(chart, value)):
                                raise AssertionError("piece source leaves its declared simplex")
                            if previous_end is not None and (first != previous_end[0] or stored_source[0] != previous_end[1]):
                                raise AssertionError("ejected pieces are not continuous")
                            previous_end = (second, stored_source[1]); continuity_checks += 1; image_segments += 1
                        if not pieces or Fraction(pieces[0]["parameter_interval"][0]) != 0 or Fraction(pieces[-1]["parameter_interval"][1]) != 1:
                            raise AssertionError("ejected pieces do not cover source segment")
                        source_segments += 1
        if next(image_file, None) is not None or next(source_file, None) is not None:
            raise AssertionError("ejected/source cache lengths differ")
    if source_segments != 12104 or image_segments != 30144:
        raise AssertionError("ejected full verification totals changed")
    return {"verdict": "PASS_X_M1_EJECTED_BAND_LANES_FULL", "fast_checks": fast_checks, "source_segments": source_segments, "image_segments": image_segments, "continuity_checks": continuity_checks, "cache_sha_checked": check_cache_sha, "full_hybrid_path_status": "OPEN_FIXED_PIECES_NOT_MERGED"}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--full", action="store_true"); parser.add_argument("--input-cache", type=Path); parser.add_argument("--check-cache-sha", action="store_true")
    args = parser.parse_args()
    result = verify_full(args.input_cache, args.check_cache_sha) if args.full else {"verdict": "PASS_X_M1_EJECTED_BAND_LANES_RECEIPT", "checks": check_receipt()[1], "image_segments": check_receipt()[0]["piecewise_affine_image_segment_count"]}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
