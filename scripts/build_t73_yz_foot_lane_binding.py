#!/usr/bin/env python3
"""Bind the actual Johnson y/z handle arcs to the Figure-2a foot reflections."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEET = ROOT / "geometry/t73_ar_foot_pairing_model.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
X_DELETION = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"
OUTPUT = ROOT / "geometry/t73_yz_foot_lane_binding.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def add(left, right):
    return tuple(left[index] + right[index] for index in range(3))


def scale(value, vector):
    return tuple(value * coordinate for coordinate in vector)


def matrix_apply(matrix, value):
    return tuple(
        sum(Fraction(entry) * coordinate for entry, coordinate in zip(row, value))
        for row in matrix
    )


def cube_triangles():
    triangles = []
    for bit in range(3):
        for value in (0, 1):
            vertices = sorted(
                index for index in range(8) if ((index >> (2 - bit)) & 1) == value
            )
            first, second, third, fourth = vertices
            triangles.extend([[first, second, fourth], [first, third, fourth]])
    return triangles


def handle_record(name, axis, foot, arcs, tangent_basis):
    positive_center = point(foot["positive_center"])
    negative_center = point(foot["negative_center"])
    radius = Fraction(foot["radius"])
    lane_scale = radius / 10
    transverse_axes = [value for value in range(3) if value != axis]
    passages = []
    for arc in arcs:
        polyline = [point(value) for value in arc["lift_polyline"]]
        if polyline[1][axis] != 2:
            raise AssertionError(f"{arc['arc_id']}: misses its {name} belt slice")
        lane = tuple(polyline[1][value] for value in transverse_axes)
        offset = add(
            scale(lane_scale * lane[0], tangent_basis[0]),
            scale(lane_scale * lane[1], tangent_basis[1]),
        )
        positive = add(positive_center, offset)
        negative = add(negative_center, offset)
        if sum(value * value for value in offset) >= radius * radius:
            raise AssertionError(f"{arc['arc_id']}: foot endpoint leaves its disk")
        if matrix_apply(foot["reflection_matrix"], positive) != negative:
            raise AssertionError(f"{arc['arc_id']}: foot reflection pairing failed")
        passages.append({
            "arc_id": arc["arc_id"],
            "component": arc["component"],
            "orientation": arc["sign"],
            "belt_point": encode((*lane, Fraction(1))),
            "negative_foot_endpoint": encode(negative),
            "positive_foot_endpoint": encode(positive),
            "source_axis_endpoints": [encode(polyline[0]), encode(polyline[-1])],
        })
    belt_vertices = []
    for index in range(8):
        transverse = [Fraction(-1 if ((index >> (2 - bit)) & 1) == 0 else 1) for bit in range(3)]
        value = [None, None, None, None]
        value[axis] = Fraction(2)
        for coordinate_axis, coordinate in zip(transverse_axes, transverse[:2]):
            value[coordinate_axis] = coordinate
        value[3] = transverse[2]
        belt_vertices.append(tuple(value))
    return {
        "name": name,
        "generator_axis": axis,
        "foot_handle_index": foot["handle_index"],
        "foot_pair_sha256": canonical_sha(foot),
        "tangent_basis": [encode(value) for value in tangent_basis],
        "lane_scale": str(lane_scale),
        "belt_sphere": {
            "chart": f"axis {axis}=2, boundary of transverse cube",
            "vertices": [encode(value) for value in belt_vertices],
            "triangles": cube_triangles(),
            "euler": 2,
        },
        "passages": passages,
        "passage_count": len(passages),
        "binding_status": "ACTUAL_JOHNSON_BASE_LANES_BOUND_TO_FIGURE2A_FEET",
    }


def build() -> dict:
    feet = json.loads(FEET.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    x_deletion = json.loads(X_DELETION.read_text(encoding="utf-8"))
    foot_by_index = {item["handle_index"]: item for item in feet["feet"]}
    arcs_by_axis = {
        axis: [item for item in spine["handle_arcs"] if item["axis"] == axis]
        for axis in (1, 2)
    }
    handles = [
        handle_record(
            "y",
            1,
            foot_by_index[2],
            arcs_by_axis[1],
            ((Fraction(1), Fraction(0), Fraction(0)), (Fraction(0), Fraction(1), Fraction(0))),
        ),
        handle_record(
            "z",
            2,
            foot_by_index[3],
            arcs_by_axis[2],
            ((Fraction(2), Fraction(-1), Fraction(0)), (Fraction(0), Fraction(1), Fraction(-1))),
        ),
    ]
    if [item["passage_count"] for item in handles] != [230, 33]:
        raise AssertionError("unexpected Johnson y/z passage counts")
    result = {
        "schema": "t73_yz_foot_lane_binding/v1",
        "ar_foot_model_sha256": feet["sha256"],
        "johnson_spine_embedding_sha256": spine["sha256"],
        "post_x_m1_deletion_sha256": x_deletion["sha256"],
        "handles": handles,
        "completion_status": "YZ_JOHNSON_BASE_LANES_ACTUALLY_BOUND_HYBRID_Z_REPLACEMENTS_OPEN",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("y/z foot-lane binding is stale")
    print(f"T73_YZ_FOOT_BINDING={result['completion_status']}")


if __name__ == "__main__":
    main()
