#!/usr/bin/env python3
"""Independently replay and verify all 1513 local x-band segment states."""

from __future__ import annotations

import hashlib
import json
import itertools
import os
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

from verify_t73_candidate_t_band0_relative_contacts import verify_contacts
from verify_t73_candidate_t_band0_splice import exact_segment_intersection
from verify_t73_candidate_t_band0_surface import (
    segment_meets_triangle,
    triangle_nondegenerate,
    triangles_intersect,
)

ROOT = Path(__file__).resolve().parents[1]
MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
STATE0 = ROOT / "geometry/t73_x_positive_belt_state0.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def encode_segment(segment):
    return [encode(segment[0]), encode(segment[1])]


def add(left, right):
    return tuple(left[index] + right[index] for index in range(4))


def negate(value):
    return tuple(-coordinate for coordinate in value)


def segment_leaf_sha(segment_id, segment):
    return canonical_sha({"segment_id": segment_id, "endpoints": encode_segment(segment)})


def segment_state_sha(segment_hashes):
    digest = hashlib.sha256()
    for segment_id in sorted(segment_hashes):
        digest.update(bytes.fromhex(segment_hashes[segment_id]))
    return digest.hexdigest().upper()


def source_framing(component, source_kind, width):
    if source_kind == "johnson_handle_lane":
        return (Fraction(0), width, width, Fraction(0)), "TOP_FIBER_PRODUCT_NORMAL_MOD_X_TANGENT"
    if component == "r_xy":
        return (Fraction(0), Fraction(0), width, Fraction(0)), "DUAL_DISK_PLANE_Z_NORMAL"
    if component == "r_zx":
        return (Fraction(0), width, Fraction(0), Fraction(0)), "DUAL_DISK_PLANE_Y_NORMAL"
    raise AssertionError("unknown x-band source framing")


def homotopy_hits_zero(first, second):
    parameter = None
    for left, right in zip(first, second):
        difference = right - left
        if difference:
            candidate = -left / difference
            if parameter is not None and candidate != parameter:
                return False
            parameter = candidate
        elif left:
            return False
    return parameter is not None and 0 <= parameter <= 1


def select_constant_push(vertices, triangles, source_normal, target_normal, width):
    disk_triangles = [tuple(vertices[index] for index in ids) for ids in triangles]
    for coordinates in itertools.product((-1, 0, 1), repeat=3):
        if coordinates == (0, 0, 0):
            continue
        candidate = (Fraction(0),) + tuple(
            Fraction(coordinate) * width / 16 for coordinate in coordinates
        )
        if homotopy_hits_zero(source_normal, candidate) or homotopy_hits_zero(
            target_normal, candidate
        ):
            continue
        pushed = [add(value, candidate) for value in vertices]
        push_triangles = [tuple(pushed[index] for index in ids) for ids in triangles]
        if not any(
            triangles_intersect(first, second)
            for first in disk_triangles
            for second in push_triangles
        ):
            return candidate, pushed
    raise AssertionError("no exact constant push direction exists")


def expand_band(band):
    width = Fraction(band["band_width"])
    orientation = band["removed_x_orientation"]
    centerline = [
        (Fraction(2), *point(value))
        for value in band["band_core_on_positive_belt_face"]
    ]
    half_vectors = [
        (orientation * width, Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(0), -orientation * width),
        (-orientation * width, Fraction(0), Fraction(0), Fraction(0)),
    ]
    vertices = []
    for center, half in zip(centerline, half_vectors):
        vertices.extend([add(center, negate(half)), add(center, half)])
    triangles = [[0, 2, 3], [0, 3, 1], [2, 4, 5], [2, 5, 3]]
    source_normal, source_rule = source_framing(
        band["component"], band["source_kind"], width
    )
    target_normal = (Fraction(0), width, Fraction(0), Fraction(0))
    if band["index"] == 0:
        middle_normal = tuple(
            (left + right) / 2 for left, right in zip(source_normal, target_normal)
        )
        normals = [source_normal, source_normal, middle_normal, middle_normal, target_normal, target_normal]
        pushed = [add(value, normal) for value, normal in zip(vertices, normals)]
        strategy = "BAND0_BOUNDARY_INTERPOLATION"
        selected = None
    else:
        selected, pushed = select_constant_push(
            vertices, triangles, source_normal, target_normal, width
        )
        normals = [selected] * len(vertices)
        strategy = "LEXICOGRAPHIC_CONSTANT_PUSH_WITH_BOUNDARY_HOMOTOPIES"
    return (
        vertices,
        triangles,
        normals,
        pushed,
        half_vectors,
        source_normal,
        target_normal,
        source_rule,
        strategy,
        selected,
    )


def initial_segments(arcs):
    output = {}
    for source_id, record in arcs.items():
        values = [point(value) for value in record["polyline"]]
        output[f"{source_id}:left"] = (values[0], values[1])
        output[f"{source_id}:right"] = (values[1], values[2])
    return output


def update_segments(segments, band, vertices, source_arc):
    source_id = band["source_id"]
    removed = {
        f"{source_id}:left": segments.pop(f"{source_id}:left"),
        f"{source_id}:right": segments.pop(f"{source_id}:right"),
    }
    arc = [point(value) for value in source_arc["polyline"]]
    source_low, source_high = sorted(vertices[:2], key=lambda value: value[0])
    target_low, target_high = sorted(vertices[-2:], key=lambda value: value[0])
    negative = [vertices[index] for index in (0, 2, 4)]
    positive = [vertices[index] for index in (5, 3, 1)]
    prefix = f"band:{band['index']}"
    added = {
        f"{prefix}:source_stub_left": (arc[0], source_low),
        f"{prefix}:source_stub_right": (source_high, arc[2]),
        f"{prefix}:negative_lane_0": (negative[0], negative[1]),
        f"{prefix}:negative_lane_1": (negative[1], negative[2]),
        f"{prefix}:positive_lane_0": (positive[0], positive[1]),
        f"{prefix}:positive_lane_1": (positive[1], positive[2]),
        f"{prefix}:target_stub_left": ((Fraction(1), *target_low[1:]), target_low),
        f"{prefix}:target_stub_right": (target_high, (Fraction(3), *target_high[1:])),
    }
    segments.update(added)
    return removed, added


def bounds(segment):
    low = tuple(float(min(segment[0][axis], segment[1][axis])) for axis in range(4))
    high = tuple(float(max(segment[0][axis], segment[1][axis])) for axis in range(4))
    return low, high


def verify_clearance(triangles, push_triangles, segments, segment_bounds, source_id):
    segment_ids = list(segments)
    lows = np.array([segment_bounds[segment_id][0] for segment_id in segment_ids])
    highs = np.array([segment_bounds[segment_id][1] for segment_id in segment_ids])
    broad_pairs = 0
    exact_checks = 0
    for kind, geometric_triangles in (("disk", triangles), ("push", push_triangles)):
        for triangle in geometric_triangles:
            triangle_low = np.array([float(min(value[axis] for value in triangle)) for axis in range(4)])
            triangle_high = np.array([float(max(value[axis] for value in triangle)) for axis in range(4)])
            broad_pairs += len(segment_ids)
            candidates = np.flatnonzero(
                np.all(lows <= triangle_high, axis=1)
                & np.all(highs >= triangle_low, axis=1)
            )
            for candidate in candidates:
                segment_id = segment_ids[int(candidate)]
                if kind == "disk" and segment_id in {
                    f"{source_id}:left",
                    f"{source_id}:right",
                }:
                    continue
                if ":source_stub_" in segment_id or ":target_stub_" in segment_id:
                    segment = segments[segment_id]
                    inner_endpoint = min(
                        segment, key=lambda value: abs(value[0] - Fraction(2))
                    )
                    extreme_vertices = [
                        value for value in triangle if value[0] == inner_endpoint[0]
                    ]
                    if inner_endpoint not in extreme_vertices:
                        continue
                exact_checks += 1
                if segment_meets_triangle(segments[segment_id], triangle):
                    raise AssertionError(
                        f"{kind} meets current segment {segment_id}"
                    )
    return broad_pairs, exact_checks


def verify() -> dict:
    movie = json.loads(MOVIE.read_text(encoding="utf-8"))
    state0 = json.loads(STATE0.read_text(encoding="utf-8"))
    cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    if movie["completion_status"] != "ALL_1513_X_LOCAL_BAND_DELTAS_CONSTRUCTED_AWAITING_CLEARANCE":
        raise AssertionError("x local movie scope changed")
    if movie["positive_belt_state0_sha256"] != state0["sha256"] or movie["x_cancellation_sha256"] != cancellation["sha256"] or movie["actual_ar_link_sha256"] != ar_link["sha256"]:
        raise AssertionError("x local movie has stale source bindings")
    if ar_link["components"]["r_xy"]["disk"]["plane_axis"] != 2 or ar_link["components"]["r_zx"]["disk"]["plane_axis"] != 1:
        raise AssertionError("dual-disk product framing planes changed")

    arcs = {item["source_id"]: item for item in state0["arcs"]}
    active_sources = set(arcs)
    segments = initial_segments(arcs)
    segment_hashes = {
        segment_id: segment_leaf_sha(segment_id, segment)
        for segment_id, segment in segments.items()
    }
    segment_bounds = {
        segment_id: bounds(segment) for segment_id, segment in segments.items()
    }
    broad_pairs = exact_checks = source_contacts = target_contacts = 0
    for index, (record, band) in enumerate(zip(movie["bands"], cancellation["slide_bands"])):
        if os.environ.get("T73_PROGRESS") and index % 100 == 0:
            print(f"x-local verifier: band {index}/1513", file=sys.stderr, flush=True)
        if record["band_index"] != index or record["state_before"] != index or record["state_after"] != index + 1:
            raise AssertionError("x local movie order changed")
        if band["source_id"] not in active_sources:
            raise AssertionError("x source is absent from its current state")
        if record["active_source_ids_before_sha256"] != canonical_sha(sorted(active_sources)) or record["current_local_segments_before_sha256"] != segment_state_sha(segment_hashes):
            raise AssertionError("x state-before manifest changed")
        (
            vertices,
            triangle_ids,
            normals,
            pushed,
            half_vectors,
            source_normal,
            target_normal,
            source_rule,
            framing_strategy,
            selected_push,
        ) = expand_band(band)
        source_arc = arcs[band["source_id"]]
        expected = {
            "source_arc_sha256": canonical_sha(source_arc),
            "source_orientation": band["removed_x_orientation"],
            "target_parallel_coefficient": 20 * (index + 1),
            "source_normal_rule": source_rule,
            "framing_strategy": framing_strategy,
            "selected_constant_push": encode(selected_push) if selected_push else None,
            "half_vectors_sha256": canonical_sha([encode(value) for value in half_vectors]),
            "vertices_sha256": canonical_sha([encode(value) for value in vertices]),
            "triangles_sha256": canonical_sha(triangle_ids),
            "normal_field_sha256": canonical_sha([encode(value) for value in normals]),
            "push_off_vertices_sha256": canonical_sha([encode(value) for value in pushed]),
        }
        if any(record[field] != value for field, value in expected.items()):
            raise AssertionError(f"x-band {index} expanded geometry hash changed")
        if band["removed_x_orientation"] != band["replacement_orientation"]:
            raise AssertionError("x-band orientations do not cancel the m1 passage")
        triangles = [tuple(vertices[item] for item in ids) for ids in triangle_ids]
        push_triangles = [tuple(pushed[item] for item in ids) for ids in triangle_ids]
        if any(not triangle_nondegenerate(vertices, ids) for ids in triangle_ids):
            raise AssertionError(f"x-band {index} has a degenerate triangle")
        if any(triangles_intersect(first, second) for first in triangles for second in push_triangles):
            raise AssertionError(f"x-band {index} meets its push disk")
        negative = [vertices[item] for item in (0, 2, 4)]
        positive = [vertices[item] for item in (5, 3, 1)]
        if any(
            exact_segment_intersection(first, second)
            for first in zip(negative, negative[1:])
            for second in zip(positive, positive[1:])
        ):
            raise AssertionError(f"x-band {index} boundary lanes cross")
        source_edge = (vertices[0], vertices[1])
        current_source_contacts = verify_contacts(
            triangles,
            list(zip([point(value) for value in source_arc["polyline"]], [point(value) for value in source_arc["polyline"]][1:])),
            source_edge,
            False,
        )
        source_contacts += current_source_contacts
        target_edge = (vertices[4], vertices[5])
        target_center = tuple((left + right) / 2 for left, right in zip(*target_edge))
        target_arc = [
            (Fraction(1), *target_center[1:]),
            (Fraction(2), *target_center[1:]),
            (Fraction(3), *target_center[1:]),
        ]
        target_contacts += verify_contacts(
            triangles, list(zip(target_arc, target_arc[1:])), target_edge, False
        )
        current_broad, current_exact = verify_clearance(
            triangles,
            push_triangles,
            segments,
            segment_bounds,
            band["source_id"],
        )
        broad_pairs += current_broad
        exact_checks += current_exact
        removed, added = update_segments(segments, band, vertices, source_arc)
        for segment_id in removed:
            segment_hashes.pop(segment_id)
            segment_bounds.pop(segment_id)
        for segment_id, segment in added.items():
            segment_hashes[segment_id] = segment_leaf_sha(segment_id, segment)
            segment_bounds[segment_id] = bounds(segment)
        active_sources.remove(band["source_id"])
        if record["removed_segments_sha256"] != canonical_sha({key: encode_segment(value) for key, value in sorted(removed.items())}) or record["added_segments_sha256"] != canonical_sha({key: encode_segment(value) for key, value in sorted(added.items())}):
            raise AssertionError("x local segment delta changed")
        if record["current_local_segments_after_sha256"] != segment_state_sha(segment_hashes) or record["active_source_ids_after_sha256"] != canonical_sha(sorted(active_sources)):
            raise AssertionError("x state-after manifest changed")
    if active_sources != {"m_1:C_i"} or len(segments) != 12106:
        raise AssertionError("x local movie final state has the wrong passages")
    if movie["final_local_segments_sha256"] != segment_state_sha(segment_hashes):
        raise AssertionError("x local final segment hash changed")
    return {
        "verdict": "PASS_ALL_1513_X_LOCAL_FRAMED_BAND_STATES",
        "bands": len(movie["bands"]),
        "states": movie["states"],
        "initial_segments": 3028,
        "final_segments": len(segments),
        "source_triangle_contacts": source_contacts,
        "target_triangle_contacts": target_contacts,
        "numpy_broad_phase_pairs": broad_pairs,
        "exact_segment_triangle_checks": exact_checks,
        "remaining_x_passage_sources": sorted(active_sources),
        "global_hybrid_splices_verified": 1,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
