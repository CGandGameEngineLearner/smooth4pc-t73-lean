#!/usr/bin/env python3
"""Exact V7 collar/retained-source ruled-ribbon cross-clearance."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v2_ribbon_self_clearance import (
    triangle_intersection_witness,
)
from build_t73_x_m1_outer_collar_v7_retained_ribbon_candidate_matrix import (
    AR_LINK,
    COLLARS,
    GAP,
    PASSAGES,
    SPINE,
    float_bounds,
    load_collars,
    load_retained,
)
from verify_t73_x_m1_transition_transition_ribbon_clearance_gmp import (
    cross3,
    subtract,
    triangles_intersect,
)

ROOT = Path(__file__).resolve().parents[1]
CYCLES = ROOT / "geometry/t73_post_x_framed_cycle_assembly.json"
MATRIX = ROOT / "audit/t73_x_m1_outer_collar_v7_retained_ribbon_candidate_matrix.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v7_retained_ribbon_clearance.json"
ZERO = (0, 0, 0)


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def dot(first, second):
    return sum(a * b for a, b in zip(first, second))


def overlap(first, second):
    return all(
        first[0][axis] <= second[1][axis] and second[0][axis] <= first[1][axis]
        for axis in range(3)
    )


def skew_axis_separates(first, second):
    axis = cross3(
        subtract(first["quad"][1], first["quad"][0]),
        subtract(second["quad"][1], second["quad"][0]),
    )
    if axis == ZERO:
        return False
    first_values = [dot(axis, vertex) for vertex in first["quad"]]
    second_values = [dot(axis, vertex) for vertex in second["quad"]]
    return max(first_values) < min(second_values) or max(second_values) < min(
        first_values
    )


def source_adjacency(collar, retained):
    shared = set(collar["quad"]) & set(retained["quad"])
    return (
        collar["type"] == 0
        and collar["neighbor_id"] == retained["owner_id"]
        and len(shared) == 2
    )


def build():
    matrix = json.loads(MATRIX.read_text())
    collars_receipt = json.loads(COLLARS.read_text())
    gap = json.loads(GAP.read_text())
    cycles = json.loads(CYCLES.read_text())
    spine = json.loads(SPINE.read_text())
    ar_link = json.loads(AR_LINK.read_text())
    passages = json.loads(PASSAGES.read_text())
    if matrix["outer_collars_v7_receipt_sha256"] != collars_receipt["sha256"]:
        raise AssertionError("retained matrix is stale relative to V7 collars")
    collars = load_collars(collars_receipt)
    retained, removed = load_retained(gap, cycles, spine, ar_link, passages)
    if (len(collars), len(retained), removed) != (18_156, 4630, 3026):
        raise AssertionError("V7 retained cross-clearance inventory changed")
    retained_low = np.asarray([item["f_bounds"][0] for item in retained])
    retained_high = np.asarray([item["f_bounds"][1] for item in retained])
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        (
            (index, float_bounds(item["bounds"]), None)
            for index, item in enumerate(retained)
        ),
        properties=properties,
    )
    stats = Counter()
    for collar in collars:
        candidates = np.fromiter(
            tree.intersection(float_bounds(collar["bounds"])), dtype=np.int64
        )
        f_low, f_high = collar["f_bounds"]
        mask = (retained_high[candidates] >= f_low) & (
            retained_low[candidates] <= f_high
        )
        for retained_index in candidates[mask]:
            retained_rectangle = retained[int(retained_index)]
            if source_adjacency(collar, retained_rectangle):
                stats["adjacency"] += 1
                continue
            stats["float_f_candidates"] += 1
            if (
                collar["f_high"] < retained_rectangle["f_low"]
                or retained_rectangle["f_high"] < collar["f_low"]
            ):
                stats["exact_f_reject"] += 1
                continue
            if not overlap(collar["bounds"], retained_rectangle["bounds"]):
                stats["bounds_reject"] += 1
                continue
            if skew_axis_separates(collar, retained_rectangle):
                stats["skew_reject"] += 1
                continue
            for first_local, first_triangle in enumerate(collar["triangles"]):
                for second_local, second_triangle in enumerate(
                    retained_rectangle["triangles"]
                ):
                    stats["triangle_checks"] += 1
                    if triangles_intersect(first_triangle, second_triangle):
                        witness = triangle_intersection_witness(
                            first_triangle, second_triangle
                        )
                        result = {
                            "schema": "t73_x_m1_outer_collar_v7_retained_ribbon_clearance/v1",
                            "candidate_matrix_sha256": matrix["sha256"],
                            "collision": {
                                "collar": [
                                    collar["interface"],
                                    collar["type"],
                                    first_local,
                                ],
                                "retained": [
                                    retained_rectangle["kind"],
                                    retained_rectangle["owner_id"],
                                    retained_rectangle["segment"],
                                    second_local,
                                ],
                                "witness": witness,
                                "checks_before_collision": dict(stats),
                            },
                            "global_retained_cross_clearance": False,
                            "classification": "CANDIDATE_REFUTED",
                            "verdict": "REFUTED_X_M1_OUTER_COLLAR_V7_RETAINED_RIBBON_CLEARANCE",
                        }
                        result["sha256"] = canonical_sha(result)
                        return result
    result = {
        "schema": "t73_x_m1_outer_collar_v7_retained_ribbon_clearance/v1",
        "candidate_matrix_sha256": matrix["sha256"],
        "collar_rectangle_count": len(collars),
        "retained_rectangle_count": len(retained),
        "aabb_and_float_outward_f_candidates": stats["float_f_candidates"],
        "source_framing_adjacencies": stats["adjacency"],
        "exact_functional_interval_rejects": stats["exact_f_reject"],
        "exact_bounds_rejects": stats["bounds_reject"],
        "exact_skew_axis_rejects": stats["skew_reject"],
        "exact_triangle_pair_checks": stats["triangle_checks"],
        "intersection_count": 0,
        "global_retained_cross_clearance": True,
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_RETAINED_RIBBON_CLEARANCE",
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
        raise AssertionError("V7 retained ribbon clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "collision": result.get("collision"),
                "f_candidates": result.get("aabb_and_float_outward_f_candidates"),
                "skew_rejects": result.get("exact_skew_axis_rejects"),
                "triangle_checks": result.get("exact_triangle_pair_checks"),
                "intersections": result.get("intersection_count"),
            },
            sort_keys=True,
        )
    )
    if result["verdict"].startswith("REFUTED"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
