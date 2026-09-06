#!/usr/bin/env python3
"""Independent full verifier for v3 negative-transition push paths."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_negative_transition_push_paths_v3_receipt.json"
TRANSITIONS = ROOT / "audit/t73_x_m1_negative_global_r3_middle_transition_cores_v3_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
MIDDLES = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
TRANSLATION = (Fraction(20_000), Fraction(2_000), Fraction(0))


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


def records(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        return [json.loads(line) for line in source]


def point(value):
    return tuple(Fraction(item) for item in value)


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
    candidate = None
    for left, right in zip(first, second):
        if left == right:
            if left != 0:
                return False
            continue
        value = -left / (right - left)
        if candidate is None:
            candidate = value
        elif candidate != value:
            return False
    return candidate is not None and 0 <= candidate <= 1


def expected_triangles(vertex_count):
    answer = []
    for index in range(vertex_count - 1):
        answer.extend((
            [index, index + 1, vertex_count + index + 1],
            [index, vertex_count + index + 1, vertex_count + index],
        ))
    return answer


def verify_full():
    data = json.loads(DATA.read_text())
    transition_receipt = json.loads(TRANSITIONS.read_text())
    stub_receipt = json.loads(STUBS.read_text())
    middle_receipt = json.loads(MIDDLES.read_text())
    if data["negative_transition_receipt_sha256"] != transition_receipt["sha256"]:
        raise AssertionError("transition push receipt is stale")
    if data["stub_push_paths_receipt_sha256"] != stub_receipt["sha256"]:
        raise AssertionError("transition push receipt misses stub source")
    if data["middle_paths_r3_receipt_sha256"] != middle_receipt["sha256"]:
        raise AssertionError("transition push receipt misses middle source")
    path = resolve(data["cache_path"])
    if file_sha(path) != data["cache_sha256"] or path.stat().st_size != data["cache_size"]:
        raise AssertionError("transition push cache bytes changed")
    transitions = records(transition_receipt)
    stubs = records(stub_receipt)
    middles = records(middle_receipt)
    displacement = point(stub_receipt["push_displacement"])
    digest = hashlib.sha256()
    counts = {"records": 0, "segments": 0, "triangles": 0, "ports": 0, "homotopies": 0}
    with gzip.open(path, "rt", encoding="utf-8") as source:
        header_line = source.readline()
        digest.update(header_line.encode())
        header = json.loads(header_line)
        if header["schema"] != "t73_x_m1_negative_transition_push_paths/v3":
            raise AssertionError("transition push cache schema changed")
        for expected_index, line in enumerate(source):
            digest.update(line.encode())
            record = json.loads(line)
            transition = transitions[expected_index]
            if record["transition_index"] != expected_index or record["band_index"] != transition["band_index"]:
                raise AssertionError("transition push record order changed")
            core = [point(value) for value in record["core_vertices"]]
            normals = [point(value) for value in record["normal_field"]]
            push = [point(value) for value in record["push_vertices"]]
            if core != [point(value) for value in transition["core_vertices"]]:
                raise AssertionError("transition push core changed")
            if push != [add(vertex, normal) for vertex, normal in zip(core, normals)]:
                raise AssertionError("transition push is not its normal graph")
            if record["ribbon_triangles"] != expected_triangles(len(core)):
                raise AssertionError("transition ribbon triangulation changed")
            side = record["side"]
            band = record["band_index"]
            middle_index = 0 if side == "first" else -1
            middle_core = add(point(middles[band]["core_vertices_r3"][middle_index]), TRANSLATION)
            middle_push = add(point(middles[band]["push_vertices_r3"][middle_index]), TRANSLATION)
            stub_name = "target_complement_first" if side == "first" else "target_complement_last"
            stub_index = -1 if side == "first" else 0
            transition_stub_index = 0 if side == "first" else -1
            transition_middle_index = -1 if side == "first" else 0
            stub = stubs[band]["stubs"][stub_name]
            if (core[transition_stub_index], push[transition_stub_index]) != (
                point(stub["core_vertices"][stub_index]), point(stub["push_vertices"][stub_index])
            ):
                raise AssertionError("transition misses stub core/push port")
            if (core[transition_middle_index], push[transition_middle_index]) != (middle_core, middle_push):
                raise AssertionError("transition misses middle core/push port")
            counts["ports"] += 2
            changes = 0
            for index in range(len(core) - 1):
                tangent = subtract(core[index + 1], core[index])
                if affine_zero(cross(tangent, normals[index]), cross(tangent, normals[index + 1])):
                    raise AssertionError("transition normal loses transversality")
                if cross(tangent, subtract(push[index + 1], core[index])) == (0, 0, 0):
                    raise AssertionError("first transition ribbon triangle degenerates")
                if cross(
                    subtract(push[index + 1], core[index]),
                    subtract(push[index], core[index]),
                ) == (0, 0, 0):
                    raise AssertionError("second transition ribbon triangle degenerates")
                changes += normals[index] != normals[index + 1]
            if changes != 1 or record["relative_twist"] != 0:
                raise AssertionError("transition normal homotopy/twist changed")
            if not record["stub_push_port_match"] or not record["middle_push_port_match"]:
                raise AssertionError("transition push port status changed")
            if record["global_ribbon_clearance_status"] != "OPEN":
                raise AssertionError("local artifact overclaims global clearance")
            if side == "first" and normals[:-1] != [displacement] * (len(normals) - 1):
                raise AssertionError("first transition stub normal collar changed")
            if side == "last" and normals[1:] != [displacement] * (len(normals) - 1):
                raise AssertionError("last transition stub normal collar changed")
            counts["records"] += 1
            counts["segments"] += len(core) - 1
            counts["triangles"] += len(record["ribbon_triangles"])
            counts["homotopies"] += changes
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("transition push decompressed stream changed")
    expected = {"records": 3026, "segments": 18156, "triangles": 36312, "ports": 6052, "homotopies": 3026}
    if counts != expected:
        raise AssertionError(f"transition push totals changed: {counts}")
    return {
        "verdict": "PASS_X_M1_NEGATIVE_TRANSITION_PUSH_PATHS_V3_FULL_LOCAL",
        "cache_sha_checked": True,
        "transitions": counts["records"],
        "core_push_segments_each": counts["segments"],
        "ribbon_triangles": counts["triangles"],
        "endpoint_push_port_matches": counts["ports"],
        "linear_normal_homotopies": counts["homotopies"],
        "relative_twist_sum": 0,
        "global_clearance": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
