#!/usr/bin/env python3
"""Verify the 4D product collar and coverage of all local post-x lanes."""

from __future__ import annotations

import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from build_t73_x_band_local_movie import initial_segment_state, update_segment_state
from verify_t73_x_band_local_movie import expand_band

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
COLLAR = ROOT / "geometry/t73_x_m1_collar_ejection_map.json"
STATE0 = ROOT / "geometry/t73_x_positive_belt_state0.json"
CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
POST_X = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
FRAMING = ROOT / "geometry/t73_x_m1_framing_exteriorization.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def determinant(matrix):
    if len(matrix) == 1:
        return matrix[0][0]
    return sum(((-1) ** column) * matrix[0][column] * determinant([row[:column] + row[column + 1:] for row in matrix[1:]]) for column in range(len(matrix)))


def simplex_determinant(vertices, simplex):
    origin = vertices[simplex[0]]
    return determinant([[vertices[index][axis] - origin[axis] for index in simplex[1:]] for axis in range(4)])


def in_product_shell_segment(segment):
    # The outer cube and x interval are convex. The last transverse coordinate
    # is >=1 along these segments, so they cannot enter the open inner cube.
    return all(Fraction(1) <= value[0] <= 3 and max(abs(x) for x in value[1:]) <= 2 and value[3] >= 1 for value in segment)


def verify():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    collar = json.loads(COLLAR.read_text(encoding="utf-8"))
    state0 = json.loads(STATE0.read_text(encoding="utf-8"))
    cancellation = json.loads(CANCELLATION.read_text(encoding="utf-8"))
    local_movie = json.loads(LOCAL_MOVIE.read_text(encoding="utf-8"))
    post_x = json.loads(POST_X.read_text(encoding="utf-8"))
    framing = json.loads(FRAMING.read_text(encoding="utf-8"))
    if data["sha256"] != canonical_sha({key: value for key, value in data.items() if key != "sha256"}):
        raise AssertionError("x/m1 product collar payload SHA changed")
    if (data["x_m1_collar_ejection_map_sha256"] != collar["sha256"]
            or data["x_band_local_movie_sha256"] != local_movie["sha256"]
            or data["post_x_framed_replacement_cells_receipt_sha256"] != post_x["sha256"]
            or data["x_m1_framing_exteriorization_sha256"] != framing["sha256"]):
        raise AssertionError("x/m1 product collar sources changed")
    source = [point(value) for value in data["source_vertices"]]
    target = [point(value) for value in data["target_vertex_images"]]
    simplices = data["four_simplices"]
    if len(source) != 32 or len(simplices) != 144:
        raise AssertionError("x/m1 product collar cell counts changed")
    ratios = []
    for simplex in simplices:
        before, after = simplex_determinant(source, simplex), simplex_determinant(target, simplex)
        if before == 0 or after == 0 or after / before <= 0:
            raise AssertionError("x/m1 product collar has a degenerate/reversing 4-simplex")
        ratios.append(after / before)
    if any(source[index][0] != target[index][0] for index in range(32)):
        raise AssertionError("x coordinate is not fixed by product collar")
    arcs = {item["source_id"]: item for item in state0["arcs"]}
    segments = initial_segment_state(arcs)
    for band in cancellation["slide_bands"]:
        vertices, _, _, _, _, _, _, _, _, _ = expand_band(band)
        update_segment_state(segments, band, {"vertices": vertices}, arcs[band["source_id"]])
    remaining = {key: value for key, value in segments.items() if not key.startswith("m_1:C_i:")}
    if len(remaining) != 12104 or any(not in_product_shell_segment(value) for value in remaining.values()):
        raise AssertionError("remaining local core is not covered by product collar")
    uniform_push = point(framing["uniform_push_vector"])
    if point(data["exteriorized_uniform_push_vector"]) != uniform_push:
        raise AssertionError("exteriorized push vector changed")
    exteriorized_remaining = {
        key: tuple(tuple(value[axis] + uniform_push[axis] for axis in range(4)) for value in segment)
        for key, segment in remaining.items()
    }
    if any(not in_product_shell_segment(value) for value in exteriorized_remaining.values()):
        raise AssertionError("exteriorized remaining push is not covered by product collar")
    lane_segments = exteriorized_push_segments = original_push_outside = 0
    cache = Path(post_x["cache_path"])
    with gzip.open(cache, "rt", encoding="utf-8") as source_file:
        next(source_file)
        for line in source_file:
            cell = json.loads(line)
            for name in ("negative_band_lane", "positive_band_lane"):
                piece = cell[name]
                values = [point(value) for value in piece["vertices"]]
                old_pushes = [point(value) for value in piece["push_vertices"]]
                new_pushes = [tuple(value[axis] + uniform_push[axis] for axis in range(4)) for value in values]
                for segment in zip(values, values[1:]):
                    if not in_product_shell_segment(segment):
                        raise AssertionError("a band lane leaves the product collar domain")
                    lane_segments += 1
                for segment in zip(old_pushes, old_pushes[1:]):
                    if not in_product_shell_segment(segment):
                        original_push_outside += 1
                for segment in zip(new_pushes, new_pushes[1:]):
                    if not in_product_shell_segment(segment):
                        raise AssertionError("an exteriorized band push leaves the product collar domain")
                    exteriorized_push_segments += 1
    if lane_segments != 6052 or exteriorized_push_segments != 6052 or not original_push_outside:
        raise AssertionError("band-lane coverage count changed")
    return {
        "verdict": "PASS_X_M1_COLLAR_PRODUCT_EXTENSION_AND_OUTWARD_FRAMING_DOMAIN",
        "vertices": 32,
        "four_simplices": 144,
        "minimum_orientation_ratio": str(min(ratios)),
        "remaining_local_segments": len(remaining),
        "band_lane_segments": lane_segments,
        "exteriorized_remaining_push_segments": len(exteriorized_remaining),
        "exteriorized_pushed_band_lane_segments": exteriorized_push_segments,
        "original_push_lane_segments_outside_domain": original_push_outside,
        "full_hybrid_path_image_status": "OPEN_APPLY_PIECEWISE_AFFINE_MAP",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
