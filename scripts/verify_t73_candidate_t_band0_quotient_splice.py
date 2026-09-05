#!/usr/bin/env python3
"""Check the first candidate t-band splice modulo the T3 deck group."""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from pathlib import Path

from verify_t73_candidate_t_band0_splice import exact_segment_intersection

ROOT = Path(__file__).resolve().parents[1]
SPLICE = ROOT / "geometry/t73_candidate_t_band0_quotient_splice.json"
PERIOD = Fraction(4)


def floor(value: Fraction) -> int:
    return value.numerator // value.denominator


def ceil(value: Fraction) -> int:
    return -floor(-value)


def translate_segment(segment, deck):
    return tuple(
        tuple(point[axis] + PERIOD * deck[axis] for axis in range(3)) + (point[3],)
        for point in segment
    )


def candidate_deck_translations(first, second):
    ranges = []
    for axis in range(3):
        first_low, first_high = sorted((first[0][axis], first[1][axis]))
        second_low, second_high = sorted((second[0][axis], second[1][axis]))
        low = ceil((first_low - second_high) / PERIOD)
        high = floor((first_high - second_low) / PERIOD)
        if low > high:
            return []
        ranges.append(range(low, high + 1))
    first_u = sorted((first[0][3], first[1][3]))
    second_u = sorted((second[0][3], second[1][3]))
    if first_u[1] < second_u[0] or second_u[1] < first_u[0]:
        return []
    return itertools.product(*ranges)


def verify() -> dict:
    data = json.loads(SPLICE.read_text(encoding="utf-8"))
    if data["completion_status"] != "CANDIDATE_QUOTIENT_CLOSED_SPLICE":
        raise AssertionError("candidate quotient splice status changed")
    points = [tuple(Fraction(value) for value in point) for point in data["lifted_polyline"]]
    deck = tuple(data["closing_deck_translation"])
    expected_end = tuple(points[0][axis] + PERIOD * deck[axis] for axis in range(3)) + (points[0][3],)
    if points[-1] != expected_end:
        raise AssertionError("lifted splice is not closed by its deck translation")
    normals = [tuple(Fraction(value) for value in normal) for normal in data["normal_field"]]
    push_points = [tuple(Fraction(value) for value in point) for point in data["push_off_lifted_polyline"]]
    if len(normals) != len(points) or len(push_points) != len(points):
        raise AssertionError("quotient splice framing arrays have incompatible lengths")
    for point, normal, pushed in zip(points, normals, push_points):
        if tuple(point[i] + normal[i] for i in range(4)) != pushed:
            raise AssertionError("quotient splice push-off is not core plus normal")
    expected_push_end = tuple(push_points[0][axis] + PERIOD * deck[axis] for axis in range(3)) + (push_points[0][3],)
    if push_points[-1] != expected_push_end:
        raise AssertionError("quotient push-off has the wrong closing deck translation")
    segments = list(zip(points, points[1:]))
    seam_segments = set(data["mapping_torus_seam_segment_indices"])
    if len(seam_segments) != 1:
        raise AssertionError("candidate splice must have exactly one seam cell")
    seam_index = next(iter(seam_segments))
    seam_start, seam_end = segments[seam_index]
    if seam_start[:3] != seam_end[:3] or (seam_start[3], seam_end[3]) != (0, 1):
        raise AssertionError("mapping-torus seam cell has incompatible endpoints")
    exact_checks = 0
    for left in range(len(segments)):
        for right in range(left, len(segments)):
            if left in seam_segments or right in seam_segments:
                continue
            for translation in candidate_deck_translations(segments[left], segments[right]):
                translation = tuple(translation)
                if left == right and translation == (0, 0, 0):
                    continue
                if right == left + 1 and translation == (0, 0, 0):
                    continue
                if left == 0 and right == len(segments) - 1 and translation == tuple(-value for value in deck):
                    continue
                exact_checks += 1
                translated = translate_segment(segments[right], translation)
                if exact_segment_intersection(segments[left], translated):
                    return {
                        "verdict": "FAIL_CANDIDATE_QUOTIENT_SELF_INTERSECTION",
                        "segments": [left, right],
                        "deck_translation": list(translation),
                        "exact_checks_before_failure": exact_checks,
                    }
    push_segments = list(zip(push_points, push_points[1:]))
    core_push_checks = 0
    for core_index, core_segment in enumerate(segments):
        if core_index in seam_segments:
            continue
        for push_index, push_segment in enumerate(push_segments):
            if push_index in seam_segments:
                continue
            for translation in candidate_deck_translations(core_segment, push_segment):
                core_push_checks += 1
                translated = translate_segment(push_segment, tuple(translation))
                if exact_segment_intersection(core_segment, translated):
                    return {
                        "verdict": "FAIL_CANDIDATE_QUOTIENT_FRAMING_INTERSECTION",
                        "core_segment": core_index,
                        "push_segment": push_index,
                        "deck_translation": list(translation),
                        "exact_checks_before_failure": core_push_checks,
                    }
    return {
        "verdict": "PASS_CANDIDATE_QUOTIENT_FRAMED_EMBEDDEDNESS_ONLY",
        "segments": len(segments),
        "exact_deck_checks": exact_checks,
        "exact_core_push_checks": core_push_checks,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
