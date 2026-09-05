#!/usr/bin/env python3
"""Construct the complete candidate band-0 disk between its attachment intervals."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from build_t73_candidate_t_band0_quotient_splice import (
    boundary_lanes,
    interpolate,
    translate,
)
from t73_pl_kirby_moves import as_point, encode

ROOT = Path(__file__).resolve().parents[1]
LIFTS = ROOT / "geometry/t73_ar_core_universal_lifts.json"
INTERVALS = ROOT / "geometry/t73_t_band_attachment_intervals.json"
MOVIE = ROOT / "geometry/t73_candidate_t_band_movie.json"
FRAMING = ROOT / "geometry/t73_t_band_framing_extensions.json"
OUTPUT = ROOT / "geometry/t73_candidate_t_band0_surface.json"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def add(point, normal):
    return tuple(point[index] + normal[index] for index in range(4))


def build() -> dict[str, Any]:
    lifts = json.loads(LIFTS.read_text(encoding="utf-8"))
    intervals = json.loads(INTERVALS.read_text(encoding="utf-8"))
    movie = json.loads(MOVIE.read_text(encoding="utf-8"))
    framing = json.loads(FRAMING.read_text(encoding="utf-8"))
    attachment = intervals["intervals"][0]
    component_lift = lifts["components"][attachment["component"]]
    deck = tuple(component_lift["closing_deck_translation"])
    lifted_core = [as_point(point) for point in component_lift["lifted_vertices"]]
    index = attachment["source_core_vertex_index"]
    width = Fraction(attachment["source_parameter_from_vertex"])
    source_pair = [
        translate(interpolate(lifted_core[index], lifted_core[index - 1], width), deck),
        translate(interpolate(lifted_core[index], lifted_core[index + 1], width), deck),
    ]
    band = movie["bands"][0]
    left, right = boundary_lanes(band["rectangle_segments"], deck)
    target_pair = [translate(as_point(point), deck) for point in attachment["target_interval"]]
    cross_sections = [source_pair, *[[a, b] for a, b in zip(left, right)], target_pair]
    vertices = [point for pair in cross_sections for point in pair]
    triangles = []
    for section in range(len(cross_sections) - 1):
        a, b = 2 * section, 2 * section + 1
        c, d = 2 * section + 2, 2 * section + 3
        triangles.extend([[a, c, d], [a, d, b]])
    extension = framing["extensions"][0]
    section_normals = [
        as_point(extension["source_normal"]),
        *[as_point(normal) for normal in extension["normal_field"]],
        as_point(extension["target_h_CS_normal"]),
    ]
    if len(section_normals) != len(cross_sections):
        raise AssertionError("band surface and framing cross-section counts disagree")
    vertex_normals = [normal for normal in section_normals for _ in range(2)]
    push_vertices = [add(point, normal) for point, normal in zip(vertices, vertex_normals)]
    last = len(cross_sections) - 1
    boundary = {
        "source_attachment": [0, 1],
        "left_lane": [2 * section for section in range(len(cross_sections))],
        "target_attachment": [2 * last, 2 * last + 1],
        "right_lane": [2 * section + 1 for section in reversed(range(len(cross_sections)))],
    }
    result = {
        "schema": "t73_candidate_t_band0_surface/v1",
        "universal_lifts_sha256": lifts["sha256"],
        "attachment_intervals_sha256": intervals["sha256"],
        "candidate_t_movie_sha256": movie["sha256"],
        "framing_extensions_sha256": framing["sha256"],
        "band_index": 0,
        "vertices": [encode(point) for point in vertices],
        "triangles": triangles,
        "boundary": boundary,
        "normal_field": [encode(normal) for normal in vertex_normals],
        "push_off_vertices": [encode(point) for point in push_vertices],
        "completion_status": "CANDIDATE_FRAMED_BAND_DISK",
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
        raise AssertionError("candidate t-band0 surface is stale")
    print("T73_T_BAND0_SURFACE=CANDIDATE_FRAMED_BAND_DISK")


if __name__ == "__main__":
    main()
