#!/usr/bin/env python3
"""Independent full replay of local two-phase outer interface collars."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_receipt.json"
GAP = ROOT / "audit/t73_x_m1_complete_framed_outer_interface_gap.json"


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


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


def affine_zero(first, second):
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


def verify_full():
    data = json.loads(DATA.read_text())
    gap = json.loads(GAP.read_text())
    if data["outer_interface_gap_sha256"] != gap["sha256"]:
        raise AssertionError("outer collar receipt is stale relative to gap")
    cache_path = resolve(data["cache_path"])
    if (
        cache_path.stat().st_size != data["cache_size"]
        or file_sha(cache_path) != data["cache_sha256"]
    ):
        raise AssertionError("outer collar cache bytes changed")
    digest = hashlib.sha256()
    records = phase_one_checks = phase_two_checks = triangles = 0
    with gzip.open(cache_path, "rt", encoding="utf-8") as source:
        header_line = source.readline()
        digest.update(header_line.encode())
        header = json.loads(header_line)
        if header["outer_interface_gap_sha256"] != gap["sha256"]:
            raise AssertionError("outer collar cache header is stale")
        for interface, line in zip(gap["interfaces"], source, strict=True):
            digest.update(line.encode())
            record = json.loads(line)
            inner = point(interface["source_inner_core"])
            source_port = point(interface["source_core_port"])
            target = point(interface["target_core_port"])
            inner_push = point(interface["source_inner_push"])
            source_push = point(interface["source_push_port"])
            target_push = point(interface["target_push_port"])
            source_normal = subtract(source_push, source_port)
            target_normal = subtract(target_push, target)
            expected_fields = {
                "interface_index": interface["interface_index"],
                "band_index": interface["band_index"],
                "component": interface["component"],
                "side": interface["side"],
                "neighbor_kind": interface["neighbor_kind"],
                "neighbor_id": interface["neighbor_id"],
                "source_core_segment": [
                    interface["source_inner_core"],
                    interface["source_core_port"],
                ],
                "source_push_segment": [
                    interface["source_inner_push"],
                    interface["source_push_port"],
                ],
                "final_core_vertices": [
                    interface["source_inner_core"],
                    interface["target_core_port"],
                ],
                "final_push_vertices": [
                    interface["source_inner_push"],
                    interface["target_push_port"],
                ],
            }
            if any(record[key] != value for key, value in expected_fields.items()):
                raise AssertionError("outer collar source/target equation changed")
            if [point(value) for value in record["final_normal_field"]] != [
                source_normal,
                target_normal,
            ]:
                raise AssertionError("outer collar final normal field changed")
            if record["final_ribbon_triangles"] != [[0, 1, 3], [0, 3, 2]]:
                raise AssertionError("outer collar ribbon triangulation changed")
            constant_target_push = add(target, source_normal)
            if [
                point(value)
                for value in record["phase_one_core_isotopy_trace_triangle"]
            ] != [inner, source_port, target]:
                raise AssertionError("outer collar core trace changed")
            if [
                point(value)
                for value in record["phase_one_constant_push_trace_triangle"]
            ] != [inner_push, source_push, constant_target_push]:
                raise AssertionError("outer collar push trace changed")
            if [
                point(value) for value in record["phase_two_terminal_push_interval"]
            ] != [constant_target_push, target_push]:
                raise AssertionError("outer collar phase-two endpoint interval changed")
            initial_tangent, final_tangent = (
                subtract(source_port, inner),
                subtract(target, inner),
            )
            if affine_zero(initial_tangent, final_tangent):
                raise AssertionError("outer collar phase-one core collapses")
            if affine_zero(
                cross(initial_tangent, source_normal),
                cross(final_tangent, source_normal),
            ):
                raise AssertionError(
                    "outer collar phase-one normal loses transversality"
                )
            if affine_zero(
                cross(final_tangent, source_normal), cross(final_tangent, target_normal)
            ):
                raise AssertionError(
                    "outer collar phase-two normal loses transversality"
                )
            if (
                record["classification"] != "CANDIDATE_UNVERIFIED"
                or record["global_core_push_ribbon_clearance_status"] != "OPEN"
            ):
                raise AssertionError("outer collar local record overclaims completion")
            records += 1
            phase_one_checks += 2
            phase_two_checks += 1
            triangles += 2
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("outer collar decompressed stream changed")
    if (records, phase_one_checks, phase_two_checks, triangles) != (
        3026,
        6052,
        3026,
        6052,
    ):
        raise AssertionError("outer collar local totals changed")
    return {
        "verdict": "PASS_X_M1_FRAMED_OUTER_INTERFACE_COLLARS_FULL_LOCAL_CANDIDATE",
        "cache_sha_checked": True,
        "collars_reconstructed": records,
        "phase_one_exact_parameter_checks": phase_one_checks,
        "phase_two_exact_parameter_checks": phase_two_checks,
        "ribbon_triangles_reconstructed": triangles,
        "relative_twist_sum": 0,
        "classification": "CANDIDATE_UNVERIFIED",
        "global_clearance": "OPEN",
        "ambient_support": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
