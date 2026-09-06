#!/usr/bin/env python3
"""Assemble every complete post-x replacement core path in one R3 chart."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUBS = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
BANDS = ROOT / "audit/t73_x_band_global_r3_port_strips_receipt.json"
TRANSITIONS = ROOT / "audit/t73_x_m1_global_r3_middle_transition_cores_receipt.json"
MIDDLES = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_cores_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_m1_complete_global_r3_replacement_cores.jsonl.gz"


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


def read_records(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        return [json.loads(line) for line in source]


def stub_path(record, name):
    pieces = record["stubs"][name]["pieces"]
    return [pieces[0]["r3_vertices"][0]] + [piece["r3_vertices"][1] for piece in pieces]


def translated_middle(record, translation):
    result = []
    for raw in record["core_vertices_r3"]:
        value = [Fraction(coordinate) for coordinate in raw]
        result.append([str(value[axis] + translation[axis]) for axis in range(3)])
    return result


def append_path(vertices, path, label, ranges):
    if vertices and vertices[-1] != path[0]:
        raise AssertionError(f"complete replacement R3 path breaks before {label}")
    start = len(vertices) - 1 if vertices else 0
    vertices.extend(path if not vertices else path[1:])
    ranges.append({
        "piece": label,
        "segment_range": [start, len(vertices) - 1],
        "segment_count": len(path) - 1,
    })


def build(output_path):
    stubs = json.loads(STUBS.read_text())
    bands = json.loads(BANDS.read_text())
    transitions = json.loads(TRANSITIONS.read_text())
    middles = json.loads(MIDDLES.read_text())
    stub_records = read_records(stubs)
    band_records = read_records(bands)
    transition_records = read_records(transitions)
    middle_records = read_records(middles)
    if (len(stub_records), len(band_records), len(transition_records), len(middle_records)) != (1513, 1513, 3026, 1513):
        raise AssertionError("complete replacement R3 source inventory changed")
    translation = tuple(Fraction(value) for value in transitions["middle_chart_translation"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_complete_global_r3_replacement_cores/v1",
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "global_band_port_strips_receipt_sha256": bands["sha256"],
        "global_middle_transition_cores_receipt_sha256": transitions["sha256"],
        "middle_paths_r3_receipt_sha256": middles["sha256"],
        "middle_chart_translation": [str(value) for value in translation],
    }
    records = segments = boundary_matches = 0
    component_counts = {}
    with output_path.open("wb") as raw_output:
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            encoded = (canonical(header) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            for index, (stub, band, middle) in enumerate(zip(stub_records, band_records, middle_records)):
                first_transition = transition_records[2 * index]
                last_transition = transition_records[2 * index + 1]
                if not (
                    stub["band_index"] == band["band_index"] == middle["band_index"] == index
                    and first_transition["band_index"] == last_transition["band_index"] == index
                    and first_transition["side"] == "first"
                    and last_transition["side"] == "last"
                ):
                    raise AssertionError("complete replacement R3 source order changed")
                pieces = (
                    ("source_stub_before", stub_path(stub, "source_stub_before")),
                    ("negative_band_lane", band["negative_lane_vertices"]),
                    ("target_complement_first", stub_path(stub, "target_complement_first")),
                    ("middle_transition_first", first_transition["core_vertices"]),
                    ("translated_m1_parallel_middle", translated_middle(middle, translation)),
                    ("middle_transition_last", last_transition["core_vertices"]),
                    ("target_complement_last", stub_path(stub, "target_complement_last")),
                    ("positive_band_lane", band["positive_lane_vertices_reverse_orientation"]),
                    ("source_stub_after", stub_path(stub, "source_stub_after")),
                )
                vertices = []
                ranges = []
                for label, path in pieces:
                    append_path(vertices, path, label, ranges)
                boundary_matches += len(pieces) - 1
                segment_count = len(vertices) - 1
                record = {
                    "record": "complete_global_r3_replacement_core",
                    "band_index": index,
                    "component": stub["component"],
                    "vertices": vertices,
                    "piece_ranges": ranges,
                    "segment_count": segment_count,
                    "closed": False,
                    "outer_start": vertices[0],
                    "outer_end": vertices[-1],
                    "source_relative_status": "ALL_ACTUAL_REPLACEMENT_CORE_PIECES_BOUND_AND_PORT_GLUED",
                }
                encoded = (canonical(record) + "\n").encode()
                output.write(encoded)
                digest.update(encoded)
                records += 1
                segments += segment_count
                component_counts[stub["component"]] = component_counts.get(stub["component"], 0) + 1

    receipt = {
        "schema": "t73_x_m1_complete_global_r3_replacement_cores_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha256(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha256(Path(__file__)),
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "global_band_port_strips_receipt_sha256": bands["sha256"],
        "global_middle_transition_cores_receipt_sha256": transitions["sha256"],
        "middle_paths_r3_receipt_sha256": middles["sha256"],
        "record_count": records,
        "component_counts": dict(sorted(component_counts.items())),
        "core_segment_count": segments,
        "cross_piece_boundary_match_count": boundary_matches,
        "piece_count_per_record": 9,
        "complete_replacement_core_paths": True,
        "global_core_embedding_clearance_status": "OPEN_EXACT_ALL_SEGMENTS",
        "complete_push_paths_status": "OPEN",
        "completion_status": "ALL_POST_X_REPLACEMENT_CORES_ASSEMBLED_IN_ONE_R3_CHART",
        "verdict": "PASS_X_M1_COMPLETE_GLOBAL_R3_REPLACEMENT_CORE_ASSEMBLY",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(os.environ.get("T73_X_M1_COMPLETE_GLOBAL_R3_CORE_CACHE", DEFAULT_OUTPUT))
    receipt = build(output)
    print(json.dumps({
        "verdict": receipt["verdict"],
        "records": receipt["record_count"],
        "segments": receipt["core_segment_count"],
        "boundary_matches": receipt["cross_piece_boundary_match_count"],
        "global_clearance": receipt["global_core_embedding_clearance_status"],
        "bytes": receipt["cache_size"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
