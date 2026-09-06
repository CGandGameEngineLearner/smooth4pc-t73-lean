#!/usr/bin/env python3
"""Glue v3 negative transition cores to stub and middle framing pushes."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRANSITIONS = ROOT / "audit/t73_x_m1_negative_global_r3_middle_transition_cores_v3_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
MIDDLES = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
CORE_EMBEDDING = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_core_embedding_v3.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_negative_transition_push_paths_v3_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_m1_negative_transition_push_paths_v3.jsonl.gz"
TRANSLATION = (Fraction(20_000), Fraction(2_000), Fraction(0))


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
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def records(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        return [json.loads(line) for line in source]


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(values):
    return [str(value) for value in values]


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
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


def ribbon_triangles(vertex_count):
    return [
        triangle
        for index in range(vertex_count - 1)
        for triangle in (
            [index, index + 1, vertex_count + index + 1],
            [index, vertex_count + index + 1, vertex_count + index],
        )
    ]


def build(output_path):
    transitions_receipt = json.loads(TRANSITIONS.read_text())
    stubs_receipt = json.loads(STUBS.read_text())
    middles_receipt = json.loads(MIDDLES.read_text())
    core_embedding = json.loads(CORE_EMBEDDING.read_text())
    transitions = records(transitions_receipt)
    stubs = records(stubs_receipt)
    middles = records(middles_receipt)
    if (len(transitions), len(stubs), len(middles)) != (3026, 1513, 1513):
        raise AssertionError("transition push input inventory changed")
    displacement = point(stubs_receipt["push_displacement"])
    if core_embedding["negative_v3_transition_receipt_sha256"] != transitions_receipt["sha256"]:
        raise AssertionError("core embedding does not bind v3 transitions")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_negative_transition_push_paths/v3",
        "negative_transition_receipt_sha256": transitions_receipt["sha256"],
        "stub_push_paths_receipt_sha256": stubs_receipt["sha256"],
        "middle_paths_r3_receipt_sha256": middles_receipt["sha256"],
        "complete_core_embedding_v3_sha256": core_embedding["sha256"],
        "middle_chart_translation": encode(TRANSLATION),
    }
    counts = {"records": 0, "segments": 0, "triangles": 0, "ports": 0, "homotopies": 0}
    with output_path.open("wb") as raw_output:
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            encoded = (canonical(header) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            for transition in transitions:
                band = transition["band_index"]
                side = transition["side"]
                core = [point(value) for value in transition["core_vertices"]]
                middle_core = [add(point(value), TRANSLATION) for value in middles[band]["core_vertices_r3"]]
                middle_push = [add(point(value), TRANSLATION) for value in middles[band]["push_vertices_r3"]]
                middle_index = 0 if side == "first" else -1
                middle_normal = subtract(middle_push[middle_index], middle_core[middle_index])
                normals = (
                    [displacement] * (len(core) - 1) + [middle_normal]
                    if side == "first"
                    else [middle_normal] + [displacement] * (len(core) - 1)
                )
                push = [add(vertex, normal) for vertex, normal in zip(core, normals)]
                stub_name = "target_complement_first" if side == "first" else "target_complement_last"
                stub = stubs[band]["stubs"][stub_name]
                stub_index = -1 if side == "first" else 0
                transition_stub_index = 0 if side == "first" else -1
                transition_middle_index = -1 if side == "first" else 0
                if core[transition_stub_index] != point(stub["core_vertices"][stub_index]):
                    raise AssertionError("transition core misses stub port")
                if push[transition_stub_index] != point(stub["push_vertices"][stub_index]):
                    raise AssertionError("transition push misses stub port")
                if core[transition_middle_index] != middle_core[middle_index]:
                    raise AssertionError("transition core misses middle port")
                if push[transition_middle_index] != middle_push[middle_index]:
                    raise AssertionError("transition push misses middle port")
                counts["ports"] += 2

                changing_segments = 0
                for index in range(len(core) - 1):
                    tangent = subtract(core[index + 1], core[index])
                    first_cross = cross(tangent, normals[index])
                    second_cross = cross(tangent, normals[index + 1])
                    if affine_vector_hits_zero(first_cross, second_cross):
                        raise AssertionError("transition normal homotopy becomes tangent")
                    if normals[index] != normals[index + 1]:
                        changing_segments += 1
                    if cross(tangent, subtract(push[index + 1], core[index])) == (0, 0, 0):
                        raise AssertionError("first transition ribbon triangle degenerates")
                    if cross(subtract(push[index + 1], core[index]), subtract(push[index], core[index])) == (0, 0, 0):
                        raise AssertionError("second transition ribbon triangle degenerates")
                if changing_segments != 1:
                    raise AssertionError("transition must contain one endpoint normal homotopy")
                triangles = ribbon_triangles(len(core))
                record = {
                    "record": "negative_transition_push_path_v3",
                    "transition_index": transition["transition_index"],
                    "band_index": band,
                    "component": transition["component"],
                    "side": side,
                    "core_vertices": [encode(value) for value in core],
                    "normal_field": [encode(value) for value in normals],
                    "push_vertices": [encode(value) for value in push],
                    "ribbon_triangles": triangles,
                    "segment_count": len(core) - 1,
                    "relative_twist": 0,
                    "stub_push_port_match": True,
                    "middle_push_port_match": True,
                    "global_ribbon_clearance_status": "OPEN",
                }
                encoded = (canonical(record) + "\n").encode()
                output.write(encoded)
                digest.update(encoded)
                counts["records"] += 1
                counts["segments"] += len(core) - 1
                counts["triangles"] += len(triangles)
                counts["homotopies"] += changing_segments

    receipt = {
        "schema": "t73_x_m1_negative_transition_push_paths_v3_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha256(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha256(Path(__file__)),
        "negative_transition_receipt_sha256": transitions_receipt["sha256"],
        "stub_push_paths_receipt_sha256": stubs_receipt["sha256"],
        "middle_paths_r3_receipt_sha256": middles_receipt["sha256"],
        "complete_core_embedding_v3_sha256": core_embedding["sha256"],
        "transition_count": counts["records"],
        "core_segment_count": counts["segments"],
        "push_segment_count": counts["segments"],
        "ribbon_triangle_count": counts["triangles"],
        "endpoint_push_port_match_count": counts["ports"],
        "linear_normal_homotopy_count": counts["homotopies"],
        "relative_twist_sum": 0,
        "local_transversality": True,
        "global_transition_ribbon_clearance_status": "OPEN",
        "completion_status": "ALL_V3_TRANSITION_PUSH_PATHS_AND_ENDPOINT_NORMAL_HOMOTOPIES_CONSTRUCTED",
        "verdict": "PASS_X_M1_NEGATIVE_TRANSITION_PUSH_PATHS_V3_LOCAL",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(os.environ.get("T73_X_M1_TRANSITION_PUSH_V3_CACHE", DEFAULT_OUTPUT))
    result = build(output)
    print(json.dumps({
        "verdict": result["verdict"],
        "transitions": result["transition_count"],
        "segments": result["push_segment_count"],
        "triangles": result["ribbon_triangle_count"],
        "port_matches": result["endpoint_push_port_match_count"],
        "global_clearance": result["global_transition_ribbon_clearance_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
