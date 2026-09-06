#!/usr/bin/env python3
"""Glue all shell stub cores to the translated middle R3 annulus chart."""

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
MIDDLES = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
OVERLAPS = ROOT / "audit/t73_x_m1_ejection_overlap_transitions_receipt.json"
OVERLAP_VERIFICATION = ROOT / "audit/t73_x_m1_ejection_overlap_transitions_verification.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_global_r3_middle_transition_cores_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_m1_global_r3_middle_transition_cores.jsonl.gz"
TRANSLATION = (Fraction(20_000), Fraction(2_000), Fraction(0))
SLOPE = 1_000_033
LIFT_DIRECTION = (Fraction(0), Fraction(-1), Fraction(1))


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


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def translate(value):
    return add(value, TRANSLATION)


def functional(value):
    return value[1] - SLOPE * value[0] + value[2]


def lift_to_height(value, height):
    parameter = height - value[2]
    return (
        value[0],
        value[1] - parameter,
        height,
    )


def route(start, end, transition_index):
    height = Fraction(3_000 + transition_index)
    exterior_x = Fraction(30_000 + 2 * transition_index)
    start_high = lift_to_height(start, height)
    end_high = lift_to_height(end, height)
    start_exterior = (
        exterior_x,
        start_high[1] + SLOPE * (exterior_x - start_high[0]),
        height,
    )
    end_exterior_x = exterior_x + 1
    end_exterior = (
        end_exterior_x,
        end_high[1] + SLOPE * (end_exterior_x - end_high[0]),
        height,
    )
    return [start, start_high, start_exterior, end_exterior, end_high, end]


def build(output_path):
    stubs = json.loads(STUBS.read_text())
    middles = json.loads(MIDDLES.read_text())
    overlaps = json.loads(OVERLAPS.read_text())
    overlap_verification = json.loads(OVERLAP_VERIFICATION.read_text())
    with gzip.open(resolve(stubs["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        stub_records = [json.loads(line) for line in source]
    with gzip.open(resolve(middles["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        middle_records = [json.loads(line) for line in source]
    with gzip.open(resolve(overlaps["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        overlap_records = [json.loads(line) for line in source]
    if (len(stub_records), len(middle_records), len(overlap_records)) != (1513, 1513, 3026):
        raise AssertionError("middle transition source inventory changed")

    endpoints = []
    transition_inputs = []
    for index, (stub, middle) in enumerate(zip(stub_records, middle_records)):
        if (stub["band_index"], middle["band_index"]) != (index, index):
            raise AssertionError("stub/middle record order changed")
        values = stub["stubs"]
        shell_first = point(values["target_complement_first"]["end_r3"])
        shell_last = point(values["target_complement_last"]["start_r3"])
        middle_first = translate(point(middle["core_vertices_r3"][0]))
        middle_last = translate(point(middle["core_vertices_r3"][-1]))
        inputs = ((shell_first, middle_first, "first"), (middle_last, shell_last, "last"))
        transition_inputs.extend(inputs)
        for start, end, _ in inputs:
            endpoints.extend((start, end))
    if len(set(endpoints)) != 6052:
        raise AssertionError("middle-transition endpoints are not distinct")
    functional_values = sorted(functional(value) for value in endpoints)
    if len(set(functional_values)) != 6052:
        raise AssertionError("3D routing functional is not injective")
    minimum_functional_separation = min(
        right - left for left, right in zip(functional_values, functional_values[1:])
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_global_r3_middle_transition_cores/v1",
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "middle_paths_r3_receipt_sha256": middles["sha256"],
        "overlap_transitions_receipt_sha256": overlaps["sha256"],
        "overlap_transitions_verification_sha256": overlap_verification["sha256"],
        "middle_chart_translation": [str(value) for value in TRANSLATION],
        "routing_functional": [str(-SLOPE), "1", "1"],
        "lift_direction": [str(value) for value in LIFT_DIRECTION],
    }
    records = segments = endpoint_matches = functional_line_checks = 0
    with output_path.open("wb") as raw_output:
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            encoded = (canonical(header) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            for transition_index, ((start, end, side), source_overlap) in enumerate(
                zip(transition_inputs, overlap_records)
            ):
                band_index = transition_index // 2
                if (
                    source_overlap["band_index"] != band_index
                    or source_overlap["side"] != side
                ):
                    raise AssertionError("source overlap transition order changed")
                path = route(start, end, transition_index)
                if functional(path[0]) != functional(path[1]):
                    raise AssertionError("start lift does not preserve routing functional")
                if functional(path[-2]) != functional(path[-1]):
                    raise AssertionError("end lift does not preserve routing functional")
                # In each routing-height plane, L-z reduces to y-Mx and is
                # constant along the two endpoint rays.
                if path[1][1] - SLOPE * path[1][0] != path[2][1] - SLOPE * path[2][0]:
                    raise AssertionError("start exterior ray changed its 2D functional")
                if path[3][1] - SLOPE * path[3][0] != path[4][1] - SLOPE * path[4][0]:
                    raise AssertionError("end exterior ray changed its 2D functional")
                functional_line_checks += 4
                record = {
                    "record": "global_r3_middle_transition_core",
                    "transition_index": transition_index,
                    "band_index": band_index,
                    "component": stub_records[band_index]["component"],
                    "side": side,
                    "source_overlap_transition_sha256": canonical_sha256(source_overlap),
                    "source_overlap_support_interval": source_overlap["support_level_interval"],
                    "core_vertices": [encode(value) for value in path],
                    "segment_count": len(path) - 1,
                    "routing_height": str(3_000 + transition_index),
                    "exterior_x_interval": [str(30_000 + 2 * transition_index), str(30_001 + 2 * transition_index)],
                    "endpoint_map_status": "EXACT_SHELL_TO_TRANSLATED_MIDDLE_PORTS",
                    "push_transition_status": "OPEN",
                }
                encoded = (canonical(record) + "\n").encode()
                output.write(encoded)
                digest.update(encoded)
                records += 1
                segments += len(path) - 1
                endpoint_matches += 2

    receipt = {
        "schema": "t73_x_m1_global_r3_middle_transition_cores_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha256(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha256(Path(__file__)),
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "middle_paths_r3_receipt_sha256": middles["sha256"],
        "overlap_transitions_receipt_sha256": overlaps["sha256"],
        "overlap_transitions_verification_sha256": overlap_verification["sha256"],
        "middle_chart_translation": [str(value) for value in TRANSLATION],
        "transition_count": records,
        "core_segment_count": segments,
        "endpoint_match_count": endpoint_matches,
        "routing_functional": [str(-SLOPE), "1", "1"],
        "routing_functional_value_count": len(functional_values),
        "minimum_routing_functional_separation": str(minimum_functional_separation),
        "lift_direction": [str(value) for value in LIFT_DIRECTION],
        "functional_line_check_count": functional_line_checks,
        "minimum_routing_height_separation": "1",
        "centerline_global_disjointness": "PASS_BY_3D_FUNCTIONAL_HEIGHT_AND_EXTERIOR_X",
        "cross_system_clearance_status": "OPEN_BAND_STRIPS_AND_MIDDLE_CURVES",
        "push_transition_status": "OPEN",
        "completion_status": "ALL_SHELL_TO_MIDDLE_CORE_TRANSITIONS_GLOBALLY_ROUTED_IN_R3",
        "verdict": "PASS_X_M1_GLOBAL_R3_MIDDLE_TRANSITION_CORES_CONSTRUCTED",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(os.environ.get("T73_X_M1_GLOBAL_MIDDLE_TRANSITIONS_CACHE", DEFAULT_OUTPUT))
    receipt = build(output)
    print(json.dumps({
        "verdict": receipt["verdict"],
        "transitions": receipt["transition_count"],
        "segments": receipt["core_segment_count"],
        "endpoints": receipt["endpoint_match_count"],
        "centerlines": receipt["centerline_global_disjointness"],
        "cross_system": receipt["cross_system_clearance_status"],
        "bytes": receipt["cache_size"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
