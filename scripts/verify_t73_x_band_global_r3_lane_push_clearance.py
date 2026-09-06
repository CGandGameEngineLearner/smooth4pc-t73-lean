#!/usr/bin/env python3
"""Verify global x-band attaching-lane push paths and ruled ribbons."""

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

from verify_t73_affine_s3_product_ribbon_clearance import (
    segment_triangle,
    triangles_intersect,
)


ROOT = Path(__file__).resolve().parents[1]
LANES = ROOT / "audit/t73_x_band_global_r3_lane_push_paths_receipt.json"
STRIPS = ROOT / "audit/t73_x_band_global_r3_port_strips_receipt.json"
CORE_CLEARANCE = ROOT / "audit/t73_x_band_global_r3_port_strip_clearance.json"
DISK_OBSTRUCTION = ROOT / "audit/t73_x_band_global_r3_push_disk_obstruction.json"


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    return path


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


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


def segment_intersection(first, second):
    a, b = first
    c, d = second
    u, v, w = subtract(b, a), subtract(d, c), subtract(c, a)
    for first_axis, second_axis in ((0, 1), (0, 2), (1, 2)):
        denominator = u[first_axis] * (-v[second_axis]) - u[second_axis] * (-v[first_axis])
        if denominator:
            first_parameter = (
                w[first_axis] * (-v[second_axis]) - w[second_axis] * (-v[first_axis])
            ) / denominator
            second_parameter = (
                u[first_axis] * w[second_axis] - u[second_axis] * w[first_axis]
            ) / denominator
            return (
                0 <= first_parameter <= 1
                and 0 <= second_parameter <= 1
                and all(
                    a[axis] + first_parameter * u[axis]
                    == c[axis] + second_parameter * v[axis]
                    for axis in range(3)
                )
            )
    return cross(u, w) == (0, 0, 0)


def bounds(values):
    return (
        tuple(min(value[axis] for value in values) for axis in range(3)),
        tuple(max(value[axis] for value in values) for axis in range(3)),
    )


def overlap(first, second):
    return all(
        first[0][axis] <= second[1][axis]
        and second[0][axis] <= first[1][axis]
        for axis in range(3)
    )


def verify():
    lanes = json.loads(LANES.read_text())
    strips = json.loads(STRIPS.read_text())
    core_clearance = json.loads(CORE_CLEARANCE.read_text())
    disk_obstruction = json.loads(DISK_OBSTRUCTION.read_text())
    unsigned = {key: value for key, value in lanes.items() if key != "sha256"}
    if lanes["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("lane push-path receipt SHA mismatch")
    cache = resolve(lanes["cache_path"])
    if not cache.is_file() or cache.stat().st_size != lanes["cache_size"]:
        raise AssertionError("lane push-path cache missing or resized")
    if file_sha256(cache) != lanes["cache_sha256"]:
        raise AssertionError("lane push-path cache SHA mismatch")
    if lanes["global_port_strips_receipt_sha256"] != strips["sha256"]:
        raise AssertionError("lane push paths strip binding changed")
    if lanes["global_push_disk_obstruction_sha256"] != disk_obstruction["sha256"]:
        raise AssertionError("lane push paths obstruction binding changed")
    displacement = point(lanes["push_displacement"])
    slope = -Fraction(strips["routing_functional"][0])
    functional_margin = (
        Fraction(strips["minimum_endpoint_functional_separation"])
        - 2 * Fraction(strips["maximum_strip_functional_halfwidth"])
    )
    functional_shift = displacement[1] - slope * displacement[0]
    height_margin = (
        Fraction(strips["minimum_routing_height_separation"])
        - 2 * Fraction(strips["maximum_strip_z_halfwidth"])
    )
    if abs(functional_shift) >= functional_margin or abs(displacement[2]) >= height_margin:
        raise AssertionError("lane push displacement exhausts cross-band clearance")
    if not core_clearance["full_result"]["globally_embedded_port_fixed_band_strips"]:
        raise AssertionError("global core band-strip clearance is missing")

    segment_pairs = segment_bounds_rejects = exact_segment_checks = 0
    triangle_pairs = triangle_incidence = triangle_bounds_rejects = 0
    exact_triangle_checks = ribbon_segment_pairs = ribbon_segment_incidence = 0
    ribbon_segment_bounds_rejects = exact_ribbon_segment_checks = records = 0
    with gzip.open(cache, "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            lane_data = []
            all_segments = []
            for lane in record["lanes"]:
                core = [point(value) for value in lane["core_vertices"]]
                push = [point(value) for value in lane["push_vertices"]]
                core_segments = list(zip(core, core[1:]))
                push_segments = list(zip(push, push[1:]))
                all_segments.extend(core_segments + push_segments)
                vertices = core + push
                triangles = [
                    tuple(vertices[index] for index in ids)
                    for ids in lane["ribbon_triangles"]
                ]
                lane_data.append((core_segments, push_segments, triangles))
            for core_segments, _, _ in lane_data:
                for core_segment in core_segments:
                    for _, push_segments, _ in lane_data:
                        for push_segment in push_segments:
                            segment_pairs += 1
                            if not overlap(bounds(core_segment), bounds(push_segment)):
                                segment_bounds_rejects += 1
                                continue
                            exact_segment_checks += 1
                            if segment_intersection(core_segment, push_segment):
                                raise AssertionError(
                                    f"band {record['band_index']} lane core meets a lane push"
                                )
            for _, _, triangles in lane_data:
                triangle_bounds = [bounds(triangle) for triangle in triangles]
                for first in range(len(triangles)):
                    for second in range(first):
                        triangle_pairs += 1
                        if set(triangles[first]) & set(triangles[second]):
                            triangle_incidence += 1
                            continue
                        if not overlap(triangle_bounds[first], triangle_bounds[second]):
                            triangle_bounds_rejects += 1
                            continue
                        exact_triangle_checks += 1
                        if triangles_intersect(triangles[first], triangles[second]):
                            raise AssertionError(
                                f"band {record['band_index']} lane ribbon self-intersects"
                            )
                for triangle, triangle_bound in zip(triangles, triangle_bounds):
                    for segment in all_segments:
                        ribbon_segment_pairs += 1
                        if set(triangle) & set(segment):
                            ribbon_segment_incidence += 1
                            continue
                        if not overlap(triangle_bound, bounds(segment)):
                            ribbon_segment_bounds_rejects += 1
                            continue
                        exact_ribbon_segment_checks += 1
                        if segment_triangle(segment, triangle):
                            raise AssertionError(
                                f"band {record['band_index']} lane ribbon meets a nonincident lane segment"
                            )
            records += 1
            if os.environ.get("T73_PROGRESS") and records % 200 == 0:
                print(
                    f"lane push clearance {records}/1513 "
                    f"seg_exact={exact_segment_checks} tri_exact={exact_triangle_checks} "
                    f"ribbon_seg_exact={exact_ribbon_segment_checks}",
                    file=sys.stderr,
                    flush=True,
                )
    if records != 1513 or segment_pairs != 151300:
        raise AssertionError("lane push clearance inventory changed")
    return {
        "verdict": "PASS_X_BAND_GLOBAL_R3_LANE_PUSH_AND_RIBBON_CLEARANCE",
        "bands": records,
        "lane_core_push_segment_pairs": segment_pairs,
        "lane_core_push_exact_bounds_rejects": segment_bounds_rejects,
        "lane_core_push_exact_segment_checks": exact_segment_checks,
        "within_lane_ribbon_triangle_pairs": triangle_pairs,
        "within_lane_ribbon_incidence_skips": triangle_incidence,
        "within_lane_ribbon_exact_bounds_rejects": triangle_bounds_rejects,
        "within_lane_ribbon_exact_triangle_checks": exact_triangle_checks,
        "ribbon_segment_pairs": ribbon_segment_pairs,
        "ribbon_segment_incidence_skips": ribbon_segment_incidence,
        "ribbon_segment_exact_bounds_rejects": ribbon_segment_bounds_rejects,
        "ribbon_segment_exact_checks": exact_ribbon_segment_checks,
        "cross_band_push_push_clearance": "PASS_BY_COMMON_TRANSLATION",
        "cross_band_core_push_functional_margin": str(functional_margin),
        "cross_band_core_push_functional_shift": str(functional_shift),
        "cross_band_core_push_height_margin": str(height_margin),
        "cross_band_core_push_height_shift": str(displacement[2]),
        "globally_embedded_band_lane_push_paths_and_ribbons": True,
        "endpoint_push_gluing": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
