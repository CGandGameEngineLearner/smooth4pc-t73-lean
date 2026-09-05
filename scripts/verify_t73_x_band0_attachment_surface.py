#!/usr/bin/env python3
"""Verify x-band 0 actual attachments and candidate interior surface."""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

from build_t73_t_hcs_cancellation_readiness import final_states
from verify_t73_candidate_t_band0_splice import exact_segment_intersection
from verify_t73_candidate_t_band0_surface import (
    triangle_nondegenerate,
    triangles_intersect,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_band0_attachment_surface.json"
POST_CANCEL = ROOT / "geometry/t73_t_hcs_handle_pair_deletion.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
PERIOD = Fraction(4)


def point(values):
    return tuple(Fraction(value) for value in values)


def edge(first, second):
    return tuple(sorted((first, second)))


def lies_on_segment(value, segment):
    start, end = segment
    direction = tuple(end[axis] - start[axis] for axis in range(4))
    delta = tuple(value[axis] - start[axis] for axis in range(4))
    axis = next(index for index, coordinate in enumerate(direction) if coordinate)
    parameter = delta[axis] / direction[axis]
    return 0 <= parameter <= 1 and all(
        delta[index] == parameter * direction[index] for index in range(4)
    )


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    post_cancel = json.loads(POST_CANCEL.read_text(encoding="utf-8"))
    x_cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    if data["completion_status"] != "X_BAND0_ACTUAL_ATTACHMENTS_BOUNDARY_FRAMING_DERIVED":
        raise AssertionError("x-band 0 scope changed")
    if data["post_t_hcs_deletion_sha256"] != post_cancel["sha256"] or data["x_cancellation_sha256"] != x_cancellation["sha256"] or data["johnson_spine_embedding_sha256"] != spine["sha256"]:
        raise AssertionError("x-band 0 has stale source bindings")

    band = x_cancellation["slide_bands"][0]
    arc_record = next(item for item in spine["handle_arcs"] if item["arc_id"] == band["source_id"])
    local_arc = [point([*value, "1"]) for value in arc_record["lift_polyline"]]
    if [point(value) for value in data["source_arc_local"]] != local_arc:
        raise AssertionError("x-band source is not the actual Johnson handle arc")
    current, current_normals, _ = final_states()["m_2"]
    start, end = data["source_arc_current_state_vertex_range"]
    deck = tuple(data["source_arc_current_state_deck"])
    translated_arc = [
        tuple(value[axis] + PERIOD * deck[axis] for axis in range(3)) + (value[3],)
        for value in local_arc
    ]
    if current[start : end + 1] != translated_arc:
        raise AssertionError("Johnson source arc is absent from the post-cancel m2 state")

    source_interval = [point(value) for value in data["source_interval_local"]]
    if not lies_on_segment(source_interval[0], (local_arc[0], local_arc[1])) or not lies_on_segment(source_interval[1], (local_arc[1], local_arc[2])):
        raise AssertionError("source interval is not on the actual Johnson arc")
    target_interval = [point(value) for value in data["target_parallel_m1_interval_local"]]
    width = Fraction(band["band_width"])
    if data["target_parallel_coefficient"] != 20:
        raise AssertionError("first x target is not the twentieth m1 framing parallel")
    if target_interval[0][1:] != target_interval[1][1:] or target_interval[0][1] != 20 * width:
        raise AssertionError("target interval left its declared m1 parallel")

    vertices = [point(value) for value in data["vertices"]]
    triangles = data["triangles"]
    if any(not triangle_nondegenerate(vertices, triangle) for triangle in triangles):
        raise AssertionError("x-band 0 contains a degenerate triangle")
    counts = Counter(
        edge(triangle[index], triangle[(index + 1) % 3])
        for triangle in triangles
        for index in range(3)
    )
    if len(vertices) - len(counts) + len(triangles) != 1:
        raise AssertionError("x-band 0 surface is not a disk")
    boundary = data["boundary"]
    if [vertices[index] for index in boundary["source_attachment"]] != source_interval:
        raise AssertionError("x-band 0 disk lost an attachment edge")
    if [vertices[index] for index in boundary["target_attachment"]] != list(
        reversed(target_interval)
    ):
        raise AssertionError("x-band target does not have the required reversed orientation")
    half_vectors = [point(value) for value in data["oriented_half_vectors"]]
    expected_half_vectors = [
        (width, Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(0), -width),
        (-width, Fraction(0), Fraction(0), Fraction(0)),
    ]
    if half_vectors != expected_half_vectors or any(not any(value) for value in half_vectors):
        raise AssertionError("x-band orientation rotation changed or collapsed")
    centerline = [point(item) for item in data["centerline"]]
    scheduled = [point(item) for item in data["scheduled_centerline"]]
    if centerline[0] != scheduled[0] or centerline[-1] != scheduled[-1]:
        raise AssertionError("x-band collar adjustment changed an attachment center")
    if centerline[1] != tuple(
        scheduled[1][axis] + (width if axis == 3 else 0) for axis in range(4)
    ):
        raise AssertionError("x-band middle center lacks its outward collar offset")
    if any(
        value[3] < 1
        or not (-1 <= value[1] <= 1 and -1 <= value[2] <= 1)
        for value in vertices
    ):
        raise AssertionError("x-band surface enters the transverse D3 interior")

    actual_source_normal = current_normals[start + 1]
    source_normal = point(data["source_normal_mod_x_tangent"])
    target_normal = point(data["target_parallel_normal"])
    if point(data["actual_source_normal_current_state"]) != actual_source_normal:
        raise AssertionError("saved source normal differs from the post-cancel framing")
    if tuple(actual_source_normal[index] - source_normal[index] for index in range(4)) != (
        actual_source_normal[0], Fraction(0), Fraction(0), Fraction(0)
    ):
        raise AssertionError("source normal was not reduced modulo the x-arc tangent")
    if target_normal != (Fraction(0), width, Fraction(0), Fraction(0)):
        raise AssertionError("target normal is not the unit m1 parallel displacement")
    normal_field = [point(value) for value in data["normal_field"]]
    if normal_field[0] != source_normal or normal_field[-1] != target_normal:
        raise AssertionError("x-band normal extension lost its boundary values")
    if any(not any(coordinate for coordinate in normal) for normal in normal_field):
        raise AssertionError("x-band normal extension crosses the zero section")
    pushed = [point(value) for value in data["push_off_vertices"]]
    if any(
        tuple(vertex[axis] + normal[axis] for axis in range(4)) != push
        for vertex, normal, push in zip(vertices, normal_field, pushed)
    ):
        raise AssertionError("x-band push-off is not disk plus normal")

    local_checks = 0
    geometric_triangles = [tuple(vertices[index] for index in triangle) for triangle in triangles]
    for first in range(len(triangles)):
        for second in range(first + 1, len(triangles)):
            if set(triangles[first]) & set(triangles[second]):
                continue
            local_checks += 1
            if triangles_intersect(geometric_triangles[first], geometric_triangles[second]):
                raise AssertionError("x-band 0 disk self-intersects")
    negative = [vertices[index] for index in boundary["negative_x_lane"]]
    positive = [vertices[index] for index in boundary["positive_x_lane"]]
    if any(
        exact_segment_intersection(first, second)
        for first in zip(negative, negative[1:])
        for second in zip(positive, positive[1:])
    ):
        raise AssertionError("x-band 0 has crossing boundary lanes")
    pushed_triangles = [tuple(pushed[index] for index in triangle) for triangle in triangles]
    if any(
        triangles_intersect(first, second)
        for first in geometric_triangles
        for second in pushed_triangles
    ):
        raise AssertionError("x-band 0 disk meets its framed push-off")
    return {
        "verdict": "PASS_X_BAND0_ACTUAL_ATTACHMENTS_AND_BOUNDARY_FRAMING",
        "post_cancel_source_vertex_range": [start, end],
        "post_cancel_source_deck": list(deck),
        "target_parallel_coefficient": 20,
        "vertices": len(vertices),
        "triangles": len(triangles),
        "local_nonadjacent_triangle_checks": local_checks,
        "disk_push_triangle_checks": len(geometric_triangles) * len(pushed_triangles),
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
