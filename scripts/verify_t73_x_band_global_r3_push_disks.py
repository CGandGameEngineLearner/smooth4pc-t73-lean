#!/usr/bin/env python3
"""Verify all global x-band push disks, lane ribbons and product tetrahedra."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_band_global_r3_push_disks_receipt.json"
STRIPS = ROOT / "audit/t73_x_band_global_r3_port_strips_receipt.json"
SOURCE = ROOT / "geometry/t73_x_band_canonical_r3_cell_atlas.json"


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


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def determinant(a, b, c, d):
    rows = [[b[i] - a[i], c[i] - a[i], d[i] - a[i]] for i in range(3)]
    return (
        rows[0][0] * (rows[1][1] * rows[2][2] - rows[1][2] * rows[2][1])
        - rows[0][1] * (rows[1][0] * rows[2][2] - rows[1][2] * rows[2][0])
        + rows[0][2] * (rows[1][0] * rows[2][1] - rows[1][1] * rows[2][0])
    )


def verify(check_cache_sha=True):
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("global band push receipt SHA mismatch")
    strips = json.loads(STRIPS.read_text())
    source_atlas = json.loads(SOURCE.read_text())
    if data["global_port_strips_receipt_sha256"] != strips["sha256"]:
        raise AssertionError("global band push strip binding changed")
    if data["canonical_source_band_atlas_sha256"] != source_atlas["sha256"]:
        raise AssertionError("global band push source binding changed")
    cache = resolve(data["cache_path"])
    if not cache.is_file() or cache.stat().st_size != data["cache_size"]:
        raise AssertionError("global band push cache missing or resized")
    if check_cache_sha and file_sha256(cache) != data["cache_sha256"]:
        raise AssertionError("global band push cache SHA mismatch")
    with gzip.open(resolve(strips["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        strip_records = [json.loads(line) for line in source]
    records = []
    digest = hashlib.sha256()
    with gzip.open(cache, "rt", encoding="utf-8") as source:
        for line_number, line in enumerate(source):
            digest.update(line.encode())
            if line_number:
                records.append(json.loads(line))
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("global band push stream SHA mismatch")
    displacement = point(data["push_displacement"])
    triangles = ribbons = tetrahedra = transverse = 0
    for index, (strip, source_band, record) in enumerate(
        zip(strip_records, source_atlas["bands"], records)
    ):
        negative = [point(value) for value in strip["negative_lane_vertices"]]
        positive = [point(value) for value in reversed(strip["positive_lane_vertices_reverse_orientation"])]
        core = negative + positive
        push = [add(vertex, displacement) for vertex in core]
        if [point(value) for value in record["core_vertices"]] != core:
            raise AssertionError("global band push core changed")
        if [point(value) for value in record["push_vertices"]] != push:
            raise AssertionError("global band push displacement changed")
        if record["source_band_surface_sha256"] != source_band["source_band_surface_sha256"]:
            raise AssertionError("global band push source SHA changed")
        if record["source_relative_twist"] != 0:
            raise AssertionError("global band push has nonzero source twist")
        expected_product = []
        for triangle in strip["strip_triangles"]:
            a, b, c = sorted(triangle)
            expected_product.extend((
                [a, b, c, c + 12],
                [a, b, b + 12, c + 12],
                [a, a + 12, b + 12, c + 12],
            ))
        if record["surface_product_tetrahedra"] != expected_product:
            raise AssertionError("global band product subdivision changed")
        vertices = core + push
        for tetrahedron in expected_product:
            if determinant(*[vertices[vertex] for vertex in tetrahedron]) == 0:
                raise AssertionError("global band product tetrahedron degenerated")
            tetrahedra += 1
        expected_ribbons = []
        for offset in (0, 6):
            for segment in range(5):
                expected_ribbons.extend((
                    [offset + segment, offset + segment + 1, 12 + offset + segment + 1],
                    [offset + segment, 12 + offset + segment + 1, 12 + offset + segment],
                ))
        if record["lane_framing_ribbon_triangles"] != expected_ribbons:
            raise AssertionError("global band lane ribbon subdivision changed")
        ribbons += len(expected_ribbons)
        triangles += len(strip["strip_triangles"])
        transverse += len(strip["strip_triangles"])
    if len(records) != 1513 or (triangles, ribbons, tetrahedra, transverse) != (15130, 30260, 45390, 15130):
        raise AssertionError("global band push verification totals changed")
    if data["global_push_disk_clearance_status"] != "OPEN_EXACT_NONINCIDENT_CHECK":
        raise AssertionError("local band pushes were overstated as globally clear")
    return {
        "verdict": "PASS_X_BAND_GLOBAL_R3_PUSH_DISKS_FULL_LOCAL_PRODUCT",
        "bands": len(records),
        "core_triangles": triangles,
        "push_triangles": triangles,
        "lane_framing_ribbon_triangles": ribbons,
        "surface_product_tetrahedra": tetrahedra,
        "cache_sha_checked": check_cache_sha,
        "global_push_disk_clearance": "OPEN",
        "endpoint_push_gluing": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
