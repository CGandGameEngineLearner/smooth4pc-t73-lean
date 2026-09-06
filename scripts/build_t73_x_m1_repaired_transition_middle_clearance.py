#!/usr/bin/env python3
"""Prove repaired transitions meet translated middle cores only at endpoints."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRANSITIONS = ROOT / "audit/t73_x_m1_repaired_global_r3_middle_transition_cores_receipt.json"
MIDDLES = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
MIDDLES_FULL = ROOT / "audit/t73_x_m1_middle_paths_r3_verification.json"
OUTPUT = ROOT / "audit/t73_x_m1_repaired_transition_middle_clearance.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


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


def build():
    transitions = json.loads(TRANSITIONS.read_text())
    middles = json.loads(MIDDLES.read_text())
    middles_full = json.loads(MIDDLES_FULL.read_text())
    transition_records = read_records(transitions)
    middle_records = read_records(middles)
    translation = tuple(Fraction(value) for value in transitions["middle_chart_translation"])
    endpoints = []
    middle_vertices = middle_segments = positive_transition_vertices = 0
    endpoint_matches = unique_zero_vertex_checks = 0
    for band, middle in enumerate(middle_records):
        core = [
            tuple(Fraction(value[axis]) + translation[axis] for axis in range(3))
            for value in middle["core_vertices_r3"]
        ]
        if any(vertex[2] != 0 for vertex in core):
            raise AssertionError("translated middle core left z=0")
        middle_vertices += len(core)
        middle_segments += len(core) - 1
        for side, transition, expected in (
            ("first", transition_records[2 * band], core[0]),
            ("last", transition_records[2 * band + 1], core[-1]),
        ):
            path = [point(value) for value in transition["core_vertices"]]
            endpoint = path[-1] if side == "first" else path[0]
            if endpoint != expected:
                raise AssertionError("repaired transition misses its translated middle endpoint")
            endpoint_matches += 1
            endpoints.append(endpoint)
            zero_indices = [index for index, vertex in enumerate(path) if vertex[2] == 0]
            expected_zero = [len(path) - 1] if side == "first" else [0]
            if zero_indices != expected_zero:
                raise AssertionError("repaired transition has a non-endpoint z=0 vertex")
            if any(vertex[2] <= 0 for index, vertex in enumerate(path) if index not in zero_indices):
                raise AssertionError("repaired transition does not leave the middle plane positively")
            positive_transition_vertices += len(path) - 1
            unique_zero_vertex_checks += 1
    if len(set(endpoints)) != 3026:
        raise AssertionError("middle-transition endpoints are not distinct")
    if not middles_full["full_result"]["pairwise_disjoint_middle_ribbons"]:
        raise AssertionError("middle pairwise-disjointness receipt is missing")
    result = {
        "schema": "t73_x_m1_repaired_transition_middle_clearance/v1",
        "repaired_middle_transition_cores_receipt_sha256": transitions["sha256"],
        "middle_paths_r3_receipt_sha256": middles["sha256"],
        "middle_paths_r3_full_verification_sha256": middles_full["sha256"],
        "middle_chart_translation": [str(value) for value in translation],
        "middle_core_count": len(middle_records),
        "middle_core_vertex_count": middle_vertices,
        "middle_core_segment_count": middle_segments,
        "middle_plane": "z=0",
        "transition_count": len(transition_records),
        "transition_middle_endpoint_match_count": endpoint_matches,
        "distinct_transition_middle_endpoints": len(set(endpoints)),
        "unique_zero_vertex_checks": unique_zero_vertex_checks,
        "positive_nonendpoint_transition_vertex_count": positive_transition_vertices,
        "separation_argument": (
            "all middle cores lie in z=0; each repaired transition has exactly "
            "its declared middle endpoint in z=0 and every other vertex in "
            "z>0, so its open segments miss every middle core"
        ),
        "extra_transition_middle_intersections": 0,
        "verdict": "PASS_X_M1_REPAIRED_TRANSITION_MIDDLE_CLEARANCE",
    }
    result["sha256"] = canonical_sha256(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("transition-middle clearance audit is stale")
    print(json.dumps({
        "verdict": result["verdict"],
        "middles": result["middle_core_count"],
        "transitions": result["transition_count"],
        "endpoint_matches": result["transition_middle_endpoint_match_count"],
        "extra": result["extra_transition_middle_intersections"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
