#!/usr/bin/env python3
"""Measure the exact remaining gate before cancelling t against h_CS."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import verify_t73_t_band_sequential_movie as replay

ROOT = Path(__file__).resolve().parents[1]
MOVIE = ROOT / "geometry/t73_t_band_sequential_movie.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
LIFTS = ROOT / "geometry/t73_ar_core_universal_lifts.json"
INTERVALS = ROOT / "geometry/t73_t_band_attachment_intervals.json"
COLLARS = ROOT / "geometry/t73_t_band_collar_surfaces.json"
BELTS = ROOT / "geometry/t73_belt_spheres.json"
LEGACY_CANCELLATION = ROOT / "geometry/t73_cancel_t_hcs.json"
OUTPUT = ROOT / "audit/t73_t_hcs_cancellation_readiness.json"
EXTERIORIZATION = ROOT / "geometry/t73_t_hcs_framing_exteriorization.json"
PERIOD = Fraction(4)


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def symmetric_coordinate(value):
    return value - PERIOD * ((value + PERIOD / 2) // PERIOD)


def closest_lift(value, reference):
    candidates = [value + PERIOD * shift for shift in range(-2, 3)]
    return min(candidates, key=lambda candidate: abs(candidate - reference))


def segment_l1_minimum(segment):
    start, end = segment
    start_spatial = [symmetric_coordinate(value) for value in start[:3]]
    raw_end = [symmetric_coordinate(value) for value in end[:3]]
    end_spatial = [
        closest_lift(value, start_spatial[axis])
        for axis, value in enumerate(raw_end)
    ]
    parameters = {Fraction(0), Fraction(1)}
    for start_value, end_value in zip(start_spatial, end_spatial):
        if start_value == end_value:
            continue
        zero = -start_value / (end_value - start_value)
        if 0 < zero < 1:
            parameters.add(zero)
    values = [
        (
            sum(
                abs(start_spatial[axis] + parameter * (end_spatial[axis] - start_spatial[axis]))
                for axis in range(3)
            ),
            parameter,
        )
        for parameter in parameters
    ]
    return min(values)


def final_states():
    movie = json.loads(MOVIE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    lifts = json.loads(LIFTS.read_text(encoding="utf-8"))
    intervals = json.loads(INTERVALS.read_text(encoding="utf-8"))
    collars = json.loads(COLLARS.read_text(encoding="utf-8"))
    states = replay.initial_states(ar_link, lifts)
    for record, interval, surface in zip(
        movie["transitions"], intervals["intervals"], collars["surfaces"]
    ):
        component = interval["component"]
        initial_points = [
            replay.point(value)
            for value in lifts["components"][component]["lifted_vertices"]
        ]
        closing_deck = tuple(
            lifts["components"][component]["closing_deck_translation"]
        )
        replay.replay_transition(
            record,
            interval,
            surface,
            states,
            initial_points,
            closing_deck,
        )
    return states


def curve_report(points, seams, radius):
    minima = []
    for index, segment in enumerate(zip(points, points[1:])):
        if index in seams:
            continue
        minimum, parameter = segment_l1_minimum(segment)
        minima.append((index, minimum, parameter))
    offending = [
        {
            "segment_index": index,
            "minimum_l1": str(minimum),
            "deficit_below_belt_radius": str(radius - minimum),
            "parameter": str(parameter),
        }
        for index, minimum, parameter in minima
        if minimum < radius
    ]
    return {
        "tested_nonseam_segments": len(minima),
        "minimum_l1": str(min(minimum for _, minimum, _ in minima)),
        "segments_below_open_t_ball_boundary": len(offending),
        "segments_touching_belt_sphere": sum(minimum == radius for _, minimum, _ in minima),
        "offending_segments": offending,
    }


def build() -> dict:
    replay_result = replay.verify()
    if replay_result["verdict"] != "PASS_SIX_T_BAND_SEQUENTIAL_FRAMED_KIRBY_SLIDES":
        raise AssertionError("six-slide movie is not ready for cancellation analysis")
    movie = json.loads(MOVIE.read_text(encoding="utf-8"))
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    legacy = json.loads(LEGACY_CANCELLATION.read_text(encoding="utf-8"))
    radius = Fraction(belts["t_handle"]["belt_sphere"]["radius"])
    components = {}
    framing_obstructions = 0
    for component, (points, normals, seams) in final_states().items():
        push = [
            tuple(value[axis] + normal[axis] for axis in range(4))
            for value, normal in zip(points, normals)
        ]
        core_report = curve_report(points, seams, radius)
        push_report = curve_report(push, seams, radius)
        if core_report["segments_below_open_t_ball_boundary"]:
            raise AssertionError(f"state-6 core {component} still enters the t-ball")
        framing_obstructions += push_report["segments_below_open_t_ball_boundary"]
        components[component] = {
            "core": core_report,
            "framing_push_off": push_report,
            "inherited_seam_segment_indices": sorted(seams),
        }
    exterior = json.loads(EXTERIORIZATION.read_text(encoding="utf-8"))
    exteriorized_reports = {}
    exteriorized_obstructions = 0
    states = final_states()
    for component, (points, normals, seams) in states.items():
        replacements = {
            item["vertex_index"]: tuple(Fraction(value) for value in item["new_normal"])
            for item in exterior["components"][component]["normal_replacements"]
        }
        new_normals = [replacements.get(index, normal) for index, normal in enumerate(normals)]
        push = [
            tuple(value[axis] + normal[axis] for axis in range(4))
            for value, normal in zip(points, new_normals)
        ]
        report = curve_report(push, seams, radius)
        exteriorized_reports[component] = report
        exteriorized_obstructions += report["segments_below_open_t_ball_boundary"]
    verdict = (
        "READY_FOR_EXPLICIT_T_HCS_CANCELLATION_MAP"
        if exteriorized_obstructions == 0
        else "OPEN_FRAMING_COLLAR_EXTERIORIZATION_REQUIRED"
    )
    result = {
        "schema": "t73_t_hcs_cancellation_readiness/v1",
        "sequential_movie_sha256": movie["sha256"],
        "belt_spheres_sha256": belts["sha256"],
        "legacy_cancellation_sha256": legacy["sha256"],
        "belt_radius": str(radius),
        "components": components,
        "total_framing_segments_entering_t_ball": framing_obstructions,
        "framing_exteriorization_sha256": exterior["sha256"],
        "exteriorized_framing_reports": exteriorized_reports,
        "exteriorized_framing_segments_entering_t_ball": exteriorized_obstructions,
        "legacy_fields_not_accepted_as_geometric_proof": [
            "status",
            "reason",
            "geometric_intersection",
            "transverse_intersection_one",
            "post_cancel_components/*/t_passages_after",
        ],
        "next_required_witness": "an explicit cellwise t-h_CS cancellation map",
        "verdict": verdict,
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
        raise AssertionError("t-h_CS cancellation readiness report is stale")
    print(json.dumps({
        "verdict": result["verdict"],
        "total_framing_segments_entering_t_ball": result["total_framing_segments_entering_t_ball"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
