#!/usr/bin/env python3
"""Verify the complete framed m1 parallel used by x-band 0."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from build_t73_t_hcs_cancellation_readiness import final_states
from verify_t73_candidate_t_band0_quotient_splice import (
    candidate_deck_translations,
    translate_segment,
)
from verify_t73_candidate_t_band0_splice import exact_segment_intersection
from verify_t73_t_band_sequential_movie import verify_spatial_dual_clearance

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_band0_m1_parallel.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def segments(values):
    return list(zip(values, values[1:]))


def homotopy_hits_zero(first, second):
    parameter = None
    for left, right in zip(first, second):
        difference = right - left
        if difference:
            candidate = -left / difference
            if parameter is not None and candidate != parameter:
                return False
            parameter = candidate
        elif left:
            return False
    return parameter is not None and 0 <= parameter <= 1


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    if data["completion_status"] != "X_BAND0_COMPLETE_FRAMED_M1_PARALLEL_CONSTRUCTED":
        raise AssertionError("m1 parallel scope changed")
    base = [point(value) for value in data["base_vertices"]]
    parallel = [point(value) for value in data["parallel_vertices"]]
    offsets = [point(value) for value in data["framing_offsets"]]
    old_offsets = [
        point(value) for value in data["framing_offsets_before_local_adjustment"]
    ]
    if base != final_states()["m_1"][0]:
        raise AssertionError("m1 parallel base differs from state 6")
    if any(
        tuple(value[axis] + offset[axis] for axis in range(4)) != pushed
        for value, offset, pushed in zip(base, offsets, parallel)
    ):
        raise AssertionError("m1 parallel is not base plus framing offset")
    if any(homotopy_hits_zero(first, second) for first, second in zip(old_offsets, offsets)):
        raise AssertionError("local m1 framing adjustment crosses zero")
    deck = (-1, 0, 1)
    if parallel[-1] != tuple(
        parallel[0][axis] + 4 * deck[axis] for axis in range(3)
    ) + (parallel[0][3],):
        raise AssertionError("m1 parallel has the wrong deck closure")
    seams = set(data["mapping_torus_seam_segment_indices"])
    exact_checks = 0
    base_segments = segments(base)
    parallel_segments = segments(parallel)
    for base_index, base_segment in enumerate(base_segments):
        if base_index in seams:
            continue
        for parallel_index, parallel_segment in enumerate(parallel_segments):
            if parallel_index in seams:
                continue
            for translation in candidate_deck_translations(base_segment, parallel_segment):
                exact_checks += 1
                if exact_segment_intersection(
                    base_segment, translate_segment(parallel_segment, tuple(translation))
                ):
                    raise AssertionError("m1 meets its twentieth framed parallel")
    states = final_states()
    for component in ("m_2", "m_3"):
        other_points, _, other_seams = states[component]
        for parallel_index, parallel_segment in enumerate(parallel_segments):
            if parallel_index in seams:
                continue
            for other_index, other_segment in enumerate(segments(other_points)):
                if other_index in other_seams:
                    continue
                for translation in candidate_deck_translations(parallel_segment, other_segment):
                    exact_checks += 1
                    if exact_segment_intersection(
                        parallel_segment, translate_segment(other_segment, tuple(translation))
                    ):
                        raise AssertionError(f"m1 parallel meets current {component}")
    dual_checks = verify_spatial_dual_clearance([parallel], ar_link)
    target = [point(value) for value in data["target_interval_global"]]
    start, end = data["local_adjustment_vertex_range"]
    if not (
        target[0][0] <= parallel[start + 1][0] <= target[1][0]
        or target[1][0] <= parallel[start + 1][0] <= target[0][0]
    ):
        raise AssertionError("target interval does not contain the parallel arc center")
    return {
        "verdict": "PASS_X_BAND0_COMPLETE_FRAMED_M1_PARALLEL",
        "parallel_coefficient": data["parallel_coefficient"],
        "vertices": len(parallel),
        "exact_core_clearance_checks": exact_checks,
        "exact_dual_projection_checks": dual_checks,
        "local_framing_homotopy_nonzero": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
