#!/usr/bin/env python3
"""Independently verify ordered final/source core clearance."""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import os
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

from rtree import index as rtree_index

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_static_core_clearance.json"
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
FINAL_CLEARANCE = ROOT / "audit/t73_x_m1_outer_collar_v7_one_skeleton_clearance.json"
SEQUENTIAL = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_isotopy_trace_receipt.json"
)
SEQUENTIAL_VERIFY = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_isotopy_trace_verification.json"
)


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
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def subtract(first, second):
    return tuple(a - b for a, b in zip(first, second))


def cross(first, second):
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def dot(first, second):
    return sum(a * b for a, b in zip(first, second))


def intersects(first, second):
    p, p1 = first
    q, q1 = second
    u, v, w = subtract(p1, p), subtract(q1, q), subtract(q, p)
    for i in range(3):
        for j in range(i + 1, 3):
            determinant = u[j] * v[i] - u[i] * v[j]
            if determinant:
                t = (w[j] * v[i] - w[i] * v[j]) / determinant
                s = (u[i] * w[j] - u[j] * w[i]) / determinant
                return (
                    0 <= t <= 1
                    and 0 <= s <= 1
                    and all(p[k] + t * u[k] == q[k] + s * v[k] for k in range(3))
                )
    if cross(u, w) != (0, 0, 0):
        return False
    axis = next(index for index, value in enumerate(u) if value)
    parameters = sorted(((q[axis] - p[axis]) / u[axis], (q1[axis] - p[axis]) / u[axis]))
    return max(Fraction(0), parameters[0]) <= min(Fraction(1), parameters[1])


def bounds(segment):
    low = [min(segment[0][axis], segment[1][axis]) for axis in range(3)]
    high = [max(segment[0][axis], segment[1][axis]) for axis in range(3)]
    return tuple(math.nextafter(float(value), -math.inf) for value in low) + tuple(
        math.nextafter(float(value), math.inf) for value in high
    )


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    collars = json.loads(COLLARS.read_text())
    final_clearance = json.loads(FINAL_CLEARANCE.read_text())
    sequential = json.loads(SEQUENTIAL.read_text())
    verification = json.loads(SEQUENTIAL_VERIFY.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or data["v7_final_core_clearance_sha256"]
        != final_clearance["core_clearance"]["sha256"]
        or data["sequential_trace_receipt_sha256"] != sequential["sha256"]
        or data["sequential_trace_verification_sha256"] != verification["sha256"]
    ):
        raise AssertionError("ordered mixed-core bindings changed")
    sources = []
    finals = []
    with gzip.open(resolve(collars["cache_path"]), "rt", encoding="utf-8") as stream:
        stream.readline()
        for line in stream:
            record = json.loads(line)
            interface = record["interface_index"]
            source_segment = tuple(
                point(value) for value in record["source_core_segment"]
            )
            sources.append((interface, record["neighbor_id"], source_segment))
            vertices = [point(value) for value in record["final_core_vertices"]]
            finals.extend(
                (interface, record["neighbor_id"], local, segment)
                for local, segment in enumerate(pairwise(vertices))
            )
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        ((index, bounds(segment), None) for index, (*_, segment) in enumerate(sources)),
        properties=properties,
    )
    broad = separated = 0
    permitted = []
    for final_interface, final_neighbor, local, final_segment in finals:
        for source_index in tree.intersection(bounds(final_segment)):
            source_interface, source_neighbor, source_segment = sources[source_index]
            if final_interface >= source_interface:
                continue
            broad += 1
            if not intersects(final_segment, source_segment):
                separated += 1
                continue
            shared = set(final_segment) & set(source_segment)
            if local != 0 or final_neighbor != source_neighbor or len(shared) != 1:
                raise AssertionError(
                    "independent verifier found a forbidden intersection"
                )
            common = next(iter(shared))
            final_other = next(value for value in final_segment if value != common)
            source_other = next(value for value in source_segment if value != common)
            first = subtract(final_other, common)
            second = subtract(source_other, common)
            if cross(first, second) != (0, 0, 0) or dot(first, second) >= 0:
                raise AssertionError("independent germ star is not opposite")
            permitted.append(
                {
                    "final_interface": final_interface,
                    "source_interface": source_interface,
                    "neighbor_id": final_neighbor,
                    "shared_endpoint": [str(value) for value in common],
                    "relation": "COLLINEAR_OPPOSITE_GERMS",
                }
            )
    if (
        broad != 3022
        or separated != 3018
        or permitted != data["permitted_opposite_germ_incidences"]
        or data["nonpermitted_intersection_count"] != 0
        or not data["ordered_mixed_static_core_clearance"]
    ):
        raise AssertionError("ordered mixed-core replay changed")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_SEQUENTIAL_STATIC_CORE_CLEARANCE_INDEPENDENT",
        "outward_float_aabb_candidates": broad,
        "exact_segment_checks": broad,
        "exact_separated_pairs": separated,
        "permitted_opposite_germ_incidences": len(permitted),
        "nonpermitted_intersections": 0,
        "ordered_mixed_static_core_clearance": True,
        "push_and_ribbon_status": "OPEN",
        "moving_static_status": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
