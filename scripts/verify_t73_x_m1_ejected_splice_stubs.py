#!/usr/bin/env python3
"""Verify all source/target splice-stub images under the x/m1 collar map."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

from verify_t73_x_m1_ejected_band_lanes import barycentric, charts, file_sha, image, interpolate, point, resolve_path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "audit/t73_x_m1_ejected_splice_stubs_receipt.json"
BUILDER = ROOT / "scripts/build_t73_x_m1_ejected_splice_stubs.py"
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
POST_X = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
GERMS = ROOT / "geometry/t73_x_source_chart_germs.json"

sys.set_int_max_str_digits(0)


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def source_to_local(value, germ):
    value = point(value); deck = germ["global_deck"]
    spatial = tuple(value[index] - 4 * deck[index] for index in range(3))
    return spatial + ((value[3],) if len(value) == 4 else (Fraction(1),))


def target_to_local(value, deck=(0, 0, 0)):
    value = point(value); spatial = tuple(value[index] - 4 * deck[index] for index in range(3))
    return (-spatial[0], spatial[1], spatial[2] - 4, Fraction(1))


def check_receipt():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8")); product = json.loads(PRODUCT.read_text(encoding="utf-8")); post_x = json.loads(POST_X.read_text(encoding="utf-8")); germs = json.loads(GERMS.read_text(encoding="utf-8"))
    checks = {
        "payload": receipt["sha256"] == canonical_sha({key: value for key, value in receipt.items() if key != "sha256"}),
        "builder": receipt["builder_sha256"] == file_sha(BUILDER),
        "sources": receipt["product_extension_sha256"] == product["sha256"] and receipt["post_x_receipt_sha256"] == post_x["sha256"] and receipt["source_germs_sha256"] == germs["sha256"],
        "counts": receipt["band_count"] == 1513 and receipt["source_core_and_push_stub_segment_count"] == 12104 and receipt["piecewise_affine_stub_image_segment_count"] == 25712 and receipt["fixed_middle_core_segment_count"] == 48416 and receipt["fixed_middle_push_segment_count"] == 48416,
        "verdict": receipt["verdict"] == "PASS_X_M1_EXACT_PIECEWISE_AFFINE_SPLICE_STUB_IMAGES",
    }
    if not all(checks.values()):
        raise AssertionError(f"ejected splice-stub receipt failed: {checks}")
    return receipt, checks


def verify_pieces(start, end, pieces, simplex_charts, targets):
    previous = None; count = 0
    for piece in pieces:
        first, second = map(Fraction, piece["parameter_interval"]); chart = simplex_charts[piece["four_simplex_index"]]
        expected_source = [interpolate(start, end, first), interpolate(start, end, second)]
        stored_source = [point(value) for value in piece["source_vertices"]]; stored_target = [point(value) for value in piece["target_vertices"]]
        if stored_source != expected_source or stored_target != [image(chart, targets, value) for value in expected_source] or any(weight < 0 for value in expected_source for weight in barycentric(chart, value)):
            raise AssertionError("splice-stub affine image changed")
        if previous is not None and (first != previous[0] or stored_source[0] != previous[1]):
            raise AssertionError("splice-stub image is discontinuous")
        previous = (second, stored_source[1]); count += 1
    if not pieces or Fraction(pieces[0]["parameter_interval"][0]) != 0 or Fraction(pieces[-1]["parameter_interval"][1]) != 1:
        raise AssertionError("splice-stub pieces do not cover source")
    return count


def verify_full(input_cache=None, check_cache_sha=False):
    receipt, checks = check_receipt(); product = json.loads(PRODUCT.read_text(encoding="utf-8")); post_x = json.loads(POST_X.read_text(encoding="utf-8")); germs_data = json.loads(GERMS.read_text(encoding="utf-8")); germs = {item["band_index"]: item for item in germs_data["germs"]}
    output_cache = resolve_path(receipt["cache_path"]); input_cache = input_cache or resolve_path(post_x["cache_path"])
    if check_cache_sha and file_sha(output_cache) != receipt["cache_sha256"]:
        raise AssertionError("ejected splice-stub cache SHA changed")
    sources = [point(value) for value in product["source_vertices"]]; targets = [point(value) for value in product["target_vertex_images"]]; simplex_charts = charts(sources, product["four_simplices"]); uniform = point(product["exteriorized_uniform_push_vector"])
    source_segments = image_segments = fixed_middle = 0
    with gzip.open(input_cache, "rt", encoding="utf-8") as source_file, gzip.open(output_cache, "rt", encoding="utf-8") as image_file:
        next(source_file); header = json.loads(next(image_file))
        if header["schema"] != "t73_x_m1_ejected_splice_stubs/v1":
            raise AssertionError("splice-stub cache header changed")
        for index, (source_line, image_line) in enumerate(zip(source_file, image_file)):
            cell, record = json.loads(source_line), json.loads(image_line); germ = germs[index]
            if cell["band_index"] != index or record["band_index"] != index or record["component"] != cell["component"]:
                raise AssertionError("splice-stub record order changed")
            complement = cell["oriented_m1_parallel_complement"]; values = complement["vertices"]; deck = tuple(complement["closing_deck"])
            segments = {
                "source_stub_before": tuple(source_to_local(value, germ) for value in cell["source_stub_before"]["vertices"]),
                "target_complement_first": (target_to_local(values[0]), target_to_local(values[1])),
                "target_complement_last": (target_to_local(values[-2], deck), target_to_local(values[-1], deck)),
                "source_stub_after": tuple(source_to_local(value, germ) for value in cell["source_stub_after"]["vertices"]),
            }
            for name, segment in segments.items():
                stored = record["stubs"][name]
                image_segments += verify_pieces(*segment, stored["core_segment_image"], simplex_charts, targets)
                pushed = tuple(tuple(value[axis] + uniform[axis] for axis in range(4)) for value in segment)
                image_segments += verify_pieces(*pushed, stored["outward_push_segment_image"], simplex_charts, targets)
                source_segments += 2
            if record["fixed_target_complement_middle_vertex_range"] != [1, len(values) - 2] or record["fixed_target_complement_middle_segment_count"] != len(values) - 3:
                raise AssertionError("fixed complement middle range changed")
            fixed_middle += len(values) - 3
        if next(source_file, None) is not None or next(image_file, None) is not None:
            raise AssertionError("splice/source cache lengths differ")
    if (source_segments, image_segments, fixed_middle) != (12104, 25712, 48416):
        raise AssertionError("splice-stub full totals changed")
    return {"verdict": "PASS_X_M1_EJECTED_SPLICE_STUBS_FULL", "fast_checks": checks, "source_segments": source_segments, "image_segments": image_segments, "fixed_middle_core_segments": fixed_middle, "cache_sha_checked": check_cache_sha, "merge_status": "OPEN_MERGE_COMPLETE_REPLACEMENT_PATHS"}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--full", action="store_true"); parser.add_argument("--input-cache", type=Path); parser.add_argument("--check-cache-sha", action="store_true"); args = parser.parse_args()
    result = verify_full(args.input_cache, args.check_cache_sha) if args.full else {"verdict": "PASS_X_M1_EJECTED_SPLICE_STUBS_RECEIPT", "checks": check_receipt()[1], "image_segments": check_receipt()[0]["piecewise_affine_stub_image_segment_count"]}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
