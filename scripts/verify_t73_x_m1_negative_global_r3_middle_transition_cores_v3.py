#!/usr/bin/env python3
"""Verify v3 negative-height routes against their repaired v2 endpoints."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_negative_global_r3_middle_transition_cores_v3_receipt.json"
V2 = ROOT / "audit/t73_x_m1_repaired_global_r3_middle_transition_cores_receipt.json"
SLOPE = 1_000_033


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


def point(values):
    return tuple(Fraction(value) for value in values)


def functional(value):
    return value[1] - SLOPE * value[0] + value[2]


def verify(check_cache_sha=True):
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("v3 negative-transition receipt SHA mismatch")
    v2 = json.loads(V2.read_text())
    if data["repaired_v2_transition_receipt_sha256"] != v2["sha256"]:
        raise AssertionError("v3 negative-transition v2 binding changed")
    cache = resolve(data["cache_path"])
    if not cache.is_file() or cache.stat().st_size != data["cache_size"]:
        raise AssertionError("v3 negative-transition cache missing or resized")
    if check_cache_sha and file_sha256(cache) != data["cache_sha256"]:
        raise AssertionError("v3 negative-transition cache SHA mismatch")
    old_records = records(v2)
    new_records = records(data)
    endpoints = []
    segments = functional_checks = 0
    for index, (old, new) in enumerate(zip(old_records, new_records)):
        old_vertices = [point(value) for value in old["core_vertices"]]
        vertices = [point(value) for value in new["core_vertices"]]
        side = old["side"]
        if len(vertices) != 7 or new["side"] != side or new["transition_index"] != index:
            raise AssertionError("v3 negative-transition identity changed")
        if side == "first":
            if vertices[0] != old_vertices[0] or vertices[1] != old_vertices[1] or vertices[-1] != old_vertices[-1]:
                raise AssertionError("v3 first endpoint/escape changed")
            route = vertices[1:]
        else:
            if vertices[0] != old_vertices[0] or vertices[-2] != old_vertices[-2] or vertices[-1] != old_vertices[-1]:
                raise AssertionError("v3 last endpoint/escape changed")
            route = vertices[:-1]
        height = Fraction(-3_000 - index)
        exterior_x = Fraction(30_000 + 2 * index)
        if not (
            route[1][2] == route[2][2] == route[3][2] == route[4][2] == height
            and route[2][0] == exterior_x
            and route[3][0] == exterior_x + 1
        ):
            raise AssertionError("v3 negative height/exterior route changed")
        if functional(route[0]) != functional(route[1]) or functional(route[-2]) != functional(route[-1]):
            raise AssertionError("v3 lift changes functional")
        if route[1][1] - SLOPE * route[1][0] != route[2][1] - SLOPE * route[2][0]:
            raise AssertionError("v3 first ray changes functional")
        if route[3][1] - SLOPE * route[3][0] != route[4][1] - SLOPE * route[4][0]:
            raise AssertionError("v3 last ray changes functional")
        endpoints.extend((route[0], route[-1]))
        functional_checks += 4
        segments += 6
    values = sorted(functional(value) for value in endpoints)
    if len(new_records) != 3026 or len(set(values)) != 6052:
        raise AssertionError("v3 functional inventory changed")
    if (segments, functional_checks) != (18156, 12104):
        raise AssertionError("v3 negative-transition totals changed")
    return {
        "verdict": "PASS_X_M1_NEGATIVE_GLOBAL_R3_MIDDLE_TRANSITION_CORES_V3_FULL",
        "transitions": len(new_records),
        "core_segments": segments,
        "routing_functional_values": len(values),
        "functional_checks": functional_checks,
        "cache_sha_checked": check_cache_sha,
        "band_cross_clearance": data["band_cross_clearance_status"],
        "push_transitions": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
