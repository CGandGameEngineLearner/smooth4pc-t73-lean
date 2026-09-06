#!/usr/bin/env python3
"""Assemble complete R3 replacement cores with repaired v2 transitions."""

from __future__ import annotations

import argparse
import gzip
import json
import os
from fractions import Fraction
from pathlib import Path

from build_t73_x_m1_complete_global_r3_replacement_cores import (
    BANDS,
    MIDDLES,
    STUBS,
    append_path,
    canonical,
    canonical_sha256,
    file_sha256,
    read_records,
    stub_path,
    translated_middle,
)


ROOT = Path(__file__).resolve().parents[1]
REPAIRED_TRANSITIONS = ROOT / "audit/t73_x_m1_repaired_global_r3_middle_transition_cores_receipt.json"
REPAIRED_CLEARANCE = ROOT / "audit/t73_x_m1_repaired_stub_cross_clearance.json"
PRIOR_V1 = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_cores_receipt.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_cores_v2_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_m1_complete_global_r3_replacement_cores_v2.jsonl.gz"


def build(output_path):
    stubs = json.loads(STUBS.read_text())
    bands = json.loads(BANDS.read_text())
    middles = json.loads(MIDDLES.read_text())
    transitions = json.loads(REPAIRED_TRANSITIONS.read_text())
    clearance = json.loads(REPAIRED_CLEARANCE.read_text())
    prior = json.loads(PRIOR_V1.read_text())
    stub_records = read_records(stubs)
    band_records = read_records(bands)
    middle_records = read_records(middles)
    transition_records = read_records(transitions)
    if (len(stub_records), len(band_records), len(middle_records), len(transition_records)) != (1513, 1513, 1513, 3026):
        raise AssertionError("v2 complete replacement source inventory changed")
    translation = tuple(Fraction(value) for value in transitions["middle_chart_translation"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    import hashlib

    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_complete_global_r3_replacement_cores/v2",
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "global_band_port_strips_receipt_sha256": bands["sha256"],
        "repaired_middle_transition_cores_receipt_sha256": transitions["sha256"],
        "repaired_stub_cross_clearance_sha256": clearance["sha256"],
        "middle_paths_r3_receipt_sha256": middles["sha256"],
        "prior_v1_receipt_sha256": prior["sha256"],
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
                first = transition_records[2 * index]
                last = transition_records[2 * index + 1]
                if not (
                    stub["band_index"] == band["band_index"] == middle["band_index"] == index
                    and first["band_index"] == last["band_index"] == index
                    and first["side"] == "first"
                    and last["side"] == "last"
                ):
                    raise AssertionError("v2 complete replacement source order changed")
                pieces = (
                    ("source_stub_before", stub_path(stub, "source_stub_before")),
                    ("negative_band_lane", band["negative_lane_vertices"]),
                    ("target_complement_first", stub_path(stub, "target_complement_first")),
                    ("repaired_middle_transition_first", first["core_vertices"]),
                    ("translated_m1_parallel_middle", translated_middle(middle, translation)),
                    ("repaired_middle_transition_last", last["core_vertices"]),
                    ("target_complement_last", stub_path(stub, "target_complement_last")),
                    ("positive_band_lane", band["positive_lane_vertices_reverse_orientation"]),
                    ("source_stub_after", stub_path(stub, "source_stub_after")),
                )
                vertices = []
                ranges = []
                for label, path in pieces:
                    append_path(vertices, path, label, ranges)
                boundary_matches += 8
                segment_count = len(vertices) - 1
                record = {
                    "record": "complete_global_r3_replacement_core_v2",
                    "band_index": index,
                    "component": stub["component"],
                    "vertices": vertices,
                    "piece_ranges": ranges,
                    "segment_count": segment_count,
                    "outer_start": vertices[0],
                    "outer_end": vertices[-1],
                    "prior_v1_collision_repaired": True,
                    "source_relative_status": "ALL_ACTUAL_CORE_PIECES_PORT_GLUED_WITH_REPAIRED_TRANSITIONS",
                }
                encoded = (canonical(record) + "\n").encode()
                output.write(encoded)
                digest.update(encoded)
                records += 1
                segments += segment_count
                component_counts[stub["component"]] = component_counts.get(stub["component"], 0) + 1

    receipt = {
        "schema": "t73_x_m1_complete_global_r3_replacement_cores_receipt/v2",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha256(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha256(Path(__file__)),
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "global_band_port_strips_receipt_sha256": bands["sha256"],
        "repaired_middle_transition_cores_receipt_sha256": transitions["sha256"],
        "repaired_stub_cross_clearance_sha256": clearance["sha256"],
        "middle_paths_r3_receipt_sha256": middles["sha256"],
        "prior_v1_receipt_sha256": prior["sha256"],
        "record_count": records,
        "component_counts": dict(sorted(component_counts.items())),
        "core_segment_count": segments,
        "cross_piece_boundary_match_count": boundary_matches,
        "piece_count_per_record": 9,
        "old_exact_collision_repaired": True,
        "stub_band_cross_clearance": "PASS_EXACT",
        "stub_transition_cross_clearance": "PASS_EXACT_RUST",
        "remaining_core_clearance": [
            "repaired transitions versus band-strip non-shell segments",
            "repaired transitions versus translated middle cores",
            "stub inherited embeddedness transfer",
        ],
        "complete_push_paths_status": "OPEN",
        "completion_status": "ALL_POST_X_REPLACEMENT_CORES_REASSEMBLED_WITH_V2_TRANSITIONS",
        "verdict": "PASS_X_M1_COMPLETE_GLOBAL_R3_REPLACEMENT_CORE_V2_ASSEMBLY",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(os.environ.get("T73_X_M1_COMPLETE_GLOBAL_R3_CORE_V2_CACHE", DEFAULT_OUTPUT))
    result = build(output)
    print(json.dumps({
        "verdict": result["verdict"],
        "records": result["record_count"],
        "segments": result["core_segment_count"],
        "boundary_matches": result["cross_piece_boundary_match_count"],
        "old_collision_repaired": result["old_exact_collision_repaired"],
        "bytes": result["cache_size"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
