#!/usr/bin/env python3
"""Replay all six t-slides as exact rational current-link state changes."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from t73_pl_kirby_moves import as_point, encode

ROOT = Path(__file__).resolve().parents[1]
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
LIFTS = ROOT / "geometry/t73_ar_core_universal_lifts.json"
INTERVALS = ROOT / "geometry/t73_t_band_attachment_intervals.json"
COLLARS = ROOT / "geometry/t73_t_band_collar_surfaces.json"
OUTPUT = ROOT / "geometry/t73_t_band_sequential_movie.json"
PERIOD = Fraction(4)


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def translate(point, deck):
    return tuple(point[axis] + PERIOD * deck[axis] for axis in range(3)) + (point[3],)


def add_decks(first, second):
    return tuple(first[axis] + second[axis] for axis in range(3))


def deck_offset(value, reference):
    if value[3] != reference[3]:
        return None
    quotients = [(value[axis] - reference[axis]) / PERIOD for axis in range(3)]
    if any(quotient.denominator != 1 for quotient in quotients):
        return None
    return tuple(int(quotient) for quotient in quotients)


def lies_on_segment(value, start, end):
    direction = tuple(end[axis] - start[axis] for axis in range(4))
    delta = tuple(value[axis] - start[axis] for axis in range(4))
    axis = next((index for index, coordinate in enumerate(direction) if coordinate), None)
    if axis is None:
        return value == start
    parameter = delta[axis] / direction[axis]
    return 0 <= parameter <= 1 and all(
        delta[index] == parameter * direction[index] for index in range(4)
    )


def affine_value(value, start, end, start_value, end_value):
    direction = tuple(end[axis] - start[axis] for axis in range(4))
    axis = next(index for index, coordinate in enumerate(direction) if coordinate)
    parameter = (value[axis] - start[axis]) / direction[axis]
    return tuple(
        start_value[index] + parameter * (end_value[index] - start_value[index])
        for index in range(4)
    )


def source_interval_lift(interval, initial_points):
    source_pair = [as_point(value) for value in interval["source_interval"]]
    midpoint = tuple((source_pair[0][axis] + source_pair[1][axis]) / 2 for axis in range(4))
    source_center = initial_points[interval["source_core_vertex_index"]]
    base_offset = deck_offset(source_center, midpoint)
    if base_offset is None:
        raise AssertionError("wrapped source interval has no lift at its declared source vertex")
    return source_pair, source_center, base_offset


def locate_source(current_points, source_pair, source_center, base_offset):
    matches = []
    for index, current_center in enumerate(current_points[1:-1], start=1):
        occurrence_offset = deck_offset(current_center, source_center)
        if occurrence_offset is None:
            continue
        interval_offset = add_decks(base_offset, occurrence_offset)
        before, after = (translate(value, interval_offset) for value in source_pair)
        if lies_on_segment(before, current_points[index - 1], current_center) and lies_on_segment(
            after, current_center, current_points[index + 1]
        ):
            matches.append((index, occurrence_offset, interval_offset, before, after))
    if len(matches) != 1:
        raise AssertionError(f"source interval has {len(matches)} occurrences in its current link state")
    return matches[0]


def cut_source_complement(points, normals, seams, index, before, after, closing_deck):
    before_normal = affine_value(before, points[index - 1], points[index], normals[index - 1], normals[index])
    after_normal = affine_value(after, points[index], points[index + 1], normals[index], normals[index + 1])
    complement_points = [
        after,
        *points[index + 1 :],
        *[translate(points[position], closing_deck) for position in range(1, index)],
        translate(before, closing_deck),
    ]
    complement_normals = [
        after_normal,
        *normals[index + 1 :],
        *normals[1:index],
        before_normal,
    ]
    segment_count = len(points) - 1
    complement_seams = {
        seam - index if seam >= index else segment_count - index + seam
        for seam in seams
    }
    return (
        complement_points,
        complement_normals,
        complement_seams,
        before_normal,
        after_normal,
    )


def append_piece(path, normals, ranges, name, piece, piece_normals):
    if len(piece) != len(piece_normals):
        raise AssertionError(f"{name}: incompatible framed piece")
    if path:
        if path[-1] != piece[0] or normals[-1] != piece_normals[0]:
            raise AssertionError(f"{name}: framed endpoint mismatch")
        start = len(path) - 1
        path.extend(piece[1:])
        normals.extend(piece_normals[1:])
    else:
        start = 0
        path.extend(piece)
        normals.extend(piece_normals)
    ranges[name] = [start, len(path) - 1]


def initial_states(ar_link, lifts):
    states = {}
    for component in ("m_1", "m_2", "m_3"):
        points = [as_point(value) for value in lifts["components"][component]["lifted_vertices"]]
        framing = ar_link["components"][component]["full_framing_annulus"]
        width = Fraction(framing["width"])
        direction = as_point([*framing["product_direction"], "0"])
        normal = tuple(width * coordinate for coordinate in direction)
        states[component] = (points, [normal] * len(points), set())
    return states


def build_transition(interval, surface, current, initial_points, closing_deck):
    component = interval["component"]
    points, normals, seams = current[component]
    before_points_sha = canonical_sha([encode(value) for value in points])
    before_normals_sha = canonical_sha([encode(value) for value in normals])
    source_pair, source_center, base_offset = source_interval_lift(interval, initial_points)
    index, occurrence_offset, interval_offset, before, after = locate_source(
        points, source_pair, source_center, base_offset
    )
    (
        complement,
        complement_normals,
        complement_seams,
        before_normal,
        after_normal,
    ) = cut_source_complement(
        points, normals, seams, index, before, after, closing_deck
    )

    surface_vertices = [as_point(value) for value in surface["vertices"]]
    surface_normals = [as_point(value) for value in surface["normal_field"]]
    boundary = surface["boundary"]
    placement_deck = add_decks(interval_offset, closing_deck)
    negative_ids = boundary["negative_u_lane"]
    positive_ids = boundary["positive_u_lane"]
    negative_lane = [translate(surface_vertices[item], placement_deck) for item in negative_ids]
    positive_lane = [translate(surface_vertices[item], placement_deck) for item in positive_ids]
    negative_normals = [surface_normals[item] for item in negative_ids]
    positive_normals = [surface_normals[item] for item in positive_ids]
    if negative_normals[0] != before_normal or positive_normals[-1] != after_normal:
        raise AssertionError("collar framing does not match the current source framing")

    target_start, target_end = negative_lane[-1], positive_lane[0]
    if target_start[:3] != target_end[:3]:
        raise AssertionError("framed h_CS target is not vertical")
    seam_start, seam_end = (
        (Fraction(0), Fraction(1))
        if target_start[3] < target_end[3]
        else (Fraction(1), Fraction(0))
    )
    target_complement = [
        target_start,
        (*target_start[:3], seam_start),
        (*target_start[:3], seam_end),
        target_end,
    ]
    target_normal = negative_normals[-1]

    output_points = []
    output_normals = []
    ranges = {}
    append_piece(output_points, output_normals, ranges, "retained_component_complement", complement, complement_normals)
    append_piece(output_points, output_normals, ranges, "negative_band_lane", negative_lane, negative_normals)
    append_piece(
        output_points,
        output_normals,
        ranges,
        "parallel_hcs_complement",
        target_complement,
        [target_normal] * len(target_complement),
    )
    append_piece(output_points, output_normals, ranges, "positive_band_lane", positive_lane, positive_normals)
    if output_points[-1] != translate(output_points[0], closing_deck):
        raise AssertionError("sequential t-slide lost quotient closure")
    push_points = [
        tuple(value[axis] + normal[axis] for axis in range(4))
        for value, normal in zip(output_points, output_normals)
    ]

    restored_subarc = [before, points[index], after]
    recovered = [*complement, translate(points[index], closing_deck), translate(after, closing_deck)]
    new_seam = ranges["parallel_hcs_complement"][0] + 1
    output_seams = complement_seams | {new_seam}
    transition = {
        "band_index": interval["band_index"],
        "state_before": interval["band_index"],
        "state_after": interval["band_index"] + 1,
        "moved_component": component,
        "source_vertex_index_in_current_state": index,
        "source_center_occurrence_deck": list(occurrence_offset),
        "wrapped_interval_base_deck": list(base_offset),
        "collar_placement_deck": list(placement_deck),
        "source_attachment_lifted": [encode(before), encode(after)],
        "target_attachment_lifted": [encode(target_start), encode(target_end)],
        "state_before_component_polyline_sha256": before_points_sha,
        "state_before_component_normal_field_sha256": before_normals_sha,
        "state_after_component_polyline_sha256": canonical_sha(
            [encode(value) for value in output_points]
        ),
        "state_after_component_normal_field_sha256": canonical_sha(
            [encode(value) for value in output_normals]
        ),
        "state_after_component_push_off_sha256": canonical_sha(
            [encode(value) for value in push_points]
        ),
        "state_after_component_vertex_count": len(output_points),
        "piece_vertex_ranges": ranges,
        "mapping_torus_seam_segment_indices": sorted(output_seams),
        "new_mapping_torus_seam_segment_index": new_seam,
        "new_mapping_torus_seam_orientation": [int(seam_start), int(seam_end)],
        "closing_deck_translation": list(closing_deck),
        "inverse_move": {
            "kind": "remove_band_sum_and_restore_source_subarc",
            "restored_source_subarc": [encode(value) for value in restored_subarc],
            "recovered_previous_refined_lift_sha256": canonical_sha(
                [encode(value) for value in recovered]
            ),
        },
        "status": "SEQUENTIAL_FRAMED_SLIDE_GEOMETRY_CONSTRUCTED",
    }
    current[component] = (output_points, output_normals, output_seams)
    return transition


def build() -> dict[str, Any]:
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    lifts = json.loads(LIFTS.read_text(encoding="utf-8"))
    intervals = json.loads(INTERVALS.read_text(encoding="utf-8"))
    collars = json.loads(COLLARS.read_text(encoding="utf-8"))
    current = initial_states(ar_link, lifts)
    transitions = []
    for interval, surface in zip(intervals["intervals"], collars["surfaces"]):
        component = interval["component"]
        initial_points = [as_point(value) for value in lifts["components"][component]["lifted_vertices"]]
        closing_deck = tuple(lifts["components"][component]["closing_deck_translation"])
        transition = build_transition(
            interval, surface, current, initial_points, closing_deck
        )
        transition["current_link_after"] = {
            name: {
                "polyline_sha256": canonical_sha([encode(value) for value in state[0]]),
                "normal_field_sha256": canonical_sha([encode(value) for value in state[1]]),
                "vertex_count": len(state[0]),
                "mapping_torus_seam_segment_indices": sorted(state[2]),
            }
            for name, state in current.items()
        }
        transitions.append(transition)
    final_components = {
        component: {
            "latest_state": 2 * (index + 1),
            "final_polyline_sha256": canonical_sha([encode(value) for value in current[component][0]]),
            "final_normal_field_sha256": canonical_sha([encode(value) for value in current[component][1]]),
            "closing_deck_translation": lifts["components"][component]["closing_deck_translation"],
            "mapping_torus_seam_segment_indices": sorted(current[component][2]),
        }
        for index, component in enumerate(("m_1", "m_2", "m_3"))
    }
    result = {
        "schema": "t73_t_band_sequential_movie/v1",
        "ar_link_sha256": ar_link["sha256"],
        "universal_lifts_sha256": lifts["sha256"],
        "attachment_intervals_sha256": intervals["sha256"],
        "collar_surfaces_sha256": collars["sha256"],
        "transitions": transitions,
        "final_component_manifest": final_components,
        "completion_status": "SIX_T_BAND_SEQUENTIAL_STATES_CONSTRUCTED_AWAITING_FULL_VERIFICATION",
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
        raise AssertionError("sequential t-band movie is stale")
    print(f"T73_T_BAND_SEQUENTIAL_MOVIE={result['completion_status']}")


if __name__ == "__main__":
    main()
