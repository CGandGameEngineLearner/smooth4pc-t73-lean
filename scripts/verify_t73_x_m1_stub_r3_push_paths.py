#!/usr/bin/env python3
"""Verify all stub R3 push paths, ribbons and band push-port matches."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
BANDS = ROOT / "audit/t73_x_band_global_r3_lane_push_paths_receipt.json"


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


def point(values):
    return tuple(Fraction(value) for value in values)


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def records(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        return [json.loads(line) for line in source]


def stub_core_path(stub):
    pieces = stub["pieces"]
    return [point(pieces[0]["r3_vertices"][0])] + [
        point(piece["r3_vertices"][1]) for piece in pieces
    ]


def expected_ribbons(vertex_count):
    result = []
    for segment in range(vertex_count - 1):
        result.extend((
            [segment, segment + 1, vertex_count + segment + 1],
            [segment, vertex_count + segment + 1, vertex_count + segment],
        ))
    return result


def verify(check_cache_sha=True):
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("stub push-path receipt SHA mismatch")
    stubs = json.loads(STUBS.read_text())
    bands = json.loads(BANDS.read_text())
    if data["splice_stub_cores_r3_receipt_sha256"] != stubs["sha256"]:
        raise AssertionError("stub push core binding changed")
    if data["band_lane_push_paths_receipt_sha256"] != bands["sha256"]:
        raise AssertionError("stub push band binding changed")
    cache = resolve(data["cache_path"])
    if not cache.is_file() or cache.stat().st_size != data["cache_size"]:
        raise AssertionError("stub push cache missing or resized")
    if check_cache_sha and file_sha256(cache) != data["cache_sha256"]:
        raise AssertionError("stub push cache SHA mismatch")
    stub_records = records(stubs)
    band_records = records(bands)
    output_records = []
    digest = hashlib.sha256()
    with gzip.open(cache, "rt", encoding="utf-8") as source:
        for line_number, line in enumerate(source):
            digest.update(line.encode())
            if line_number:
                output_records.append(json.loads(line))
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("stub push record-stream SHA mismatch")
    displacement = point(data["push_displacement"])
    path_count = segment_count = ribbon_count = transverse = port_matches = 0
    for index, (stub_record, band_record, output) in enumerate(
        zip(stub_records, band_records, output_records)
    ):
        for name, stub in stub_record["stubs"].items():
            core = stub_core_path(stub)
            push = [add(value, displacement) for value in core]
            saved = output["stubs"][name]
            if [point(value) for value in saved["core_vertices"]] != core:
                raise AssertionError("stub push saved core changed")
            if [point(value) for value in saved["push_vertices"]] != push:
                raise AssertionError("stub push saved companion changed")
            ribbons = expected_ribbons(len(core))
            if saved["ribbon_triangles"] != ribbons:
                raise AssertionError("stub push ribbon subdivision changed")
            for first, second in zip(core, core[1:]):
                if cross(subtract(second, first), displacement) == (0, 0, 0):
                    raise AssertionError("stub push displacement became tangent")
                transverse += 1
            path_count += 1
            segment_count += len(core) - 1
            ribbon_count += len(ribbons)
        band_lanes = {lane["lane"]: lane for lane in band_record["lanes"]}
        comparisons = (
            (output["stubs"]["source_stub_before"]["push_vertices"][-1], band_lanes["negative"]["push_vertices"][0]),
            (output["stubs"]["target_complement_first"]["push_vertices"][0], band_lanes["negative"]["push_vertices"][-1]),
            (output["stubs"]["target_complement_last"]["push_vertices"][-1], band_lanes["positive"]["push_vertices"][0]),
            (output["stubs"]["source_stub_after"]["push_vertices"][0], band_lanes["positive"]["push_vertices"][-1]),
        )
        if any(first != second for first, second in comparisons):
            raise AssertionError("stub push no longer meets its band push")
        port_matches += len(comparisons)
    if len(output_records) != 1513 or (path_count, segment_count, ribbon_count, transverse, port_matches) != (6052, 10582, 21164, 10582, 6052):
        raise AssertionError("stub push verification totals changed")
    if data["source_normal_homotopy_status"] != "OPEN" or data["global_stub_push_clearance_status"] != "OPEN":
        raise AssertionError("stub push construction was overstated")
    return {
        "verdict": "PASS_X_M1_STUB_R3_PUSH_PATHS_FULL_LOCAL",
        "stub_push_paths": path_count,
        "core_segments": segment_count,
        "push_segments": segment_count,
        "ribbon_triangles": ribbon_count,
        "transversality_checks": transverse,
        "band_push_port_matches": port_matches,
        "cache_sha_checked": check_cache_sha,
        "source_normal_homotopy": "OPEN",
        "global_stub_push_clearance": "OPEN",
        "transition_push_ports": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
