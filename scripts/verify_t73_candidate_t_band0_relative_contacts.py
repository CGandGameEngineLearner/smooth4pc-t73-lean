#!/usr/bin/env python3
"""Prove band-0 disk contacts m1/h_CS only along its attachment edges."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from verify_t73_candidate_t_band0_surface import segment_triangle_parameter_interval
from verify_t73_candidate_t_band0_surface_clearance import (
    candidate_translations,
    translate_segment,
)

ROOT = Path(__file__).resolve().parents[1]
SURFACE = ROOT / "geometry/t73_candidate_t_band0_surface.json"
LIFTS = ROOT / "geometry/t73_ar_core_universal_lifts.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def lies_on_segment(value, segment) -> bool:
    start, end = segment
    direction = tuple(end[i] - start[i] for i in range(4))
    delta = tuple(value[i] - start[i] for i in range(4))
    axis = next((i for i, coordinate in enumerate(direction) if coordinate), None)
    if axis is None:
        return value == start
    parameter = delta[axis] / direction[axis]
    return 0 <= parameter <= 1 and all(delta[i] == parameter * direction[i] for i in range(4))


def intersection_endpoints(segment, parameter_interval):
    start, end = segment
    direction = tuple(end[i] - start[i] for i in range(4))
    return [
        tuple(start[i] + parameter * direction[i] for i in range(4))
        for parameter in parameter_interval
    ]


def verify_contacts(triangles, source_segments, allowed_edge, use_deck_translations):
    contacts = 0
    for triangle in triangles:
        for segment in source_segments:
            translated_segments = []
            if use_deck_translations:
                translated_segments = [
                    translate_segment(segment, tuple(deck))
                    for deck in candidate_translations(triangle, segment)
                ]
            else:
                translated_segments = [segment]
            for translated in translated_segments:
                parameter_interval = segment_triangle_parameter_interval(translated, triangle)
                if parameter_interval is None:
                    continue
                contacts += 1
                if any(not lies_on_segment(value, allowed_edge) for value in intersection_endpoints(translated, parameter_interval)):
                    raise AssertionError("band disk has contact outside its declared attachment edge")
    return contacts


def verify() -> dict:
    surface = json.loads(SURFACE.read_text(encoding="utf-8"))
    lifts = json.loads(LIFTS.read_text(encoding="utf-8"))
    vertices = [point(value) for value in surface["vertices"]]
    triangles = [tuple(vertices[index] for index in ids) for ids in surface["triangles"]]
    boundary = surface["boundary"]
    source_edge = tuple(vertices[index] for index in boundary["source_attachment"])
    target_edge = tuple(vertices[index] for index in boundary["target_attachment"])
    m1_points = [point(value) for value in lifts["components"]["m_1"]["lifted_vertices"]]
    m1_segments = list(zip(m1_points, m1_points[1:]))
    source_contacts = verify_contacts(triangles, m1_segments, source_edge, True)
    target_xyz = target_edge[0][:3]
    hcs_parallel = ((*target_xyz, Fraction(0)), (*target_xyz, Fraction(1)))
    target_contacts = verify_contacts(triangles, [hcs_parallel], target_edge, False)
    if source_contacts == 0 or target_contacts == 0:
        raise AssertionError("band disk lost a declared attachment contact")
    return {
        "verdict": "PASS_CANDIDATE_BAND0_RELATIVE_CONTACTS_ONLY",
        "source_triangle_segment_contacts": source_contacts,
        "target_triangle_segment_contacts": target_contacts,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
