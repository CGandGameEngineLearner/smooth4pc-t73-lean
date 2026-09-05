#!/usr/bin/env python3
"""Check candidate band-0 disk/push clearance from the other five core curves."""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from pathlib import Path

from verify_t73_candidate_t_band0_surface import segment_meets_triangle

ROOT = Path(__file__).resolve().parents[1]
SURFACE = ROOT / "geometry/t73_candidate_t_band0_surface.json"
ACTUAL_LIFTS = ROOT / "geometry/t73_ar_core_universal_lifts.json"
DUAL_LIFTS = ROOT / "geometry/t73_candidate_dual_core_lifts.json"
PERIOD = Fraction(4)


def floor(value: Fraction) -> int:
    return value.numerator // value.denominator


def ceil(value: Fraction) -> int:
    return -floor(-value)


def candidate_translations(triangle, segment):
    ranges = []
    for axis in range(3):
        triangle_low = min(point[axis] for point in triangle)
        triangle_high = max(point[axis] for point in triangle)
        segment_low, segment_high = sorted((segment[0][axis], segment[1][axis]))
        low = ceil((triangle_low - segment_high) / PERIOD)
        high = floor((triangle_high - segment_low) / PERIOD)
        if low > high:
            return []
        ranges.append(range(low, high + 1))
    triangle_u = (min(point[3] for point in triangle), max(point[3] for point in triangle))
    segment_u = sorted((segment[0][3], segment[1][3]))
    if triangle_u[1] < segment_u[0] or segment_u[1] < triangle_u[0]:
        return []
    return itertools.product(*ranges)


def translate_segment(segment, deck):
    return tuple(
        tuple(point[axis] + PERIOD * deck[axis] for axis in range(3)) + (point[3],)
        for point in segment
    )


def verify() -> dict:
    surface = json.loads(SURFACE.read_text(encoding="utf-8"))
    actual = json.loads(ACTUAL_LIFTS.read_text(encoding="utf-8"))["components"]
    dual = json.loads(DUAL_LIFTS.read_text(encoding="utf-8"))["components"]
    triangles = surface["triangles"]
    surface_vertices = [tuple(Fraction(value) for value in point) for point in surface["vertices"]]
    push_vertices = [tuple(Fraction(value) for value in point) for point in surface["push_off_vertices"]]
    other_components = {"m_2": actual["m_2"], "m_3": actual["m_3"], **dual}
    exact_checks = 0
    broad_phase_pairs = 0
    broad_phase_rejections = 0
    for disk_kind, vertices in (("disk", surface_vertices), ("push_disk", push_vertices)):
        for triangle_index, triangle_ids in enumerate(triangles):
            triangle = tuple(vertices[index] for index in triangle_ids)
            for component, component_lift in other_components.items():
                points = [tuple(Fraction(value) for value in point) for point in component_lift["lifted_vertices"]]
                for segment_index, segment in enumerate(zip(points, points[1:])):
                    broad_phase_pairs += 1
                    translations = list(candidate_translations(triangle, segment))
                    if not translations:
                        broad_phase_rejections += 1
                    for deck in translations:
                        exact_checks += 1
                        translated = translate_segment(segment, tuple(deck))
                        if segment_meets_triangle(translated, triangle):
                            return {
                                "verdict": "FAIL_CANDIDATE_BAND_SURFACE_CLEARANCE",
                                "disk_kind": disk_kind,
                                "triangle": triangle_index,
                                "other_component": component,
                                "other_segment": segment_index,
                                "deck_translation": list(deck),
                                "exact_checks_before_failure": exact_checks,
                            }
    return {
        "verdict": "PASS_CANDIDATE_BAND_SURFACE_OTHER_CORE_CLEARANCE_ONLY",
        "checked_actual_components": ["m_2", "m_3"],
        "checked_candidate_dual_components": ["r_xy", "r_yz", "r_zx"],
        "exact_segment_triangle_checks": exact_checks,
        "broad_phase_pairs": broad_phase_pairs,
        "broad_phase_rejections": broad_phase_rejections,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
