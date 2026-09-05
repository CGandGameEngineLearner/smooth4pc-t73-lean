#!/usr/bin/env python3
"""Check band-0 candidate core clearance from actual m2/m3 AR core lifts."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from verify_t73_candidate_t_band0_quotient_splice import (
    candidate_deck_translations,
    translate_segment,
)
from verify_t73_candidate_t_band0_splice import exact_segment_intersection

ROOT = Path(__file__).resolve().parents[1]
SPLICE = ROOT / "geometry/t73_candidate_t_band0_quotient_splice.json"
LIFTS = ROOT / "geometry/t73_ar_core_universal_lifts.json"
DUAL_LIFTS = ROOT / "geometry/t73_candidate_dual_core_lifts.json"


def segments(points):
    return list(zip(points, points[1:]))


def verify() -> dict:
    splice = json.loads(SPLICE.read_text(encoding="utf-8"))
    lifts = json.loads(LIFTS.read_text(encoding="utf-8"))
    dual_lifts = json.loads(DUAL_LIFTS.read_text(encoding="utf-8"))
    candidate_paths = {
        "core": [tuple(Fraction(value) for value in point) for point in splice["lifted_polyline"]],
        "push_off": [tuple(Fraction(value) for value in point) for point in splice["push_off_lifted_polyline"]],
    }
    seam = set(splice["mapping_torus_seam_segment_indices"])
    exact_checks = 0
    other_components = {
        "m_2": lifts["components"]["m_2"],
        "m_3": lifts["components"]["m_3"],
        **dual_lifts["components"],
    }
    for component, component_lift in other_components.items():
        other_points = [
            tuple(Fraction(value) for value in point)
            for point in component_lift["lifted_vertices"]
        ]
        for candidate_kind, candidate_points in candidate_paths.items():
            for candidate_index, candidate_segment in enumerate(segments(candidate_points)):
                if candidate_index in seam:
                    continue
                for other_index, other_segment in enumerate(segments(other_points)):
                    for deck in candidate_deck_translations(candidate_segment, other_segment):
                        exact_checks += 1
                        translated = translate_segment(other_segment, tuple(deck))
                        if exact_segment_intersection(candidate_segment, translated):
                            return {
                                "verdict": "FAIL_CANDIDATE_FRAMED_CORE_CLEARANCE",
                                "candidate_kind": candidate_kind,
                                "other_component": component,
                                "candidate_segment": candidate_index,
                                "other_segment": other_index,
                                "deck_translation": list(deck),
                                "exact_checks_before_failure": exact_checks,
                            }
    return {
        "verdict": "PASS_CANDIDATE_FRAMED_ALL_CORE_CLEARANCE_ONLY",
        "checked_actual_components": ["m_2", "m_3"],
        "checked_candidate_dual_components": ["r_xy", "r_yz", "r_zx"],
        "exact_deck_checks": exact_checks,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
