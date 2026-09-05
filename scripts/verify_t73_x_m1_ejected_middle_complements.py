#!/usr/bin/env python3
"""Verify every middle-complement core/push image under ambient ejection."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "audit/t73_x_m1_ejected_middle_complements_receipt.json"
BUILDER = ROOT / "scripts/build_t73_x_m1_ejected_middle_complements.py"
EJECTION = ROOT / "geometry/t73_m1_parallel_annulus_ambient_ejection.json"
EJECTION_RECEIPT = ROOT / "audit/t73_m1_parallel_annulus_ambient_ejection_receipt.json"
POST_X = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"

sys.set_int_max_str_digits(0)


def canonical_sha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()
def point(values): return tuple(Fraction(value) for value in values)
def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""): digest.update(block)
    return digest.hexdigest().upper()
def resolve(value):
    path = Path(value)
    if path.exists() or len(value) < 3 or value[1:3] not in (":\\", ":/"): return path
    return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")


def check_receipt():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8")); ejection = json.loads(EJECTION.read_text(encoding="utf-8")); ejection_receipt = json.loads(EJECTION_RECEIPT.read_text(encoding="utf-8")); post_x = json.loads(POST_X.read_text(encoding="utf-8"))
    checks = {"payload": receipt["sha256"] == canonical_sha({key: value for key, value in receipt.items() if key != "sha256"}), "builder": receipt["builder_sha256"] == file_sha(BUILDER), "sources": receipt["ambient_ejection_sha256"] == ejection["sha256"] and receipt["ambient_ejection_receipt_sha256"] == ejection_receipt["sha256"] and receipt["post_x_receipt_sha256"] == post_x["sha256"], "counts": receipt["band_count"] == 1513 and receipt["middle_core_segment_count"] == 48416 and receipt["middle_push_segment_count"] == 48416, "verdict": receipt["verdict"] == "PASS_X_M1_ALL_MIDDLE_COMPLEMENT_AMBIENT_EJECTION_IMAGES"}
    if not all(checks.values()): raise AssertionError(f"middle-complement receipt failed: {checks}")
    return receipt, checks


def verify_full(input_cache=None, check_cache_sha=False):
    receipt, checks = check_receipt(); ejection = json.loads(EJECTION.read_text(encoding="utf-8")); post_x = json.loads(POST_X.read_text(encoding="utf-8")); displacement = point(ejection["outward_displacement"])
    output_cache = resolve(receipt["cache_path"]); input_cache = input_cache or resolve(post_x["cache_path"])
    if check_cache_sha and file_sha(output_cache) != receipt["cache_sha256"]: raise AssertionError("middle-complement cache SHA changed")
    core_segments = push_segments = vertex_image_checks = 0
    with gzip.open(input_cache, "rt", encoding="utf-8") as source_file, gzip.open(output_cache, "rt", encoding="utf-8") as image_file:
        next(source_file); header = json.loads(next(image_file))
        if header["schema"] != "t73_x_m1_ejected_middle_complements/v1" or header["ambient_ejection_sha256"] != ejection["sha256"]: raise AssertionError("middle-complement cache header changed")
        for index, (source_line, image_line) in enumerate(zip(source_file, image_file)):
            cell, record = json.loads(source_line), json.loads(image_line); piece = cell["oriented_m1_parallel_complement"]
            if record["band_index"] != index or record["component"] != cell["component"] or record["parallel_level"] != piece["level"] or record["closing_deck"] != piece["closing_deck"]: raise AssertionError("middle-complement provenance changed")
            source_core = [point(value) for value in piece["vertices"]][1:-1]; source_push = [point(value) for value in piece["push_vertices"]][1:-1]
            if [point(value) for value in record["source_core_vertices"]] != source_core or [point(value) for value in record["source_push_vertices"]] != source_push: raise AssertionError("middle source paths changed")
            for source_values, field in ((source_core, "target_core_vertices"), (source_push, "target_push_vertices")):
                targets = [point(value) for value in record[field]]
                expected = [tuple(value[axis] + displacement[axis] for axis in range(4)) for value in source_values]
                if targets != expected: raise AssertionError("middle ambient-ejection image changed")
                vertex_image_checks += len(expected)
            if record["segment_count_each"] != 32: raise AssertionError("middle segment count per band changed")
            core_segments += 32; push_segments += 32
        if next(source_file, None) is not None or next(image_file, None) is not None: raise AssertionError("middle/source cache lengths differ")
    if (core_segments, push_segments) != (48416, 48416): raise AssertionError("middle full totals changed")
    return {"verdict": "PASS_X_M1_EJECTED_MIDDLE_COMPLEMENTS_FULL", "fast_checks": checks, "core_segments": core_segments, "push_segments": push_segments, "vertex_image_checks": vertex_image_checks, "cache_sha_checked": check_cache_sha, "framing_gluing_status": "OPEN_NORMAL_HOMOTOPY_AT_SPLICE_BOUNDARIES"}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--full", action="store_true"); parser.add_argument("--input-cache", type=Path); parser.add_argument("--check-cache-sha", action="store_true"); args = parser.parse_args()
    result = verify_full(args.input_cache, args.check_cache_sha) if args.full else {"verdict": "PASS_X_M1_EJECTED_MIDDLE_COMPLEMENTS_RECEIPT", "checks": check_receipt()[1], "core_segments": check_receipt()[0]["middle_core_segment_count"]}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__": main()
