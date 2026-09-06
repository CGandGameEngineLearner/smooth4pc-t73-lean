#!/usr/bin/env python3
"""Verify all repaired shell-escape and middle-transition R3 core paths."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_repaired_global_r3_middle_transition_cores_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
MIDDLES = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
OBSTRUCTION = ROOT / "audit/t73_x_m1_cross_system_core_clearance_obstruction.json"
SLOPE = 1_000_033
TRANSLATION = (Fraction(20_000), Fraction(2_000), Fraction(0))
ESCAPE = Fraction(1, 1_000_000)


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


def read_records(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        return [json.loads(line) for line in source]


def stub_path(record):
    pieces = record["pieces"]
    return [point(pieces[0]["r3_vertices"][0])] + [
        point(piece["r3_vertices"][1]) for piece in pieces
    ]


def functional(value):
    return value[1] - SLOPE * value[0] + value[2]


def verify(check_cache_sha=True):
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("repaired transition receipt SHA mismatch")
    stubs = json.loads(STUBS.read_text())
    middles = json.loads(MIDDLES.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    if data["splice_stub_cores_r3_receipt_sha256"] != stubs["sha256"]:
        raise AssertionError("repaired transition stub binding changed")
    if data["middle_paths_r3_receipt_sha256"] != middles["sha256"]:
        raise AssertionError("repaired transition middle binding changed")
    if data["prior_collision_obstruction_sha256"] != obstruction["sha256"]:
        raise AssertionError("repaired transition obstruction binding changed")
    cache = resolve(data["cache_path"])
    if not cache.is_file() or cache.stat().st_size != data["cache_size"]:
        raise AssertionError("repaired transition cache missing or resized")
    if check_cache_sha and file_sha256(cache) != data["cache_sha256"]:
        raise AssertionError("repaired transition cache SHA mismatch")
    stub_records = read_records(stubs)
    middle_records = read_records(middles)
    output_records = []
    digest = hashlib.sha256()
    with gzip.open(cache, "rt", encoding="utf-8") as source:
        for line_number, line in enumerate(source):
            digest.update(line.encode())
            if line_number:
                output_records.append(json.loads(line))
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("repaired transition stream SHA mismatch")
    endpoints = []
    escape_checks = functional_checks = segments = 0
    for transition_index, record in enumerate(output_records):
        band = transition_index // 2
        side = "first" if transition_index % 2 == 0 else "last"
        vertices = [point(value) for value in record["core_vertices"]]
        if len(vertices) != 7 or record["segment_count"] != 6:
            raise AssertionError("repaired transition subdivision changed")
        if side == "first":
            path = stub_path(stub_records[band]["stubs"]["target_complement_first"])
            shell, previous = path[-1], path[-2]
            expected_escape = tuple(shell[axis] + ESCAPE * (shell[axis] - previous[axis]) for axis in range(3))
            middle = tuple(point(middle_records[band]["core_vertices_r3"][0])[axis] + TRANSLATION[axis] for axis in range(3))
            if vertices[0] != shell or vertices[1] != expected_escape or vertices[-1] != middle:
                raise AssertionError("repaired first transition endpoint/germ changed")
            route = vertices[1:]
        else:
            path = stub_path(stub_records[band]["stubs"]["target_complement_last"])
            shell, following = path[0], path[1]
            expected_escape = tuple(shell[axis] + ESCAPE * (shell[axis] - following[axis]) for axis in range(3))
            middle = tuple(point(middle_records[band]["core_vertices_r3"][-1])[axis] + TRANSLATION[axis] for axis in range(3))
            if vertices[0] != middle or vertices[-2] != expected_escape or vertices[-1] != shell:
                raise AssertionError("repaired last transition endpoint/germ changed")
            route = vertices[:-1]
        if record["side"] != side or record["band_index"] != band:
            raise AssertionError("repaired transition identity changed")
        height = Fraction(3_000 + transition_index)
        exterior_x = Fraction(30_000 + 2 * transition_index)
        if not (
            route[1][2] == route[2][2] == route[3][2] == route[4][2] == height
            and route[2][0] == exterior_x
            and route[3][0] == exterior_x + 1
        ):
            raise AssertionError("repaired transition height/exterior route changed")
        if functional(route[0]) != functional(route[1]) or functional(route[-2]) != functional(route[-1]):
            raise AssertionError("repaired transition lift functional changed")
        if route[1][1] - SLOPE * route[1][0] != route[2][1] - SLOPE * route[2][0]:
            raise AssertionError("repaired transition first ray changed")
        if route[3][1] - SLOPE * route[3][0] != route[4][1] - SLOPE * route[4][0]:
            raise AssertionError("repaired transition last ray changed")
        endpoints.extend((route[0], route[-1]))
        escape_checks += 1
        functional_checks += 4
        segments += 6
    values = sorted(functional(value) for value in endpoints)
    if len(output_records) != 3026 or len(set(values)) != 6052:
        raise AssertionError("repaired transition functional inventory changed")
    minimum = min(right - left for left, right in zip(values, values[1:]))
    if minimum != Fraction(data["minimum_routing_functional_separation"]):
        raise AssertionError("repaired transition minimum functional separation changed")
    if (segments, escape_checks, functional_checks) != (18156, 3026, 12104):
        raise AssertionError("repaired transition totals changed")
    if data["stub_cross_clearance_status"] != "OPEN_RUST_EXACT_REPLAY":
        raise AssertionError("repaired transition clearance was overstated")
    return {
        "verdict": "PASS_X_M1_REPAIRED_GLOBAL_R3_MIDDLE_TRANSITION_CORES_FULL",
        "transitions": 3026,
        "core_segments": segments,
        "shell_escape_germs": escape_checks,
        "functional_checks": functional_checks,
        "cache_sha_checked": check_cache_sha,
        "stub_cross_clearance": "OPEN_RUST_EXACT_REPLAY",
        "push_transitions": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
