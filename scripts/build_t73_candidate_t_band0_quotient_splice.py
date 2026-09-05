#!/usr/bin/env python3
"""Construct band-0 as a continuous universal-cover path closed in T3."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from t73_pl_kirby_moves import as_point, encode

ROOT = Path(__file__).resolve().parents[1]
LIFTS = ROOT / "geometry/t73_ar_core_universal_lifts.json"
INTERVALS = ROOT / "geometry/t73_t_band_attachment_intervals.json"
MOVIE = ROOT / "geometry/t73_candidate_t_band_movie.json"
FRAMING = ROOT / "geometry/t73_t_band_framing_extensions.json"
OUTPUT = ROOT / "geometry/t73_candidate_t_band0_quotient_splice.json"
PERIOD = Fraction(4)


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def translate(point: tuple[Fraction, ...], deck: tuple[int, int, int]) -> tuple[Fraction, ...]:
    return tuple(point[i] + PERIOD * deck[i] for i in range(3)) + (point[3],)


def interpolate(origin, neighbour, parameter: Fraction):
    return tuple(origin[i] + parameter * (neighbour[i] - origin[i]) for i in range(4))


def boundary_lanes(segments: list[dict[str, Any]], deck: tuple[int, int, int]):
    left = [translate(as_point(segments[0]["band_vertices"][0]), deck)]
    right = [translate(as_point(segments[0]["band_vertices"][3]), deck)]
    for segment in segments:
        left.append(translate(as_point(segment["band_vertices"][1]), deck))
        right.append(translate(as_point(segment["band_vertices"][2]), deck))
    return left, right


def build() -> dict[str, Any]:
    lifts = json.loads(LIFTS.read_text(encoding="utf-8"))
    intervals = json.loads(INTERVALS.read_text(encoding="utf-8"))
    movie = json.loads(MOVIE.read_text(encoding="utf-8"))
    framing = json.loads(FRAMING.read_text(encoding="utf-8"))
    attachment = intervals["intervals"][0]
    component = attachment["component"]
    lift = lifts["components"][component]
    points = [as_point(point) for point in lift["lifted_vertices"]]
    deck = tuple(lift["closing_deck_translation"])
    width = Fraction(attachment["source_parameter_from_vertex"])
    index = attachment["source_core_vertex_index"]
    before = interpolate(points[index], points[index - 1], width)
    after = interpolate(points[index], points[index + 1], width)
    source_complement = [after, *points[index + 1 :], *[translate(point, deck) for point in points[1:index]], translate(before, deck)]
    left, right = boundary_lanes(movie["bands"][0]["rectangle_segments"], deck)
    extension = framing["extensions"][0]
    extension_normals = [as_point(normal) for normal in extension["normal_field"]]
    if len(extension_normals) != len(left):
        raise AssertionError("band boundary and framing extension lengths disagree")
    source_normal = as_point(extension["source_normal"])
    target_normal = as_point(extension["target_h_CS_normal"])
    raw_target = [as_point(point) for point in attachment["target_interval"]]
    target = [translate(point, deck) for point in raw_target]
    target_xyz = target[0][:3]
    target_complement = [target[0], (*target_xyz, Fraction(0)), (*target_xyz, Fraction(1)), target[1]]
    lifted_path = [*source_complement, left[0], *left[1:], target[0], *target_complement[1:], right[-1], *reversed(right[:-1]), translate(after, deck)]
    normal_field = (
        [source_normal] * len(source_complement)
        + extension_normals
        + [target_normal] * 4
        + list(reversed(extension_normals))
        + [source_normal]
    )
    if len(normal_field) != len(lifted_path):
        raise AssertionError("quotient splice framing field has the wrong length")
    push_off_path = [
        tuple(point[i] + normal[i] for i in range(4))
        for point, normal in zip(lifted_path, normal_field)
    ]
    expected_end = translate(lifted_path[0], deck)
    if lifted_path[-1] != expected_end:
        raise AssertionError("quotient splice endpoint does not differ by the source deck translation")
    if push_off_path[-1] != translate(push_off_path[0], deck):
        raise AssertionError("quotient push-off endpoint has the wrong deck translation")
    seam_segments = [
        index
        for index, (start, end) in enumerate(zip(lifted_path, lifted_path[1:]))
        if start[:3] == end[:3] and start[3] == 0 and end[3] == 1
    ]
    if len(seam_segments) != 1:
        raise AssertionError("candidate splice does not contain one mapping-torus seam cell")
    result = {
        "schema": "t73_candidate_t_band0_quotient_splice/v1",
        "universal_lifts_sha256": lifts["sha256"],
        "attachment_intervals_sha256": intervals["sha256"],
        "candidate_t_movie_sha256": movie["sha256"],
        "framing_extensions_sha256": framing["sha256"],
        "component": component,
        "band_index": 0,
        "lifted_polyline": [encode(point) for point in lifted_path],
        "normal_field": [encode(normal) for normal in normal_field],
        "push_off_lifted_polyline": [encode(point) for point in push_off_path],
        "mapping_torus_seam_segment_indices": seam_segments,
        "closing_deck_translation": list(deck),
        "completion_status": "CANDIDATE_QUOTIENT_CLOSED_SPLICE",
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
        raise AssertionError("candidate quotient splice is stale")
    print("T73_T_BAND0_QUOTIENT_SPLICE=CANDIDATE_QUOTIENT_CLOSED_SPLICE")


if __name__ == "__main__":
    main()
