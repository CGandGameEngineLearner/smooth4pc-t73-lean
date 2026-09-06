#!/usr/bin/env python3
"""Exact rectangle-level ribbon self-clearance for source-germ collars v2."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import sys
from collections import Counter
from pathlib import Path

from gmpy2 import mpq
from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from verify_t73_x_m1_transition_transition_ribbon_clearance_gmp import (
    cross3,
    det,
    subtract,
    triangles_intersect,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v2_receipt.json"
CORE_PUSH = ROOT / "audit/t73_x_m1_outer_collar_v2_core_push_clearance.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v2_ribbon_self_clearance.json"
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
    rectangles = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            value = json.loads(line)
            core = [point(vertex) for vertex in value["final_core_vertices"]]
            push = [point(vertex) for vertex in value["final_push_vertices"]]
            vertices = core + push
            for local in range(2):
                triangle_ids = value["final_ribbon_triangles"][
                    2 * local : 2 * local + 2
                ]
                rectangles.append(
                    {
                        "interface": value["interface_index"],
                        "neighbor_id": value["neighbor_id"],
                        "local": local,
                        "inner_edge": (core[local], push[local]),
                        "target_edge": (core[local + 1], push[local + 1]),
                        "quad": (
                            core[local],
                            core[local + 1],
                            push[local + 1],
                            push[local],
                        ),
                        "triangles": tuple(
                            tuple(vertices[index] for index in ids)
                            for ids in triangle_ids
                        ),
                    }
                )
    return rectangles


def shared_edge(first, second):
    shared = set(first["quad"]) & set(second["quad"])
    return tuple(shared) if len(shared) == 2 else None


def permitted_neighbors(first, second, edge):
    if edge is None:
        return False
    if first["interface"] == second["interface"]:
        return abs(first["local"] - second["local"]) == 1
    return (
        first["neighbor_id"] == second["neighbor_id"]
        and first["local"] == second["local"] == 0
        and first["inner_edge"] == second["inner_edge"]
    )


def star_relation(first, second, edge):
    a, b = edge

    def edge_triangle(rectangle):
        matches = [
            triangle
            for triangle in rectangle["triangles"]
            if a in triangle and b in triangle
        ]
        if len(matches) != 1:
            raise AssertionError(
                "framing edge is not contained in exactly one triangle"
            )
        return matches[0]

    first_triangle, second_triangle = edge_triangle(first), edge_triangle(second)
    first_third = next(vertex for vertex in first_triangle if vertex not in edge)
    second_third = next(vertex for vertex in second_triangle if vertex not in edge)
    direction = subtract(b, a)
    first_normal = cross3(direction, subtract(first_third, a))
    second_normal = cross3(direction, subtract(second_third, a))
    if first_normal == ZERO or second_normal == ZERO:
        raise AssertionError("local ribbon star triangle degenerates")
    if cross3(first_normal, second_normal) != ZERO:
        return "TRANSVERSE_PLANES"
    sign = dot(first_normal, second_normal)
    if sign < 0:
        return "COPLANAR_OPPOSITE_SIDES"
    if sign > 0:
        return "COPLANAR_SAME_SIDE_OVERLAP"
    raise AssertionError("local ribbon star normals have indeterminate sign")


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


def segment_triangle_witness(segment, triangle):
    start, end = segment
    a, b, c = triangle
    direction = subtract(end, start)
    first_edge = subtract(b, a)
    second_edge = subtract(c, a)
    right = subtract(a, start)
    minus_first = tuple(-value for value in first_edge)
    minus_second = tuple(-value for value in second_edge)
    denominator = det(direction, minus_first, minus_second)
    if not denominator:
        return None
    parameter = det(right, minus_first, minus_second) / denominator
    alpha = det(direction, right, minus_second) / denominator
    beta = det(direction, minus_first, right) / denominator
    if 0 <= parameter <= 1 and alpha >= 0 and beta >= 0 and alpha + beta <= 1:
        witness = tuple(start[axis] + parameter * direction[axis] for axis in range(3))
        return witness, parameter, alpha, beta
    return None


def triangle_intersection_witness(first, second):
    for source, target, source_name in (
        (first, second, "first_edge"),
        (second, first, "second_edge"),
    ):
        for edge_index in range(3):
            result = segment_triangle_witness(
                (source[edge_index], source[(edge_index + 1) % 3]), target
            )
            if result:
                point_value, parameter, alpha, beta = result
                return {
                    "source": source_name,
                    "edge_index": edge_index,
                    "point": [str(value) for value in point_value],
                    "edge_parameter": str(parameter),
                    "triangle_alpha": str(alpha),
                    "triangle_beta": str(beta),
                }
    return None


def build():
    collars = json.loads(COLLARS.read_text())
    core_push = json.loads(CORE_PUSH.read_text())
    if (
        core_push["outer_collars_v2_receipt_sha256"] != collars["sha256"]
        or not core_push["global_core_push_clearance"]
    ):
        raise AssertionError("v2 collar core/push clearance is stale or failed")
    rectangles = load(collars)
    bounds = [exact_bounds(rectangle["quad"]) for rectangle in rectangles]
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        ((index, float_bounds(value), None) for index, value in enumerate(bounds)),
        properties=properties,
    )
    broad = bounds_rejects = skew_rejects = exact_triangles = 0
    star_counts = Counter()
    for first_index, first in enumerate(rectangles):
        candidates = [
            index
            for index in tree.intersection(float_bounds(bounds[first_index]))
            if index < first_index
        ]
        broad += len(candidates)
        if os.environ.get("T73_PROGRESS") and first_index % 500 == 0:
            print(
                f"v2 ribbon rectangles {first_index}/{len(rectangles)} broad={broad} exact={exact_triangles}",
                file=sys.stderr,
                flush=True,
            )
        for second_index in candidates:
            if not overlap(bounds[first_index], bounds[second_index]):
                bounds_rejects += 1
                continue
            second = rectangles[second_index]
            edge = shared_edge(first, second)
            if permitted_neighbors(first, second, edge):
                relation = star_relation(first, second, edge)
                star_counts[relation] += 1
                if relation == "COPLANAR_SAME_SIDE_OVERLAP":
                    result = {
                        "schema": "t73_x_m1_outer_collar_v2_ribbon_self_clearance/v1",
                        "outer_collars_v2_receipt_sha256": collars["sha256"],
                        "outer_collars_v2_core_push_clearance_sha256": core_push[
                            "sha256"
                        ],
                        "collision": {
                            "first_rectangle": first_index,
                            "second_rectangle": second_index,
                            "kind": relation,
                        },
                        "global_ribbon_self_clearance": False,
                        "classification": "CANDIDATE_REFUTED",
                        "verdict": "REFUTED_X_M1_OUTER_COLLAR_V2_RIBBON_SELF_CLEARANCE",
                    }
                    result["sha256"] = canonical_sha(result)
                    return result
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
                                "nonincident ribbon collision lacks a noncoplanar witness"
                            )
                        result = {
                            "schema": "t73_x_m1_outer_collar_v2_ribbon_self_clearance/v1",
                            "outer_collars_v2_receipt_sha256": collars["sha256"],
                            "outer_collars_v2_core_push_clearance_sha256": core_push[
                                "sha256"
                            ],
                            "collision": {
                                "first_rectangle": first_index,
                                "first_triangle": first_local,
                                "second_rectangle": second_index,
                                "second_triangle": second_local,
                                "kind": "NONINCIDENT_TRIANGLE_INTERSECTION",
                                "witness": witness,
                            },
                            "global_ribbon_self_clearance": False,
                            "classification": "CANDIDATE_REFUTED",
                            "verdict": "REFUTED_X_M1_OUTER_COLLAR_V2_RIBBON_SELF_CLEARANCE",
                        }
                        result["sha256"] = canonical_sha(result)
                        return result
    result = {
        "schema": "t73_x_m1_outer_collar_v2_ribbon_self_clearance/v1",
        "outer_collars_v2_receipt_sha256": collars["sha256"],
        "outer_collars_v2_core_push_clearance_sha256": core_push["sha256"],
        "collar_count": collars["collar_count"],
        "rectangle_count": len(rectangles),
        "ribbon_triangle_count": 2 * len(rectangles),
        "expanded_3d_aabb_rectangle_candidate_count": broad,
        "exact_bounds_reject_count": bounds_rejects,
        "local_star_relation_counts": dict(sorted(star_counts.items())),
        "exact_skew_axis_rectangle_reject_count": skew_rejects,
        "exact_nonincident_triangle_check_count": exact_triangles,
        "intersection_count": 0,
        "global_ribbon_self_clearance": True,
        "classification": "SELF_CLEAR_ACTUAL_RIBBON_SYSTEM",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V2_RIBBON_SELF_CLEARANCE",
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
        raise AssertionError("v2 outer collar ribbon self-clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "collision": result.get("collision"),
                "star_relations": result.get("local_star_relation_counts"),
                "exact_checks": result.get("exact_nonincident_triangle_check_count"),
            },
            sort_keys=True,
        )
    )
    if result["verdict"].startswith("REFUTED"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
