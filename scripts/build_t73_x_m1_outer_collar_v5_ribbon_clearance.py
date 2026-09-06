#!/usr/bin/env python3
"""Exact global clearance of all V5 ruled collar rectangles."""

from __future__ import annotations

import argparse
import bisect
import gzip
import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

from gmpy2 import mpq

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v2_ribbon_self_clearance import (
    exact_bounds,
    overlap,
    triangle_intersection_witness,
)
from verify_t73_x_m1_transition_transition_ribbon_clearance_gmp import (
    cross3,
    subtract,
    triangles_intersect,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v5_receipt.json"
MATRIX = ROOT / "audit/t73_x_m1_outer_collar_v5_ribbon_candidate_matrix.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v5_ribbon_clearance.json"
SLOPE = 1_000_033
FUNCTIONAL_Z = 2
TYPE_NAMES = (
    "retained_source_germ",
    "start_skew_lift",
    "first_exterior_ray",
    "staggered_height_bridge",
    "staggered_last_exterior_ray",
    "end_skew_lift",
)
ZERO = (mpq(0), mpq(0), mpq(0))


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
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


def point(value):
    return tuple(mpq(coordinate) for coordinate in value)


def functional(value):
    return value[1] - SLOPE * value[0] + FUNCTIONAL_Z * value[2]


def dot(first, second):
    return sum(a * b for a, b in zip(first, second))


def load(receipt):
    groups = defaultdict(list)
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            core = [point(value) for value in record["final_core_vertices"]]
            push = [point(value) for value in record["final_push_vertices"]]
            vertices = core + push
            size = len(core)
            for segment_type in range(size - 1):
                quad = (
                    core[segment_type],
                    core[segment_type + 1],
                    push[segment_type + 1],
                    push[segment_type],
                )
                values = [functional(vertex) for vertex in quad]
                groups[segment_type].append(
                    {
                        "interface": record["interface_index"],
                        "type": segment_type,
                        "quad": quad,
                        "bounds": exact_bounds(quad),
                        "f_low": min(values),
                        "f_high": max(values),
                        "triangles": tuple(
                            tuple(vertices[index] for index in ids)
                            for ids in record["final_ribbon_triangles"][
                                2 * segment_type : 2 * segment_type + 2
                            ]
                        ),
                    }
                )
    return groups


def interval_candidates(first_group, second_group, symmetric):
    ordered = sorted(second_group, key=lambda record: record["f_low"])
    lows = [record["f_low"] for record in ordered]
    for first in first_group:
        stop = bisect.bisect_right(lows, first["f_high"])
        for second in ordered[:stop]:
            if second["f_high"] < first["f_low"]:
                continue
            if symmetric and second["interface"] >= first["interface"]:
                continue
            yield first, second


def local_adjacency(first, second):
    return (
        first["interface"] == second["interface"]
        and abs(first["type"] - second["type"]) == 1
    )


def skew_axis_separates(first, second):
    first_tangent = subtract(first["quad"][1], first["quad"][0])
    second_tangent = subtract(second["quad"][1], second["quad"][0])
    axis = cross3(first_tangent, second_tangent)
    if axis == ZERO:
        return False
    first_values = [dot(axis, vertex) for vertex in first["quad"]]
    second_values = [dot(axis, vertex) for vertex in second["quad"]]
    return max(first_values) < min(second_values) or max(second_values) < min(
        first_values
    )


def check_pair(pair, groups, broad):
    first_type, second_type = pair
    candidates = interval_candidates(
        groups[first_type], groups[second_type], first_type == second_type
    )
    interval_overlaps = adjacency_skips = bounds_rejects = skew_rejects = (
        exact_triangles
    ) = 0
    for first, second in candidates:
        interval_overlaps += 1
        if local_adjacency(first, second):
            adjacency_skips += 1
            continue
        if not overlap(first["bounds"], second["bounds"]):
            bounds_rejects += 1
            continue
        if skew_axis_separates(first, second):
            skew_rejects += 1
            continue
        for first_local, first_triangle in enumerate(first["triangles"]):
            for second_local, second_triangle in enumerate(second["triangles"]):
                exact_triangles += 1
                if triangles_intersect(first_triangle, second_triangle):
                    witness = triangle_intersection_witness(
                        first_triangle, second_triangle
                    )
                    if witness is None:
                        raise AssertionError(
                            "v5 ribbon collision lacks a noncoplanar exact witness"
                        )
                    return {
                        "status": "REFUTED",
                        "pair": f"{TYPE_NAMES[first_type]}/{TYPE_NAMES[second_type]}",
                        "first": [first["interface"], first_type, first_local],
                        "second": [second["interface"], second_type, second_local],
                        "witness": witness,
                        "functional_interval_overlaps_before_collision": interval_overlaps,
                        "exact_triangle_checks_before_collision": exact_triangles,
                    }
    return {
        "status": "PASS",
        "pair": f"{TYPE_NAMES[first_type]}/{TYPE_NAMES[second_type]}",
        "broad_aabb_nonincident_candidates": broad,
        "global_exact_functional_interval_overlaps": interval_overlaps,
        "declared_local_adjacencies": adjacency_skips,
        "exact_bounds_rejects": bounds_rejects,
        "exact_skew_axis_rejects": skew_rejects,
        "exact_triangle_pair_checks": exact_triangles,
        "intersections": 0,
    }


def build():
    collars = json.loads(COLLARS.read_text())
    matrix = json.loads(MATRIX.read_text())
    if matrix["outer_collars_v5_receipt_sha256"] != collars["sha256"]:
        raise AssertionError("v5 ribbon matrix is stale")
    groups = load(collars)
    name_to_type = {name: index for index, name in enumerate(TYPE_NAMES)}
    results = []
    for name, broad in matrix["nonincident_candidate_matrix"].items():
        pair = tuple(name_to_type[value] for value in name.split("/"))
        result = check_pair(pair, groups, broad)
        results.append(result)
        if result["status"] != "PASS":
            output = {
                "schema": "t73_x_m1_outer_collar_v5_ribbon_clearance/v1",
                "outer_collars_v5_receipt_sha256": collars["sha256"],
                "v5_ribbon_candidate_matrix_sha256": matrix["sha256"],
                "completed_type_pair_results_before_collision": results[:-1],
                "collision": result,
                "global_ribbon_clearance": False,
                "classification": "CANDIDATE_REFUTED",
                "verdict": "REFUTED_X_M1_OUTER_COLLAR_V5_RIBBON_CLEARANCE",
            }
            output["sha256"] = canonical_sha(output)
            return output
    if {result["pair"] for result in results} != set(
        matrix["nonincident_candidate_matrix"]
    ):
        raise AssertionError("v5 ribbon proof does not consume the complete matrix")
    output = {
        "schema": "t73_x_m1_outer_collar_v5_ribbon_clearance/v1",
        "outer_collars_v5_receipt_sha256": collars["sha256"],
        "v5_ribbon_candidate_matrix_sha256": matrix["sha256"],
        "rectangle_count": matrix["rectangle_count"],
        "ribbon_triangle_count": matrix["ribbon_triangle_count"],
        "local_star_count": matrix["local_star_count"],
        "nonincident_type_pair_results": results,
        "covered_nonincident_type_pair_count": len(results),
        "broad_aabb_nonincident_candidate_count": matrix["nonincident_candidate_count"],
        "global_functional_interval_overlap_count": sum(
            item["global_exact_functional_interval_overlaps"] for item in results
        ),
        "declared_local_adjacency_count": sum(
            item["declared_local_adjacencies"] for item in results
        ),
        "exact_bounds_reject_count": sum(
            item["exact_bounds_rejects"] for item in results
        ),
        "exact_skew_axis_reject_count": sum(
            item["exact_skew_axis_rejects"] for item in results
        ),
        "exact_triangle_pair_check_count": sum(
            item["exact_triangle_pair_checks"] for item in results
        ),
        "intersection_count": 0,
        "global_ribbon_clearance": True,
        "classification": "GLOBALLY_EMBEDDED_RIBBON_SYSTEM",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V5_RIBBON_CLEARANCE",
    }
    output["sha256"] = canonical_sha(output)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("v5 ribbon clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "collision": result.get("collision"),
                "type_pairs": result.get("covered_nonincident_type_pair_count"),
                "broad": result.get("broad_aabb_nonincident_candidate_count"),
                "f_overlaps": result.get("global_functional_interval_overlap_count"),
                "exact_triangles": result.get("exact_triangle_pair_check_count"),
                "intersections": result.get("intersection_count"),
            },
            sort_keys=True,
        )
    )
    if result["verdict"].startswith("REFUTED"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
