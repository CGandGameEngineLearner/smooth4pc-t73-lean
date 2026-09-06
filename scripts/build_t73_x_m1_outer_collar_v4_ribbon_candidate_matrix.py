#!/usr/bin/env python3
"""Build V4 ribbon-rectangle candidates and verify every local framing star."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from itertools import pairwise
from pathlib import Path

from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v2_ribbon_self_clearance import (
    exact_bounds,
    float_bounds,
    point,
    star_relation,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v4_receipt.json"
ONE_SKELETON = ROOT / "audit/t73_x_m1_outer_collar_v4_core_push_clearance.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v4_ribbon_candidate_matrix.json"
TYPE_NAMES = (
    "retained_source_germ",
    "start_skew_lift",
    "first_exterior_ray",
    "staggered_height_bridge",
    "staggered_last_exterior_ray",
    "end_skew_lift",
)


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


def load(receipt):
    rectangles = []
    by_interface = defaultdict(list)
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            core = [point(vertex) for vertex in record["final_core_vertices"]]
            push = [point(vertex) for vertex in record["final_push_vertices"]]
            vertices = core + push
            size = len(core)
            for local in range(size - 1):
                rectangle = {
                    "interface": record["interface_index"],
                    "neighbor_id": record["neighbor_id"],
                    "type": local,
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
                        for ids in record["final_ribbon_triangles"][
                            2 * local : 2 * local + 2
                        ]
                    ),
                }
                rectangles.append(rectangle)
                by_interface[record["interface_index"]].append(rectangle)
    return rectangles, by_interface


def dot(first, second):
    return sum(a * b for a, b in zip(first, second))


def same_side_certificate(first, second, edge):
    from verify_t73_x_m1_transition_transition_ribbon_clearance_gmp import (
        cross3,
        subtract,
    )

    a, b = edge

    def normal(rectangle):
        triangle = next(
            triangle
            for triangle in rectangle["triangles"]
            if a in triangle and b in triangle
        )
        third = next(vertex for vertex in triangle if vertex not in edge)
        return cross3(subtract(b, a), subtract(third, a))

    first_normal, second_normal = normal(first), normal(second)
    return {
        "shared_edge": [[str(value) for value in vertex] for vertex in edge],
        "first_star_normal": [str(value) for value in first_normal],
        "second_star_normal": [str(value) for value in second_normal],
        "normal_cross_is_zero": cross3(first_normal, second_normal) == (0, 0, 0),
        "normal_dot": str(dot(first_normal, second_normal)),
        "normal_dot_is_positive": dot(first_normal, second_normal) > 0,
    }


def build(
    collars_path=COLLARS,
    one_skeleton_path=ONE_SKELETON,
    version="v4",
):
    collars = json.loads(collars_path.read_text())
    one_skeleton = json.loads(one_skeleton_path.read_text())
    if (
        one_skeleton[f"outer_collars_{version}_receipt_sha256"] != collars["sha256"]
        or not one_skeleton["global_core_push_clearance"]
    ):
        raise AssertionError("v4 mutual one-skeleton clearance is stale or failed")
    rectangles, by_interface = load(collars)
    if len(rectangles) != 18_156:
        raise AssertionError("v4 ribbon rectangle inventory changed")

    star_counts = Counter()
    for interface, values in by_interface.items():
        if len(values) != 6:
            raise AssertionError(
                f"v4 interface {interface} does not have six rectangles"
            )
        for first, second in pairwise(values):
            edge = tuple(set(first["quad"]) & set(second["quad"]))
            if len(edge) != 2:
                raise AssertionError(
                    "successive v4 rectangles do not share one framing edge"
                )
            relation = star_relation(first, second, edge)
            star_counts[f"same_interface/{relation}"] += 1
            if relation == "COPLANAR_SAME_SIDE_OVERLAP":
                result = {
                    "schema": f"t73_x_m1_outer_collar_{version}_ribbon_candidate_matrix/v1",
                    f"outer_collars_{version}_receipt_sha256": collars["sha256"],
                    f"{version}_core_push_clearance_sha256": one_skeleton["sha256"],
                    "collision": {
                        "kind": relation,
                        "interface": interface,
                        "first_type": TYPE_NAMES[first["type"]],
                        "second_type": TYPE_NAMES[second["type"]],
                        "certificate": same_side_certificate(first, second, edge),
                    },
                    "global_ribbon_clearance": False,
                    "classification": "CANDIDATE_REFUTED",
                    "verdict": f"REFUTED_X_M1_OUTER_COLLAR_{version.upper()}_RIBBON_LOCAL_STAR",
                }
                result["sha256"] = canonical_sha(result)
                return result
    germ_groups = defaultdict(list)
    for rectangle in rectangles:
        if rectangle["type"] == 0:
            germ_groups[(rectangle["neighbor_id"], rectangle["inner_edge"])].append(
                rectangle
            )
    dual_pairs = 0
    for values in germ_groups.values():
        if len(values) == 1:
            continue
        if len(values) != 2:
            raise AssertionError("unexpected multiplicity at shared source germ")
        edge = tuple(set(values[0]["quad"]) & set(values[1]["quad"]))
        relation = star_relation(values[0], values[1], edge)
        star_counts[f"shared_dual_germ/{relation}"] += 1
        dual_pairs += 1
        if relation == "COPLANAR_SAME_SIDE_OVERLAP":
            raise AssertionError("v4 shared dual source germs fold to the same side")
    if dual_pairs != 4:
        raise AssertionError("v4 shared dual germ pair count changed")

    bounds = [exact_bounds(rectangle["quad"]) for rectangle in rectangles]
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        ((index, float_bounds(value), None) for index, value in enumerate(bounds)),
        properties=properties,
    )
    matrix = Counter()
    broad = local_adjacencies = 0
    for first_index, first in enumerate(rectangles):
        for second_index in tree.intersection(float_bounds(bounds[first_index])):
            if second_index >= first_index:
                continue
            broad += 1
            second = rectangles[second_index]
            same_interface_adjacent = (
                first["interface"] == second["interface"]
                and abs(first["type"] - second["type"]) == 1
            )
            shared_dual_germ = (
                first["type"] == second["type"] == 0
                and first["neighbor_id"] == second["neighbor_id"]
                and first["inner_edge"] == second["inner_edge"]
            )
            if same_interface_adjacent or shared_dual_germ:
                local_adjacencies += 1
                continue
            matrix[tuple(sorted((first["type"], second["type"])))] += 1
    result = {
        "schema": f"t73_x_m1_outer_collar_{version}_ribbon_candidate_matrix/v1",
        f"outer_collars_{version}_receipt_sha256": collars["sha256"],
        f"{version}_core_push_clearance_sha256": one_skeleton["sha256"],
        "collar_count": collars["collar_count"],
        "rectangle_count": len(rectangles),
        "ribbon_triangle_count": 2 * len(rectangles),
        "local_star_relation_counts": dict(sorted(star_counts.items())),
        "local_star_count": sum(star_counts.values()),
        "expanded_3d_aabb_rectangle_pair_count": broad,
        "declared_local_adjacency_pair_count": local_adjacencies,
        "nonincident_candidate_matrix": {
            f"{TYPE_NAMES[first]}/{TYPE_NAMES[second]}": count
            for (first, second), count in sorted(matrix.items())
        },
        "nonincident_candidate_count": sum(matrix.values()),
        "nonempty_nonincident_type_pair_count": len(matrix),
        "clearance_status": "OPEN_APPLY_EXACT_RULED_RECTANGLE_SEPARATION",
        "verdict": f"PASS_X_M1_OUTER_COLLAR_{version.upper()}_RIBBON_CANDIDATE_MATRIX_AND_LOCAL_STARS_ONLY",
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
        raise AssertionError("v4 ribbon candidate matrix is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "collision": result.get("collision"),
                "rectangles": result.get("rectangle_count"),
                "nonincident": result.get("nonincident_candidate_count"),
                "clearance": result.get("clearance_status"),
            },
            sort_keys=True,
        )
    )
    if result["verdict"].startswith("REFUTED"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
