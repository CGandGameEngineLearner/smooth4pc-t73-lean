#!/usr/bin/env python3
"""Independently rebuild all complete post-x replacement core paths."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_cores_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
BANDS = ROOT / "audit/t73_x_band_global_r3_port_strips_receipt.json"
TRANSITIONS = ROOT / "audit/t73_x_m1_global_r3_middle_transition_cores_receipt.json"
MIDDLES = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"


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


def stub_path(record, name):
    pieces = record["stubs"][name]["pieces"]
    return [pieces[0]["r3_vertices"][0]] + [piece["r3_vertices"][1] for piece in pieces]


def translate_middle(record, translation):
    return [
        [str(Fraction(value[axis]) + translation[axis]) for axis in range(3)]
        for value in record["core_vertices_r3"]
    ]


def verify(check_cache_sha=True):
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("complete R3 replacement receipt SHA mismatch")
    sources = {
        "stubs": json.loads(STUBS.read_text()),
        "bands": json.loads(BANDS.read_text()),
        "transitions": json.loads(TRANSITIONS.read_text()),
        "middles": json.loads(MIDDLES.read_text()),
    }
    bindings = {
        "splice_stub_cores_r3_receipt_sha256": sources["stubs"]["sha256"],
        "global_band_port_strips_receipt_sha256": sources["bands"]["sha256"],
        "global_middle_transition_cores_receipt_sha256": sources["transitions"]["sha256"],
        "middle_paths_r3_receipt_sha256": sources["middles"]["sha256"],
    }
    if any(data[key] != value for key, value in bindings.items()):
        raise AssertionError("complete R3 replacement source binding changed")
    cache = resolve(data["cache_path"])
    if not cache.is_file() or cache.stat().st_size != data["cache_size"]:
        raise AssertionError("complete R3 replacement cache missing or resized")
    if check_cache_sha and file_sha256(cache) != data["cache_sha256"]:
        raise AssertionError("complete R3 replacement cache SHA mismatch")
    source_records = {name: records(receipt) for name, receipt in sources.items()}
    output_records = []
    digest = hashlib.sha256()
    with gzip.open(cache, "rt", encoding="utf-8") as source:
        for line_number, line in enumerate(source):
            digest.update(line.encode())
            if line_number:
                output_records.append(json.loads(line))
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("complete R3 replacement record stream SHA mismatch")
    if len(output_records) != 1513:
        raise AssertionError("complete R3 replacement output count changed")
    translation = tuple(Fraction(value) for value in sources["transitions"]["middle_chart_translation"])
    piece_names = (
        "source_stub_before", "negative_band_lane", "target_complement_first",
        "middle_transition_first", "translated_m1_parallel_middle",
        "middle_transition_last", "target_complement_last",
        "positive_band_lane", "source_stub_after",
    )
    segments = boundary_matches = 0
    component_counts = {}
    for index, output in enumerate(output_records):
        stub = source_records["stubs"][index]
        band = source_records["bands"][index]
        middle = source_records["middles"][index]
        first = source_records["transitions"][2 * index]
        last = source_records["transitions"][2 * index + 1]
        paths = (
            stub_path(stub, "source_stub_before"),
            band["negative_lane_vertices"],
            stub_path(stub, "target_complement_first"),
            first["core_vertices"],
            translate_middle(middle, translation),
            last["core_vertices"],
            stub_path(stub, "target_complement_last"),
            band["positive_lane_vertices_reverse_orientation"],
            stub_path(stub, "source_stub_after"),
        )
        vertices = []
        expected_ranges = []
        for name, path in zip(piece_names, paths):
            if vertices and vertices[-1] != path[0]:
                raise AssertionError(f"replayed complete path {index} breaks before {name}")
            start = len(vertices) - 1 if vertices else 0
            vertices.extend(path if not vertices else path[1:])
            expected_ranges.append({
                "piece": name,
                "segment_range": [start, len(vertices) - 1],
                "segment_count": len(path) - 1,
            })
        if output["vertices"] != vertices or output["piece_ranges"] != expected_ranges:
            raise AssertionError(f"complete R3 replacement path {index} changed")
        if output["outer_start"] != vertices[0] or output["outer_end"] != vertices[-1]:
            raise AssertionError("complete R3 replacement outer ports changed")
        segments += len(vertices) - 1
        boundary_matches += 8
        component_counts[output["component"]] = component_counts.get(output["component"], 0) + 1
    if (segments, boundary_matches) != (89258, 12104):
        raise AssertionError("complete R3 replacement replay totals changed")
    if dict(sorted(component_counts.items())) != data["component_counts"]:
        raise AssertionError("complete R3 replacement component counts changed")
    if data["global_core_embedding_clearance_status"] != "OPEN_EXACT_ALL_SEGMENTS":
        raise AssertionError("complete core assembly was overstated as embedded")
    return {
        "verdict": "PASS_X_M1_COMPLETE_GLOBAL_R3_REPLACEMENT_CORES_FULL",
        "records_reconstructed": 1513,
        "core_segments_reconstructed": segments,
        "cross_piece_boundary_matches": boundary_matches,
        "pieces_per_record": 9,
        "cache_sha_checked": check_cache_sha,
        "global_core_embedding_clearance": "OPEN",
        "complete_push_paths": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
