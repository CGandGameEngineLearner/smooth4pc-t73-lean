#!/usr/bin/env python3
"""Extract the required attaching-lane push paths from the failed disk model."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STRIPS = ROOT / "audit/t73_x_band_global_r3_port_strips_receipt.json"
LOCAL_PUSH = ROOT / "audit/t73_x_band_global_r3_push_disks_receipt.json"
DISK_OBSTRUCTION = ROOT / "audit/t73_x_band_global_r3_push_disk_obstruction.json"
CORE_EMBEDDING = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_core_embedding_v3.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_band_global_r3_lane_push_paths_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_band_global_r3_lane_push_paths.jsonl.gz"


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


def encode(values):
    return [str(value) for value in values]


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def lane_ribbon_triangles():
    triangles = []
    for segment in range(5):
        triangles.extend((
            [segment, segment + 1, 6 + segment + 1],
            [segment, 6 + segment + 1, 6 + segment],
        ))
    return triangles


def build(output_path):
    strips = json.loads(STRIPS.read_text())
    local_push = json.loads(LOCAL_PUSH.read_text())
    obstruction = json.loads(DISK_OBSTRUCTION.read_text())
    core_embedding = json.loads(CORE_EMBEDDING.read_text())
    displacement = point(local_push["push_displacement"])
    with gzip.open(resolve(strips["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        strip_records = [json.loads(line) for line in source]
    if not core_embedding["complete_replacement_core_embedding"]:
        raise AssertionError("complete v3 core embedding is missing")
    if obstruction["global_push_disk_status"] != "REFUTED":
        raise AssertionError("failed full-disk scope has not been recorded")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_band_global_r3_lane_push_paths/v1",
        "global_port_strips_receipt_sha256": strips["sha256"],
        "failed_local_push_disk_receipt_sha256": local_push["sha256"],
        "global_push_disk_obstruction_sha256": obstruction["sha256"],
        "complete_v3_core_embedding_sha256": core_embedding["sha256"],
        "push_displacement": [str(value) for value in displacement],
    }
    records = lanes = core_segments = push_segments = ribbon_triangles = 0
    template = lane_ribbon_triangles()
    with output_path.open("wb") as raw_output:
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            encoded = (canonical(header) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            for strip in strip_records:
                lane_records = []
                for name, raw_core in (
                    ("negative", strip["negative_lane_vertices"]),
                    ("positive", strip["positive_lane_vertices_reverse_orientation"]),
                ):
                    core = [point(value) for value in raw_core]
                    push = [add(value, displacement) for value in core]
                    lane_records.append({
                        "lane": name,
                        "orientation": "stored_attaching_component_order",
                        "core_vertices": [encode(value) for value in core],
                        "push_vertices": [encode(value) for value in push],
                        "ribbon_triangles": template,
                        "segment_count": len(core) - 1,
                        "ribbon_triangle_count": len(template),
                        "relative_twist": 0,
                    })
                    lanes += 1
                    core_segments += len(core) - 1
                    push_segments += len(push) - 1
                    ribbon_triangles += len(template)
                record = {
                    "record": "global_r3_x_band_lane_push_paths",
                    "band_index": strip["band_index"],
                    "component": strip["component"],
                    "lanes": lane_records,
                    "source_band_surface_sha256": strip["source_band_surface_sha256"],
                    "full_disk_translation_status": "REFUTED_NOT_USED",
                    "lane_framing_status": "CONSTRUCTED_AWAITING_GLOBAL_CLEARANCE",
                }
                encoded = (canonical(record) + "\n").encode()
                output.write(encoded)
                digest.update(encoded)
                records += 1
    receipt = {
        "schema": "t73_x_band_global_r3_lane_push_paths_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha256(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha256(Path(__file__)),
        "global_port_strips_receipt_sha256": strips["sha256"],
        "failed_local_push_disk_receipt_sha256": local_push["sha256"],
        "global_push_disk_obstruction_sha256": obstruction["sha256"],
        "complete_v3_core_embedding_sha256": core_embedding["sha256"],
        "push_displacement": [str(value) for value in displacement],
        "band_count": records,
        "lane_count": lanes,
        "core_segment_count": core_segments,
        "push_segment_count": push_segments,
        "ribbon_triangle_count": ribbon_triangles,
        "relative_twist_sum": 0,
        "full_disk_translation_status": "REFUTED_NOT_USED",
        "global_lane_push_clearance_status": "OPEN_EXACT_CORE_PUSH_AND_RIBBON_CHECK",
        "endpoint_push_gluing_status": "OPEN",
        "completion_status": "ALL_X_BAND_ATTACHING_LANE_PUSH_PATHS_CONSTRUCTED",
        "verdict": "PASS_X_BAND_GLOBAL_R3_LANE_PUSH_PATHS_CONSTRUCTED",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(os.environ.get("T73_X_BAND_GLOBAL_LANE_PUSH_CACHE", DEFAULT_OUTPUT))
    result = build(output)
    print(json.dumps({
        "verdict": result["verdict"],
        "bands": result["band_count"],
        "lanes": result["lane_count"],
        "segments": result["core_segment_count"],
        "ribbon_triangles": result["ribbon_triangle_count"],
        "clearance": result["global_lane_push_clearance_status"],
        "bytes": result["cache_size"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
