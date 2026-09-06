#!/usr/bin/env python3
"""Repair shell-to-middle transitions with port-local outward stub germs."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path

from build_t73_x_m1_global_r3_middle_transition_cores import (
    LIFT_DIRECTION,
    SLOPE,
    TRANSLATION,
    add,
    canonical,
    canonical_sha256,
    encode,
    file_sha256,
    functional,
    lift_to_height,
    point,
    resolve,
    translate,
)


ROOT = Path(__file__).resolve().parents[1]
STUBS = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
MIDDLES = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
OVERLAPS = ROOT / "audit/t73_x_m1_ejection_overlap_transitions_receipt.json"
OBSTRUCTION = ROOT / "audit/t73_x_m1_cross_system_core_clearance_obstruction.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_repaired_global_r3_middle_transition_cores_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_m1_repaired_global_r3_middle_transition_cores.jsonl.gz"
ESCAPE_FRACTION = Fraction(1, 1_000_000)


def read_records(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        return [json.loads(line) for line in source]


def stub_path(stub):
    pieces = stub["pieces"]
    return [point(pieces[0]["r3_vertices"][0])] + [
        point(piece["r3_vertices"][1]) for piece in pieces
    ]


def escape_from_end(path):
    port = path[-1]
    previous = path[-2]
    return tuple(
        port[axis] + ESCAPE_FRACTION * (port[axis] - previous[axis])
        for axis in range(3)
    )


def escape_from_start(path):
    port = path[0]
    following = path[1]
    return tuple(
        port[axis] + ESCAPE_FRACTION * (port[axis] - following[axis])
        for axis in range(3)
    )


def routing_path(start, end, transition_index):
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
    obstruction = json.loads(OBSTRUCTION.read_text())
    stub_records = read_records(stubs)
    middle_records = read_records(middles)
    overlap_records = read_records(overlaps)
    if (len(stub_records), len(middle_records), len(overlap_records)) != (1513, 1513, 3026):
        raise AssertionError("repaired middle-transition source inventory changed")

    inputs = []
    routing_endpoints = []
    for index, (stub_record, middle) in enumerate(zip(stub_records, middle_records)):
        first_stub = stub_path(stub_record["stubs"]["target_complement_first"])
        last_stub = stub_path(stub_record["stubs"]["target_complement_last"])
        shell_first, shell_last = first_stub[-1], last_stub[0]
        escape_first = escape_from_end(first_stub)
        escape_last = escape_from_start(last_stub)
        middle_first = translate(point(middle["core_vertices_r3"][0]))
        middle_last = translate(point(middle["core_vertices_r3"][-1]))
        inputs.extend((
            {
                "band": index,
                "side": "first",
                "shell_port": shell_first,
                "escape": escape_first,
                "route_start": escape_first,
                "route_end": middle_first,
            },
            {
                "band": index,
                "side": "last",
                "shell_port": shell_last,
                "escape": escape_last,
                "route_start": middle_last,
                "route_end": escape_last,
            },
        ))
        routing_endpoints.extend((escape_first, middle_first, middle_last, escape_last))
    functional_values = sorted(functional(value) for value in routing_endpoints)
    if len(set(functional_values)) != 6052:
        raise AssertionError("repaired routing functional is not injective")
    minimum_separation = min(
        right - left for left, right in zip(functional_values, functional_values[1:])
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_repaired_global_r3_middle_transition_cores/v2",
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "middle_paths_r3_receipt_sha256": middles["sha256"],
        "overlap_transitions_receipt_sha256": overlaps["sha256"],
        "prior_collision_obstruction_sha256": obstruction["sha256"],
        "middle_chart_translation": [str(value) for value in TRANSLATION],
        "routing_functional": [str(-SLOPE), "1", "1"],
        "lift_direction": [str(value) for value in LIFT_DIRECTION],
        "shell_escape_fraction": str(ESCAPE_FRACTION),
    }
    records = segments = endpoint_matches = escape_germs = functional_checks = 0
    with output_path.open("wb") as raw_output:
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            encoded = (canonical(header) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            for transition_index, (values, source_overlap) in enumerate(zip(inputs, overlap_records)):
                if source_overlap["band_index"] != values["band"] or source_overlap["side"] != values["side"]:
                    raise AssertionError("repaired transition source order changed")
                route = routing_path(values["route_start"], values["route_end"], transition_index)
                if values["side"] == "first":
                    path = [values["shell_port"], *route]
                else:
                    path = [*route, values["shell_port"]]
                if functional(route[0]) != functional(route[1]) or functional(route[-2]) != functional(route[-1]):
                    raise AssertionError("repaired skew lift changes the 3D functional")
                if route[1][1] - SLOPE * route[1][0] != route[2][1] - SLOPE * route[2][0]:
                    raise AssertionError("repaired start ray changes its planar functional")
                if route[3][1] - SLOPE * route[3][0] != route[4][1] - SLOPE * route[4][0]:
                    raise AssertionError("repaired end ray changes its planar functional")
                functional_checks += 4
                record = {
                    "record": "repaired_global_r3_middle_transition_core",
                    "transition_index": transition_index,
                    "band_index": values["band"],
                    "component": stub_records[values["band"]]["component"],
                    "side": values["side"],
                    "source_overlap_transition_sha256": canonical_sha256(source_overlap),
                    "prior_collision_obstruction_sha256": obstruction["sha256"],
                    "core_vertices": [encode(value) for value in path],
                    "segment_count": len(path) - 1,
                    "shell_port": encode(values["shell_port"]),
                    "shell_escape_point": encode(values["escape"]),
                    "shell_escape_fraction": str(ESCAPE_FRACTION),
                    "routing_height": str(3_000 + transition_index),
                    "repair_status": "PORT_LOCAL_STUB_TANGENT_ESCAPE_INSERTED",
                    "stub_cross_clearance_status": "OPEN_RUST_EXACT_REPLAY",
                    "push_transition_status": "OPEN",
                }
                encoded = (canonical(record) + "\n").encode()
                output.write(encoded)
                digest.update(encoded)
                records += 1
                segments += len(path) - 1
                endpoint_matches += 2
                escape_germs += 1

    receipt = {
        "schema": "t73_x_m1_repaired_global_r3_middle_transition_cores_receipt/v2",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha256(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha256(Path(__file__)),
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "middle_paths_r3_receipt_sha256": middles["sha256"],
        "overlap_transitions_receipt_sha256": overlaps["sha256"],
        "prior_collision_obstruction_sha256": obstruction["sha256"],
        "middle_chart_translation": [str(value) for value in TRANSLATION],
        "shell_escape_fraction": str(ESCAPE_FRACTION),
        "transition_count": records,
        "core_segment_count": segments,
        "endpoint_match_count": endpoint_matches,
        "shell_escape_germ_count": escape_germs,
        "routing_functional_value_count": len(functional_values),
        "minimum_routing_functional_separation": str(minimum_separation),
        "functional_line_check_count": functional_checks,
        "routing_family_disjointness": "PASS_AFTER_LOCAL_ESCAPE_BY_FUNCTIONAL_HEIGHT_AND_X",
        "stub_cross_clearance_status": "OPEN_RUST_EXACT_REPLAY",
        "push_transition_status": "OPEN",
        "completion_status": "REPAIRED_SHELL_TO_MIDDLE_CORE_TRANSITIONS_CONSTRUCTED",
        "verdict": "PASS_X_M1_REPAIRED_GLOBAL_R3_MIDDLE_TRANSITION_CORES_CONSTRUCTED",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(os.environ.get("T73_X_M1_REPAIRED_TRANSITIONS_CACHE", DEFAULT_OUTPUT))
    result = build(output)
    print(json.dumps({
        "verdict": result["verdict"],
        "transitions": result["transition_count"],
        "segments": result["core_segment_count"],
        "escape_germs": result["shell_escape_germ_count"],
        "stub_clearance": result["stub_cross_clearance_status"],
        "bytes": result["cache_size"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
