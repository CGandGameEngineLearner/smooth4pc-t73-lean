#!/usr/bin/env python3
"""Build R3 push paths and ruled ribbons for all mapped splice stubs."""

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
SOURCE_STUBS = ROOT / "audit/t73_x_m1_ejected_splice_stubs_receipt.json"
BAND_PUSH = ROOT / "audit/t73_x_band_global_r3_lane_push_paths_receipt.json"
BAND_CLEARANCE = ROOT / "audit/t73_x_band_global_r3_lane_push_clearance.json"
STUB_TRANSFER = ROOT / "audit/t73_x_m1_stub_r3_embeddedness_transfer.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_m1_stub_r3_push_paths.jsonl.gz"


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


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(values):
    return [str(value) for value in values]


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def path(stub):
    pieces = stub["pieces"]
    return [point(pieces[0]["r3_vertices"][0])] + [
        point(piece["r3_vertices"][1]) for piece in pieces
    ]


def ribbon_triangles(vertex_count):
    triangles = []
    for segment in range(vertex_count - 1):
        triangles.extend((
            [segment, segment + 1, vertex_count + segment + 1],
            [segment, vertex_count + segment + 1, vertex_count + segment],
        ))
    return triangles


def build(output_path):
    stubs = json.loads(STUBS.read_text())
    source_stubs = json.loads(SOURCE_STUBS.read_text())
    band_push = json.loads(BAND_PUSH.read_text())
    band_clearance = json.loads(BAND_CLEARANCE.read_text())
    stub_transfer = json.loads(STUB_TRANSFER.read_text())
    displacement = point(band_push["push_displacement"])
    stub_records = read_records(stubs)
    band_records = read_records(band_push)
    if len(stub_records) != 1513 or len(band_records) != 1513:
        raise AssertionError("stub/band push record inventory changed")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_stub_r3_push_paths/v1",
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "source_ejected_splice_stubs_receipt_sha256": source_stubs["sha256"],
        "band_lane_push_paths_receipt_sha256": band_push["sha256"],
        "band_lane_push_clearance_sha256": band_clearance["sha256"],
        "stub_r3_embeddedness_transfer_sha256": stub_transfer["sha256"],
        "push_displacement": [str(value) for value in displacement],
    }
    records = paths = core_segments = push_segments = ribbon_count = 0
    transversality = band_port_matches = 0
    with output_path.open("wb") as raw_output:
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            encoded = (canonical(header) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            for index, (stub_record, band_record) in enumerate(zip(stub_records, band_records)):
                output_stubs = {}
                for name, stub in stub_record["stubs"].items():
                    core = path(stub)
                    push = [add(value, displacement) for value in core]
                    triangles = ribbon_triangles(len(core))
                    for first, second in zip(core, core[1:]):
                        if cross(subtract(second, first), displacement) == (0, 0, 0):
                            raise AssertionError("stub push displacement becomes tangent")
                        transversality += 1
                    output_stubs[name] = {
                        "core_vertices": [encode(value) for value in core],
                        "push_vertices": [encode(value) for value in push],
                        "ribbon_triangles": triangles,
                        "segment_count": len(core) - 1,
                        "ribbon_triangle_count": len(triangles),
                        "source_normal_homotopy_status": "OPEN_BIND_SOURCE_NORMAL_TO_R3_DISPLACEMENT",
                    }
                    paths += 1
                    core_segments += len(core) - 1
                    push_segments += len(push) - 1
                    ribbon_count += len(triangles)
                band_lanes = {lane["lane"]: lane for lane in band_record["lanes"]}
                expected = (
                    (output_stubs["source_stub_before"]["push_vertices"][-1], band_lanes["negative"]["push_vertices"][0]),
                    (output_stubs["target_complement_first"]["push_vertices"][0], band_lanes["negative"]["push_vertices"][-1]),
                    (output_stubs["target_complement_last"]["push_vertices"][-1], band_lanes["positive"]["push_vertices"][0]),
                    (output_stubs["source_stub_after"]["push_vertices"][0], band_lanes["positive"]["push_vertices"][-1]),
                )
                if any(first != second for first, second in expected):
                    raise AssertionError("stub push misses a global band-lane push port")
                band_port_matches += len(expected)
                record = {
                    "record": "x_m1_stub_r3_push_paths",
                    "band_index": index,
                    "component": stub_record["component"],
                    "stubs": output_stubs,
                    "band_push_port_match_count": len(expected),
                    "global_stub_push_clearance_status": "OPEN",
                }
                encoded = (canonical(record) + "\n").encode()
                output.write(encoded)
                digest.update(encoded)
                records += 1
    receipt = {
        "schema": "t73_x_m1_stub_r3_push_paths_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha256(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha256(Path(__file__)),
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "source_ejected_splice_stubs_receipt_sha256": source_stubs["sha256"],
        "band_lane_push_paths_receipt_sha256": band_push["sha256"],
        "band_lane_push_clearance_sha256": band_clearance["sha256"],
        "stub_r3_embeddedness_transfer_sha256": stub_transfer["sha256"],
        "push_displacement": [str(value) for value in displacement],
        "record_count": records,
        "stub_push_path_count": paths,
        "core_segment_count": core_segments,
        "push_segment_count": push_segments,
        "ribbon_triangle_count": ribbon_count,
        "transversality_check_count": transversality,
        "band_push_port_match_count": band_port_matches,
        "source_normal_homotopy_status": "OPEN",
        "global_stub_push_clearance_status": "OPEN",
        "transition_push_port_status": "OPEN",
        "completion_status": "ALL_R3_STUB_PUSH_PATHS_AND_BAND_PORT_MATCHES_CONSTRUCTED",
        "verdict": "PASS_X_M1_STUB_R3_PUSH_PATHS_LOCAL",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(os.environ.get("T73_X_M1_STUB_PUSH_CACHE", DEFAULT_OUTPUT))
    result = build(output)
    print(json.dumps({
        "verdict": result["verdict"],
        "paths": result["stub_push_path_count"],
        "segments": result["push_segment_count"],
        "ribbons": result["ribbon_triangle_count"],
        "band_ports": result["band_push_port_match_count"],
        "source_homotopy": result["source_normal_homotopy_status"],
        "clearance": result["global_stub_push_clearance_status"],
        "bytes": result["cache_size"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
