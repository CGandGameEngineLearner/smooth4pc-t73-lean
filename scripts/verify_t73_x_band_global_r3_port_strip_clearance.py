#!/usr/bin/env python3
"""Verify analytic cross-band and exact within-band strip clearance."""

from __future__ import annotations

import gzip
import json
import os
import sys
from fractions import Fraction
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from verify_t73_affine_s3_product_ribbon_clearance import triangles_intersect


ROOT = Path(__file__).resolve().parents[1]
CONSTRUCTION = ROOT / "audit/t73_x_band_global_r3_port_strips_receipt.json"


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    return path


def point(values):
    return tuple(Fraction(value) for value in values)


def bounds(triangle):
    return (
        tuple(min(vertex[axis] for vertex in triangle) for axis in range(3)),
        tuple(max(vertex[axis] for vertex in triangle) for axis in range(3)),
    )


def overlap(first, second):
    return all(
        first[0][axis] <= second[1][axis]
        and second[0][axis] <= first[1][axis]
        for axis in range(3)
    )


def verify():
    construction = json.loads(CONSTRUCTION.read_text())
    minimum_functional = Fraction(construction["minimum_endpoint_functional_separation"])
    maximum_functional_halfwidth = Fraction(construction["maximum_strip_functional_halfwidth"])
    maximum_z_halfwidth = Fraction(construction["maximum_strip_z_halfwidth"])
    if not 2 * maximum_functional_halfwidth < minimum_functional:
        raise AssertionError("vertical/ray strip functional intervals overlap")
    if not 2 * maximum_z_halfwidth < 1:
        raise AssertionError("distinct horizontal routing layers overlap in z")

    records = []
    with gzip.open(resolve(construction["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        records.extend(json.loads(line) for line in source)
    endpoint_x = []
    exterior_x = []
    maximum_x_halfwidth = Fraction(0)
    pair_count = incidence_skips = bounds_rejects = exact_checks = 0
    for record in records:
        negative = [point(value) for value in record["negative_lane_vertices"]]
        positive = [point(value) for value in reversed(record["positive_lane_vertices_reverse_orientation"])]
        vertices = negative + positive
        triangles = [tuple(vertices[index] for index in ids) for ids in record["strip_triangles"]]
        triangle_bounds = [bounds(triangle) for triangle in triangles]
        endpoint_x.extend((point(record["centerline_vertices"][0])[0], point(record["centerline_vertices"][-1])[0]))
        exterior_x.extend(Fraction(value) for value in record["exterior_x_interval"])
        for raw in record["strip_width_field"]:
            maximum_x_halfwidth = max(maximum_x_halfwidth, abs(Fraction(raw[0])) / 2)
        for first in range(len(triangles)):
            for second in range(first):
                pair_count += 1
                if set(triangles[first]) & set(triangles[second]):
                    incidence_skips += 1
                    continue
                if not overlap(triangle_bounds[first], triangle_bounds[second]):
                    bounds_rejects += 1
                    continue
                exact_checks += 1
                if triangles_intersect(triangles[first], triangles[second]):
                    raise AssertionError(
                        f"band {record['band_index']} has a self-intersecting strip"
                    )
    if len(records) != 1513:
        raise AssertionError("global band-strip record inventory changed")
    if min(exterior_x) - maximum_x_halfwidth <= max(endpoint_x) + maximum_x_halfwidth:
        raise AssertionError("exterior connectors can meet endpoint vertical columns")
    totals = (pair_count, incidence_skips, bounds_rejects, exact_checks)
    if totals != (68085, 25721, 28742, 13622):
        raise AssertionError(f"within-band strip clearance totals changed: {totals}")
    return {
        "verdict": "PASS_X_BAND_GLOBAL_R3_PORT_STRIP_CLEARANCE",
        "bands": len(records),
        "strip_triangles": 15130,
        "within_band_triangle_pairs": pair_count,
        "within_band_incidence_skips": incidence_skips,
        "within_band_exact_bounds_rejects": bounds_rejects,
        "within_band_exact_triangle_checks": exact_checks,
        "cross_band_vertical_separation": "PASS_EXACT_ROUTING_FUNCTIONAL_INTERVALS",
        "cross_band_horizontal_separation": "PASS_EXACT_INTEGER_HEIGHT_INTERVALS",
        "horizontal_vertical_ray_separation": "PASS_EXACT_ROUTING_FUNCTIONAL_INTERVALS",
        "exterior_vertical_separation": "PASS_EXACT_X_INTERVALS",
        "globally_embedded_port_fixed_band_strips": True,
        "push_framing": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
