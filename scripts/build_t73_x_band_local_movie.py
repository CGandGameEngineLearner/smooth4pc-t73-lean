#!/usr/bin/env python3
"""Build compact replay deltas for all 1513 local x-band disks."""

from __future__ import annotations

import argparse
import hashlib
import json
import itertools
from fractions import Fraction
from pathlib import Path

from verify_t73_candidate_t_band0_surface import triangles_intersect

ROOT = Path(__file__).resolve().parents[1]
STATE0 = ROOT / "geometry/t73_x_positive_belt_state0.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
OUTPUT = ROOT / "geometry/t73_x_band_local_movie.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def encode_segment(segment):
    return [encode(segment[0]), encode(segment[1])]


def segment_leaf_sha(segment_id, segment):
    return canonical_sha({"segment_id": segment_id, "endpoints": encode_segment(segment)})


def segment_state_sha(segment_hashes):
    digest = hashlib.sha256()
    for segment_id in sorted(segment_hashes):
        digest.update(bytes.fromhex(segment_hashes[segment_id]))
    return digest.hexdigest().upper()


def add(left, right):
    return tuple(left[index] + right[index] for index in range(4))


def negate(value):
    return tuple(-coordinate for coordinate in value)


def scale(factor, value):
    return tuple(factor * coordinate for coordinate in value)


def source_framing(component, source_kind, width):
    if source_kind == "johnson_handle_lane":
        return (Fraction(0), width, width, Fraction(0)), "TOP_FIBER_PRODUCT_NORMAL_MOD_X_TANGENT"
    if component == "r_xy":
        return (Fraction(0), Fraction(0), width, Fraction(0)), "DUAL_DISK_PLANE_Z_NORMAL"
    if component == "r_zx":
        return (Fraction(0), width, Fraction(0), Fraction(0)), "DUAL_DISK_PLANE_Y_NORMAL"
    raise AssertionError(f"no actual source framing rule for {component}/{source_kind}")


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
    raise AssertionError("x-band has no canonical constant push direction")


def expanded_band(band, source_arc):
    width = Fraction(band["band_width"])
    orientation = band["removed_x_orientation"]
    centerline = [
        (Fraction(2), *point(value))
        for value in band["band_core_on_positive_belt_face"]
    ]
    centerline[1] = (
        *centerline[1][:3],
        centerline[1][3] + (band["index"] + 1) * width,
    )
    source_half = (orientation * width, Fraction(0), Fraction(0), Fraction(0))
    middle_half = (Fraction(0), Fraction(0), Fraction(0), -orientation * width)
    target_half = negate(source_half)
    half_vectors = [source_half, middle_half, target_half]
    cross_sections = [
        [add(center, negate(half)), add(center, half)]
        for center, half in zip(centerline, half_vectors)
    ]
    vertices = [value for pair in cross_sections for value in pair]
    triangles = [[0, 2, 3], [0, 3, 1], [2, 4, 5], [2, 5, 3]]
    source_normal, source_normal_rule = source_framing(
        band["component"], band["source_kind"], width
    )
    target_normal = (Fraction(0), width, Fraction(0), Fraction(0))
    if band["index"] == 0:
        middle_normal = tuple(
            (left + right) / 2 for left, right in zip(source_normal, target_normal)
        )
        normal_field = [
            source_normal,
            source_normal,
            middle_normal,
            middle_normal,
            target_normal,
            target_normal,
        ]
        pushed = [add(value, normal) for value, normal in zip(vertices, normal_field)]
        framing_strategy = "BAND0_BOUNDARY_INTERPOLATION"
        selected_push = None
    else:
        selected_push, pushed = select_constant_push(
            vertices, triangles, source_normal, target_normal, width
        )
        normal_field = [selected_push] * len(vertices)
        framing_strategy = "LEXICOGRAPHIC_CONSTANT_PUSH_WITH_BOUNDARY_HOMOTOPIES"
    target_coefficient = Fraction(band["parallel_m1_target"][0]) / width
    if target_coefficient.denominator != 1:
        raise AssertionError("x target parallel coefficient is not integral")
    if source_arc["orientation"] != orientation or band["replacement_orientation"] != orientation:
        raise AssertionError("x-band source/replacement orientation mismatch")
    record = {
        "source_arc_sha256": canonical_sha(source_arc),
        "source_orientation": orientation,
        "target_parallel_coefficient": int(target_coefficient),
        "source_normal_rule": source_normal_rule,
        "framing_strategy": framing_strategy,
        "outward_movie_height_multiplier": band["index"] + 1,
        "selected_constant_push": encode(selected_push) if selected_push else None,
        "half_vectors_sha256": canonical_sha([encode(value) for value in half_vectors]),
        "vertices_sha256": canonical_sha([encode(value) for value in vertices]),
        "triangles_sha256": canonical_sha(triangles),
        "normal_field_sha256": canonical_sha([encode(value) for value in normal_field]),
        "push_off_vertices_sha256": canonical_sha([encode(value) for value in pushed]),
        "expanded_vertex_count": len(vertices),
        "expanded_triangle_count": len(triangles),
    }
    geometry = {
        "vertices": vertices,
        "triangles": triangles,
        "normal_field": normal_field,
        "pushed": pushed,
    }
    return record, geometry


def initial_segment_state(arcs):
    segments = {}
    for source_id, arc in arcs.items():
        points = [point(value) for value in arc["polyline"]]
        segments[f"{source_id}:left"] = (points[0], points[1])
        segments[f"{source_id}:right"] = (points[1], points[2])
    return segments


def update_segment_state(segments, band, geometry, source_arc):
    source_id = band["source_id"]
    removed = {
        f"{source_id}:left": segments.pop(f"{source_id}:left"),
        f"{source_id}:right": segments.pop(f"{source_id}:right"),
    }
    arc = [point(value) for value in source_arc["polyline"]]
    vertices = geometry["vertices"]
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
        f"{prefix}:target_stub_left": (
            (Fraction(1), *target_low[1:]),
            target_low,
        ),
        f"{prefix}:target_stub_right": (
            target_high,
            (Fraction(3), *target_high[1:]),
        ),
    }
    segments.update(added)
    return removed, added


def build() -> dict:
    state0 = json.loads(STATE0.read_text(encoding="utf-8"))
    cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    if ar_link["components"]["r_xy"]["disk"]["plane_axis"] != 2:
        raise AssertionError("r_xy dual disk no longer supplies the z normal")
    if ar_link["components"]["r_zx"]["disk"]["plane_axis"] != 1:
        raise AssertionError("r_zx dual disk no longer supplies the y normal")
    arcs = {item["source_id"]: item for item in state0["arcs"]}
    active_sources = set(arcs)
    local_segments = initial_segment_state(arcs)
    segment_hashes = {
        segment_id: segment_leaf_sha(segment_id, segment)
        for segment_id, segment in local_segments.items()
    }
    records = []
    for band in cancellation["slide_bands"]:
        source_id = band["source_id"]
        if source_id not in active_sources:
            raise AssertionError(f"{source_id}: absent from its local current state")
        before_sources = sorted(active_sources)
        before_segment_sha = segment_state_sha(segment_hashes)
        before_segment_count = len(local_segments)
        expanded, geometry = expanded_band(band, arcs[source_id])
        removed_segments, added_segments = update_segment_state(
            local_segments, band, geometry, arcs[source_id]
        )
        for segment_id in removed_segments:
            segment_hashes.pop(segment_id)
        for segment_id, segment in added_segments.items():
            segment_hashes[segment_id] = segment_leaf_sha(segment_id, segment)
        active_sources.remove(source_id)
        records.append({
            "band_index": band["index"],
            "state_before": band["index"],
            "state_after": band["index"] + 1,
            "source_id": source_id,
            "component": band["component"],
            "active_source_count_before": len(before_sources),
            "active_source_ids_before_sha256": canonical_sha(before_sources),
            "active_source_count_after": len(active_sources),
            "active_source_ids_after_sha256": canonical_sha(sorted(active_sources)),
            "current_local_segment_count_before": before_segment_count,
            "current_local_segments_before_sha256": before_segment_sha,
            "removed_segments_sha256": canonical_sha(
                {
                    key: encode_segment(value)
                    for key, value in sorted(removed_segments.items())
                }
            ),
            "added_segments_sha256": canonical_sha(
                {
                    key: encode_segment(value)
                    for key, value in sorted(added_segments.items())
                }
            ),
            "current_local_segment_count_after": len(local_segments),
            "current_local_segments_after_sha256": segment_state_sha(segment_hashes),
            **expanded,
            "status": "LOCAL_FRAMED_BAND_DELTA_CONSTRUCTED",
        })
    if active_sources != {"m_1:C_i"}:
        raise AssertionError("x local movie did not remove exactly the 1513 noncancelling passages")
    result = {
        "schema": "t73_x_band_local_movie/v1",
        "positive_belt_state0_sha256": state0["sha256"],
        "x_cancellation_sha256": cancellation["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "band_count": len(records),
        "states": len(records) + 1,
        "bands": records,
        "final_active_source_ids": sorted(active_sources),
        "final_local_segment_count": len(local_segments),
        "final_local_segments_sha256": segment_state_sha(segment_hashes),
        "segment_state_hash_rule": "SHA256 of sorted concatenated per-segment SHA256 leaves",
        "completion_status": "ALL_1513_X_LOCAL_BAND_DELTAS_CONSTRUCTED_AWAITING_CLEARANCE",
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
        raise AssertionError("x local band movie is stale")
    print(f"T73_X_LOCAL_MOVIE={result['completion_status']}")


if __name__ == "__main__":
    main()
