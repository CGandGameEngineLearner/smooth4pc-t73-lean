#!/usr/bin/env python3
"""Independent full replay of separated-waypoint outer collars v3."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v3_receipt.json"
GAP = ROOT / "audit/t73_x_m1_complete_framed_outer_interface_gap.json"
V2_OBSTRUCTION = ROOT / "audit/t73_x_m1_outer_collar_v2_ribbon_self_clearance.json"
GERM_FRACTION = Fraction(1, 1_000_000)
SLOPE = 1_000_033
FUNCTIONAL_Z = 2
LIFT = (Fraction(0), Fraction(-2), Fraction(1))


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


def functional(value):
    return value[1] - SLOPE * value[0] + FUNCTIONAL_Z * value[2]


def lift(value, height):
    return add(value, scale(height - value[2], LIFT))


def route(start, end, index):
    height = Fraction(10_000 + index)
    exterior_x = Fraction(50_000 + 2 * index)
    start_high, end_high = lift(start, height), lift(end, height)
    return [
        start,
        start_high,
        (exterior_x, start_high[1] + SLOPE * (exterior_x - start_high[0]), height),
        (exterior_x + 1, end_high[1] + SLOPE * (exterior_x + 1 - end_high[0]), height),
        end_high,
        end,
    ]


def triangles(size):
    return [
        triangle
        for index in range(size - 1)
        for triangle in (
            [index, index + 1, size + index + 1],
            [index, size + index + 1, size + index],
        )
    ]


def verify_full():
    data = json.loads(DATA.read_text())
    gap = json.loads(GAP.read_text())
    obstruction = json.loads(V2_OBSTRUCTION.read_text())
    if (
        data["outer_interface_gap_sha256"] != gap["sha256"]
        or data["v2_ribbon_obstruction_sha256"] != obstruction["sha256"]
    ):
        raise AssertionError("v3 collar source binding changed")
    cache_path = resolve(data["cache_path"])
    if (
        cache_path.stat().st_size != data["cache_size"]
        or file_sha(cache_path) != data["cache_sha256"]
    ):
        raise AssertionError("v3 collar cache bytes changed")
    digest = hashlib.sha256()
    endpoints = []
    records = segments = triangle_count = transversality = functional_checks = 0
    with gzip.open(cache_path, "rt", encoding="utf-8") as source:
        header_line = source.readline()
        digest.update(header_line.encode())
        header = json.loads(header_line)
        if header["routing_functional"] != [
            str(-SLOPE),
            "1",
            str(FUNCTIONAL_Z),
        ] or header["lift_direction"] != [str(value) for value in LIFT]:
            raise AssertionError("v3 routing invariant changed")
        for interface, line in zip(gap["interfaces"], source, strict=True):
            digest.update(line.encode())
            record = json.loads(line)
            index = interface["interface_index"]
            inner = point(interface["source_inner_core"])
            source_port = point(interface["source_core_port"])
            target = point(interface["target_core_port"])
            germ = add(inner, scale(GERM_FRACTION, subtract(source_port, inner)))
            expected_core = [inner, *route(germ, target, index)]
            source_normal = subtract(point(interface["source_push_port"]), source_port)
            target_normal = subtract(point(interface["target_push_port"]), target)
            expected_normals = [source_normal] * (len(expected_core) - 1) + [
                target_normal
            ]
            expected_push = [
                add(vertex, normal)
                for vertex, normal in zip(expected_core, expected_normals)
            ]
            core = [point(vertex) for vertex in record["final_core_vertices"]]
            normals = [point(vertex) for vertex in record["final_normal_field"]]
            push = [point(vertex) for vertex in record["final_push_vertices"]]
            if (
                core != expected_core
                or normals != expected_normals
                or push != expected_push
                or record["final_ribbon_triangles"] != triangles(len(core))
            ):
                raise AssertionError("v3 collar geometry changed")
            routed = core[1:]
            if functional(routed[0]) != functional(routed[1]) or functional(
                routed[-2]
            ) != functional(routed[-1]):
                raise AssertionError("v3 skew lift functional changed")
            if (
                routed[1][1] - SLOPE * routed[1][0]
                != routed[2][1] - SLOPE * routed[2][0]
                or routed[3][1] - SLOPE * routed[3][0]
                != routed[4][1] - SLOPE * routed[4][0]
            ):
                raise AssertionError("v3 exterior ray functional changed")
            functional_checks += 4
            for segment in range(len(core) - 1):
                tangent = subtract(core[segment + 1], core[segment])
                if affine_zero(
                    cross(tangent, normals[segment]),
                    cross(tangent, normals[segment + 1]),
                ):
                    raise AssertionError("v3 collar normal loses transversality")
                transversality += 1
            if (
                record["classification"] != "CANDIDATE_UNVERIFIED"
                or record["global_core_push_ribbon_clearance_status"] != "OPEN"
            ):
                raise AssertionError("v3 local cache overclaims clearance")
            endpoints.extend((germ, target))
            records += 1
            segments += len(core) - 1
            triangle_count += len(record["final_ribbon_triangles"])
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("v3 collar decompressed stream changed")
    values = sorted(functional(value) for value in endpoints)
    if len(values) != len(set(values)) or min(
        right - left for left, right in pairwise(values)
    ) != Fraction(1, 500_000):
        raise AssertionError("v3 functional endpoint separation changed")
    if (records, segments, triangle_count, transversality, functional_checks) != (
        3026,
        18156,
        36312,
        18156,
        12104,
    ):
        raise AssertionError("v3 collar totals changed")
    return {
        "verdict": "PASS_X_M1_FRAMED_OUTER_INTERFACE_COLLARS_V3_FULL_LOCAL_CANDIDATE",
        "cache_sha_checked": True,
        "collars_reconstructed": records,
        "core_push_segments_each": segments,
        "ribbon_triangles_reconstructed": triangle_count,
        "functional_endpoint_count": len(values),
        "minimum_functional_separation": "1/500000",
        "normal_transversality_checks": transversality,
        "functional_route_checks": functional_checks,
        "relative_twist_sum": 0,
        "classification": "CANDIDATE_UNVERIFIED",
        "global_clearance": "OPEN",
        "ambient_support": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
