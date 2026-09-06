#!/usr/bin/env python3
"""Verify the complete core assembly using negative-height v3 transitions."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_cores_v3_receipt.json"
V2 = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_cores_v2_receipt.json"
V3 = ROOT / "audit/t73_x_m1_negative_global_r3_middle_transition_cores_v3_receipt.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


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


def extract(record, name):
    piece = next(value for value in record["piece_ranges"] if value["piece"] == name)
    low, high = piece["segment_range"]
    return record["vertices"][low:high + 1]


def verify(check_cache_sha=True):
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("v3 complete-core receipt SHA mismatch")
    v2 = json.loads(V2.read_text())
    v3 = json.loads(V3.read_text())
    if data["complete_v2_assembly_receipt_sha256"] != v2["sha256"]:
        raise AssertionError("v3 complete-core v2 binding changed")
    if data["negative_v3_transition_receipt_sha256"] != v3["sha256"]:
        raise AssertionError("v3 complete-core transition binding changed")
    cache = resolve(data["cache_path"])
    if not cache.is_file() or cache.stat().st_size != data["cache_size"]:
        raise AssertionError("v3 complete-core cache missing or resized")
    if check_cache_sha and file_sha256(cache) != data["cache_sha256"]:
        raise AssertionError("v3 complete-core cache SHA mismatch")
    old_records = records(v2)
    transitions = records(v3)
    output = []
    digest = hashlib.sha256()
    with gzip.open(cache, "rt", encoding="utf-8") as source:
        for line_number, line in enumerate(source):
            digest.update(line.encode())
            if line_number:
                output.append(json.loads(line))
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("v3 complete-core stream SHA mismatch")
    names = (
        "source_stub_before", "negative_band_lane", "target_complement_first",
        "negative_middle_transition_first", "translated_m1_parallel_middle",
        "negative_middle_transition_last", "target_complement_last",
        "positive_band_lane", "source_stub_after",
    )
    segments = matches = 0
    for index, (old, saved) in enumerate(zip(old_records, output)):
        paths = (
            extract(old, "source_stub_before"),
            extract(old, "negative_band_lane"),
            extract(old, "target_complement_first"),
            transitions[2 * index]["core_vertices"],
            extract(old, "translated_m1_parallel_middle"),
            transitions[2 * index + 1]["core_vertices"],
            extract(old, "target_complement_last"),
            extract(old, "positive_band_lane"),
            extract(old, "source_stub_after"),
        )
        vertices = []
        ranges = []
        for name, path in zip(names, paths):
            if vertices and vertices[-1] != path[0]:
                raise AssertionError(f"v3 complete path {index} breaks before {name}")
            low = len(vertices) - 1 if vertices else 0
            vertices.extend(path if not vertices else path[1:])
            ranges.append({
                "piece": name,
                "segment_range": [low, len(vertices) - 1],
                "segment_count": len(path) - 1,
            })
        if saved["vertices"] != vertices or saved["piece_ranges"] != ranges:
            raise AssertionError(f"v3 complete-core record {index} changed")
        if not saved["negative_height_transition_separation"]:
            raise AssertionError("v3 record lost negative-height marker")
        segments += len(vertices) - 1
        matches += 8
    if len(output) != 1513 or (segments, matches) != (92284, 12104):
        raise AssertionError("v3 complete-core totals changed")
    return {
        "verdict": "PASS_X_M1_COMPLETE_GLOBAL_R3_REPLACEMENT_CORES_V3_FULL",
        "records_reconstructed": len(output),
        "core_segments_reconstructed": segments,
        "cross_piece_boundary_matches": matches,
        "negative_height_transitions": 3026,
        "cache_sha_checked": check_cache_sha,
        "complete_core_embedding": data["complete_core_embedding_status"],
        "complete_push_paths": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
