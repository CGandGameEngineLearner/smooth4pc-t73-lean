#!/usr/bin/env python3
"""Merge the four x/m1 ejection streams into complete explicit 4D paths."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANES_RECEIPT = ROOT / "audit/t73_x_m1_ejected_band_lanes_receipt.json"
STUBS_RECEIPT = ROOT / "audit/t73_x_m1_ejected_splice_stubs_receipt.json"
MIDDLES_RECEIPT = ROOT / "audit/t73_x_m1_ejected_middle_complements_receipt.json"
TRANSITIONS_RECEIPT = ROOT / "audit/t73_x_m1_ejection_overlap_transitions_receipt.json"
TRANSITIONS_VERIFICATION = ROOT / "audit/t73_x_m1_ejection_overlap_transitions_verification.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_complete_explicit_replacement_images_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_m1_complete_explicit_replacement_images.jsonl.gz"


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest().upper()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def resolve_cache_path(value: str) -> Path:
    path = Path(value)
    if path.exists():
        return path
    if len(value) >= 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    if value.startswith("/mnt/") and os.name == "nt":
        drive = value[5].upper()
        return Path(f"{drive}:/{value[7:]}")
    return path


def iter_piece_records(value):
    if isinstance(value, dict):
        yield value
        return
    for item in value:
        yield from iter_piece_records(item)


def flatten_target_path(piece_images) -> list[list[str]]:
    vertices: list[list[str]] = []
    for piece in iter_piece_records(piece_images):
        start, end = piece["target_vertices"]
        if vertices and vertices[-1] != start:
            raise AssertionError("piecewise-affine segment images are discontinuous")
        if not vertices:
            vertices.append(start)
        vertices.append(end)
    if len(vertices) < 2:
        raise AssertionError("empty piecewise-affine path")
    return vertices


def append_path(vertices, values, label, ranges):
    if vertices and vertices[-1] != values[0]:
        raise AssertionError(f"replacement image discontinuity before {label}")
    start = len(vertices) - 1 if vertices else 0
    vertices.extend(values if not vertices else values[1:])
    ranges.append({
        "piece": label,
        "segment_range": [start, len(vertices) - 1],
        "segment_count": len(values) - 1,
    })


def assemble_path(lane, stub, middle, first_transition, last_transition, field):
    if field == "core":
        lane_key = "core_segment_images"
        stub_key = "core_segment_image"
        middle_key = "target_core_vertices"
        center_key = "center_core"
    else:
        lane_key = "outward_push_segment_images"
        stub_key = "outward_push_segment_image"
        middle_key = "target_push_vertices"
        center_key = "center_push"

    pieces = [
        ("source_stub_before", flatten_target_path(
            stub["stubs"]["source_stub_before"][stub_key]
        )),
        ("negative_band_lane", flatten_target_path(
            lane["lanes"]["negative_band_lane"][lane_key]
        )),
        ("target_complement_first", flatten_target_path(
            stub["stubs"]["target_complement_first"][stub_key]
        )),
        ("transition_first", [
            first_transition["local_cubical_boundary"][center_key],
            first_transition["global_annulus_boundary"][center_key],
        ]),
        ("oriented_m1_parallel_middle", middle[middle_key]),
        ("transition_last", [
            last_transition["global_annulus_boundary"][center_key],
            last_transition["local_cubical_boundary"][center_key],
        ]),
        ("target_complement_last", flatten_target_path(
            stub["stubs"]["target_complement_last"][stub_key]
        )),
        ("positive_band_lane", flatten_target_path(
            lane["lanes"]["positive_band_lane"][lane_key]
        )),
        ("source_stub_after", flatten_target_path(
            stub["stubs"]["source_stub_after"][stub_key]
        )),
    ]
    vertices = []
    ranges = []
    for label, values in pieces:
        append_path(vertices, values, label, ranges)
    if any(len(vertex) != 4 for vertex in vertices):
        raise AssertionError("replacement image is not represented in Q4")
    return vertices, ranges


def read_header(source, expected_schema):
    header = json.loads(source.readline())
    if header.get("record") != "header" or header.get("schema") != expected_schema:
        raise AssertionError(f"unexpected input stream header: {header}")
    return header


def build(output_path: Path) -> dict:
    receipts = {
        "lanes": json.loads(LANES_RECEIPT.read_text()),
        "stubs": json.loads(STUBS_RECEIPT.read_text()),
        "middles": json.loads(MIDDLES_RECEIPT.read_text()),
        "transitions": json.loads(TRANSITIONS_RECEIPT.read_text()),
    }
    transition_verification = json.loads(TRANSITIONS_VERIFICATION.read_text())
    input_paths = {
        name: resolve_cache_path(receipt["cache_path"])
        for name, receipt in receipts.items()
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)

    counts = Counter()
    core_segments = push_segments = boundary_matches = transition_tracks = 0
    stream_digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_complete_explicit_replacement_images/v1",
        "source_receipt_sha256s": {
            name: receipt["sha256"] for name, receipt in receipts.items()
        },
        "transition_verification_sha256": transition_verification["sha256"],
    }

    with (
        gzip.open(input_paths["lanes"], "rt", encoding="utf-8") as lane_source,
        gzip.open(input_paths["stubs"], "rt", encoding="utf-8") as stub_source,
        gzip.open(input_paths["middles"], "rt", encoding="utf-8") as middle_source,
        gzip.open(input_paths["transitions"], "rt", encoding="utf-8") as transition_source,
        output_path.open("wb") as raw_output,
    ):
        read_header(lane_source, "t73_x_m1_ejected_band_lanes/v1")
        read_header(stub_source, "t73_x_m1_ejected_splice_stubs/v1")
        read_header(middle_source, "t73_x_m1_ejected_middle_complements/v1")
        read_header(transition_source, "t73_x_m1_ejection_overlap_transitions/v1")
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            encoded = (canonical(header) + "\n").encode()
            output.write(encoded)
            stream_digest.update(encoded)
            for lane_line, stub_line, middle_line in zip(
                lane_source, stub_source, middle_source, strict=True
            ):
                lane = json.loads(lane_line)
                stub = json.loads(stub_line)
                middle = json.loads(middle_line)
                first_transition = json.loads(transition_source.readline())
                last_transition = json.loads(transition_source.readline())
                keys = {
                    (record["band_index"], record["component"])
                    for record in (lane, stub, middle, first_transition, last_transition)
                }
                if len(keys) != 1:
                    raise AssertionError(f"ejection stream order mismatch: {keys}")
                if (first_transition["side"], last_transition["side"]) != ("first", "last"):
                    raise AssertionError("transition pair order changed")

                core, core_ranges = assemble_path(
                    lane, stub, middle, first_transition, last_transition, "core"
                )
                push, push_ranges = assemble_path(
                    lane, stub, middle, first_transition, last_transition, "push"
                )
                if len(core_ranges) != 9 or len(push_ranges) != 9:
                    raise AssertionError("replacement piece inventory changed")
                boundary_matches += 16
                transition_tracks += 4
                core_segments += len(core) - 1
                push_segments += len(push) - 1
                counts[lane["component"]] += 1
                record = {
                    "record": "complete_explicit_replacement_image",
                    "band_index": lane["band_index"],
                    "component": lane["component"],
                    "ambient_coordinate_dimension": 4,
                    "core_vertices": core,
                    "push_vertices": push,
                    "core_piece_ranges": core_ranges,
                    "push_piece_ranges": push_ranges,
                    "core_segment_count": len(core) - 1,
                    "push_segment_count": len(push) - 1,
                    "transition_center_tracks": {
                        "core": [
                            core_ranges[3]["segment_range"],
                            core_ranges[5]["segment_range"],
                        ],
                        "push": [
                            push_ranges[3]["segment_range"],
                            push_ranges[5]["segment_range"],
                        ],
                    },
                    "source_relative_status": "BOUND_TO_VERIFIED_EJECTION_CELLS",
                }
                encoded = (canonical(record) + "\n").encode()
                output.write(encoded)
                stream_digest.update(encoded)
            if transition_source.readline():
                raise AssertionError("unused transition records remain")

    receipt = {
        "schema": "t73_x_m1_complete_explicit_replacement_images_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha256(output_path),
        "record_stream_sha256": stream_digest.hexdigest().upper(),
        "builder_sha256": file_sha256(Path(__file__)),
        "source_receipt_sha256s": {
            name: receipt["sha256"] for name, receipt in receipts.items()
        },
        "transition_verification_sha256": transition_verification["sha256"],
        "replacement_block_count": sum(counts.values()),
        "component_counts": dict(sorted(counts.items())),
        "explicit_core_segment_count": core_segments,
        "explicit_push_segment_count": push_segments,
        "transition_center_track_count": transition_tracks,
        "exact_piece_boundary_matches": boundary_matches,
        "ambient_coordinate_dimension": 4,
        "common_three_manifold_chart_status": "OPEN",
        "verdict": "PASS_COMPLETE_EXPLICIT_POST_X_REPLACEMENT_IMAGE_STREAM_4D_ATLAS",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(os.environ.get(
        "T73_X_M1_COMPLETE_EXPLICIT_CACHE", DEFAULT_OUTPUT
    ))
    receipt = build(output)
    print(json.dumps({
        "verdict": receipt["verdict"],
        "blocks": receipt["replacement_block_count"],
        "core_segments": receipt["explicit_core_segment_count"],
        "push_segments": receipt["explicit_push_segment_count"],
        "bytes": receipt["cache_size"],
        "common_3d_chart": receipt["common_three_manifold_chart_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
