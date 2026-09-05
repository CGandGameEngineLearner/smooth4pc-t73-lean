#!/usr/bin/env python3
"""Build the first sequential t-slide from the verified belt-collar disk."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from t73_pl_kirby_moves import as_point, encode

ROOT = Path(__file__).resolve().parents[1]
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
LIFTS = ROOT / "geometry/t73_ar_core_universal_lifts.json"
INTERVALS = ROOT / "geometry/t73_t_band_attachment_intervals.json"
COLLARS = ROOT / "geometry/t73_t_band_collar_surfaces.json"
OUTPUT = ROOT / "geometry/t73_t_band_sequential_state_01.json"
PERIOD = Fraction(4)


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def translate(point, deck):
    return tuple(point[axis] + PERIOD * deck[axis] for axis in range(3)) + (point[3],)


def interpolate(origin, neighbour, parameter):
    return tuple(
        origin[axis] + parameter * (neighbour[axis] - origin[axis])
        for axis in range(4)
    )


def append_framed_piece(path, normals, ranges, name, piece, piece_normals):
    if len(piece) != len(piece_normals):
        raise AssertionError(f"{name}: point/normal counts differ")
    if path:
        if path[-1] != piece[0] or normals[-1] != piece_normals[0]:
            raise AssertionError(f"{name}: framed boundary does not glue")
        start = len(path) - 1
        path.extend(piece[1:])
        normals.extend(piece_normals[1:])
    else:
        start = 0
        path.extend(piece)
        normals.extend(piece_normals)
    ranges[name] = [start, len(path) - 1]


def build() -> dict[str, Any]:
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    lifts = json.loads(LIFTS.read_text(encoding="utf-8"))
    intervals = json.loads(INTERVALS.read_text(encoding="utf-8"))
    collars = json.loads(COLLARS.read_text(encoding="utf-8"))

    attachment = intervals["intervals"][0]
    surface = collars["surfaces"][0]
    component = attachment["component"]
    lift = lifts["components"][component]
    source_points = [as_point(point) for point in lift["lifted_vertices"]]
    deck = tuple(lift["closing_deck_translation"])
    source_index = attachment["source_core_vertex_index"]
    width = Fraction(attachment["source_parameter_from_vertex"])
    before = interpolate(source_points[source_index], source_points[source_index - 1], width)
    after = interpolate(source_points[source_index], source_points[source_index + 1], width)
    declared_source = [as_point(point) for point in attachment["source_interval"]]
    if [before, after] != declared_source:
        raise AssertionError("band-0 source interval is not the refined m1 subarc")

    source_complement = [
        after,
        *source_points[source_index + 1 :],
        *[translate(point, deck) for point in source_points[1:source_index]],
        translate(before, deck),
    ]
    vertices = [as_point(point) for point in surface["vertices"]]
    surface_normals = [as_point(normal) for normal in surface["normal_field"]]
    boundary = surface["boundary"]
    negative_ids = boundary["negative_u_lane"]
    positive_ids = boundary["positive_u_lane"]
    negative_lane = [translate(vertices[index], deck) for index in negative_ids]
    positive_lane = [translate(vertices[index], deck) for index in positive_ids]
    negative_normals = [surface_normals[index] for index in negative_ids]
    positive_normals = [surface_normals[index] for index in positive_ids]

    target_start = negative_lane[-1]
    target_end = positive_lane[0]
    target_xyz = target_start[:3]
    if target_end[:3] != target_xyz:
        raise AssertionError("band-0 target attachment is not vertical")
    target_complement = [
        target_start,
        (*target_xyz, Fraction(0)),
        (*target_xyz, Fraction(1)),
        target_end,
    ]

    source_normal = surface_normals[boundary["source_attachment"][0]]
    target_normal = surface_normals[boundary["target_attachment"][0]]
    path: list[tuple[Fraction, ...]] = []
    normals: list[tuple[Fraction, ...]] = []
    ranges: dict[str, list[int]] = {}
    append_framed_piece(
        path,
        normals,
        ranges,
        "retained_m1_complement",
        source_complement,
        [source_normal] * len(source_complement),
    )
    append_framed_piece(path, normals, ranges, "negative_band_lane", negative_lane, negative_normals)
    append_framed_piece(
        path,
        normals,
        ranges,
        "parallel_hcs_complement",
        target_complement,
        [target_normal] * len(target_complement),
    )
    append_framed_piece(path, normals, ranges, "positive_band_lane", positive_lane, positive_normals)

    if path[-1] != translate(path[0], deck):
        raise AssertionError("post-slide m1 does not close with the original deck translation")
    push_path = [
        tuple(point[axis] + normal[axis] for axis in range(4))
        for point, normal in zip(path, normals)
    ]
    if push_path[-1] != translate(push_path[0], deck):
        raise AssertionError("post-slide framing does not close with the source deck translation")

    translated_vertex = translate(source_points[source_index], deck)
    recovered_source = [*source_complement, translated_vertex, translate(after, deck)]
    result = {
        "schema": "t73_t_band_sequential_state/v1",
        "ar_link_sha256": ar_link["sha256"],
        "universal_lifts_sha256": lifts["sha256"],
        "attachment_intervals_sha256": intervals["sha256"],
        "collar_surfaces_sha256": collars["sha256"],
        "state_before": 0,
        "state_after": 1,
        "band_index": 0,
        "moved_component": component,
        "stationary_components": ["h_CS", "m_2", "m_3", "r_xy", "r_yz", "r_zx"],
        "post_slide_lifted_polyline": [encode(point) for point in path],
        "post_slide_normal_field": [encode(normal) for normal in normals],
        "post_slide_push_off": [encode(point) for point in push_path],
        "piece_vertex_ranges": ranges,
        "mapping_torus_seam_segment_indices": [ranges["parallel_hcs_complement"][0] + 1],
        "closing_deck_translation": list(deck),
        "inverse_move": {
            "kind": "cut_band_sum_and_restore_source_subarc",
            "recovered_source_lift": [encode(point) for point in recovered_source],
            "restored_vertex": encode(translated_vertex),
            "expected_closing_deck_translation": list(deck),
        },
        "completion_status": "BAND0_SEQUENTIAL_FRAMED_SLIDE_GEOMETRY_CONSTRUCTED",
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
        raise AssertionError("band-0 sequential state is stale")
    print(f"T73_T_BAND_STATE_01={result['completion_status']}")


if __name__ == "__main__":
    main()
