#!/usr/bin/env python3
"""Verify all actual x-band disks and their canonical disjoint R3 atlas."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_band_canonical_r3_cell_atlas.json"
REPLACEMENT = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
HYBRID = ROOT / "geometry/t73_x_band_hybrid_movie.json"
TRIANGLES = [[0, 2, 3], [0, 3, 1], [2, 4, 5], [2, 5, 3]]


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/home/") and os.name == "nt":
        return Path("//wsl.localhost/Ubuntu") / value[1:]
    return path


def point(values):
    return tuple(Fraction(value) for value in values)


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def determinant(a, b, c, d):
    first, second, third = subtract(b, a), subtract(c, a), subtract(d, a)
    return (
        first[0] * (second[1] * third[2] - second[2] * third[1])
        - first[1] * (second[0] * third[2] - second[2] * third[0])
        + first[2] * (second[0] * third[1] - second[1] * third[0])
    )


def verify():
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("x-band R3 atlas payload SHA mismatch")
    replacement = json.loads(REPLACEMENT.read_text())
    hybrid = json.loads(HYBRID.read_text())
    if data["post_x_replacement_cells_receipt_sha256"] != replacement["sha256"]:
        raise AssertionError("x-band R3 atlas replacement binding changed")
    if data["x_band_hybrid_movie_sha256"] != hybrid["sha256"]:
        raise AssertionError("x-band R3 atlas hybrid binding changed")
    saved_bands = data["bands"]
    source_records = []
    with gzip.open(resolve(replacement["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        source_records.extend(json.loads(line) for line in source)
    if len(source_records) != len(saved_bands) != 1513:
        raise AssertionError("x-band R3 atlas record count changed")

    source_cell_checks = canonical_cell_checks = ribbon_triangle_checks = 0
    product_tetrahedron_checks = support_clearance_checks = 0
    previous_high = None
    for index, (source, saved) in enumerate(zip(source_records, saved_bands)):
        if source["band_index"] != index or saved["band_index"] != index:
            raise AssertionError("x-band R3 atlas order changed")
        surface = source["band_surface"]
        vertices = surface["vertices"]
        push_vertices = surface["push_vertices"]
        if len(vertices) != 6 or len(push_vertices) != 6 or surface["triangles"] != TRIANGLES:
            raise AssertionError("source x-band disk template changed")
        if source["negative_band_lane"]["vertices"] != [vertices[i] for i in (0, 2, 4)]:
            raise AssertionError("source negative lane is not the band boundary")
        if source["positive_band_lane"]["vertices"] != [vertices[i] for i in (5, 3, 1)]:
            raise AssertionError("source positive lane is not the band boundary")
        if source["relative_twist"] != 0:
            raise AssertionError("source band has nonzero relative twist")
        if saved["source_band_surface_sha256"] != canonical_sha256(surface):
            raise AssertionError("saved band is not bound to its actual source disk")
        if (
            saved["component"] != source["component"]
            or saved["orientation"] != source["orientation"]
            or saved["source_id"] != source["source_id"]
            or saved["hybrid_replacement_cell_sha256"] != source["hybrid_replacement_cell_sha256"]
        ):
            raise AssertionError("saved band provenance changed")
        source_cell_checks += 1

        x = 4 * index
        expected_core = [
            [str(x), "0", "0"], [str(x), "1", "0"],
            [str(x + 1), "0", "0"], [str(x + 1), "1", "0"],
            [str(x + 2), "0", "0"], [str(x + 2), "1", "0"],
        ]
        expected_push = [[value[0], value[1], "1/10"] for value in expected_core]
        if saved["core_vertices"] != expected_core or saved["push_vertices"] != expected_push:
            raise AssertionError("canonical band coordinates changed")
        if saved["core_triangles"] != TRIANGLES or saved["push_triangles"] != TRIANGLES:
            raise AssertionError("canonical band triangulation changed")
        core = [point(value) for value in expected_core]
        push = [point(value) for value in expected_push]
        for triangle in TRIANGLES:
            a, b, c = [core[vertex] for vertex in triangle]
            if cross(subtract(b, a), subtract(c, a)) == (0, 0, 0):
                raise AssertionError("canonical band triangle degenerated")
            low = sorted(triangle)
            a, b, c = low
            tetrahedra = (
                (a, b, c, c + 6),
                (a, b, b + 6, c + 6),
                (a, a + 6, b + 6, c + 6),
            )
            for tetrahedron in tetrahedra:
                if determinant(*[(core + push)[vertex] for vertex in tetrahedron]) == 0:
                    raise AssertionError("canonical band product tetrahedron degenerated")
                product_tetrahedron_checks += 1
        vertices12 = core + push
        for triangle in saved["lane_ribbon_triangles"]:
            a, b, c = [vertices12[vertex] for vertex in triangle]
            if cross(subtract(b, a), subtract(c, a)) == (0, 0, 0):
                raise AssertionError("canonical lane ribbon triangle degenerated")
            ribbon_triangle_checks += 1
        low, high = map(Fraction, saved["x_support_interval"])
        if previous_high is not None:
            if low - previous_high != 2:
                raise AssertionError("canonical band support gap changed")
            support_clearance_checks += 1
        previous_high = high
        canonical_cell_checks += 1

    totals = (
        source_cell_checks,
        canonical_cell_checks,
        ribbon_triangle_checks,
        product_tetrahedron_checks,
        support_clearance_checks,
    )
    if totals != (1513, 1513, 12104, 18156, 1512):
        raise AssertionError(f"canonical x-band atlas totals changed: {totals}")
    if data["global_port_gluing_status"] != "OPEN_MAP_FOUR_ATTACHMENT_PORTS_PER_BAND":
        raise AssertionError("disconnected band atlas was overstated as globally glued")
    return {
        "verdict": "PASS_ALL_X_BAND_CANONICAL_R3_CELL_ATLAS_FULL",
        "actual_source_band_cells": source_cell_checks,
        "canonical_r3_band_cells": canonical_cell_checks,
        "core_triangles": 6052,
        "lane_ribbon_triangles": ribbon_triangle_checks,
        "surface_product_tetrahedra": product_tetrahedron_checks,
        "pairwise_support_clearance_checks": support_clearance_checks,
        "global_port_gluing": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
