#!/usr/bin/env python3
"""Verify the outward state-6 framing and its homotopy exactly."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from build_t73_t_hcs_cancellation_readiness import curve_report, final_states
from build_t73_t_hcs_framing_exteriorization import exteriorize_component
from verify_t73_candidate_t_band0_quotient_splice import (
    candidate_deck_translations,
    translate_segment,
)
from verify_t73_candidate_t_band0_splice import exact_segment_intersection

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_t_hcs_framing_exteriorization.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
BELTS = ROOT / "geometry/t73_belt_spheres.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(values):
    return [[str(coordinate) for coordinate in value] for value in values]


def canonical_sha(value):
    import hashlib

    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def homotopy_hits_zero(old, new):
    parameter = None
    for old_value, new_value in zip(old, new):
        difference = new_value - old_value
        if difference:
            candidate = -old_value / difference
            if parameter is not None and candidate != parameter:
                return False
            parameter = candidate
        elif old_value:
            return False
    return parameter is not None and 0 <= parameter <= 1


def segments(values):
    return list(zip(values, values[1:]))


def verify_changed_push_clearance(component, points, push, seams, changed_vertices, states):
    changed_segments = {
        segment_index
        for vertex in changed_vertices
        for segment_index in (vertex - 1, vertex)
        if 0 <= segment_index < len(points) - 1
    }
    exact_checks = 0
    closing_deck = tuple(
        int((points[-1][axis] - points[0][axis]) / 4) for axis in range(3)
    )
    for push_index in sorted(changed_segments):
        if push_index in seams:
            continue
        push_segment = segments(push)[push_index]
        for other_component, (other_points, _, other_seams) in states.items():
            for core_index, core_segment in enumerate(segments(other_points)):
                if core_index in other_seams:
                    continue
                for deck in candidate_deck_translations(push_segment, core_segment):
                    exact_checks += 1
                    if exact_segment_intersection(
                        push_segment, translate_segment(core_segment, tuple(deck))
                    ):
                        raise AssertionError(
                            f"exteriorized {component} push segment {push_index} meets "
                            f"{other_component} core segment {core_index} at deck {tuple(deck)}"
                        )
        for other_index, other_segment in enumerate(segments(push)):
            if other_index in seams:
                continue
            for deck in candidate_deck_translations(push_segment, other_segment):
                deck = tuple(deck)
                if push_index == other_index and deck == (0, 0, 0):
                    continue
                if abs(push_index - other_index) == 1 and deck == (0, 0, 0):
                    continue
                if (
                    push_index == 0
                    and other_index == len(push) - 2
                    and deck == tuple(-value for value in closing_deck)
                ) or (
                    push_index == len(push) - 2
                    and other_index == 0
                    and deck == closing_deck
                ):
                    continue
                exact_checks += 1
                if exact_segment_intersection(
                    push_segment, translate_segment(other_segment, deck)
                ):
                    raise AssertionError(
                        f"exteriorized {component} push-off intersects at "
                        f"{push_index}/{other_index}/{deck}"
                    )
    return exact_checks


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    if data["completion_status"] != "STATE6_OUTWARD_FRAMING_NORMALS_CONSTRUCTED":
        raise AssertionError("framing exteriorization status changed")
    radius = Fraction(belts["t_handle"]["belt_sphere"]["radius"])
    states = final_states()
    exact_checks = 0
    total_replacements = 0
    minimum_clearances = {}
    for component, (points, old_normals, seams) in states.items():
        record = data["components"][component]
        width = Fraction(record["width"])
        new_normals, expected_replacements = exteriorize_component(
            points, old_normals, radius, width
        )
        if record["normal_replacements"] != expected_replacements:
            raise AssertionError("saved outward-normal choices changed")
        if record["exteriorized_normal_field_sha256"] != canonical_sha(encode(new_normals)):
            raise AssertionError("exteriorized normal-field hash changed")
        if any(
            homotopy_hits_zero(old, new)
            for old, new in zip(old_normals, new_normals)
        ):
            raise AssertionError("linear normal homotopy crosses the zero section")
        push = [
            tuple(value[axis] + normal[axis] for axis in range(4))
            for value, normal in zip(points, new_normals)
        ]
        if record["exteriorized_push_off_sha256"] != canonical_sha(encode(push)):
            raise AssertionError("exteriorized push-off hash changed")
        report = curve_report(push, seams, radius)
        if report["segments_below_open_t_ball_boundary"]:
            raise AssertionError("exteriorized push-off still enters the t-ball")
        minimum_clearances[component] = str(Fraction(report["minimum_l1"]) - radius)
        changed_vertices = [item["vertex_index"] for item in expected_replacements]
        exact_checks += verify_changed_push_clearance(
            component, points, push, seams, changed_vertices, states
        )
        total_replacements += len(expected_replacements)
    return {
        "verdict": "PASS_STATE6_FRAMING_EXTERIORIZATION",
        "normal_replacements": total_replacements,
        "minimum_clearance_above_belt_radius": minimum_clearances,
        "exact_changed_push_clearance_checks": exact_checks,
        "linear_normal_homotopy_avoids_zero": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
