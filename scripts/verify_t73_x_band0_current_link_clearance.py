#!/usr/bin/env python3
"""Verify x-band 0 disk/push clearance from the actual positive-belt state."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from verify_t73_candidate_t_band0_relative_contacts import verify_contacts
from verify_t73_candidate_t_band0_surface import segment_meets_triangle

ROOT = Path(__file__).resolve().parents[1]
SURFACE = ROOT / "geometry/t73_x_band0_attachment_surface.json"
STATE = ROOT / "geometry/t73_x_positive_belt_state0.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def segments(values):
    return list(zip(values, values[1:]))


def verify() -> dict:
    surface = json.loads(SURFACE.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state["completion_status"] != "ACTUAL_POSITIVE_X_BELT_PASSAGE_STATE0":
        raise AssertionError("positive x-belt state scope changed")
    vertices = [point(value) for value in surface["vertices"]]
    pushed = [point(value) for value in surface["push_off_vertices"]]
    triangle_ids = surface["triangles"]
    triangles = [tuple(vertices[index] for index in ids) for ids in triangle_ids]
    push_triangles = [tuple(pushed[index] for index in ids) for ids in triangle_ids]
    source_edge = tuple(
        vertices[index] for index in surface["boundary"]["source_attachment"]
    )
    source_arc = next(item for item in state["arcs"] if item["source_id"] == surface["source_id"])
    source_contacts = verify_contacts(
        triangles,
        segments([point(value) for value in source_arc["polyline"]]),
        source_edge,
        False,
    )
    if not source_contacts:
        raise AssertionError("x-band 0 lost its source attachment")

    exact_checks = 0
    for arc in state["arcs"]:
        arc_segments = segments([point(value) for value in arc["polyline"]])
        if arc["source_id"] != surface["source_id"]:
            for triangle in triangles:
                for segment in arc_segments:
                    exact_checks += 1
                    if segment_meets_triangle(segment, triangle):
                        raise AssertionError(
                            f"x-band 0 disk meets current arc {arc['source_id']}"
                        )
        for triangle in push_triangles:
            for segment in arc_segments:
                exact_checks += 1
                if segment_meets_triangle(segment, triangle):
                    raise AssertionError(
                        f"x-band 0 push disk meets current arc {arc['source_id']}"
                    )

    target_edge = tuple(
        vertices[index] for index in surface["boundary"]["target_attachment"]
    )
    target_center = tuple((first + second) / 2 for first, second in zip(*target_edge))
    target_parallel = [
        (Fraction(1), *target_center[1:]),
        (Fraction(2), *target_center[1:]),
        (Fraction(3), *target_center[1:]),
    ]
    target_contacts = verify_contacts(
        triangles, segments(target_parallel), target_edge, False
    )
    if not target_contacts:
        raise AssertionError("x-band 0 lost its target-parallel attachment")
    return {
        "verdict": "PASS_X_BAND0_CURRENT_LINK_AND_PUSH_CLEARANCE",
        "current_passage_arcs": len(state["arcs"]),
        "source_triangle_contacts": source_contacts,
        "target_triangle_contacts": target_contacts,
        "exact_segment_triangle_checks": exact_checks,
        "scope": "POSITIVE_X_BELT_LOCAL_FRAMED_SLIDE_DISK",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
