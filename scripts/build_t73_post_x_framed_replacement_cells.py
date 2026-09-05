#!/usr/bin/env python3
"""Stream all 1513 explicit post-x framed replacement cells to JSONL gzip."""

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

from build_t73_x_band_hybrid_movie import cut_complement, source_interval_global
from verify_t73_x_band_local_movie import expand_band

ROOT = Path(__file__).resolve().parents[1]
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
SOURCE_GERMS = ROOT / "geometry/t73_x_source_chart_germs.json"
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
HYBRID = ROOT / "geometry/t73_x_band_hybrid_movie.json"
RECEIPT = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
DEFAULT_CACHE = Path("/home/lifesize/.cache/t73_post_x_framed_replacement_cells.jsonl.gz")

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


def encode_points(values):
    return [encode(value) for value in values]


def add(left, right):
    return tuple(left[index] + right[index] for index in range(len(left)))


def pushed(points, normals):
    return [add(value, normal) for value, normal in zip(points, normals)]


def inputs():
    return {
        "local_movie": json.loads(LOCAL_MOVIE.read_text(encoding="utf-8")),
        "source_germs": json.loads(SOURCE_GERMS.read_text(encoding="utf-8")),
        "foliation": json.loads(FOLIATION.read_text(encoding="utf-8")),
        "cancellation": json.loads(CANCELLATION.read_text(encoding="utf-8")),
        "hybrid": json.loads(HYBRID.read_text(encoding="utf-8")),
    }


def source_hashes(data):
    return {
        "x_band_local_movie_sha256": data["local_movie"]["sha256"],
        "x_source_chart_germs_sha256": data["source_germs"]["sha256"],
        "x_m1_parallel_foliation_sha256": data["foliation"]["sha256"],
        "x_cancellation_sha256": data["cancellation"]["sha256"],
        "x_band_hybrid_movie_sha256": data["hybrid"]["sha256"],
    }


def iter_cells(data):
    local_records = data["local_movie"]["bands"]
    germs = {item["band_index"]: item for item in data["source_germs"]["germs"]}
    bands = data["cancellation"]["slide_bands"]
    transitions = data["hybrid"]["transitions"]
    base = [point(value) for value in data["foliation"]["base_vertices"]]
    base_normals = [point(value) for value in data["foliation"]["unit_normal_field"]]
    for band, local, transition in zip(bands, local_records, transitions):
        index = band["index"]
        if local["band_index"] != index or transition["band_index"] != index:
            raise AssertionError("x-band source streams lost alignment")
        germ = germs[index]
        vertices, triangles, normals, push_vertices, _, source_normal, _, _, strategy, selected = expand_band(band)
        orientation = band["replacement_orientation"]
        width = Fraction(band["band_width"])
        source_interval_local = [vertices[0], vertices[1]]
        source_interval = source_interval_global(source_interval_local, germ)
        source_arc = [point(value) for value in germ["global_oriented_arc"]]
        source_stub_normal = source_normal
        if germ["chart"] == "fiber_dual_global":
            source_arc = [value[:3] for value in source_arc]
            source_stub_normal = source_normal[:3]
        source_stub_before = [source_arc[0], source_interval[0]]
        source_stub_after = [source_interval[1], source_arc[-1]]
        source_stub_normals = [source_stub_normal, source_stub_normal]
        target_center = tuple((left + right) / 2 for left, right in zip(vertices[4], vertices[5]))
        before_local = (Fraction(2) - orientation * width, *target_center[1:])
        after_local = (Fraction(2) + orientation * width, *target_center[1:])
        level = local["target_parallel_coefficient"]
        level_points = [tuple(value[axis] + level * normal[axis] for axis in range(4))
                        for value, normal in zip(base, base_normals)]
        if orientation == 1:
            oriented_points, oriented_normals = level_points, list(base_normals)
            deck, center_index = (-1, 0, 1), 3
        else:
            oriented_points, oriented_normals = list(reversed(level_points)), list(reversed(base_normals))
            deck, center_index = (1, 0, -1), len(level_points) - 4
        before_global = (-before_local[0], before_local[1], before_local[2] + 4, Fraction(0))
        after_global = (-after_local[0], after_local[1], after_local[2] + 4, Fraction(0))
        complement, complement_normals = cut_complement(
            oriented_points, oriented_normals, center_index, before_global, after_global, deck
        )
        negative_ids, positive_ids = (0, 2, 4), (5, 3, 1)
        negative = [vertices[value] for value in negative_ids]
        negative_normals = [normals[value] for value in negative_ids]
        positive = [vertices[value] for value in positive_ids]
        positive_normals = [normals[value] for value in positive_ids]
        cell = {
            "record": "framed_replacement_cell",
            "band_index": index,
            "component": band["component"],
            "source_id": band["source_id"],
            "orientation": orientation,
            "relative_twist": band["relative_twist"],
            "framing_strategy": strategy,
            "selected_constant_push": encode(selected) if selected else None,
            "source_chart": germ["chart"],
            "source_interval_global": encode_points(source_interval),
            "source_stub_before": {
                "vertices": encode_points(source_stub_before),
                "normal_field": encode_points(source_stub_normals),
                "push_vertices": encode_points(pushed(source_stub_before, source_stub_normals)),
            },
            "band_surface": {
                "vertices": encode_points(vertices),
                "triangles": triangles,
                "normal_field": encode_points(normals),
                "push_vertices": encode_points(push_vertices),
            },
            "negative_band_lane": {
                "vertices": encode_points(negative),
                "normal_field": encode_points(negative_normals),
                "push_vertices": encode_points(pushed(negative, negative_normals)),
            },
            "oriented_m1_parallel_complement": {
                "level": level,
                "closing_deck": list(deck),
                "vertices": encode_points(complement),
                "normal_field": encode_points(complement_normals),
                "push_vertices": encode_points(pushed(complement, complement_normals)),
            },
            "positive_band_lane": {
                "vertices": encode_points(positive),
                "normal_field": encode_points(positive_normals),
                "push_vertices": encode_points(pushed(positive, positive_normals)),
            },
            "source_stub_after": {
                "vertices": encode_points(source_stub_after),
                "normal_field": encode_points(source_stub_normals),
                "push_vertices": encode_points(pushed(source_stub_after, source_stub_normals)),
            },
            "chart_gluing_order": [
                "source_stub_before",
                "negative_band_lane",
                "oriented_m1_parallel_complement",
                "positive_band_lane",
                "source_stub_after",
            ],
            "hybrid_replacement_cell_sha256": transition["replacement_cell_sha256"],
        }
        yield cell


def write_cache(cache_path: Path):
    data = inputs()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    stream_digest = hashlib.sha256()
    counts = Counter()
    header = {"record": "header", "schema": "t73_post_x_framed_replacement_cells/v1", "sources": source_hashes(data)}
    with cache_path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=6, mtime=0) as target:
            values = iter_cells(data)
            for value in (header,):
                line = (canonical(value) + "\n").encode()
                target.write(line); stream_digest.update(line)
            for value in values:
                line = (canonical(value) + "\n").encode()
                target.write(line); stream_digest.update(line)
                counts[value["component"]] += 1
    if sum(counts.values()) != 1513:
        raise AssertionError("post-x framed-cell count changed")
    receipt = {
        "schema": "t73_post_x_framed_replacement_cells_receipt/v1",
        "cache_path": str(cache_path),
        "cache_size": cache_path.stat().st_size,
        "cache_sha256": file_sha(cache_path),
        "record_stream_sha256": stream_digest.hexdigest().upper(),
        "builder_sha256": file_sha(Path(__file__)),
        "sources": source_hashes(data),
        "framed_replacement_cell_count": sum(counts.values()),
        "component_counts": dict(sorted(counts.items())),
        "band_surface_triangles": 1513 * 4,
        "replacement_core_segments_per_cell": 40,
        "explicit_core_path_vertices": 1513 * (2 + 3 + 35 + 3 + 2),
        "explicit_push_path_vertices": 1513 * (2 + 3 + 35 + 3 + 2),
        "verdict": "PASS_POST_X_EXPLICIT_FRAMED_REPLACEMENT_CELL_CACHE",
        "scope_boundary": "cells are explicit in their glued source/local charts; source-native S3 push-off projection and integer diagonal framings remain open",
    }
    receipt["sha256"] = canonical_sha(receipt)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cache = args.output or Path(os.environ.get("T73_POST_X_FRAMED_CACHE", DEFAULT_CACHE))
    receipt = write_cache(cache)
    print(json.dumps({"verdict": receipt["verdict"], "cells": receipt["framed_replacement_cell_count"], "bytes": receipt["cache_size"]}, sort_keys=True))


if __name__ == "__main__":
    main()
