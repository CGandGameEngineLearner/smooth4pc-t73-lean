#!/usr/bin/env python3
"""Verify band-0 disk boundary against actual attachment records and movie lanes."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SURFACE = ROOT / "geometry/t73_candidate_t_band0_surface.json"
LIFTS = ROOT / "geometry/t73_ar_core_universal_lifts.json"
INTERVALS = ROOT / "geometry/t73_t_band_attachment_intervals.json"
MOVIE = ROOT / "geometry/t73_candidate_t_band_movie.json"
FRAMING = ROOT / "geometry/t73_t_band_framing_extensions.json"
PERIOD = Fraction(4)


def point(values):
    return tuple(Fraction(value) for value in values)


def translate(value, deck):
    return tuple(value[axis] + PERIOD * deck[axis] for axis in range(3)) + (value[3],)


def interpolate(origin, neighbour, parameter):
    return tuple(origin[index] + parameter * (neighbour[index] - origin[index]) for index in range(4))


def boundary_lane_points(segments):
    left = [point(segments[0]["band_vertices"][0])]
    right = [point(segments[0]["band_vertices"][3])]
    for segment in segments:
        left.append(point(segment["band_vertices"][1]))
        right.append(point(segment["band_vertices"][2]))
    return left, right


def verify() -> dict:
    surface = json.loads(SURFACE.read_text(encoding="utf-8"))
    lifts = json.loads(LIFTS.read_text(encoding="utf-8"))
    intervals = json.loads(INTERVALS.read_text(encoding="utf-8"))
    movie = json.loads(MOVIE.read_text(encoding="utf-8"))
    framing = json.loads(FRAMING.read_text(encoding="utf-8"))
    vertices = [point(value) for value in surface["vertices"]]
    normals = [point(value) for value in surface["normal_field"]]
    attachment = intervals["intervals"][0]
    component_lift = lifts["components"][attachment["component"]]
    lifted_core = [point(value) for value in component_lift["lifted_vertices"]]
    deck = tuple(component_lift["closing_deck_translation"])
    index = attachment["source_core_vertex_index"]
    width = Fraction(attachment["source_parameter_from_vertex"])
    expected_source = [
        translate(interpolate(lifted_core[index], lifted_core[index - 1], width), deck),
        translate(interpolate(lifted_core[index], lifted_core[index + 1], width), deck),
    ]
    expected_target = [translate(point(value), deck) for value in attachment["target_interval"]]
    boundary = surface["boundary"]
    if [vertices[item] for item in boundary["source_attachment"]] != expected_source:
        raise AssertionError("band disk source edge is not the lifted actual attachment interval")
    if [vertices[item] for item in boundary["target_attachment"]] != expected_target:
        raise AssertionError("band disk target edge is not the parallel h_CS interval")
    raw_left, raw_right = boundary_lane_points(movie["bands"][0]["rectangle_segments"])
    left = [expected_source[0], *[translate(value, deck) for value in raw_left], expected_target[0]]
    right = [expected_target[1], *[translate(value, deck) for value in reversed(raw_right)], expected_source[1]]
    if [vertices[item] for item in boundary["left_lane"]] != left:
        raise AssertionError("band disk left boundary is not the movie lane")
    if [vertices[item] for item in boundary["right_lane"]] != right:
        raise AssertionError("band disk right boundary is not the movie lane")
    extension = framing["extensions"][0]
    source_normal = point(extension["source_normal"])
    target_normal = point(extension["target_h_CS_normal"])
    if any(normals[item] != source_normal for item in boundary["source_attachment"]):
        raise AssertionError("source boundary framing does not match the actual component")
    if any(normals[item] != target_normal for item in boundary["target_attachment"]):
        raise AssertionError("target boundary framing does not match h_CS")
    return {
        "verdict": "PASS_CANDIDATE_BAND0_RELATIVE_BOUNDARY_ONLY",
        "source_component": attachment["component"],
        "band_index": 0,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
