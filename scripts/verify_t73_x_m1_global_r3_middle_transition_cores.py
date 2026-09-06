#!/usr/bin/env python3
"""Verify every globally routed shell-to-middle R3 core transition."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_global_r3_middle_transition_cores_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
MIDDLES = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
OVERLAPS = ROOT / "audit/t73_x_m1_ejection_overlap_transitions_receipt.json"
SLOPE = 1_000_033
TRANSLATION = (Fraction(20_000), Fraction(2_000), Fraction(0))


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


def encode(values):
    return [str(value) for value in values]


def functional(value):
    return value[1] - SLOPE * value[0] + value[2]


def route(start, end, transition_index):
    height = Fraction(3_000 + transition_index)
    exterior_x = Fraction(30_000 + 2 * transition_index)
    start_parameter = height - start[2]
    end_parameter = height - end[2]
    start_high = (start[0], start[1] - start_parameter, height)
    end_high = (end[0], end[1] - end_parameter, height)
    return [
        start,
        start_high,
        (exterior_x, start_high[1] + SLOPE * (exterior_x - start_high[0]), height),
        (exterior_x + 1, end_high[1] + SLOPE * (exterior_x + 1 - end_high[0]), height),
        end_high,
        end,
    ]


def load_records(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        return [json.loads(line) for line in source]


def verify(check_cache_sha=True):
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("middle-transition receipt SHA mismatch")
    stubs = json.loads(STUBS.read_text())
    middles = json.loads(MIDDLES.read_text())
    overlaps = json.loads(OVERLAPS.read_text())
    bindings = {
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "middle_paths_r3_receipt_sha256": middles["sha256"],
        "overlap_transitions_receipt_sha256": overlaps["sha256"],
    }
    if any(data[key] != value for key, value in bindings.items()):
        raise AssertionError("middle-transition source binding changed")
    cache = resolve(data["cache_path"])
    if not cache.is_file() or cache.stat().st_size != data["cache_size"]:
        raise AssertionError("middle-transition cache missing or resized")
    if check_cache_sha and file_sha256(cache) != data["cache_sha256"]:
        raise AssertionError("middle-transition cache SHA mismatch")
    stub_records = load_records(stubs)
    middle_records = load_records(middles)
    overlap_records = load_records(overlaps)
    output_records = []
    digest = hashlib.sha256()
    with gzip.open(cache, "rt", encoding="utf-8") as source:
        for line_number, line in enumerate(source):
            digest.update(line.encode())
            record = json.loads(line)
            if line_number:
                output_records.append(record)
            elif record["routing_functional"] != [str(-SLOPE), "1", "1"]:
                raise AssertionError("middle-transition routing functional changed")
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("middle-transition record stream SHA mismatch")
    if (len(stub_records), len(middle_records), len(overlap_records), len(output_records)) != (1513, 1513, 3026, 3026):
        raise AssertionError("middle-transition record inventory changed")

    endpoints = []
    segment_count = endpoint_matches = line_checks = 0
    for transition_index, record in enumerate(output_records):
        band_index = transition_index // 2
        side = "first" if transition_index % 2 == 0 else "last"
        stub = stub_records[band_index]["stubs"]
        middle = middle_records[band_index]
        if side == "first":
            start = point(stub["target_complement_first"]["end_r3"])
            end = add(point(middle["core_vertices_r3"][0]), TRANSLATION)
        else:
            start = add(point(middle["core_vertices_r3"][-1]), TRANSLATION)
            end = point(stub["target_complement_last"]["start_r3"])
        expected = route(start, end, transition_index)
        if record["core_vertices"] != [encode(value) for value in expected]:
            raise AssertionError(f"middle-transition route {transition_index} changed")
        overlap = overlap_records[transition_index]
        if overlap["band_index"] != band_index or overlap["side"] != side:
            raise AssertionError("middle-transition overlap provenance changed")
        if record["source_overlap_transition_sha256"] != canonical_sha256(overlap):
            raise AssertionError("middle-transition source overlap SHA changed")
        if functional(expected[0]) != functional(expected[1]) or functional(expected[-2]) != functional(expected[-1]):
            raise AssertionError("middle-transition lift changes the 3D functional")
        if expected[1][1] - SLOPE * expected[1][0] != expected[2][1] - SLOPE * expected[2][0]:
            raise AssertionError("middle-transition start ray changes functional")
        if expected[3][1] - SLOPE * expected[3][0] != expected[4][1] - SLOPE * expected[4][0]:
            raise AssertionError("middle-transition end ray changes functional")
        endpoints.extend((start, end))
        segment_count += 5
        endpoint_matches += 2
        line_checks += 4
    values = sorted(functional(endpoint) for endpoint in endpoints)
    if len(set(endpoints)) != 6052 or len(set(values)) != 6052:
        raise AssertionError("middle-transition endpoint functional is not injective")
    minimum = min(right - left for left, right in zip(values, values[1:]))
    if minimum != Fraction(data["minimum_routing_functional_separation"]):
        raise AssertionError("middle-transition functional separation changed")
    if (segment_count, endpoint_matches, line_checks) != (15130, 6052, 12104):
        raise AssertionError("middle-transition replay totals changed")
    if data["cross_system_clearance_status"] != "OPEN_BAND_STRIPS_AND_MIDDLE_CURVES":
        raise AssertionError("middle-transition cross-system clearance was overstated")
    return {
        "verdict": "PASS_X_M1_GLOBAL_R3_MIDDLE_TRANSITION_CORES_FULL",
        "transitions": 3026,
        "core_segments": segment_count,
        "endpoint_matches": endpoint_matches,
        "functional_line_checks": line_checks,
        "routing_functional_values": len(values),
        "centerlines_globally_disjoint": True,
        "cache_sha_checked": check_cache_sha,
        "cross_system_clearance": "OPEN",
        "push_transitions": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
