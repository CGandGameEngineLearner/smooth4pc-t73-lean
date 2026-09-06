#!/usr/bin/env python3
"""Replace v2 transitions by negative-height v3 routes in the full assembly."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V2_ASSEMBLY = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_cores_v2_receipt.json"
V3_TRANSITIONS = ROOT / "audit/t73_x_m1_negative_global_r3_middle_transition_cores_v3_receipt.json"
V3_BAND_CLEARANCE = ROOT / "audit/t73_x_m1_negative_transition_band_clearance.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_cores_v3_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_m1_complete_global_r3_replacement_cores_v3.jsonl.gz"


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


def records(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        return [json.loads(line) for line in source]


def extract(record, piece_name):
    piece = next(value for value in record["piece_ranges"] if value["piece"] == piece_name)
    low, high = piece["segment_range"]
    return record["vertices"][low:high + 1]


def append(vertices, path, name, ranges):
    if vertices and vertices[-1] != path[0]:
        raise AssertionError(f"v3 full assembly breaks before {name}")
    low = len(vertices) - 1 if vertices else 0
    vertices.extend(path if not vertices else path[1:])
    ranges.append({
        "piece": name,
        "segment_range": [low, len(vertices) - 1],
        "segment_count": len(path) - 1,
    })


def build(output_path):
    v2 = json.loads(V2_ASSEMBLY.read_text())
    v3 = json.loads(V3_TRANSITIONS.read_text())
    clearance = json.loads(V3_BAND_CLEARANCE.read_text())
    old_records = records(v2)
    transitions = records(v3)
    if (len(old_records), len(transitions)) != (1513, 3026):
        raise AssertionError("v3 full assembly source inventory changed")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_complete_global_r3_replacement_cores/v3",
        "complete_v2_assembly_receipt_sha256": v2["sha256"],
        "negative_v3_transition_receipt_sha256": v3["sha256"],
        "negative_transition_band_clearance_sha256": clearance["sha256"],
    }
    count = segments = matches = 0
    with output_path.open("wb") as raw_output:
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            encoded = (canonical(header) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            for index, old in enumerate(old_records):
                first = transitions[2 * index]
                last = transitions[2 * index + 1]
                pieces = (
                    ("source_stub_before", extract(old, "source_stub_before")),
                    ("negative_band_lane", extract(old, "negative_band_lane")),
                    ("target_complement_first", extract(old, "target_complement_first")),
                    ("negative_middle_transition_first", first["core_vertices"]),
                    ("translated_m1_parallel_middle", extract(old, "translated_m1_parallel_middle")),
                    ("negative_middle_transition_last", last["core_vertices"]),
                    ("target_complement_last", extract(old, "target_complement_last")),
                    ("positive_band_lane", extract(old, "positive_band_lane")),
                    ("source_stub_after", extract(old, "source_stub_after")),
                )
                vertices = []
                ranges = []
                for name, path in pieces:
                    append(vertices, path, name, ranges)
                record = {
                    "record": "complete_global_r3_replacement_core_v3",
                    "band_index": index,
                    "component": old["component"],
                    "vertices": vertices,
                    "piece_ranges": ranges,
                    "segment_count": len(vertices) - 1,
                    "outer_start": vertices[0],
                    "outer_end": vertices[-1],
                    "v1_collision_repaired": True,
                    "negative_height_transition_separation": True,
                    "source_relative_status": "COMPLETE_REPLACEMENT_CORE_V3_ALL_PIECES_PORT_GLUED",
                }
                encoded = (canonical(record) + "\n").encode()
                output.write(encoded)
                digest.update(encoded)
                count += 1
                segments += len(vertices) - 1
                matches += 8
    receipt = {
        "schema": "t73_x_m1_complete_global_r3_replacement_cores_receipt/v3",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha256(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha256(Path(__file__)),
        "complete_v2_assembly_receipt_sha256": v2["sha256"],
        "negative_v3_transition_receipt_sha256": v3["sha256"],
        "negative_transition_band_clearance_sha256": clearance["sha256"],
        "record_count": count,
        "core_segment_count": segments,
        "cross_piece_boundary_match_count": matches,
        "piece_count_per_record": 9,
        "complete_core_embedding_status": "OPEN_AGGREGATE_ALL_CLEARANCE_CERTIFICATES",
        "complete_push_paths_status": "OPEN",
        "completion_status": "ALL_POST_X_REPLACEMENT_CORES_REASSEMBLED_WITH_NEGATIVE_V3_TRANSITIONS",
        "verdict": "PASS_X_M1_COMPLETE_GLOBAL_R3_REPLACEMENT_CORE_V3_ASSEMBLY",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(os.environ.get("T73_X_M1_COMPLETE_GLOBAL_R3_CORE_V3_CACHE", DEFAULT_OUTPUT))
    result = build(output)
    print(json.dumps({
        "verdict": result["verdict"],
        "records": result["record_count"],
        "segments": result["core_segment_count"],
        "matches": result["cross_piece_boundary_match_count"],
        "embedding": result["complete_core_embedding_status"],
        "bytes": result["cache_size"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
