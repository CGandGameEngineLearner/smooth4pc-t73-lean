#!/usr/bin/env python3
"""Aggregate exact transition-ribbon clearance against every x-m1 subsystem."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from verify_t73_x_m1_transition_transition_ribbon_clearance_gmp import (
    point,
    segment_triangle,
    subtract,
)


ROOT = Path(__file__).resolve().parents[1]
PUSH = ROOT / "audit/t73_x_m1_negative_transition_push_paths_v3_receipt.json"
TT = ROOT / "audit/t73_x_m1_transition_transition_ribbon_clearance_verification.json"
TS = ROOT / "audit/t73_x_m1_transition_stub_ribbon_clearance_verification.json"
BAND = ROOT / "audit/t73_x_m1_transition_ribbon_band_candidates.json"
MIDDLE_CANDIDATES = ROOT / "audit/t73_x_m1_transition_ribbon_middle_candidates.json"
MIDDLE_RECEIPT = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
MIDDLE_VERIFY = ROOT / "audit/t73_x_m1_middle_paths_r3_verification.json"
OUTPUT = ROOT / "audit/t73_x_m1_transition_ribbon_global_clearance.json"
TRANSLATION = (point(["20000", "2000", "0"]))


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def cache_records(receipt):
    path = resolve(receipt["cache_path"])
    with gzip.open(path, "rt", encoding="utf-8") as source:
        source.readline()
        return [json.loads(line) for line in source]


def is_variable_transition_triangle(index):
    record, local = divmod(index, 12)
    return local >= 10 if record % 2 == 0 else local < 2


def add(first, second):
    return tuple(a + b for a, b in zip(first, second))


def build():
    push = json.loads(PUSH.read_text())
    tt = json.loads(TT.read_text())
    ts = json.loads(TS.read_text())
    band = json.loads(BAND.read_text())
    middle_candidates = json.loads(MIDDLE_CANDIDATES.read_text())
    middle_receipt = json.loads(MIDDLE_RECEIPT.read_text())
    middle_verify = json.loads(MIDDLE_VERIFY.read_text())
    if tt["full_result"]["intersections"] or ts["full_result"]["intersections"]:
        raise AssertionError("prior transition ribbon exact clearance failed")
    if band["broad_candidates"] != 0 or band["exact_triangle_checks"] != 0:
        raise AssertionError("transition/band expanded 3D bounds are not disjoint")
    if file_sha(resolve(band["candidate_path"])) != band["candidate_sha256"]:
        raise AssertionError("transition/band candidate stream changed")
    if not middle_verify["full_result"]["pairwise_disjoint_middle_ribbons"]:
        raise AssertionError("middle ribbon global embedding is not verified")

    variable_candidates = 0
    middle_candidate_path = resolve(middle_candidates["candidate_path"])
    if file_sha(middle_candidate_path) != middle_candidates["candidate_sha256"]:
        raise AssertionError("transition/middle candidate stream changed")
    with gzip.open(middle_candidate_path, "rt", encoding="utf-8") as source:
        if json.loads(source.readline()) != {"comparison": "middle", "record": "header"}:
            raise AssertionError("transition/middle candidate schema changed")
        for line in source:
            transition_index = int(line.split(",", 1)[0])
            if not is_variable_transition_triangle(transition_index):
                raise AssertionError("a constant transition ribbon reaches z=0 middle ribbons")
            variable_candidates += 1
    if variable_candidates != 10_220_750:
        raise AssertionError("transition/middle candidate count changed")

    transitions = cache_records(push)
    middles = cache_records(middle_receipt)
    port_triangle_checks = port_triangle_incidences = z_pattern_checks = 0
    for transition in transitions:
        band_index = transition["band_index"]
        side = transition["side"]
        core = [point(value) for value in transition["core_vertices"]]
        pushed = [point(value) for value in transition["push_vertices"]]
        size = len(core)
        segment = 5 if side == "first" else 0
        vertices = core + pushed
        triangles = [tuple(vertices[index] for index in ids) for ids in transition["ribbon_triangles"][2 * segment:2 * segment + 2]]
        zero_counts = sorted(sum(vertex[2] == 0 for vertex in triangle) for triangle in triangles)
        nonzero_values = [vertex[2] for triangle in triangles for vertex in triangle if vertex[2] != 0]
        if zero_counts != [1, 2] or not nonzero_values or not all(value < 0 for value in nonzero_values):
            raise AssertionError("transition variable ribbon does not meet z=0 only at its port")
        z_pattern_checks += 2

        middle = middles[band_index]
        middle_core = [add(point(value), TRANSLATION) for value in middle["core_vertices_r3"]]
        middle_push = [add(point(value), TRANSLATION) for value in middle["push_vertices_r3"]]
        endpoint = 0 if side == "first" else -1
        port = (middle_core[endpoint], middle_push[endpoint])
        transition_endpoint = -1 if side == "first" else 0
        if port != (core[transition_endpoint], pushed[transition_endpoint]):
            raise AssertionError("transition/middle framing port changed")
        middle_vertices = middle_core + middle_push
        middle_size = len(middle_core)
        hits = []
        for middle_segment in range(middle_size - 1):
            ids = (
                (middle_segment, middle_segment + 1, middle_size + middle_segment + 1),
                (middle_segment, middle_size + middle_segment + 1, middle_size + middle_segment),
            )
            for local_half, triangle_ids in enumerate(ids):
                triangle = tuple(middle_vertices[index] for index in triangle_ids)
                port_triangle_checks += 1
                if segment_triangle(port, triangle):
                    hits.append(2 * middle_segment + local_half)
        expected_hits = [0, 1] if side == "first" else [62, 63]
        if hits != expected_hits:
            raise AssertionError(f"middle port has unexpected triangle incidences: {band_index}/{side}/{hits}")
        port_triangle_incidences += len(hits)

    result = {
        "schema": "t73_x_m1_transition_ribbon_global_clearance/v1",
        "transition_push_receipt_sha256": push["sha256"],
        "transition_transition_verification_sha256": tt["sha256"],
        "transition_stub_verification_sha256": ts["sha256"],
        "transition_band_candidate_audit_content_sha256": hashlib.sha256(BAND.read_bytes()).hexdigest().upper(),
        "middle_paths_verification_sha256": middle_verify["sha256"],
        "transition_middle_candidate_audit_content_sha256": hashlib.sha256(MIDDLE_CANDIDATES.read_bytes()).hexdigest().upper(),
        "transition_triangle_count": push["ribbon_triangle_count"],
        "transition_transition_constant_rectangle_checks": tt["full_result"]["constant_rectangle_checks"],
        "transition_transition_variable_triangle_checks": tt["full_result"]["variable_triangle_checks"],
        "transition_stub_rectangle_checks": ts["full_result"]["exact_rectangle_checks"],
        "transition_band_expanded_3d_aabb_candidates": 0,
        "transition_middle_broad_candidates": variable_candidates,
        "transition_middle_z_pattern_checks": z_pattern_checks,
        "middle_port_segment_triangle_checks": port_triangle_checks,
        "middle_port_permitted_triangle_incidences": port_triangle_incidences,
        "intersection_count": 0,
        "global_transition_ribbon_clearance": True,
        "completion_status": "ALL_V3_TRANSITION_RIBBONS_GLOBALLY_CLEAR_AGAINST_TRANSITION_STUB_BAND_MIDDLE_SYSTEMS",
        "verdict": "PASS_X_M1_TRANSITION_RIBBON_GLOBAL_CLEARANCE",
    }
    result["sha256"] = canonical_sha(result)
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
        raise AssertionError("transition global ribbon clearance is stale")
    print(json.dumps({"verdict": result["verdict"], "triangles": result["transition_triangle_count"], "port_checks": result["middle_port_segment_triangle_checks"], "intersections": result["intersection_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()
