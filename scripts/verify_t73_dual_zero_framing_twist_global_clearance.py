#!/usr/bin/env python3
"""Check the three twist patches against every retained ribbon and segment."""

from __future__ import annotations

import json
import os
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from verify_t73_affine_s3_product_ribbon_clearance import (
    float_segment_plane_separated,
    float_triangle_separated,
    projected_segment_triangle_intersect,
    projected_triangles_intersect,
    segment_triangle,
    triangles_intersect,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_dual_zero_framing_twist_ribbons.json"
FRAMED_RECEIPT = ROOT / "audit/t73_affine_s3_product_framed_realization_receipt.json"
DOTTED = ROOT / "geometry/t73_actual_dotted_s3_passage_cells.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def resolve_cache_path(value: str) -> Path:
    path = Path(value)
    if path.exists() or len(value) < 3 or value[1:3] not in (":\\", ":/"):
        return path
    return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")


def exact_bounds_overlap(first, second) -> bool:
    first_low, first_high = first
    second_low, second_high = second
    return all(
        first_low[axis] <= second_high[axis]
        and second_low[axis] <= first_high[axis]
        for axis in range(3)
    )


def exact_bounds(vertices):
    return (
        tuple(min(vertex[axis] for vertex in vertices) for axis in range(3)),
        tuple(max(vertex[axis] for vertex in vertices) for axis in range(3)),
    )


def numeric_bounds(items):
    lows = np.array([
        [math_value(item[3], axis, min) for axis in range(3)] for item in items
    ])
    highs = np.array([
        [math_value(item[3], axis, max) for axis in range(3)] for item in items
    ])
    return np.nextafter(lows, -np.inf), np.nextafter(highs, np.inf)


def math_value(vertices, axis, operation):
    return float(operation(vertex[axis] for vertex in vertices))


def make_twist_triangles(data):
    triangles = []
    for component in data["components"]:
        core = [point(value) for value in component["local_core_vertices"]]
        push = [point(value) for value in component["local_push_vertices"]]
        vertices = core + push
        for index, ids in enumerate(component["local_ribbon_triangles"]):
            triangles.append((
                "twist",
                component["component"],
                index,
                tuple(vertices[item] for item in ids),
            ))
    return triangles


def make_retained_triangles(model, dotted, replaced_passages):
    triangles = []
    core_points_by_name = {
        component["component"]: [point(value) for value in component["vertices"]]
        for component in model["core_components"]
    }
    for ribbon in model["corridor_product_ribbons"]:
        component_core = core_points_by_name[ribbon["component"]]
        low, high = ribbon["core_vertex_range"]
        vertices = component_core[low:high + 1] + [
            point(value) for value in ribbon["push_vertices"]
        ]
        for index, ids in enumerate(ribbon["ribbon_triangles"]):
            triangles.append((
                "corridor",
                ribbon["component"],
                f"{ribbon['corridor_index']}:{index}",
                tuple(vertices[item] for item in ids),
            ))
    for chart in dotted["charts"]:
        for passage in chart["passages"]:
            if passage["passage_id"] in replaced_passages:
                continue
            vertices = [point(value) for value in passage["ribbon_vertices"]]
            for index, ids in enumerate(passage["ribbon_triangles"]):
                triangles.append((
                    "passage",
                    passage["owner"],
                    f"{passage['passage_id']}:{index}",
                    tuple(vertices[item] for item in ids),
                ))
    return triangles


def make_framed_segments(model, corrections):
    corrected = {component["component"]: component for component in corrections}
    segments = []
    for component in model["core_components"]:
        name = component["component"]
        values = (
            corrected[name]["corrected_core_vertices"]
            if name in corrected else component["vertices"]
        )
        vertices = [point(value) for value in values]
        segments.extend(("core", name, index, (start, end))
                        for index, (start, end) in enumerate(zip(vertices, vertices[1:])))
    for component in model["push_components"]:
        name = component["component"]
        values = (
            corrected[name]["corrected_push_vertices"]
            if name in corrected else component["vertices"]
        )
        vertices = [point(value) for value in values]
        segments.extend(("push", name, index, (start, end))
                        for index, (start, end) in enumerate(zip(vertices, vertices[1:])))
    for component in model["dotted_components"]:
        vertices = [point(value) for value in component["vertices"]]
        segments.extend(("dotted", component["component"], index, (start, end))
                        for index, (start, end) in enumerate(zip(vertices, vertices[1:])))
    return segments


def verify() -> dict:
    data = json.loads(DATA.read_text())
    framed = json.loads(FRAMED_RECEIPT.read_text())
    dotted = json.loads(DOTTED.read_text())
    model = json.loads(resolve_cache_path(framed["cache_path"]).read_text())
    if os.environ.get("T73_PROGRESS"):
        print("loaded sources", file=sys.stderr, flush=True)
    if data["affine_product_framed_receipt_sha256"] != framed["sha256"]:
        raise AssertionError("twist data is not bound to the framed model")

    local_triangles = make_twist_triangles(data)
    replaced = {component["source_passage_id"] for component in data["components"]}
    retained_triangles = make_retained_triangles(model, dotted, replaced)
    all_other_triangles = retained_triangles + local_triangles
    if os.environ.get("T73_PROGRESS"):
        print(f"assembled {len(all_other_triangles)} triangles", file=sys.stderr, flush=True)

    other_bounds = [exact_bounds(item[3]) for item in all_other_triangles]
    other_lows, other_highs = numeric_bounds(all_other_triangles)
    other_numeric = [
        np.array([[float(coordinate) for coordinate in vertex] for vertex in item[3]])
        for item in all_other_triangles
    ]
    if os.environ.get("T73_PROGRESS"):
        print("built triangle bounds", file=sys.stderr, flush=True)

    broad_triangle_pairs = incidence_triangle_pairs = exact_triangle_pairs = 0
    for local_index, local in enumerate(local_triangles):
        if os.environ.get("T73_PROGRESS") and local_index % 8 == 0:
            print(f"triangle patch {local_index}/{len(local_triangles)}", file=sys.stderr, flush=True)
        local_bound = exact_bounds(local[3])
        local_low = np.nextafter(np.array([float(value) for value in local_bound[0]]), -np.inf)
        local_high = np.nextafter(np.array([float(value) for value in local_bound[1]]), np.inf)
        local_numeric = np.array([
            [float(coordinate) for coordinate in vertex] for vertex in local[3]
        ])
        candidates = np.flatnonzero(np.all(other_highs >= local_low, axis=1)
                                    & np.all(local_high >= other_lows, axis=1))
        for other_index in candidates:
            other_index = int(other_index)
            other = all_other_triangles[other_index]
            if other[0] == "twist" and other_index >= len(retained_triangles) + local_index:
                continue
            broad_triangle_pairs += 1
            if not exact_bounds_overlap(local_bound, other_bounds[other_index]):
                continue
            shared_vertices = set(local[3]) & set(other[3])
            if shared_vertices:
                incidence_triangle_pairs += 1
                continue
            if float_triangle_separated(local_numeric, other_numeric[other_index]):
                continue
            if not projected_triangles_intersect(local[3], other[3]):
                continue
            exact_triangle_pairs += 1
            if triangles_intersect(local[3], other[3]):
                raise AssertionError(
                    f"twist ribbon triangle intersects {local[:3]} / {other[:3]}"
                )

    segments = make_framed_segments(model, data["components"])
    if os.environ.get("T73_PROGRESS"):
        print(f"assembled {len(segments)} segments", file=sys.stderr, flush=True)
    segment_bounds = [exact_bounds(item[3]) for item in segments]
    segment_lows, segment_highs = numeric_bounds(segments)
    segment_numeric = [
        np.array([[float(coordinate) for coordinate in vertex] for vertex in item[3]])
        for item in segments
    ]
    if os.environ.get("T73_PROGRESS"):
        print("built segment bounds", file=sys.stderr, flush=True)
    broad_segment_pairs = incidence_segment_pairs = exact_segment_pairs = 0
    for local_index, local in enumerate(local_triangles):
        if os.environ.get("T73_PROGRESS") and local_index % 8 == 0:
            print(f"segment patch {local_index}/{len(local_triangles)}", file=sys.stderr, flush=True)
        local_bound = exact_bounds(local[3])
        local_low = np.nextafter(np.array([float(value) for value in local_bound[0]]), -np.inf)
        local_high = np.nextafter(np.array([float(value) for value in local_bound[1]]), np.inf)
        local_numeric = np.array([
            [float(coordinate) for coordinate in vertex] for vertex in local[3]
        ])
        candidates = np.flatnonzero(np.all(segment_highs >= local_low, axis=1)
                                    & np.all(local_high >= segment_lows, axis=1))
        for segment_index in candidates:
            segment_index = int(segment_index)
            segment = segments[segment_index]
            broad_segment_pairs += 1
            if not exact_bounds_overlap(local_bound, segment_bounds[segment_index]):
                continue
            shared_vertices = set(local[3]) & set(segment[3])
            if shared_vertices:
                incidence_segment_pairs += 1
                continue
            if float_segment_plane_separated(segment_numeric[segment_index], local_numeric):
                continue
            if not projected_segment_triangle_intersect(segment[3], local[3]):
                continue
            exact_segment_pairs += 1
            if segment_triangle(segment[3], local[3]):
                raise AssertionError(
                    f"twist ribbon meets nonincident segment {local[:3]} / {segment[:3]}"
                )

    return {
        "verdict": "PASS_DUAL_ZERO_FRAMING_TWIST_GLOBAL_CLEARANCE",
        "twist_ribbon_triangles": len(local_triangles),
        "retained_ribbon_triangles": len(retained_triangles),
        "framed_segments": len(segments),
        "triangle_broad_pairs": broad_triangle_pairs,
        "triangle_incidence_pairs": incidence_triangle_pairs,
        "exact_triangle_triangle_checks": exact_triangle_pairs,
        "segment_broad_pairs": broad_segment_pairs,
        "segment_incidence_pairs": incidence_segment_pairs,
        "exact_segment_triangle_checks": exact_segment_pairs,
        "embedded_and_disjoint_from_retained_model": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
