#!/usr/bin/env python3
"""Exact rectangle-level self-clearance for all outer-collar ribbons."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import sys
from pathlib import Path

from gmpy2 import mpq
from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from verify_t73_x_m1_transition_transition_ribbon_clearance_gmp import (
    cross3,
    det,
    point_in_triangle,
    project2,
    subtract,
    triangles_intersect,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_receipt.json"
CORE_PUSH = ROOT / "audit/t73_x_m1_outer_collar_core_push_clearance_verification.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_ribbon_self_clearance.json"
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


def dot(first, second):
    return sum(a * b for a, b in zip(first, second))


def exact_bounds(vertices):
    return tuple(min(vertex[axis] for vertex in vertices) for axis in range(3)), tuple(
        max(vertex[axis] for vertex in vertices) for axis in range(3)
    )


def float_bounds(bounds):
    return tuple(
        math.nextafter(float(value), -math.inf) for value in bounds[0]
    ) + tuple(math.nextafter(float(value), math.inf) for value in bounds[1])


def overlap(first, second):
    return all(
        first[0][axis] <= second[1][axis] and second[0][axis] <= first[1][axis]
        for axis in range(3)
    )


def load(receipt):
    records = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            value = json.loads(line)
            core = [point(vertex) for vertex in value["final_core_vertices"]]
            push = [point(vertex) for vertex in value["final_push_vertices"]]
            vertices = core + push
            records.append(
                {
                    "interface": value["interface_index"],
                    "neighbor_id": value["neighbor_id"],
                    "inner_edge": (core[0], push[0]),
                    "target_edge": (core[1], push[1]),
                    "quad": (core[0], core[1], push[1], push[0]),
                    "triangles": tuple(
                        tuple(vertices[index] for index in indices)
                        for indices in value["final_ribbon_triangles"]
                    ),
                }
            )
    return records


def adjacent_records(first, second):
    return (
        first["neighbor_id"] == second["neighbor_id"]
        and first["inner_edge"] == second["inner_edge"]
    )


def verify_adjacent_star(first, second):
    edge = subtract(first["inner_edge"][1], first["inner_edge"][0])
    first_ray = subtract(first["target_edge"][1], first["inner_edge"][0])
    second_ray = subtract(second["target_edge"][1], second["inner_edge"][0])
    if det(edge, first_ray, second_ray) == 0:
        return False
    if cross3(edge, first_ray) == ZERO or cross3(edge, second_ray) == ZERO:
        raise AssertionError("adjacent collar ribbon degenerates at shared edge")
    return True


def triangle_contains(point_value, triangle):
    normal = cross3(
        subtract(triangle[1], triangle[0]),
        subtract(triangle[2], triangle[0]),
    )
    if dot(normal, subtract(point_value, triangle[0])):
        return False
    drop = max(range(3), key=lambda axis: abs(normal[axis]))
    projected = tuple(project2(vertex, drop) for vertex in triangle)
    return point_in_triangle(project2(point_value, drop), projected)


def interior_overlap_witness(first, second):
    inner_core, inner_push = first["inner_edge"]
    first_target_push = first["target_edge"][1]
    second_target_push = second["target_edge"][1]
    for exponent in range(1, 13):
        parameter = mpq(1, 10**exponent)
        first_boundary = tuple(
            (1 - parameter) * inner_core[axis] + parameter * first_target_push[axis]
            for axis in range(3)
        )
        second_boundary = tuple(
            (1 - parameter) * inner_push[axis] + parameter * second_target_push[axis]
            for axis in range(3)
        )
        witness = tuple(
            (first_boundary[axis] + second_boundary[axis]) / 2 for axis in range(3)
        )
        if (
            triangle_contains(witness, first["triangles"][1])
            and triangle_contains(witness, second["triangles"][1])
            and cross3(subtract(witness, inner_core), subtract(inner_push, inner_core))
            != ZERO
        ):
            return witness, exponent
    return None


def skew_axis_separates(first, second):
    first_tangent = subtract(first["target_edge"][0], first["inner_edge"][0])
    second_tangent = subtract(second["target_edge"][0], second["inner_edge"][0])
    axis = cross3(first_tangent, second_tangent)
    if axis == ZERO:
        return False
    first_values = [dot(axis, vertex) for vertex in first["quad"]]
    second_values = [dot(axis, vertex) for vertex in second["quad"]]
    return max(first_values) < min(second_values) or max(second_values) < min(
        first_values
    )


def build():
    collars = json.loads(COLLARS.read_text())
    core_push = json.loads(CORE_PUSH.read_text())
    if core_push["outer_collar_receipt_sha256"] != collars["sha256"]:
        raise AssertionError("collar core/push clearance is stale")
    records = load(collars)
    bounds = [exact_bounds(record["quad"]) for record in records]
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        ((index, float_bounds(value), None) for index, value in enumerate(bounds)),
        properties=properties,
    )
    broad = bounds_rejects = adjacent_star_pairs = skew_axis_rejects = 0
    exact_triangle_checks = 0
    for first_index, first in enumerate(records):
        candidates = [
            index
            for index in tree.intersection(float_bounds(bounds[first_index]))
            if index < first_index
        ]
        broad += len(candidates)
        if os.environ.get("T73_PROGRESS") and first_index % 250 == 0:
            print(
                f"collar quads {first_index}/{len(records)} broad={broad} exact_triangles={exact_triangle_checks}",
                file=sys.stderr,
                flush=True,
            )
        for second_index in candidates:
            if not overlap(bounds[first_index], bounds[second_index]):
                bounds_rejects += 1
                continue
            second = records[second_index]
            if adjacent_records(first, second):
                if not verify_adjacent_star(first, second):
                    witness = interior_overlap_witness(first, second)
                    if witness is None:
                        raise AssertionError(
                            "coplanar adjacent star lacks an exact overlap witness"
                        )
                    point_value, exponent = witness
                    result = {
                        "schema": "t73_x_m1_outer_collar_ribbon_self_clearance/v1",
                        "outer_collars_receipt_sha256": collars["sha256"],
                        "outer_collar_core_push_clearance_sha256": core_push["sha256"],
                        "collision": {
                            "kind": "COPLANAR_ADJACENT_DUAL_RIBBON_POSITIVE_AREA_OVERLAP",
                            "first_interface": first_index,
                            "second_interface": second_index,
                            "shared_neighbor_id": first["neighbor_id"],
                            "witness": [str(value) for value in point_value],
                            "witness_cross_section_parameter": f"1/10^{exponent}",
                            "witness_is_off_shared_inner_edge": True,
                            "witness_in_both_second_triangles": True,
                        },
                        "expanded_3d_aabb_rectangle_candidates_before_collision": broad,
                        "exact_skew_axis_rectangle_rejects_before_collision": skew_axis_rejects,
                        "global_ribbon_self_clearance": False,
                        "classification": "CANDIDATE_REFUTED",
                        "verdict": "REFUTED_X_M1_OUTER_COLLAR_RIBBON_SELF_CLEARANCE",
                    }
                    result["sha256"] = canonical_sha(result)
                    return result
                adjacent_star_pairs += 1
                continue
            if skew_axis_separates(first, second):
                skew_axis_rejects += 1
                continue
            for first_local, first_triangle in enumerate(first["triangles"]):
                for second_local, second_triangle in enumerate(second["triangles"]):
                    exact_triangle_checks += 1
                    if triangles_intersect(first_triangle, second_triangle):
                        result = {
                            "schema": "t73_x_m1_outer_collar_ribbon_self_clearance/v1",
                            "outer_collars_receipt_sha256": collars["sha256"],
                            "outer_collar_core_push_clearance_sha256": core_push[
                                "sha256"
                            ],
                            "collision": {
                                "first": [first_index, first_local],
                                "second": [second_index, second_local],
                            },
                            "exact_checks_before_collision": exact_triangle_checks,
                            "global_ribbon_self_clearance": False,
                            "classification": "CANDIDATE_REFUTED",
                            "verdict": "REFUTED_X_M1_OUTER_COLLAR_RIBBON_SELF_CLEARANCE",
                        }
                        result["sha256"] = canonical_sha(result)
                        return result
    result = {
        "schema": "t73_x_m1_outer_collar_ribbon_self_clearance/v1",
        "outer_collars_receipt_sha256": collars["sha256"],
        "outer_collar_core_push_clearance_sha256": core_push["sha256"],
        "collar_count": len(records),
        "ribbon_triangle_count": 2 * len(records),
        "expanded_3d_aabb_rectangle_candidate_count": broad,
        "exact_bounds_reject_count": bounds_rejects,
        "same_collar_triangle_incidence_count": len(records),
        "adjacent_dual_local_star_count": adjacent_star_pairs,
        "exact_skew_axis_rectangle_reject_count": skew_axis_rejects,
        "exact_nonincident_triangle_check_count": exact_triangle_checks,
        "intersection_count": 0,
        "global_ribbon_self_clearance": True,
        "classification": "SELF_CLEAR_ACTUAL_RIBBON_SYSTEM",
        "verdict": "PASS_X_M1_OUTER_COLLAR_RIBBON_SELF_CLEARANCE",
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
        raise AssertionError("outer collar ribbon self-clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "collision": result.get("collision"),
                "exact_checks": result.get(
                    "exact_nonincident_triangle_check_count",
                    result.get("exact_checks_before_collision"),
                ),
            },
            sort_keys=True,
        )
    )
    if result["verdict"].startswith("REFUTED"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
