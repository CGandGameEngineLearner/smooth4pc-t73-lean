#!/usr/bin/env python3
"""Independent full replay of source-germ outer collar candidates v2."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v2_receipt.json"
GAP = ROOT / "audit/t73_x_m1_complete_framed_outer_interface_gap.json"
OBSTRUCTION = ROOT / "audit/t73_x_m1_outer_collar_ribbon_self_clearance.json"
GERM_FRACTION = Fraction(1, 1_000_000)


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


def scale(factor, value):
    return tuple(factor * coordinate for coordinate in value)


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
    obstruction = json.loads(OBSTRUCTION.read_text())
    if (
        data["outer_interface_gap_sha256"] != gap["sha256"]
        or data["v1_ribbon_obstruction_sha256"] != obstruction["sha256"]
    ):
        raise AssertionError("v2 outer collar receipt source binding changed")
    cache_path = resolve(data["cache_path"])
    if (
        cache_path.stat().st_size != data["cache_size"]
        or file_sha(cache_path) != data["cache_sha256"]
    ):
        raise AssertionError("v2 outer collar cache bytes changed")
    digest = hashlib.sha256()
    records = segments = triangles = phase_one_checks = phase_two_checks = 0
    with gzip.open(cache_path, "rt", encoding="utf-8") as source:
        header_line = source.readline()
        digest.update(header_line.encode())
        header = json.loads(header_line)
        if header["schema"] != "t73_x_m1_framed_outer_interface_collars/v2" or header[
            "source_germ_fraction"
        ] != str(GERM_FRACTION):
            raise AssertionError("v2 outer collar cache header changed")
        for interface, line in zip(gap["interfaces"], source, strict=True):
            digest.update(line.encode())
            record = json.loads(line)
            inner = point(interface["source_inner_core"])
            source_port = point(interface["source_core_port"])
            target = point(interface["target_core_port"])
            source_normal = subtract(point(interface["source_push_port"]), source_port)
            target_normal = subtract(point(interface["target_push_port"]), target)
            germ = add(inner, scale(GERM_FRACTION, subtract(source_port, inner)))
            inner_push, germ_push = (
                add(inner, source_normal),
                add(germ, source_normal),
            )
            expected = {
                "interface_index": interface["interface_index"],
                "source_germ_fraction": str(GERM_FRACTION),
                "final_core_vertices": [
                    interface["source_inner_core"],
                    [str(value) for value in germ],
                    interface["target_core_port"],
                ],
                "final_push_vertices": [
                    [str(value) for value in inner_push],
                    [str(value) for value in germ_push],
                    interface["target_push_port"],
                ],
                "final_normal_field": [
                    [str(value) for value in source_normal],
                    [str(value) for value in source_normal],
                    [str(value) for value in target_normal],
                ],
                "final_ribbon_triangles": [[0, 1, 4], [0, 4, 3], [1, 2, 5], [1, 5, 4]],
            }
            if any(record[key] != value for key, value in expected.items()):
                raise AssertionError("v2 outer collar geometry changed")
            retained = subtract(germ, inner)
            initial, final = subtract(source_port, germ), subtract(target, germ)
            if cross(retained, source_normal) == (0, 0, 0) or affine_zero(
                initial, final
            ):
                raise AssertionError("v2 retained/moving core degenerates")
            if affine_zero(cross(initial, source_normal), cross(final, source_normal)):
                raise AssertionError("v2 phase-one normal loses transversality")
            if affine_zero(cross(final, source_normal), cross(final, target_normal)):
                raise AssertionError("v2 phase-two normal loses transversality")
            if (
                record["classification"] != "CANDIDATE_UNVERIFIED"
                or record["global_core_push_ribbon_clearance_status"] != "OPEN"
            ):
                raise AssertionError("v2 local cache overclaims clearance")
            records += 1
            segments += 2
            triangles += 4
            phase_one_checks += 3
            phase_two_checks += 1
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("v2 outer collar decompressed stream changed")
    if (records, segments, triangles, phase_one_checks, phase_two_checks) != (
        3026,
        6052,
        12104,
        9078,
        3026,
    ):
        raise AssertionError("v2 outer collar totals changed")
    return {
        "verdict": "PASS_X_M1_FRAMED_OUTER_INTERFACE_COLLARS_V2_FULL_LOCAL_CANDIDATE",
        "cache_sha_checked": True,
        "collars_reconstructed": records,
        "core_push_segments_each": segments,
        "ribbon_triangles_reconstructed": triangles,
        "phase_one_exact_parameter_checks": phase_one_checks,
        "phase_two_exact_parameter_checks": phase_two_checks,
        "relative_twist_sum": 0,
        "classification": "CANDIDATE_UNVERIFIED",
        "global_clearance": "OPEN",
        "ambient_support": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
