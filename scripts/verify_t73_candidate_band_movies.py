#!/usr/bin/env python3
"""Independently verify the candidate t/x framed-band movie records.

The verdict is deliberately candidate-only.  This verifier proves exact PL
record consistency; it does not identify the chosen rectangles with the
actual Aitchison--Rubinstein Kirby movie.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from t73_pl_kirby_moves import BandRectangle, as_point, encode

ROOT = Path(__file__).resolve().parents[1]
RECTANGLES = ROOT / "geometry/t73_candidate_band_rectangles.json"
SPLICES = ROOT / "geometry/t73_candidate_band_splice_descriptors.json"
MOVIES = {
    "t": ROOT / "geometry/t73_candidate_t_band_movie.json",
    "x": ROOT / "geometry/t73_candidate_x_band_movie.json",
}
SOURCES = {
    "t": ROOT / "geometry/t73_cancel_t_hcs.json",
    "x": ROOT / "geometry/t73_cancel_x_m1.json",
}
EXPECTED_COUNTS = {"t": 6, "x": 1513}


def subtract(left: tuple, right: tuple) -> tuple:
    return tuple(a - b for a, b in zip(left, right))


def verify_rectangle(segment: dict[str, Any]) -> None:
    start, end = (as_point(point) for point in segment["centerline"])
    normal = as_point(segment["normal"])
    recorded_vertices = tuple(as_point(point) for point in segment["band_vertices"])
    recorded_push = tuple(as_point(point) for point in segment["push_off_vertices"])
    push_normal = subtract(recorded_push[0], recorded_vertices[0])
    rectangle = BandRectangle(start, end, normal, push_normal)
    if tuple(encode(point) for point in rectangle.vertices()) != tuple(segment["band_vertices"]):
        raise AssertionError("candidate band rectangle vertices changed")
    if tuple(encode(point) for point in rectangle.push_off_vertices()) != tuple(segment["push_off_vertices"]):
        raise AssertionError("candidate band push-off vertices changed")
    if segment["band_triangles"] != [[0, 1, 2], [0, 2, 3]]:
        raise AssertionError("candidate band triangulation changed")
    if segment["band_boundary"] != [[0, 1], [3, 2], [0, 3], [1, 2]]:
        raise AssertionError("candidate band boundary changed")


def verify_movie(
    kind: str,
    movie: dict[str, Any],
    source: dict[str, Any],
    rectangle_lookup: dict[tuple[str, int, int], dict[str, Any]],
    splice_lookup: dict[tuple[str, int], dict[str, Any]],
) -> set[tuple[str, int, int]]:
    if movie["completion_status"] != "CANDIDATE_UNVERIFIED":
        raise AssertionError("candidate band movie was promoted")
    expected_count = EXPECTED_COUNTS[kind]
    if len(movie["bands"]) != expected_count:
        raise AssertionError(f"{kind}-band movie count changed")
    source_by_index = {band["index"]: band for band in source["slide_bands"]}
    used: set[tuple[str, int, int]] = set()
    for position, band in enumerate(movie["bands"]):
        if band["index"] != position or band["movie_time_order"] != position:
            raise AssertionError(f"{kind}-band movie order changed")
        original = source_by_index[position]
        if band["component"] != original["component"]:
            raise AssertionError(f"{kind}-band component binding changed")
        if band["current_link_before"] != f"candidate_{kind}_state_{position}":
            raise AssertionError(f"{kind}-band source state chain changed")
        if band["updated_link_after"] != f"candidate_{kind}_state_{position + 1}":
            raise AssertionError(f"{kind}-band target state chain changed")
        descriptor = splice_lookup[(kind, position)]
        if band["splice"] != descriptor:
            raise AssertionError(f"{kind}-band splice binding changed")
        if band["source_attachment"] != descriptor["source_attachment"] or band["target_attachment"] != descriptor["target_attachment"]:
            raise AssertionError(f"{kind}-band attachment binding changed")
        previous_end = None
        for segment_position, segment in enumerate(band["rectangle_segments"]):
            key = (kind, position, segment_position)
            if segment != rectangle_lookup[key]:
                raise AssertionError(f"{kind}-band rectangle binding changed")
            if previous_end is not None and segment["centerline"][0] != previous_end:
                raise AssertionError(f"{kind}-band centerline is discontinuous")
            previous_end = segment["centerline"][1]
            verify_rectangle(segment)
            used.add(key)
    return used


def verify() -> dict[str, Any]:
    rectangles = json.loads(RECTANGLES.read_text(encoding="utf-8"))
    splices = json.loads(SPLICES.read_text(encoding="utf-8"))
    rectangle_lookup = {
        (item["kind"], item["index"], item["segment_index"]): item
        for item in rectangles["bands"]
    }
    splice_lookup = {(item["kind"], item["index"]): item for item in splices["bands"]}
    used: set[tuple[str, int, int]] = set()
    for kind in ("t", "x"):
        movie = json.loads(MOVIES[kind].read_text(encoding="utf-8"))
        source = json.loads(SOURCES[kind].read_text(encoding="utf-8"))
        used |= verify_movie(kind, movie, source, rectangle_lookup, splice_lookup)
    if used != set(rectangle_lookup):
        raise AssertionError("candidate band movies do not cover every rectangle segment")
    return {
        "verdict": "PASS_CANDIDATE_MOVIE_RECORDS_ONLY",
        "bands": sum(EXPECTED_COUNTS.values()),
        "rectangle_segments": len(used),
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
