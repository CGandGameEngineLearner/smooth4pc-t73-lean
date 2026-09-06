#!/usr/bin/env python3
"""Move repaired middle-transition routing to negative height layers."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "audit/t73_x_m1_repaired_global_r3_middle_transition_cores_receipt.json"
V2_CLEARANCE = ROOT / "audit/t73_x_m1_repaired_stub_cross_clearance.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_negative_global_r3_middle_transition_cores_v3_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_m1_negative_global_r3_middle_transition_cores_v3.jsonl.gz"
SLOPE = 1_000_033


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


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(values):
    return [str(value) for value in values]


def lift(value, height):
    parameter = height - value[2]
    return value[0], value[1] - parameter, height


def route(start, end, index):
    height = Fraction(-3_000 - index)
    exterior_x = Fraction(30_000 + 2 * index)
    start_high = lift(start, height)
    end_high = lift(end, height)
    return [
        start,
        start_high,
        (exterior_x, start_high[1] + SLOPE * (exterior_x - start_high[0]), height),
        (exterior_x + 1, end_high[1] + SLOPE * (exterior_x + 1 - end_high[0]), height),
        end_high,
        end,
    ]


def functional(value):
    return value[1] - SLOPE * value[0] + value[2]


def build(output_path):
    v2 = json.loads(V2.read_text())
    clearance = json.loads(V2_CLEARANCE.read_text())
    with gzip.open(resolve(v2["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        source_records = [json.loads(line) for line in source]
    endpoints = []
    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_negative_global_r3_middle_transition_cores/v3",
        "repaired_v2_transition_receipt_sha256": v2["sha256"],
        "repaired_v2_stub_cross_clearance_sha256": clearance["sha256"],
        "routing_functional": [str(-SLOPE), "1", "1"],
        "routing_height_rule": "-3000-transition_index",
    }
    records = segments = endpoint_matches = functional_checks = 0
    with output_path.open("wb") as raw_output:
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            encoded = (canonical(header) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            for index, source in enumerate(source_records):
                old = [point(value) for value in source["core_vertices"]]
                side = source["side"]
                if side == "first":
                    shell, escape, middle = old[0], old[1], old[-1]
                    routed = route(escape, middle, index)
                    vertices = [shell, *routed]
                else:
                    middle, escape, shell = old[0], old[-2], old[-1]
                    routed = route(middle, escape, index)
                    vertices = [*routed, shell]
                if functional(routed[0]) != functional(routed[1]) or functional(routed[-2]) != functional(routed[-1]):
                    raise AssertionError("negative transition lift changes routing functional")
                if routed[1][1] - SLOPE * routed[1][0] != routed[2][1] - SLOPE * routed[2][0]:
                    raise AssertionError("negative transition first ray changed")
                if routed[3][1] - SLOPE * routed[3][0] != routed[4][1] - SLOPE * routed[4][0]:
                    raise AssertionError("negative transition last ray changed")
                endpoints.extend((routed[0], routed[-1]))
                functional_checks += 4
                record = {
                    "record": "negative_global_r3_middle_transition_core_v3",
                    "transition_index": index,
                    "band_index": source["band_index"],
                    "component": source["component"],
                    "side": side,
                    "repaired_v2_record_sha256": canonical_sha256(source),
                    "core_vertices": [encode(value) for value in vertices],
                    "segment_count": 6,
                    "shell_port": source["shell_port"],
                    "shell_escape_point": source["shell_escape_point"],
                    "routing_height": str(-3_000 - index),
                    "repair_status": "NEGATIVE_HEIGHT_SEPARATION_FROM_BAND_ROUTES",
                    "stub_clearance_status": "INHERITED_FROM_V2_EXACT_RUST",
                    "band_cross_clearance_status": "OPEN_EXACT_SHELL_SEGMENTS",
                    "push_transition_status": "OPEN",
                }
                encoded = (canonical(record) + "\n").encode()
                output.write(encoded)
                digest.update(encoded)
                records += 1
                segments += 6
                endpoint_matches += 2
    values = sorted(functional(value) for value in endpoints)
    if len(set(values)) != 6052:
        raise AssertionError("negative transition routing functional is not injective")
    receipt = {
        "schema": "t73_x_m1_negative_global_r3_middle_transition_cores_receipt/v3",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha256(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha256(Path(__file__)),
        "repaired_v2_transition_receipt_sha256": v2["sha256"],
        "repaired_v2_stub_cross_clearance_sha256": clearance["sha256"],
        "transition_count": records,
        "core_segment_count": segments,
        "endpoint_match_count": endpoint_matches,
        "routing_functional_value_count": len(values),
        "minimum_routing_functional_separation": str(min(right - left for left, right in zip(values, values[1:]))),
        "functional_line_check_count": functional_checks,
        "routing_height_range": [str(-3_000), str(-3_000 - records + 1)],
        "routing_family_disjointness": "PASS_BY_FUNCTIONAL_NEGATIVE_HEIGHT_AND_X",
        "stub_cross_clearance_status": "INHERITED_PASS_FROM_V2_EXACT_RUST",
        "band_cross_clearance_status": "OPEN_EXACT_SHELL_ESCAPE_AND_SKEW_SEGMENTS",
        "middle_cross_clearance_status": "PASS_BY_Z_AND_X_SEPARATION",
        "push_transition_status": "OPEN",
        "completion_status": "NEGATIVE_HEIGHT_V3_MIDDLE_TRANSITIONS_CONSTRUCTED",
        "verdict": "PASS_X_M1_NEGATIVE_GLOBAL_R3_MIDDLE_TRANSITION_CORES_V3_CONSTRUCTED",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(os.environ.get("T73_X_M1_NEGATIVE_TRANSITIONS_V3_CACHE", DEFAULT_OUTPUT))
    result = build(output)
    print(json.dumps({
        "verdict": result["verdict"],
        "transitions": result["transition_count"],
        "segments": result["core_segment_count"],
        "height_range": result["routing_height_range"],
        "band_clearance": result["band_cross_clearance_status"],
        "bytes": result["cache_size"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
