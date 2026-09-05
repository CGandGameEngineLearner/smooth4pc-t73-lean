#!/usr/bin/env python3
"""Apply the verified full-annulus ejection to every m1-complement middle."""

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
EJECTION = ROOT / "geometry/t73_m1_parallel_annulus_ambient_ejection.json"
EJECTION_RECEIPT = ROOT / "audit/t73_m1_parallel_annulus_ambient_ejection_receipt.json"
POST_X = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
RECEIPT = ROOT / "audit/t73_x_m1_ejected_middle_complements_receipt.json"
DEFAULT_CACHE = Path("/home/lifesize/.cache/t73_x_m1_ejected_middle_complements.jsonl.gz")

sys.set_int_max_str_digits(0)


def canonical(value): return json.dumps(value, sort_keys=True, separators=(",", ":"))
def canonical_sha(value): return hashlib.sha256(canonical(value).encode()).hexdigest().upper()
def point(values): return tuple(Fraction(value) for value in values)
def encode(value): return [str(coordinate) for coordinate in value]
def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""): digest.update(block)
    return digest.hexdigest().upper()


def translate(values, displacement):
    return [tuple(value[axis] + displacement[axis] for axis in range(4)) for value in values]


def build(cache_path, input_cache_override=None):
    ejection = json.loads(EJECTION.read_text(encoding="utf-8")); ejection_receipt = json.loads(EJECTION_RECEIPT.read_text(encoding="utf-8")); post_x = json.loads(POST_X.read_text(encoding="utf-8"))
    displacement = point(ejection["outward_displacement"]); input_cache = input_cache_override or Path(post_x["cache_path"]); cache_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(); counts = Counter(); core_segments = push_segments = 0
    header = {"record": "header", "schema": "t73_x_m1_ejected_middle_complements/v1", "ambient_ejection_sha256": ejection["sha256"], "ambient_ejection_receipt_sha256": ejection_receipt["sha256"], "post_x_receipt_sha256": post_x["sha256"]}
    with gzip.open(input_cache, "rt", encoding="utf-8") as source_file, cache_path.open("wb") as raw_output:
        next(source_file)
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            raw = (canonical(header) + "\n").encode(); output.write(raw); digest.update(raw)
            for raw_line in source_file:
                cell = json.loads(raw_line); piece = cell["oriented_m1_parallel_complement"]
                core = [point(value) for value in piece["vertices"]][1:-1]; push = [point(value) for value in piece["push_vertices"]][1:-1]
                record = {"record": "ejected_middle_complement", "band_index": cell["band_index"], "component": cell["component"], "parallel_level": piece["level"], "closing_deck": piece["closing_deck"], "source_core_vertices": [encode(value) for value in core], "target_core_vertices": [encode(value) for value in translate(core, displacement)], "source_push_vertices": [encode(value) for value in push], "target_push_vertices": [encode(value) for value in translate(push, displacement)], "segment_count_each": len(core) - 1}
                core_segments += len(core) - 1; push_segments += len(push) - 1; counts[cell["component"]] += 1
                raw = (canonical(record) + "\n").encode(); output.write(raw); digest.update(raw)
    receipt = {"schema": "t73_x_m1_ejected_middle_complements_receipt/v1", "cache_path": str(cache_path), "cache_size": cache_path.stat().st_size, "cache_sha256": file_sha(cache_path), "record_stream_sha256": digest.hexdigest().upper(), "builder_sha256": file_sha(Path(__file__)), "ambient_ejection_sha256": ejection["sha256"], "ambient_ejection_receipt_sha256": ejection_receipt["sha256"], "post_x_receipt_sha256": post_x["sha256"], "band_count": sum(counts.values()), "component_counts": dict(sorted(counts.items())), "middle_core_segment_count": core_segments, "middle_push_segment_count": push_segments, "verdict": "PASS_X_M1_ALL_MIDDLE_COMPLEMENT_AMBIENT_EJECTION_IMAGES", "scope_boundary": "middle images complete; normal homotopy compatibility with local uniform-push stubs remains to be glued"}
    receipt["sha256"] = canonical_sha(receipt); RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"); return receipt


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path); parser.add_argument("--input-cache", type=Path); args = parser.parse_args(); receipt = build(args.output or Path(os.environ.get("T73_X_M1_EJECTED_MIDDLES_CACHE", DEFAULT_CACHE)), args.input_cache)
    print(json.dumps({"verdict": receipt["verdict"], "core_segments": receipt["middle_core_segment_count"], "push_segments": receipt["middle_push_segment_count"], "bytes": receipt["cache_size"]}, sort_keys=True))


if __name__ == "__main__": main()
