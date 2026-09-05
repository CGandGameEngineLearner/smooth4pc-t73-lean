#!/usr/bin/env python3
"""Construct the first t-band candidate slide as an explicit closed polyline."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from t73_pl_kirby_moves import as_point, encode, validate_polyline

ROOT = Path(__file__).resolve().parents[1]
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
INTERVALS = ROOT / "geometry/t73_t_band_attachment_intervals.json"
MOVIE = ROOT / "geometry/t73_candidate_t_band_movie.json"
OUTPUT = ROOT / "geometry/t73_candidate_t_band0_splice.json"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def cycle_without_duplicate(points: list[list[str]]) -> list[tuple[Fraction, ...]]:
    cycle = [as_point(point) for point in points]
    return cycle[:-1] if cycle[0] == cycle[-1] else cycle


def remaining_source_arc(cycle: list[tuple[Fraction, ...]], vertex: int,
                         source_interval: list[tuple[Fraction, ...]]) -> list[tuple[Fraction, ...]]:
    before, after = source_interval
    return [after, *cycle[vertex + 1 :], *cycle[:vertex], before]


def band_boundary_lanes(segments: list[dict[str, Any]]) -> tuple[list[tuple[Fraction, ...]], list[tuple[Fraction, ...]]]:
    left = [as_point(segments[0]["band_vertices"][0])]
    right = [as_point(segments[0]["band_vertices"][3])]
    for segment in segments:
        left.append(as_point(segment["band_vertices"][1]))
        right.append(as_point(segment["band_vertices"][2]))
    return left, right


def build() -> dict[str, Any]:
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    intervals = json.loads(INTERVALS.read_text(encoding="utf-8"))
    movie = json.loads(MOVIE.read_text(encoding="utf-8"))
    attachment = intervals["intervals"][0]
    band = movie["bands"][0]
    component = attachment["component"]
    cycle = cycle_without_duplicate(ar_link["components"][component]["core_polyline_T3xI"])
    source_interval = [as_point(point) for point in attachment["source_interval"]]
    target_interval = [as_point(point) for point in attachment["target_interval"]]
    source_arc = remaining_source_arc(cycle, attachment["source_core_vertex_index"], source_interval)
    left, right = band_boundary_lanes(band["rectangle_segments"])
    target_xyz = target_interval[0][:3]
    target_complement = [
        target_interval[0], (*target_xyz, Fraction(0)),
        (*target_xyz, Fraction(1)), target_interval[1],
    ]
    closed = [
        *source_arc,
        left[0], *left[1:], target_interval[0],
        *target_complement[1:], right[-1], *reversed(right[:-1]),
        source_arc[0],
    ]
    validate_polyline(closed)
    if closed[0] != closed[-1]:
        raise AssertionError("candidate t-band splice is not closed")
    result = {
        "schema": "t73_candidate_t_band0_splice/v1",
        "ar_link_sha256": ar_link["sha256"],
        "attachment_intervals_sha256": intervals["sha256"],
        "candidate_t_movie_sha256": movie["sha256"],
        "band_index": 0,
        "component": component,
        "closed_core_polyline_T3xI": [encode(point) for point in closed],
        "vertex_count": len(closed),
        "completion_status": "CANDIDATE_CLOSED_SPLICE_ONLY",
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
        raise AssertionError("candidate first t-band splice is stale")
    print(f"T73_T_BAND0_SPLICE={result['completion_status']}")


if __name__ == "__main__":
    main()
