#!/usr/bin/env python3
"""Apply the x/m1 collar map to all source and target splice-end stubs."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

from build_t73_x_m1_ejected_band_lanes import canonical, file_sha, map_segment, point, simplex_chart

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
POST_X = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
GERMS = ROOT / "geometry/t73_x_source_chart_germs.json"
RECEIPT = ROOT / "audit/t73_x_m1_ejected_splice_stubs_receipt.json"
DEFAULT_CACHE = Path("/home/lifesize/.cache/t73_x_m1_ejected_splice_stubs.jsonl.gz")

sys.set_int_max_str_digits(0)


def canonical_sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest().upper()


def source_to_local(value, germ):
    value = point(value); deck = germ["global_deck"]
    spatial = tuple(value[index] - 4 * deck[index] for index in range(3))
    return spatial + ((value[3],) if len(value) == 4 else (Fraction(1),))


def target_to_local(value, deck=(0, 0, 0)):
    value = point(value)
    spatial = tuple(value[index] - 4 * deck[index] for index in range(3))
    return (-spatial[0], spatial[1], spatial[2] - 4, Fraction(1))


def mapped_pair(segment, uniform, charts, targets):
    pushed = tuple(tuple(value[axis] + uniform[axis] for axis in range(4)) for value in segment)
    return {"core_segment_image": map_segment(*segment, charts, targets), "outward_push_segment_image": map_segment(*pushed, charts, targets)}


def build(cache_path, input_cache_override=None):
    product = json.loads(PRODUCT.read_text(encoding="utf-8")); post_x = json.loads(POST_X.read_text(encoding="utf-8")); germs_data = json.loads(GERMS.read_text(encoding="utf-8"))
    germs = {item["band_index"]: item for item in germs_data["germs"]}
    source_vertices = [point(value) for value in product["source_vertices"]]; targets = [point(value) for value in product["target_vertex_images"]]
    charts = [simplex_chart(source_vertices, simplex) for simplex in product["four_simplices"]]; uniform = point(product["exteriorized_uniform_push_vector"])
    input_cache = input_cache_override or Path(post_x["cache_path"]); cache_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(); counts = Counter(); source_segments = image_segments = fixed_middle_segments = 0
    header = {"record": "header", "schema": "t73_x_m1_ejected_splice_stubs/v1", "product_extension_sha256": product["sha256"], "post_x_receipt_sha256": post_x["sha256"], "source_germs_sha256": germs_data["sha256"]}
    with gzip.open(input_cache, "rt", encoding="utf-8") as source_file, cache_path.open("wb") as raw_output:
        next(source_file)
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            raw = (canonical(header) + "\n").encode(); output.write(raw); digest.update(raw)
            for raw_line in source_file:
                cell = json.loads(raw_line); index = cell["band_index"]; germ = germs[index]
                before_global = cell["source_stub_before"]["vertices"]; after_global = cell["source_stub_after"]["vertices"]
                source_before = tuple(source_to_local(value, germ) for value in before_global)
                source_after = tuple(source_to_local(value, germ) for value in after_global)
                complement = cell["oriented_m1_parallel_complement"]; values = complement["vertices"]; deck = tuple(complement["closing_deck"])
                target_before = (target_to_local(values[0]), target_to_local(values[1]))
                target_after = (target_to_local(values[-2], deck), target_to_local(values[-1], deck))
                negative = [point(value) for value in cell["negative_band_lane"]["vertices"]]; positive = [point(value) for value in cell["positive_band_lane"]["vertices"]]
                if source_before[-1] != negative[0] or target_before[0] != negative[-1] or target_after[-1] != positive[0] or source_after[0] != positive[-1]:
                    raise AssertionError(f"band {index} splice germs do not meet band lanes")
                stubs = {
                    "source_stub_before": mapped_pair(source_before, uniform, charts, targets),
                    "target_complement_first": mapped_pair(target_before, uniform, charts, targets),
                    "target_complement_last": mapped_pair(target_after, uniform, charts, targets),
                    "source_stub_after": mapped_pair(source_after, uniform, charts, targets),
                }
                record = {"record": "ejected_splice_stubs", "band_index": index, "component": cell["component"], "stubs": stubs, "fixed_target_complement_middle_vertex_range": [1, len(values) - 2], "fixed_target_complement_middle_segment_count": len(values) - 3}
                for value in stubs.values():
                    source_segments += 2; image_segments += len(value["core_segment_image"]) + len(value["outward_push_segment_image"])
                fixed_middle_segments += len(values) - 3; counts[cell["component"]] += 1
                raw = (canonical(record) + "\n").encode(); output.write(raw); digest.update(raw)
    receipt = {
        "schema": "t73_x_m1_ejected_splice_stubs_receipt/v1", "cache_path": str(cache_path), "cache_size": cache_path.stat().st_size, "cache_sha256": file_sha(cache_path), "record_stream_sha256": digest.hexdigest().upper(), "builder_sha256": file_sha(Path(__file__)),
        "product_extension_sha256": product["sha256"], "post_x_receipt_sha256": post_x["sha256"], "source_germs_sha256": germs_data["sha256"], "band_count": sum(counts.values()), "component_counts": dict(sorted(counts.items())),
        "source_core_and_push_stub_segment_count": source_segments, "piecewise_affine_stub_image_segment_count": image_segments, "fixed_middle_core_segment_count": fixed_middle_segments, "fixed_middle_push_segment_count": fixed_middle_segments,
        "verdict": "PASS_X_M1_EXACT_PIECEWISE_AFFINE_SPLICE_STUB_IMAGES", "scope_boundary": "all nontrivial replacement segments now imaged; fixed m1-complement middles remain to be merged with F-590 lanes",
    }
    receipt["sha256"] = canonical_sha(receipt); RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"); return receipt


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path); parser.add_argument("--input-cache", type=Path); args = parser.parse_args()
    receipt = build(args.output or Path(os.environ.get("T73_X_M1_EJECTED_STUBS_CACHE", DEFAULT_CACHE)), args.input_cache)
    print(json.dumps({"verdict": receipt["verdict"], "source_segments": receipt["source_core_and_push_stub_segment_count"], "image_segments": receipt["piecewise_affine_stub_image_segment_count"], "fixed_middle_core_segments": receipt["fixed_middle_core_segment_count"], "bytes": receipt["cache_size"]}, sort_keys=True))


if __name__ == "__main__":
    main()
