#!/usr/bin/env python3
"""Verify the receipt or fully stream the explicit post-x framed-cell cache."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
BUILDER = ROOT / "scripts/build_t73_post_x_framed_replacement_cells.py"
SOURCES = {
    "x_band_local_movie_sha256": ROOT / "geometry/t73_x_band_local_movie.json",
    "x_source_chart_germs_sha256": ROOT / "geometry/t73_x_source_chart_germs.json",
    "x_m1_parallel_foliation_sha256": ROOT / "geometry/t73_x_m1_parallel_foliation.json",
    "x_cancellation_sha256": ROOT / "geometry/t73_cancel_x_m1.json",
    "x_band_hybrid_movie_sha256": ROOT / "geometry/t73_x_band_hybrid_movie.json",
}

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


def check_receipt():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    source_hashes = {key: json.loads(path.read_text(encoding="utf-8"))["sha256"] for key, path in SOURCES.items()}
    checks = {
        "payload": receipt["sha256"] == canonical_sha({key: value for key, value in receipt.items() if key != "sha256"}),
        "builder": receipt["builder_sha256"] == file_sha(BUILDER),
        "sources": receipt["sources"] == source_hashes,
        "counts": receipt["framed_replacement_cell_count"] == 1513
        and receipt["component_counts"] == {"m_2": 269, "m_3": 1240, "r_xy": 2, "r_zx": 2}
        and receipt["band_surface_triangles"] == 6052
        and receipt["replacement_core_segments_per_cell"] == 40
        and receipt["explicit_core_path_vertices"] == 68085
        and receipt["explicit_push_path_vertices"] == 68085,
        "verdict": receipt["verdict"] == "PASS_POST_X_EXPLICIT_FRAMED_REPLACEMENT_CELL_CACHE",
    }
    if not all(checks.values()):
        raise AssertionError(f"post-x framed-cell receipt failed: {checks}")
    return receipt, checks


def nondegenerate_triangle(vertices, triangle):
    first, second, third = [vertices[index] for index in triangle]
    left = tuple(second[index] - first[index] for index in range(4))
    right = tuple(third[index] - first[index] for index in range(4))
    return any(left[i] * right[j] - left[j] * right[i] != 0 for i in range(4) for j in range(i + 1, 4))


def verify_full(check_cache_sha=False):
    receipt, fast_checks = check_receipt()
    cache = Path(receipt["cache_path"])
    if not cache.is_file():
        raise FileNotFoundError(cache)
    if cache.stat().st_size != receipt["cache_size"]:
        raise AssertionError("post-x cache size changed")
    if check_cache_sha and file_sha(cache) != receipt["cache_sha256"]:
        raise AssertionError("post-x cache byte SHA changed")
    local = json.loads(SOURCES["x_band_local_movie_sha256"].read_text(encoding="utf-8"))
    germs_data = json.loads(SOURCES["x_source_chart_germs_sha256"].read_text(encoding="utf-8"))
    germs = {item["band_index"]: item for item in germs_data["germs"]}
    cancellation = json.loads(SOURCES["x_cancellation_sha256"].read_text(encoding="utf-8"))
    hybrid = json.loads(SOURCES["x_band_hybrid_movie_sha256"].read_text(encoding="utf-8"))
    digest = hashlib.sha256()
    counts = Counter()
    triangles_checked = push_vertices_checked = normal_vertices_checked = 0
    with gzip.open(cache, "rb") as source:
        header_line = source.readline(); digest.update(header_line)
        header = json.loads(header_line)
        if header != {"record": "header", "schema": "t73_post_x_framed_replacement_cells/v1", "sources": receipt["sources"]}:
            raise AssertionError("post-x cache header changed")
        for expected_index, raw_line in enumerate(source):
            digest.update(raw_line)
            cell = json.loads(raw_line)
            if cell["record"] != "framed_replacement_cell" or cell["band_index"] != expected_index:
                raise AssertionError("post-x cache order changed")
            band = cancellation["slide_bands"][expected_index]
            local_record = local["bands"][expected_index]
            transition = hybrid["transitions"][expected_index]
            if (cell["component"] != band["component"] or cell["source_id"] != band["source_id"]
                    or cell["orientation"] != band["replacement_orientation"]
                    or cell["relative_twist"] != 0
                    or cell["framing_strategy"] != local_record["framing_strategy"]
                    or cell["hybrid_replacement_cell_sha256"] != transition["replacement_cell_sha256"]):
                raise AssertionError("post-x cell provenance changed")
            surface = cell["band_surface"]
            if (canonical_sha(surface["vertices"]) != local_record["vertices_sha256"]
                    or canonical_sha(surface["triangles"]) != local_record["triangles_sha256"]
                    or canonical_sha(surface["normal_field"]) != local_record["normal_field_sha256"]
                    or canonical_sha(surface["push_vertices"]) != local_record["push_off_vertices_sha256"]):
                raise AssertionError("post-x band surface hashes changed")
            if canonical_sha(cell["source_interval_global"]) != transition["source_interval_global_sha256"]:
                raise AssertionError("post-x source interval changed")
            source_interval = cell["source_interval_global"]
            source_arc = germs[expected_index]["global_oriented_arc"]
            width = Fraction(band["band_width"])
            if band["source_kind"] == "johnson_handle_lane":
                source_normal = (Fraction(0), width, width, Fraction(0))
            elif band["component"] == "r_xy":
                source_normal = (Fraction(0), Fraction(0), width, Fraction(0))
            elif band["component"] == "r_zx":
                source_normal = (Fraction(0), width, Fraction(0), Fraction(0))
            else:
                raise AssertionError("unknown source-stub framing rule")
            if germs[expected_index]["chart"] == "fiber_dual_global":
                source_arc = [value[:3] for value in source_arc]
                source_normal = source_normal[:3]
            for key, expected_vertices in (
                ("source_stub_before", [source_arc[0], source_interval[0]]),
                ("source_stub_after", [source_interval[1], source_arc[-1]]),
            ):
                piece = cell[key]
                if piece["vertices"] != expected_vertices or [point(value) for value in piece["normal_field"]] != [source_normal, source_normal]:
                    raise AssertionError(f"post-x source stub changed at band {expected_index}/{key}")
            for key, prefix in (("negative_band_lane", "negative_lane"), ("positive_band_lane", "positive_lane")):
                piece = cell[key]
                if (canonical_sha(piece["vertices"]) != transition[f"{prefix}_sha256"]
                        or canonical_sha(piece["normal_field"]) != transition[f"{prefix}_normal_sha256"]):
                    raise AssertionError("post-x band lane changed")
            target = cell["oriented_m1_parallel_complement"]
            if (target["level"] != transition["target_parallel_level"]
                    or target["closing_deck"] != transition["target_oriented_closing_deck"]
                    or canonical_sha(target["vertices"]) != transition["target_parallel_complement_sha256"]
                    or canonical_sha(target["normal_field"]) != transition["target_parallel_complement_normal_sha256"]):
                raise AssertionError("post-x target complement changed")
            vertices = [point(value) for value in surface["vertices"]]
            for triangle in surface["triangles"]:
                triangles_checked += 1
                if not nondegenerate_triangle(vertices, triangle):
                    raise AssertionError("post-x band has a degenerate triangle")
            if cell["chart_gluing_order"] != ["source_stub_before", "negative_band_lane", "oriented_m1_parallel_complement", "positive_band_lane", "source_stub_after"]:
                raise AssertionError("post-x path gluing order changed")
            for piece_name in ("band_surface", "source_stub_before", "negative_band_lane", "oriented_m1_parallel_complement", "positive_band_lane", "source_stub_after"):
                piece = cell[piece_name]
                values = [point(value) for value in piece["vertices"]]
                normals = [point(value) for value in piece["normal_field"]]
                pushes = [point(value) for value in piece["push_vertices"]]
                if not (len(values) == len(normals) == len(pushes)):
                    raise AssertionError("post-x framed path lengths disagree")
                for value, normal, push in zip(values, normals, pushes):
                    normal_vertices_checked += 1
                    if not any(normal):
                        raise AssertionError("post-x normal field vanished")
                    if push != tuple(value[index] + normal[index] for index in range(len(value))):
                        raise AssertionError("post-x push vertex is not value+normal")
                    push_vertices_checked += 1
            counts[cell["component"]] += 1
    if digest.hexdigest().upper() != receipt["record_stream_sha256"] or dict(sorted(counts.items())) != receipt["component_counts"]:
        raise AssertionError("post-x record stream/counts changed")
    if triangles_checked != 6052 or push_vertices_checked != 77163 or normal_vertices_checked != 77163:
        raise AssertionError("post-x full verification totals changed")
    return {
        "verdict": "PASS_POST_X_EXPLICIT_FRAMED_REPLACEMENT_CELLS_FULL",
        "fast_checks": fast_checks,
        "cells": sum(counts.values()),
        "component_counts": dict(sorted(counts.items())),
        "triangles_checked": triangles_checked,
        "normal_vertices_checked": normal_vertices_checked,
        "push_vertices_checked": push_vertices_checked,
        "cache_sha_checked": check_cache_sha,
        "scope_boundary": receipt["scope_boundary"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--check-cache-sha", action="store_true")
    args = parser.parse_args()
    if args.full:
        result = verify_full(args.check_cache_sha)
    else:
        receipt, checks = check_receipt()
        result = {"verdict": "PASS_POST_X_FRAMED_REPLACEMENT_CELL_RECEIPT", "checks": checks, "cells": receipt["framed_replacement_cell_count"]}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
