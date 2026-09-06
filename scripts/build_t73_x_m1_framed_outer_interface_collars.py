#!/usr/bin/env python3
"""Construct canonical straight two-phase collars for all outer interfaces."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAP = ROOT / "audit/t73_x_m1_complete_framed_outer_interface_gap.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_m1_framed_outer_interface_collars.jsonl.gz"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest().upper()


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def encode(value):
    return [str(coordinate) for coordinate in value]


def add(first, second):
    return tuple(a + b for a, b in zip(first, second))


def subtract(first, second):
    return tuple(a - b for a, b in zip(first, second))


def cross(first, second):
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def affine_vector_hits_zero(first, second):
    parameter = None
    for left, right in zip(first, second):
        if left == right:
            if left:
                return False
            continue
        candidate = -left / (right - left)
        if parameter is None:
            parameter = candidate
        elif parameter != candidate:
            return False
    return parameter is not None and 0 <= parameter <= 1


def build(output_path):
    gap = json.loads(GAP.read_text())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_framed_outer_interface_collars/v1",
        "outer_interface_gap_sha256": gap["sha256"],
        "construction_classification": "CANDIDATE_UNVERIFIED_UNTIL_GLOBAL_CLEARANCE_AND_AMBIENT_SUPPORT",
        "two_phase_rule": [
            "move source port to target port with constant source normal",
            "fix final core and linearly homotope terminal normal to target normal",
        ],
    }
    counts = Counter()
    with (
        output_path.open("wb") as raw,
        gzip.GzipFile(
            filename="", fileobj=raw, mode="wb", compresslevel=6, mtime=0
        ) as output,
    ):
        encoded = (canonical(header) + "\n").encode()
        output.write(encoded)
        digest.update(encoded)
        for interface in gap["interfaces"]:
            inner = point(interface["source_inner_core"])
            source = point(interface["source_core_port"])
            target = point(interface["target_core_port"])
            inner_push = point(interface["source_inner_push"])
            source_push = point(interface["source_push_port"])
            target_push = point(interface["target_push_port"])
            source_normal = subtract(source_push, source)
            target_normal = subtract(target_push, target)
            if subtract(inner_push, inner) != source_normal:
                raise AssertionError("source terminal segment normal is not constant")

            initial_tangent = subtract(source, inner)
            final_tangent = subtract(target, inner)
            if affine_vector_hits_zero(initial_tangent, final_tangent):
                raise AssertionError("phase-one core segment collapses")
            initial_cross = cross(initial_tangent, source_normal)
            final_source_cross = cross(final_tangent, source_normal)
            if affine_vector_hits_zero(initial_cross, final_source_cross):
                raise AssertionError("phase-one constant normal becomes tangent")
            final_target_cross = cross(final_tangent, target_normal)
            if affine_vector_hits_zero(final_source_cross, final_target_cross):
                raise AssertionError("phase-two endpoint normal becomes tangent")

            constant_target_push = add(target, source_normal)
            record = {
                "record": "framed_outer_interface_collar",
                "interface_index": interface["interface_index"],
                "band_index": interface["band_index"],
                "component": interface["component"],
                "side": interface["side"],
                "neighbor_kind": interface["neighbor_kind"],
                "neighbor_id": interface["neighbor_id"],
                "source_core_segment": [encode(inner), encode(source)],
                "source_push_segment": [encode(inner_push), encode(source_push)],
                "final_core_vertices": [encode(inner), encode(target)],
                "final_normal_field": [encode(source_normal), encode(target_normal)],
                "final_push_vertices": [encode(inner_push), encode(target_push)],
                "final_ribbon_triangles": [[0, 1, 3], [0, 3, 2]],
                "phase_one_core_isotopy_trace_triangle": [
                    encode(inner),
                    encode(source),
                    encode(target),
                ],
                "phase_one_constant_push_trace_triangle": [
                    encode(inner_push),
                    encode(source_push),
                    encode(constant_target_push),
                ],
                "phase_two_terminal_push_interval": [
                    encode(constant_target_push),
                    encode(target_push),
                ],
                "phase_one_core_noncollapse": True,
                "phase_one_normal_transversality": True,
                "phase_two_normal_transversality": True,
                "relative_twist": 0,
                "global_core_push_ribbon_clearance_status": "OPEN",
                "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_ISOTOPY_EXTENSION",
                "classification": "CANDIDATE_UNVERIFIED",
            }
            encoded = (canonical(record) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            counts["records"] += 1
            counts["core_trace_triangles"] += 1
            counts["push_trace_triangles"] += 1
            counts["ribbon_triangles"] += 2
            counts["phase_one_checks"] += 2
            counts["phase_two_checks"] += 1
            counts[f"kind/{interface['neighbor_kind']}"] += 1
    if counts["records"] != 3026:
        raise AssertionError("outer collar inventory changed")
    receipt = {
        "schema": "t73_x_m1_framed_outer_interface_collars_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha(Path(__file__)),
        "outer_interface_gap_sha256": gap["sha256"],
        "collar_count": counts["records"],
        "final_core_segment_count": counts["records"],
        "final_push_segment_count": counts["records"],
        "final_ribbon_triangle_count": counts["ribbon_triangles"],
        "phase_one_core_trace_triangle_count": counts["core_trace_triangles"],
        "phase_one_push_trace_triangle_count": counts["push_trace_triangles"],
        "phase_one_exact_parameter_checks": counts["phase_one_checks"],
        "phase_two_exact_parameter_checks": counts["phase_two_checks"],
        "neighbor_kind_counts": {
            key.removeprefix("kind/"): value
            for key, value in sorted(counts.items())
            if key.startswith("kind/")
        },
        "relative_twist_sum": 0,
        "classification": "CANDIDATE_UNVERIFIED",
        "global_clearance_status": "OPEN",
        "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_ISOTOPY_EXTENSION",
        "completion_status": "ALL_OUTER_INTERFACE_COLLAR_CANDIDATES_LOCALLY_CONSTRUCTED",
        "verdict": "PASS_X_M1_FRAMED_OUTER_INTERFACE_COLLARS_LOCAL_CANDIDATE",
    }
    receipt["sha256"] = canonical_sha(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build(
        args.output
        or Path(os.environ.get("T73_X_M1_OUTER_COLLAR_CACHE", DEFAULT_OUTPUT))
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "collars": result["collar_count"],
                "ribbon_triangles": result["final_ribbon_triangle_count"],
                "classification": result["classification"],
                "global_clearance": result["global_clearance_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
