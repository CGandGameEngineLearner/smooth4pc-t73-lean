#!/usr/bin/env python3
"""Verify all port-fixed global R3 x-band strips and centerline separation."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_band_global_r3_port_strips_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
BANDS = ROOT / "geometry/t73_x_band_canonical_r3_cell_atlas.json"
SLOPE = 1_000_003


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


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
    return path


def point(values):
    return tuple(Fraction(value) for value in values)


def midpoint(first, second):
    return tuple((a + b) / 2 for a, b in zip(first, second))


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def scale(factor, value):
    return tuple(factor * coordinate for coordinate in value)


def encode(value):
    return [str(coordinate) for coordinate in value]


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def verify(check_cache_sha=True):
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("global band-strip receipt SHA mismatch")
    stubs = json.loads(STUBS.read_text())
    bands = json.loads(BANDS.read_text())
    if data["splice_stub_cores_r3_receipt_sha256"] != stubs["sha256"]:
        raise AssertionError("global band strips stub binding changed")
    if data["x_band_canonical_r3_cell_atlas_sha256"] != bands["sha256"]:
        raise AssertionError("global band strips source-cell binding changed")
    cache = resolve(data["cache_path"])
    if not cache.is_file() or cache.stat().st_size != data["cache_size"]:
        raise AssertionError("global band-strip cache missing or resized")
    if check_cache_sha and file_sha256(cache) != data["cache_sha256"]:
        raise AssertionError("global band-strip cache SHA mismatch")

    stub_records = []
    with gzip.open(resolve(stubs["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        stub_records.extend(json.loads(line) for line in source)
    output_records = []
    digest = hashlib.sha256()
    with gzip.open(cache, "rt", encoding="utf-8") as source:
        for line_number, line in enumerate(source):
            digest.update(line.encode())
            value = json.loads(line)
            if line_number:
                output_records.append(value)
            elif value["routing_functional"] != [str(-SLOPE), "1", "0"]:
                raise AssertionError("global band-strip routing functional changed")
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("global band-strip record stream SHA mismatch")
    if len(output_records) != len(stub_records) != 1513:
        raise AssertionError("global band-strip record count changed")

    endpoint_centers = []
    port_matches = triangle_checks = transversality = 0
    maximum_functional_halfwidth = maximum_z_halfwidth = Fraction(0)
    for index, (stub, source_band, record) in enumerate(
        zip(stub_records, bands["bands"], output_records)
    ):
        values = stub["stubs"]
        v0 = point(values["source_stub_before"]["end_r3"])
        v1 = point(values["source_stub_after"]["start_r3"])
        v4 = point(values["target_complement_first"]["start_r3"])
        v5 = point(values["target_complement_last"]["end_r3"])
        start, end = midpoint(v0, v1), midpoint(v4, v5)
        endpoint_centers.extend((start, end))
        height = Fraction(100 + index)
        exterior_x = Fraction(10_000 + 2 * index)
        centerline = [
            start,
            (start[0], start[1], height),
            (exterior_x, start[1] + SLOPE * (exterior_x - start[0]), height),
            (exterior_x + 1, end[1] + SLOPE * (exterior_x + 1 - end[0]), height),
            (end[0], end[1], height),
            end,
        ]
        band_width = Fraction(data["maximum_strip_z_halfwidth"]) * Fraction(2, 3)
        generic = (band_width, 2 * band_width, 3 * band_width)
        widths = [subtract(v1, v0), generic, generic, generic, generic, subtract(v5, v4)]
        negative = [add(center, scale(Fraction(-1, 2), width)) for center, width in zip(centerline, widths)]
        positive = [add(center, scale(Fraction(1, 2), width)) for center, width in zip(centerline, widths)]
        if record["centerline_vertices"] != [encode(value) for value in centerline]:
            raise AssertionError("global band centerline changed")
        if record["strip_width_field"] != [encode(value) for value in widths]:
            raise AssertionError("global band width field changed")
        if record["negative_lane_vertices"] != [encode(value) for value in negative]:
            raise AssertionError("global negative lane changed")
        if record["positive_lane_vertices_reverse_orientation"] != [encode(value) for value in reversed(positive)]:
            raise AssertionError("global positive lane changed")
        if record["source_band_surface_sha256"] != source_band["source_band_surface_sha256"]:
            raise AssertionError("global strip source band binding changed")
        if (negative[0], positive[0], negative[-1], positive[-1]) != (v0, v1, v4, v5):
            raise AssertionError("global band strip misses a fixed shell port")
        port_matches += 4
        vertices = negative + positive
        for triangle in record["strip_triangles"]:
            first, second, third = [vertices[vertex] for vertex in triangle]
            if cross(subtract(second, first), subtract(third, first)) == (0, 0, 0):
                raise AssertionError("global band-strip triangle degenerated")
            triangle_checks += 1
        for segment in range(5):
            tangent = subtract(centerline[segment + 1], centerline[segment])
            for width in widths[segment:segment + 2]:
                if cross(tangent, width) == (0, 0, 0):
                    raise AssertionError("global band-strip width becomes tangent")
                transversality += 1
        for width in widths:
            maximum_functional_halfwidth = max(
                maximum_functional_halfwidth,
                abs(width[1] - SLOPE * width[0]) / 2,
            )
            maximum_z_halfwidth = max(maximum_z_halfwidth, abs(width[2]) / 2)

    functional_values = sorted(value[1] - SLOPE * value[0] for value in endpoint_centers)
    minimum_separation = min(right - left for left, right in zip(functional_values, functional_values[1:]))
    if len(set(endpoint_centers)) != 3026 or len(set(functional_values)) != 3026:
        raise AssertionError("global band endpoint functional is not injective")
    if minimum_separation != Fraction(data["minimum_endpoint_functional_separation"]):
        raise AssertionError("global band functional separation changed")
    if maximum_functional_halfwidth != Fraction(data["maximum_strip_functional_halfwidth"]):
        raise AssertionError("global band functional halfwidth changed")
    if not 2 * maximum_functional_halfwidth < minimum_separation:
        raise AssertionError("global band strips exhaust endpoint functional clearance")
    if not 2 * maximum_z_halfwidth < 1:
        raise AssertionError("global band strips exhaust height clearance")
    if (port_matches, triangle_checks, transversality) != (6052, 15130, 15130):
        raise AssertionError("global band-strip totals changed")
    if data["strip_global_clearance_status"] != "OPEN_EXACT_TRIANGLE_CHECK":
        raise AssertionError("global strip triangles were overstated as clear")
    return {
        "verdict": "PASS_X_BAND_GLOBAL_R3_PORT_STRIPS_FULL_CONSTRUCTION",
        "bands": 1513,
        "fixed_shell_ports": port_matches,
        "strip_triangles": triangle_checks,
        "width_transversality_checks": transversality,
        "endpoint_functional_values": len(functional_values),
        "centerlines_globally_disjoint": True,
        "cache_sha_checked": check_cache_sha,
        "strip_global_clearance": "OPEN",
        "push_framing": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
