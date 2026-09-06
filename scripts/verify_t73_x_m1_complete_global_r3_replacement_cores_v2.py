#!/usr/bin/env python3
"""Verify the complete R3 replacement-core assembly with v2 transitions."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_cores_v2_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
BANDS = ROOT / "audit/t73_x_band_global_r3_port_strips_receipt.json"
TRANSITIONS = ROOT / "audit/t73_x_m1_repaired_global_r3_middle_transition_cores_receipt.json"
MIDDLES = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
CLEARANCE = ROOT / "audit/t73_x_m1_repaired_stub_cross_clearance.json"


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


def read_records(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        return [json.loads(line) for line in source]


def stub_path(record, name):
    pieces = record["stubs"][name]["pieces"]
    return [pieces[0]["r3_vertices"][0]] + [piece["r3_vertices"][1] for piece in pieces]


def translated_middle(record, translation):
    return [
        [str(Fraction(value[axis]) + translation[axis]) for axis in range(3)]
        for value in record["core_vertices_r3"]
    ]


def verify(check_cache_sha=True):
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("v2 complete-core receipt SHA mismatch")
    sources = {
        "stubs": json.loads(STUBS.read_text()),
        "bands": json.loads(BANDS.read_text()),
        "transitions": json.loads(TRANSITIONS.read_text()),
        "middles": json.loads(MIDDLES.read_text()),
        "clearance": json.loads(CLEARANCE.read_text()),
    }
    bindings = {
        "splice_stub_cores_r3_receipt_sha256": sources["stubs"]["sha256"],
        "global_band_port_strips_receipt_sha256": sources["bands"]["sha256"],
        "repaired_middle_transition_cores_receipt_sha256": sources["transitions"]["sha256"],
        "middle_paths_r3_receipt_sha256": sources["middles"]["sha256"],
        "repaired_stub_cross_clearance_sha256": sources["clearance"]["sha256"],
    }
    if any(data[key] != value for key, value in bindings.items()):
        raise AssertionError("v2 complete-core source binding changed")
    cache = resolve(data["cache_path"])
    if not cache.is_file() or cache.stat().st_size != data["cache_size"]:
        raise AssertionError("v2 complete-core cache missing or resized")
    if check_cache_sha and file_sha256(cache) != data["cache_sha256"]:
        raise AssertionError("v2 complete-core cache SHA mismatch")
    records = {name: read_records(value) for name, value in sources.items() if name != "clearance"}
    output = []
    digest = hashlib.sha256()
    with gzip.open(cache, "rt", encoding="utf-8") as source:
        for line_number, line in enumerate(source):
            digest.update(line.encode())
            if line_number:
                output.append(json.loads(line))
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("v2 complete-core record-stream SHA mismatch")
    translation = tuple(Fraction(value) for value in sources["transitions"]["middle_chart_translation"])
    names = (
        "source_stub_before", "negative_band_lane", "target_complement_first",
        "repaired_middle_transition_first", "translated_m1_parallel_middle",
        "repaired_middle_transition_last", "target_complement_last",
        "positive_band_lane", "source_stub_after",
    )
    segment_count = boundary_matches = 0
    for index, saved in enumerate(output):
        stub = records["stubs"][index]
        band = records["bands"][index]
        middle = records["middles"][index]
        first = records["transitions"][2 * index]
        last = records["transitions"][2 * index + 1]
        paths = (
            stub_path(stub, "source_stub_before"),
            band["negative_lane_vertices"],
            stub_path(stub, "target_complement_first"),
            first["core_vertices"],
            translated_middle(middle, translation),
            last["core_vertices"],
            stub_path(stub, "target_complement_last"),
            band["positive_lane_vertices_reverse_orientation"],
            stub_path(stub, "source_stub_after"),
        )
        vertices = []
        ranges = []
        for name, path in zip(names, paths):
            if vertices and vertices[-1] != path[0]:
                raise AssertionError(f"v2 path {index} breaks before {name}")
            low = len(vertices) - 1 if vertices else 0
            vertices.extend(path if not vertices else path[1:])
            ranges.append({
                "piece": name,
                "segment_range": [low, len(vertices) - 1],
                "segment_count": len(path) - 1,
            })
        if saved["vertices"] != vertices or saved["piece_ranges"] != ranges:
            raise AssertionError(f"v2 complete-core record {index} changed")
        if not saved["prior_v1_collision_repaired"]:
            raise AssertionError("v2 record lost its repair marker")
        segment_count += len(vertices) - 1
        boundary_matches += 8
    if len(output) != 1513 or (segment_count, boundary_matches) != (92284, 12104):
        raise AssertionError("v2 complete-core totals changed")
    if not data["old_exact_collision_repaired"]:
        raise AssertionError("v2 receipt lost its collision repair")
    return {
        "verdict": "PASS_X_M1_COMPLETE_GLOBAL_R3_REPLACEMENT_CORES_V2_FULL",
        "records_reconstructed": len(output),
        "core_segments_reconstructed": segment_count,
        "cross_piece_boundary_matches": boundary_matches,
        "old_exact_collision_repaired": True,
        "cache_sha_checked": check_cache_sha,
        "remaining_core_clearance": data["remaining_core_clearance"],
        "complete_push_paths": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
