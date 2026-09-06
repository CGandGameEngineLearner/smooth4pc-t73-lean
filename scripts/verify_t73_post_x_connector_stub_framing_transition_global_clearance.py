#!/usr/bin/env python3
"""Exact incremental global clearance for connector/stub framing collars."""

from __future__ import annotations

import gzip
import json
import math
import os
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from shapely.geometry import box
from shapely.strtree import STRtree

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from verify_t73_affine_s3_product_ribbon_clearance import (
    float_segment_plane_separated,
    float_triangle_separated,
    segment_triangle,
    triangles_intersect,
)


ROOT = Path(__file__).resolve().parents[1]
TRANSITIONS = ROOT / "audit/t73_post_x_connector_stub_framing_transitions_receipt.json"
ASSEMBLY = ROOT / "geometry/t73_post_x_framed_cycle_assembly.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
DUAL = ROOT / "geometry/t73_actual_dual_product_ribbons.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    return path


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def exact_bounds(vertices):
    return (
        tuple(min(vertex[axis] for vertex in vertices) for axis in range(3)),
        tuple(max(vertex[axis] for vertex in vertices) for axis in range(3)),
    )


def bounds_overlap(first, second):
    return all(
        first[0][axis] <= second[1][axis]
        and second[0][axis] <= first[1][axis]
        for axis in range(3)
    )


def xy_box(vertices):
    low_x = math.nextafter(float(min(vertex[0] for vertex in vertices)), -math.inf)
    low_y = math.nextafter(float(min(vertex[1] for vertex in vertices)), -math.inf)
    high_x = math.nextafter(float(max(vertex[0] for vertex in vertices)), math.inf)
    high_y = math.nextafter(float(max(vertex[1] for vertex in vertices)), math.inf)
    return box(low_x, low_y, high_x, high_y)


def numeric(vertices):
    return np.array([[float(coordinate) for coordinate in vertex] for vertex in vertices])


SCREEN_AXES = np.array([
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [0.0, 0.0, 1.0],
    [1.0, 1.0, 1.0],
    [1.0, 2.0, 3.0],
    [2.0, -3.0, 5.0],
    [-5.0, 7.0, 2.0],
])


def interval_screen_bounds(numeric_items):
    lows = []
    highs = []
    for vertices in numeric_items:
        projections = vertices @ SCREEN_AXES.T
        lows.append(np.nextafter(projections.min(axis=0), -np.inf))
        highs.append(np.nextafter(projections.max(axis=0), np.inf))
    return np.array(lows), np.array(highs)


def endpoint_key(first, second):
    return tuple(sorted((first, second)))


def load_transition_records(receipt):
    records = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            core = [point(value) for value in record["core_vertices"]]
            push = [point(value) for value in record["push_vertices"]]
            records.append((record, core, push))
    return records


def base_paths(spine, ar_link, dual, assembly):
    used_connectors = {
        block["connector_id"]
        for component in assembly["components"]
        for block in component["blocks"]
        if block["kind"] == "actual_johnson_central_connector"
    }
    width = Fraction(ar_link["framing"]["spine_ribbon_transport"]["width"])
    connector_normal = (width, width, width)
    paths = []
    for connector in spine["central_connectors"]:
        if connector["connector_id"] not in used_connectors:
            continue
        core = [point(value) for value in connector["polyline"]]
        push = [add(value, connector_normal) for value in core]
        paths.append((
            "connector", connector["connector_id"], core, push,
            set(range(len(core) - 1)),
        ))
    dual_by_name = {item["name"]: item for item in dual["components"]}
    surviving_dual_segments = {}
    for component in assembly["components"]:
        indices = set()
        for block in component["blocks"]:
            if block["kind"] == "actual_dual_two_segment_passage":
                low, high = block["source_segment_range"]
                indices.update(range(low, high + 1))
        if indices:
            surviving_dual_segments[component["component"]] = indices
    for name in ("r_xy", "r_yz", "r_zx"):
        core = [point(value) for value in ar_link["components"][name]["polyline"]]
        normal = point(dual_by_name[name]["product_normal"])
        push = [add(value, normal) for value in core]
        paths.append(("dual", name, core, push, surviving_dual_segments[name]))
    return paths


def verify():
    receipt = json.loads(TRANSITIONS.read_text())
    assembly = json.loads(ASSEMBLY.read_text())
    spine = json.loads(SPINE.read_text())
    ar_link = json.loads(AR_LINK.read_text())
    dual = json.loads(DUAL.read_text())
    transition_records = load_transition_records(receipt)
    if len(transition_records) != 3026:
        raise AssertionError("transition record inventory changed")

    replaced = {
        endpoint_key(core[0], core[-1]) for _, core, _ in transition_records
    }
    if len(replaced) != 3026:
        raise AssertionError("transition collars do not replace distinct base segments")

    retained_triangles = []
    retained_segments = []
    base_segment_count = excluded_segment_count = 0
    for kind, owner, core, push, allowed_segments in base_paths(
        spine, ar_link, dual, assembly
    ):
        for segment_index in sorted(allowed_segments):
            base_segment_count += 1
            key = endpoint_key(core[segment_index], core[segment_index + 1])
            if key in replaced:
                excluded_segment_count += 1
                continue
            vertices = (
                core[segment_index], core[segment_index + 1],
                push[segment_index], push[segment_index + 1],
            )
            retained_triangles.extend((
                ("base", owner, segment_index, (vertices[0], vertices[1], vertices[3])),
                ("base", owner, segment_index, (vertices[0], vertices[3], vertices[2])),
            ))
            retained_segments.extend((
                ("core", owner, segment_index, (vertices[0], vertices[1])),
                ("push", owner, segment_index, (vertices[2], vertices[3])),
            ))
    if (base_segment_count, excluded_segment_count) != (7108, 3026):
        raise AssertionError(
            f"base/replaced segment inventory changed: {base_segment_count}/{excluded_segment_count}"
        )

    transition_triangles = []
    transition_segments = []
    for record_index, (record, core, push) in enumerate(transition_records):
        vertices = core + push
        for triangle_index, indices in enumerate(record["ribbon_triangles"]):
            transition_triangles.append((
                "transition", record_index, triangle_index,
                tuple(vertices[index] for index in indices),
            ))
        for index in range(2):
            transition_segments.extend((
                ("core", record_index, index, (core[index], core[index + 1])),
                ("push", record_index, index, (push[index], push[index + 1])),
            ))

    comparison_triangles = retained_triangles + transition_triangles
    comparison_segments = retained_segments + transition_segments
    triangle_tree = STRtree([xy_box(item[3]) for item in comparison_triangles])
    triangle_bounds = [exact_bounds(item[3]) for item in comparison_triangles]
    triangle_numeric = [numeric(item[3]) for item in comparison_triangles]
    triangle_screen_low, triangle_screen_high = interval_screen_bounds(
        triangle_numeric
    )
    segment_tree = STRtree([xy_box(item[3]) for item in comparison_segments])
    segment_bounds = [exact_bounds(item[3]) for item in comparison_segments]
    segment_numeric = [numeric(item[3]) for item in comparison_segments]
    segment_screen_low, segment_screen_high = interval_screen_bounds(
        segment_numeric
    )

    triangle_broad = triangle_axis_reject = triangle_bounds_reject = 0
    triangle_incidence = 0
    triangle_float_reject = triangle_exact = 0
    transition_offset = len(retained_triangles)
    for local_index, transition in enumerate(transition_triangles):
        if os.environ.get("T73_PROGRESS") and local_index % 1000 == 0:
            print(
                f"transition triangles {local_index}/{len(transition_triangles)} "
                f"broad={triangle_broad} exact={triangle_exact}",
                file=sys.stderr,
                flush=True,
            )
        global_index = transition_offset + local_index
        raw_candidates = triangle_tree.query(xy_box(transition[3]))
        candidates = raw_candidates[raw_candidates < global_index]
        triangle_broad += len(candidates)
        local_low = triangle_screen_low[global_index]
        local_high = triangle_screen_high[global_index]
        mask = np.all(triangle_screen_high[candidates] >= local_low, axis=1)
        mask &= np.all(local_high >= triangle_screen_low[candidates], axis=1)
        triangle_axis_reject += int((~mask).sum())
        for raw_index in candidates[mask]:
            other_index = int(raw_index)
            other = comparison_triangles[other_index]
            if not bounds_overlap(triangle_bounds[global_index], triangle_bounds[other_index]):
                triangle_bounds_reject += 1
                continue
            if set(transition[3]) & set(other[3]):
                triangle_incidence += 1
                continue
            if float_triangle_separated(
                triangle_numeric[global_index], triangle_numeric[other_index]
            ):
                triangle_float_reject += 1
                continue
            triangle_exact += 1
            if triangles_intersect(transition[3], other[3]):
                raise AssertionError(
                    f"nonincident framing ribbons intersect: {transition[:3]} / {other[:3]}"
                )

    segment_broad = segment_axis_reject = segment_bounds_reject = 0
    segment_incidence = 0
    segment_float_reject = segment_exact = 0
    for local_index, transition in enumerate(transition_triangles):
        if os.environ.get("T73_PROGRESS") and local_index % 1000 == 0:
            print(
                f"transition segments {local_index}/{len(transition_triangles)} "
                f"broad={segment_broad} exact={segment_exact}",
                file=sys.stderr,
                flush=True,
            )
        transition_bound = exact_bounds(transition[3])
        transition_numeric = numeric(transition[3])
        candidates = segment_tree.query(xy_box(transition[3]))
        segment_broad += len(candidates)
        local_projections = transition_numeric @ SCREEN_AXES.T
        local_low = np.nextafter(local_projections.min(axis=0), -np.inf)
        local_high = np.nextafter(local_projections.max(axis=0), np.inf)
        mask = np.all(segment_screen_high[candidates] >= local_low, axis=1)
        mask &= np.all(local_high >= segment_screen_low[candidates], axis=1)
        segment_axis_reject += int((~mask).sum())
        for raw_index in candidates[mask]:
            segment_index = int(raw_index)
            segment = comparison_segments[segment_index]
            if not bounds_overlap(transition_bound, segment_bounds[segment_index]):
                segment_bounds_reject += 1
                continue
            if set(transition[3]) & set(segment[3]):
                segment_incidence += 1
                continue
            if float_segment_plane_separated(
                segment_numeric[segment_index], transition_numeric
            ):
                segment_float_reject += 1
                continue
            segment_exact += 1
            if segment_triangle(segment[3], transition[3]):
                raise AssertionError(
                    f"framing ribbon meets nonincident segment: {transition[:3]} / {segment[:3]}"
                )

    return {
        "verdict": "PASS_POST_X_CONNECTOR_STUB_FRAMING_TRANSITION_GLOBAL_CLEARANCE",
        "base_product_segments": base_segment_count,
        "replaced_base_product_segments": excluded_segment_count,
        "retained_product_ribbon_triangles": len(retained_triangles),
        "transition_ribbon_triangles": len(transition_triangles),
        "corrected_framed_segments": len(comparison_segments),
        "triangle_broad_candidates": triangle_broad,
        "triangle_float_axis_interval_rejects": triangle_axis_reject,
        "triangle_exact_bounds_rejects": triangle_bounds_reject,
        "triangle_incidence_skips": triangle_incidence,
        "triangle_float_separation_rejects": triangle_float_reject,
        "exact_triangle_triangle_checks": triangle_exact,
        "segment_broad_candidates": segment_broad,
        "segment_float_axis_interval_rejects": segment_axis_reject,
        "segment_exact_bounds_rejects": segment_bounds_reject,
        "segment_incidence_skips": segment_incidence,
        "segment_float_separation_rejects": segment_float_reject,
        "exact_segment_triangle_checks": segment_exact,
        "globally_embedded_corrected_product_ribbons": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
