#!/usr/bin/env python3
"""Apply the exact x/m1 product-collar map to every framed band lane."""

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

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
POST_X = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
RECEIPT = ROOT / "audit/t73_x_m1_ejected_band_lanes_receipt.json"
DEFAULT_CACHE = Path("/home/lifesize/.cache/t73_x_m1_ejected_band_lanes.jsonl.gz")

sys.set_int_max_str_digits(0)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest().upper()


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def invert(matrix):
    size = len(matrix)
    rows = [list(row) + [Fraction(int(i == j)) for j in range(size)] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next(row for row in range(column, size) if rows[row][column])
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [value / scale for value in rows[column]]
        for row in range(size):
            if row == column:
                continue
            factor = rows[row][column]
            if factor:
                rows[row] = [left - factor * right for left, right in zip(rows[row], rows[column])]
    return [row[size:] for row in rows]


def simplex_chart(vertices, simplex):
    values = [vertices[index] for index in simplex]
    origin = values[0]
    matrix = [[values[column + 1][row] - origin[row] for column in range(4)] for row in range(4)]
    return simplex, origin, invert(matrix)


def barycentric(chart, value):
    _, origin, inverse = chart
    delta = [value[index] - origin[index] for index in range(4)]
    tail = [sum(inverse[row][column] * delta[column] for column in range(4)) for row in range(4)]
    return (1 - sum(tail), *tail)


def parameter_interval(first, second):
    low, high = Fraction(0), Fraction(1)
    for left, right in zip(first, second):
        slope = right - left
        if slope > 0:
            low = max(low, -left / slope)
        elif slope < 0:
            high = min(high, -left / slope)
        elif left < 0:
            return None
    low, high = max(low, Fraction(0)), min(high, Fraction(1))
    return (low, high) if low <= high else None


def interpolate(start, end, parameter):
    return tuple(start[index] + parameter * (end[index] - start[index]) for index in range(4))


def affine_image(chart, target_vertices, value):
    simplex = chart[0]
    weights = barycentric(chart, value)
    return tuple(sum(weights[index] * target_vertices[simplex[index]][axis] for index in range(5)) for axis in range(4))


def map_segment(start, end, charts, target_vertices):
    intervals = []
    breaks = {Fraction(0), Fraction(1)}
    for index, chart in enumerate(charts):
        interval = parameter_interval(barycentric(chart, start), barycentric(chart, end))
        if interval is not None and interval[0] <= interval[1]:
            intervals.append((interval[0], interval[1], index)); breaks.update(interval)
    parameters = sorted(breaks)
    pieces = []
    for first, second in zip(parameters, parameters[1:]):
        if first == second:
            continue
        middle = (first + second) / 2
        candidates = [index for low, high, index in intervals if low <= middle <= high]
        if not candidates:
            raise AssertionError("segment interval is not covered by product simplices")
        simplex_index = min(candidates)
        chart = charts[simplex_index]
        source_first, source_second = interpolate(start, end, first), interpolate(start, end, second)
        target_first = affine_image(chart, target_vertices, source_first)
        target_second = affine_image(chart, target_vertices, source_second)
        pieces.append({
            "parameter_interval": [str(first), str(second)],
            "four_simplex_index": simplex_index,
            "source_vertices": [encode(source_first), encode(source_second)],
            "target_vertices": [encode(target_first), encode(target_second)],
        })
    if not pieces or Fraction(pieces[0]["parameter_interval"][0]) != 0 or Fraction(pieces[-1]["parameter_interval"][1]) != 1:
        raise AssertionError("piecewise-affine image does not cover the whole segment")
    return pieces


def map_polyline(values, charts, targets):
    return [map_segment(start, end, charts, targets) for start, end in zip(values, values[1:])]


def build(cache_path, input_cache_override=None):
    product = json.loads(PRODUCT.read_text(encoding="utf-8"))
    post_x = json.loads(POST_X.read_text(encoding="utf-8"))
    source_vertices = [point(value) for value in product["source_vertices"]]
    target_vertices = [point(value) for value in product["target_vertex_images"]]
    charts = [simplex_chart(source_vertices, simplex) for simplex in product["four_simplices"]]
    uniform_push = point(product["exteriorized_uniform_push_vector"])
    input_cache = input_cache_override or Path(post_x["cache_path"])
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(); counts = Counter(); source_segments = image_segments = 0
    header = {"record": "header", "schema": "t73_x_m1_ejected_band_lanes/v1", "product_extension_sha256": product["sha256"], "post_x_receipt_sha256": post_x["sha256"]}
    with input_cache.open("rb") as raw_input, cache_path.open("wb") as raw_output:
        with gzip.GzipFile(fileobj=raw_input, mode="rb") as compressed_input, gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as compressed_output:
            compressed_input.readline()
            line = (canonical(header) + "\n").encode(); compressed_output.write(line); digest.update(line)
            for raw_line in compressed_input:
                cell = json.loads(raw_line)
                record = {"record": "ejected_band_lanes", "band_index": cell["band_index"], "component": cell["component"], "lanes": {}}
                for lane_name in ("negative_band_lane", "positive_band_lane"):
                    core = [point(value) for value in cell[lane_name]["vertices"]]
                    pushed = [tuple(value[axis] + uniform_push[axis] for axis in range(4)) for value in core]
                    core_images = map_polyline(core, charts, target_vertices)
                    push_images = map_polyline(pushed, charts, target_vertices)
                    record["lanes"][lane_name] = {"core_segment_images": core_images, "outward_push_segment_images": push_images}
                    source_segments += len(core_images) + len(push_images)
                    image_segments += sum(len(value) for value in core_images) + sum(len(value) for value in push_images)
                line = (canonical(record) + "\n").encode(); compressed_output.write(line); digest.update(line)
                counts[cell["component"]] += 1
    receipt = {
        "schema": "t73_x_m1_ejected_band_lanes_receipt/v1",
        "cache_path": str(cache_path),
        "cache_size": cache_path.stat().st_size,
        "cache_sha256": file_sha(cache_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha(Path(__file__)),
        "product_extension_sha256": product["sha256"],
        "post_x_receipt_sha256": post_x["sha256"],
        "band_count": sum(counts.values()),
        "component_counts": dict(sorted(counts.items())),
        "source_core_and_push_segment_count": source_segments,
        "piecewise_affine_image_segment_count": image_segments,
        "verdict": "PASS_X_M1_EXACT_PIECEWISE_AFFINE_BAND_LANE_IMAGES",
        "scope_boundary": "band lanes and exteriorized pushes only; fixed source stubs and m1 complements remain to be merged into full hybrid path images",
    }
    receipt["sha256"] = canonical_sha(receipt)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path)
    parser.add_argument("--input-cache", type=Path)
    args = parser.parse_args(); cache = args.output or Path(os.environ.get("T73_X_M1_EJECTED_LANES_CACHE", DEFAULT_CACHE))
    receipt = build(cache, args.input_cache); print(json.dumps({"verdict": receipt["verdict"], "source_segments": receipt["source_core_and_push_segment_count"], "image_segments": receipt["piecewise_affine_image_segment_count"], "bytes": receipt["cache_size"]}, sort_keys=True))


if __name__ == "__main__":
    main()
