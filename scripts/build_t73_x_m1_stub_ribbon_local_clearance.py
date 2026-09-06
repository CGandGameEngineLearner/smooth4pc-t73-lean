#!/usr/bin/env python3
"""Verify all stub ribbons within each replacement-band record."""

from __future__ import annotations

import argparse
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
STUBS = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
CORE_PUSH = ROOT / "audit/t73_x_m1_stub_core_push_clearance.json"
OUTPUT = ROOT / "audit/t73_x_m1_stub_ribbon_local_clearance.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    return path


def point(values):
    return tuple(Fraction(value) for value in values)


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


def build():
    stubs = json.loads(STUBS.read_text())
    core_push = json.loads(CORE_PUSH.read_text())
    triangle_pairs = triangle_incidence = triangle_bounds_rejects = 0
    exact_triangle_checks = segment_pairs = segment_incidence = 0
    segment_bounds_rejects = exact_segment_checks = records = 0
    with gzip.open(resolve(stubs["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            triangles = []
            segments = []
            for stub in record["stubs"].values():
                core = [point(value) for value in stub["core_vertices"]]
                push = [point(value) for value in stub["push_vertices"]]
                vertices = core + push
                triangles.extend(
                    tuple(vertices[index] for index in ids)
                    for ids in stub["ribbon_triangles"]
                )
                segments.extend(zip(core, core[1:]))
                segments.extend(zip(push, push[1:]))
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
                            f"stub ribbon self-intersection in band {record['band_index']}"
                        )
            for triangle, triangle_bound in zip(triangles, triangle_bounds):
                for segment in segments:
                    segment_pairs += 1
                    if set(triangle) & set(segment):
                        segment_incidence += 1
                        continue
                    if not overlap(triangle_bound, bounds(segment)):
                        segment_bounds_rejects += 1
                        continue
                    exact_segment_checks += 1
                    if segment_triangle(segment, triangle):
                        raise AssertionError(
                            f"stub ribbon meets nonincident segment in band {record['band_index']}"
                        )
            records += 1
    totals = (
        records,
        triangle_pairs,
        triangle_incidence,
        triangle_bounds_rejects,
        exact_triangle_checks,
        segment_pairs,
        segment_incidence,
        segment_bounds_rejects,
        exact_segment_checks,
    )
    expected = (1513, 137474, 24172, 113302, 0, 296112, 69508, 226604, 0)
    if totals != expected:
        raise AssertionError(f"stub local ribbon totals changed: {totals}")
    result = {
        "schema": "t73_x_m1_stub_ribbon_local_clearance/v1",
        "stub_r3_push_paths_receipt_sha256": stubs["sha256"],
        "stub_core_push_clearance_sha256": core_push["sha256"],
        "band_record_count": records,
        "ribbon_triangle_count": stubs["ribbon_triangle_count"],
        "within_band_ribbon_triangle_pairs": triangle_pairs,
        "within_band_ribbon_incidence_skips": triangle_incidence,
        "within_band_ribbon_exact_bounds_rejects": triangle_bounds_rejects,
        "within_band_ribbon_exact_triangle_checks": exact_triangle_checks,
        "within_band_ribbon_segment_pairs": segment_pairs,
        "within_band_ribbon_segment_incidence_skips": segment_incidence,
        "within_band_ribbon_segment_exact_bounds_rejects": segment_bounds_rejects,
        "within_band_ribbon_segment_exact_checks": exact_segment_checks,
        "within_band_stub_ribbon_embedding": True,
        "cross_band_ribbon_clearance_status": "OPEN_PROJECT_TO_DISPLACEMENT_QUOTIENT",
        "verdict": "PASS_X_M1_STUB_RIBBON_LOCAL_CLEARANCE",
    }
    result["sha256"] = canonical_sha256(result)
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
        raise AssertionError("stub local ribbon clearance is stale")
    print(json.dumps({
        "verdict": result["verdict"],
        "bands": result["band_record_count"],
        "triangle_pairs": result["within_band_ribbon_triangle_pairs"],
        "segment_pairs": result["within_band_ribbon_segment_pairs"],
        "cross_band": result["cross_band_ribbon_clearance_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
