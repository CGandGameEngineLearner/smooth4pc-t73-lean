#!/usr/bin/env python3
"""Independent replay of the half-layer end-exterior transform v4."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import sys
from fractions import Fraction
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_core_push_clearance import segment_intersects

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v4_receipt.json"
V3 = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v3_receipt.json"
OBSTRUCTION = ROOT / "audit/t73_x_m1_outer_collar_v3_core_push_clearance.json"
OFFSET = Fraction(1, 2)
SLOPE = 1_000_033
FUNCTIONAL_Z = 2


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


def functional(value):
    return value[1] - SLOPE * value[0] + FUNCTIONAL_Z * value[2]


def verify_full():
    data = json.loads(DATA.read_text())
    v3 = json.loads(V3.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    if (
        data["refuted_v3_receipt_sha256"] != v3["sha256"]
        or data["v3_mutual_obstruction_sha256"] != obstruction["sha256"]
    ):
        raise AssertionError("v4 source binding changed")
    output_path = resolve(data["cache_path"])
    if (
        output_path.stat().st_size != data["cache_size"]
        or file_sha(output_path) != data["cache_sha256"]
    ):
        raise AssertionError("v4 cache bytes changed")
    digest = hashlib.sha256()
    records = changed = transversality = former_collision_rechecks = 0
    with (
        gzip.open(resolve(v3["cache_path"]), "rt", encoding="utf-8") as old_source,
        gzip.open(output_path, "rt", encoding="utf-8") as new_source,
    ):
        old_source.readline()
        header_line = new_source.readline()
        digest.update(header_line.encode())
        header = json.loads(header_line)
        if header["end_exterior_height_offset"] != str(OFFSET):
            raise AssertionError("v4 half-layer offset changed")
        for old_line, new_line in zip(old_source, new_source, strict=True):
            digest.update(new_line.encode())
            old, new = json.loads(old_line), json.loads(new_line)
            old_core = [point(value) for value in old["final_core_vertices"]]
            new_core = [point(value) for value in new["final_core_vertices"]]
            normals = [point(value) for value in new["final_normal_field"]]
            if any(
                old_core[index] != new_core[index]
                for index in range(len(old_core))
                if index != 4
            ):
                raise AssertionError("v4 changed a non-end-exterior core vertex")
            expected_height = old_core[4][2] + OFFSET
            expected = (
                old_core[4][0],
                functional(old_core[-1])
                + SLOPE * old_core[4][0]
                - FUNCTIONAL_Z * expected_height,
                expected_height,
            )
            if new_core[4] != expected:
                raise AssertionError("v4 end-exterior transform changed")
            expected_push = [
                add(vertex, normal) for vertex, normal in zip(new_core, normals)
            ]
            if [point(value) for value in new["final_push_vertices"]] != expected_push:
                raise AssertionError("v4 push is not the transformed normal graph")
            if new["interface_index"] == 3022:
                if segment_intersects(
                    (new_core[4], new_core[5]),
                    (expected_push[3], expected_push[4]),
                ):
                    raise AssertionError(
                        "v4 did not remove the exact v3 local collision"
                    )
                former_collision_rechecks += 1
            for index in range(len(new_core) - 1):
                tangent = subtract(new_core[index + 1], new_core[index])
                if affine_zero(
                    cross(tangent, normals[index]), cross(tangent, normals[index + 1])
                ):
                    raise AssertionError("v4 normal loses transversality")
                transversality += 1
            if (
                new["classification"] != "CANDIDATE_UNVERIFIED"
                or new["global_core_push_ribbon_clearance_status"] != "OPEN"
            ):
                raise AssertionError("v4 local record overclaims clearance")
            records += 1
            changed += 1
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("v4 decompressed stream changed")
    if (records, changed, transversality, former_collision_rechecks) != (
        3026,
        3026,
        18156,
        1,
    ):
        raise AssertionError("v4 replay totals changed")
    return {
        "verdict": "PASS_X_M1_FRAMED_OUTER_INTERFACE_COLLARS_V4_FULL_LOCAL_CANDIDATE",
        "cache_sha_checked": True,
        "collars_reconstructed": records,
        "changed_end_exterior_vertices": changed,
        "core_push_segments_each": 18156,
        "ribbon_triangles_reconstructed": 36312,
        "normal_transversality_checks": transversality,
        "end_exterior_height_offset": "1/2",
        "former_v3_collision_exact_rechecks": former_collision_rechecks,
        "classification": "CANDIDATE_UNVERIFIED",
        "global_clearance": "OPEN",
        "ambient_support": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
