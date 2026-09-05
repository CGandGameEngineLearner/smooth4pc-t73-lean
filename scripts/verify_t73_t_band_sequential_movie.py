#!/usr/bin/env python3
"""Independently replay and verify the six sequential framed t-slides."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from verify_t73_candidate_t_band0_quotient_splice import (
    candidate_deck_translations,
    translate_segment,
)
from verify_t73_candidate_t_band0_relative_contacts import verify_contacts
from verify_t73_candidate_t_band0_splice import exact_segment_intersection
from verify_t73_candidate_t_band0_surface import (
    segment_meets_triangle,
    triangles_intersect,
)

ROOT = Path(__file__).resolve().parents[1]
MOVIE = ROOT / "geometry/t73_t_band_sequential_movie.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
LIFTS = ROOT / "geometry/t73_ar_core_universal_lifts.json"
INTERVALS = ROOT / "geometry/t73_t_band_attachment_intervals.json"
COLLARS = ROOT / "geometry/t73_t_band_collar_surfaces.json"
PERIOD = Fraction(4)


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def encode_points(values):
    return [encode(value) for value in values]


def segments(values):
    return list(zip(values, values[1:]))


def translate(value, deck):
    return tuple(value[axis] + PERIOD * deck[axis] for axis in range(3)) + (value[3],)


def add_decks(first, second):
    return tuple(first[axis] + second[axis] for axis in range(3))


def deck_offset(value, reference):
    if value[3] != reference[3]:
        return None
    quotients = [(value[axis] - reference[axis]) / PERIOD for axis in range(3)]
    if any(quotient.denominator != 1 for quotient in quotients):
        return None
    return tuple(int(quotient) for quotient in quotients)


def lies_on_segment(value, segment):
    start, end = segment
    dimension = len(value)
    direction = tuple(end[axis] - start[axis] for axis in range(dimension))
    delta = tuple(value[axis] - start[axis] for axis in range(dimension))
    axis = next((index for index, coordinate in enumerate(direction) if coordinate), None)
    if axis is None:
        return value == start
    parameter = delta[axis] / direction[axis]
    return 0 <= parameter <= 1 and all(
        delta[index] == parameter * direction[index] for index in range(dimension)
    )


def affine_value(value, segment, endpoint_values):
    start, end = segment
    start_value, end_value = endpoint_values
    direction = tuple(end[axis] - start[axis] for axis in range(4))
    axis = next(index for index, coordinate in enumerate(direction) if coordinate)
    parameter = (value[axis] - start[axis]) / direction[axis]
    return tuple(
        start_value[index] + parameter * (end_value[index] - start_value[index])
        for index in range(4)
    )


def initial_states(ar_link, lifts):
    states = {}
    for component in ("m_1", "m_2", "m_3"):
        values = [point(item) for item in lifts["components"][component]["lifted_vertices"]]
        framing = ar_link["components"][component]["full_framing_annulus"]
        width = Fraction(framing["width"])
        direction = point([*framing["product_direction"], "0"])
        normal = tuple(width * coordinate for coordinate in direction)
        states[component] = (values, [normal] * len(values), set())
    return states


def independently_locate_source(interval, initial_points, current_points):
    wrapped_pair = [point(value) for value in interval["source_interval"]]
    midpoint = tuple((wrapped_pair[0][axis] + wrapped_pair[1][axis]) / 2 for axis in range(4))
    initial_center = initial_points[interval["source_core_vertex_index"]]
    base_deck = deck_offset(initial_center, midpoint)
    if base_deck is None:
        raise AssertionError("source interval cannot be lifted to its declared initial vertex")
    matches = []
    for index, current_center in enumerate(current_points[1:-1], start=1):
        occurrence_deck = deck_offset(current_center, initial_center)
        if occurrence_deck is None:
            continue
        interval_deck = add_decks(base_deck, occurrence_deck)
        before, after = (translate(value, interval_deck) for value in wrapped_pair)
        if lies_on_segment(before, (current_points[index - 1], current_center)) and lies_on_segment(
            after, (current_center, current_points[index + 1])
        ):
            matches.append((index, occurrence_deck, base_deck, interval_deck, before, after))
    if len(matches) != 1:
        raise AssertionError(f"source interval has {len(matches)} current-state occurrences")
    return matches[0]


def cut_complement(points, normals, seams, index, before, after, deck):
    before_normal = affine_value(
        before, (points[index - 1], points[index]), (normals[index - 1], normals[index])
    )
    after_normal = affine_value(
        after, (points[index], points[index + 1]), (normals[index], normals[index + 1])
    )
    output_points = [
        after,
        *points[index + 1 :],
        *[translate(points[position], deck) for position in range(1, index)],
        translate(before, deck),
    ]
    output_normals = [
        after_normal,
        *normals[index + 1 :],
        *normals[1:index],
        before_normal,
    ]
    segment_count = len(points) - 1
    output_seams = {
        seam - index if seam >= index else segment_count - index + seam
        for seam in seams
    }
    return output_points, output_normals, output_seams, before_normal, after_normal


def append_piece(points, normals, ranges, name, new_points, new_normals):
    if points:
        if points[-1] != new_points[0] or normals[-1] != new_normals[0]:
            raise AssertionError(f"{name}: framed pieces do not glue")
        start = len(points) - 1
        points.extend(new_points[1:])
        normals.extend(new_normals[1:])
    else:
        start = 0
        points.extend(new_points)
        normals.extend(new_normals)
    ranges[name] = [start, len(points) - 1]


def replay_transition(record, interval, surface, states, initial_points, closing_deck):
    component = interval["component"]
    old_points, old_normals, old_seams = states[component]
    located = independently_locate_source(interval, initial_points, old_points)
    index, occurrence_deck, base_deck, interval_deck, before, after = located
    if record["source_vertex_index_in_current_state"] != index:
        raise AssertionError("saved current-state source index changed")
    if record["source_center_occurrence_deck"] != list(occurrence_deck):
        raise AssertionError("saved source occurrence deck changed")
    if record["wrapped_interval_base_deck"] != list(base_deck):
        raise AssertionError("saved wrapped interval base deck changed")
    if record["source_attachment_lifted"] != [encode(before), encode(after)]:
        raise AssertionError("saved lifted source attachment changed")
    if record["state_before_component_polyline_sha256"] != canonical_sha(encode_points(old_points)):
        raise AssertionError("state-before component polyline hash changed")
    if record["state_before_component_normal_field_sha256"] != canonical_sha(encode_points(old_normals)):
        raise AssertionError("state-before normal-field hash changed")

    (
        complement,
        complement_normals,
        complement_seams,
        before_normal,
        after_normal,
    ) = cut_complement(
        old_points, old_normals, old_seams, index, before, after, closing_deck
    )
    vertices = [point(value) for value in surface["vertices"]]
    surface_normals = [point(value) for value in surface["normal_field"]]
    boundary = surface["boundary"]
    placement_deck = add_decks(interval_deck, closing_deck)
    if record["collar_placement_deck"] != list(placement_deck):
        raise AssertionError("saved collar placement deck changed")
    negative_ids = boundary["negative_u_lane"]
    positive_ids = boundary["positive_u_lane"]
    negative = [translate(vertices[item], placement_deck) for item in negative_ids]
    positive = [translate(vertices[item], placement_deck) for item in positive_ids]
    negative_normals = [surface_normals[item] for item in negative_ids]
    positive_normals = [surface_normals[item] for item in positive_ids]
    if negative_normals[0] != before_normal or positive_normals[-1] != after_normal:
        raise AssertionError("current framing does not glue to the collar framing")
    seam_start, seam_end = (
        (Fraction(0), Fraction(1))
        if negative[-1][3] < positive[0][3]
        else (Fraction(1), Fraction(0))
    )
    target = [
        negative[-1],
        (*negative[-1][:3], seam_start),
        (*negative[-1][:3], seam_end),
        positive[0],
    ]
    if record["target_attachment_lifted"] != [encode(target[0]), encode(target[-1])]:
        raise AssertionError("saved lifted target attachment changed")

    new_points = []
    new_normals = []
    ranges = {}
    append_piece(new_points, new_normals, ranges, "retained_component_complement", complement, complement_normals)
    append_piece(new_points, new_normals, ranges, "negative_band_lane", negative, negative_normals)
    append_piece(
        new_points,
        new_normals,
        ranges,
        "parallel_hcs_complement",
        target,
        [negative_normals[-1]] * len(target),
    )
    append_piece(new_points, new_normals, ranges, "positive_band_lane", positive, positive_normals)
    new_seam = ranges["parallel_hcs_complement"][0] + 1
    new_seams = complement_seams | {new_seam}
    pushed = [
        tuple(value[axis] + normal[axis] for axis in range(4))
        for value, normal in zip(new_points, new_normals)
    ]
    expected_fields = {
        "state_after_component_polyline_sha256": canonical_sha(encode_points(new_points)),
        "state_after_component_normal_field_sha256": canonical_sha(encode_points(new_normals)),
        "state_after_component_push_off_sha256": canonical_sha(encode_points(pushed)),
        "state_after_component_vertex_count": len(new_points),
        "piece_vertex_ranges": ranges,
        "mapping_torus_seam_segment_indices": sorted(new_seams),
        "new_mapping_torus_seam_segment_index": new_seam,
        "new_mapping_torus_seam_orientation": [int(seam_start), int(seam_end)],
    }
    for field, expected in expected_fields.items():
        if record[field] != expected:
            raise AssertionError(f"saved transition field {field} changed")
    if new_points[-1] != translate(new_points[0], closing_deck):
        raise AssertionError("replayed transition lost quotient closure")

    recovered = [
        *complement,
        translate(old_points[index], closing_deck),
        translate(after, closing_deck),
    ]
    if record["inverse_move"]["recovered_previous_refined_lift_sha256"] != canonical_sha(
        encode_points(recovered)
    ):
        raise AssertionError("inverse move does not recover the previous refined lift")
    states[component] = (new_points, new_normals, new_seams)
    return (
        old_points,
        old_normals,
        old_seams,
        new_points,
        new_normals,
        pushed,
        new_seams,
        ranges,
    )


def check_segment_families(first_segments, second_segments, skip_first=frozenset(), skip_second=frozenset(), allowed=None):
    exact_checks = 0
    for first_index, first in first_segments:
        if first_index in skip_first:
            continue
        for second_index, second in second_segments:
            if second_index in skip_second:
                continue
            for deck in candidate_deck_translations(first, second):
                deck = tuple(deck)
                if allowed and allowed(first_index, second_index, deck):
                    continue
                exact_checks += 1
                if exact_segment_intersection(first, translate_segment(second, deck)):
                    raise AssertionError(
                        f"unexpected segment intersection {first_index}/{second_index}/{deck}"
                    )
    return exact_checks


def check_self_family(indexed_segments, seams):
    exact_checks = 0
    for position, (first_index, first) in enumerate(indexed_segments):
        if first_index in seams:
            continue
        for second_index, second in indexed_segments[position:]:
            if second_index in seams:
                continue
            for deck in candidate_deck_translations(first, second):
                deck = tuple(deck)
                if first_index == second_index and deck == (0, 0, 0):
                    continue
                if second_index == first_index + 1 and deck == (0, 0, 0):
                    continue
                exact_checks += 1
                if exact_segment_intersection(first, translate_segment(second, deck)):
                    raise AssertionError(
                        "new band-sum piece has a quotient self-intersection "
                        f"at {first_index}/{second_index}/{deck}"
                    )
    return exact_checks


def verify_incremental_curve(old_points, old_normals, new_points, new_normals, pushed, ranges, seam, deck):
    start = ranges["negative_band_lane"][0]
    end = ranges["positive_band_lane"][1]
    core_segments = segments(new_points)
    push_segments = segments(pushed)
    old_push = [
        tuple(value[axis] + normal[axis] for axis in range(4))
        for value, normal in zip(old_points, old_normals)
    ]
    changed_core = list(enumerate(core_segments[start:end], start=start))
    retained_core = list(enumerate(core_segments[:start]))
    changed_push = list(enumerate(push_segments[start:end], start=start))
    retained_push = list(enumerate(push_segments[:start]))

    def allow_core_adjacency(first, second, translation):
        return (
            first == start
            and second == start - 1
            and translation == (0, 0, 0)
        ) or (
            first == end - 1
            and second == 0
            and translation == deck
        )

    checks = check_segment_families(
        changed_core, retained_core, skip_first=seam, allowed=allow_core_adjacency
    )
    checks += check_segment_families(
        changed_push, retained_push, skip_first=seam, allowed=allow_core_adjacency
    )
    checks += check_self_family(changed_core, seam)
    checks += check_self_family(changed_push, seam)
    checks += check_segment_families(changed_core, list(enumerate(push_segments)), skip_first=seam, skip_second=seam)
    checks += check_segment_families(
        list(enumerate(core_segments[:start])),
        changed_push,
        skip_first=seam,
        skip_second=seam,
    )
    if new_points[-1] != translate(new_points[0], deck) or pushed[-1] != translate(pushed[0], deck):
        raise AssertionError("incremental framed curve does not close")
    if len(old_push) != len(old_points):
        raise AssertionError("state-before framing is incomplete")
    return checks


def quotient_coordinate(value):
    return value - PERIOD * (value // PERIOD)


def verify_spatial_dual_clearance(curves, ar_link):
    exact_checks = 0
    for curve in curves:
        spatial = [
            tuple(quotient_coordinate(coordinate) for coordinate in value[:3])
            for value in curve
        ]
        for component in ("r_xy", "r_yz", "r_zx"):
            dual = [point(value) for value in ar_link["components"][component]["polyline"]]
            for curve_segment in segments(spatial):
                for dual_segment in segments(dual):
                    exact_checks += 1
                    if curve_segment[0] == curve_segment[1]:
                        meets = lies_on_segment(curve_segment[0], dual_segment)
                    else:
                        meets = exact_segment_intersection(curve_segment, dual_segment)
                    if meets:
                        raise AssertionError(
                            f"new geometry spatially meets actual {component}"
                        )
    return exact_checks


def verify_changed_stationary_clearance(
    moved_component, new_points, pushed, ranges, seams, states, ar_link
):
    start = ranges["negative_band_lane"][0]
    end = ranges["positive_band_lane"][1]
    changed_core = list(enumerate(segments(new_points)[start:end], start=start))
    changed_push = list(enumerate(segments(pushed)[start:end], start=start))
    checks = 0
    for component, (other_points, _, other_seams) in states.items():
        if component == moved_component:
            continue
        stationary = list(enumerate(segments(other_points)))
        checks += check_segment_families(
            changed_core,
            stationary,
            skip_first=seams,
            skip_second=other_seams,
        )
        checks += check_segment_families(
            changed_push,
            stationary,
            skip_first=seams,
            skip_second=other_seams,
        )

    hcs_xyz = point(ar_link["components"]["h_CS"]["section_point"])
    hcs = [(0, ((*hcs_xyz, Fraction(0)), (*hcs_xyz, Fraction(1))))]
    checks += check_segment_families(changed_core, hcs, skip_first=seams)
    checks += check_segment_families(changed_push, hcs, skip_first=seams)
    changed_core_points = new_points[start : end + 1]
    changed_push_points = pushed[start : end + 1]
    checks += verify_spatial_dual_clearance(
        [changed_core_points, changed_push_points], ar_link
    )
    return checks


def verify_disk_contacts(
    surface, placement_deck, moved_component, old_points, other_states, ar_link
):
    vertices = [translate(point(value), placement_deck) for value in surface["vertices"]]
    pushed = [translate(point(value), placement_deck) for value in surface["push_off_vertices"]]
    triangles = [tuple(vertices[index] for index in ids) for ids in surface["triangles"]]
    push_triangles = [tuple(pushed[index] for index in ids) for ids in surface["triangles"]]
    boundary = surface["boundary"]
    source_edge = tuple(vertices[index] for index in boundary["source_attachment"])
    target_edge = tuple(vertices[index] for index in boundary["target_attachment"])
    source_contacts = verify_contacts(triangles, segments(old_points), source_edge, True)
    target_xyz = target_edge[0][:3]
    target_parallel = ((*target_xyz, Fraction(0)), (*target_xyz, Fraction(1)))
    target_contacts = verify_contacts(triangles, [target_parallel], target_edge, False)
    if not source_contacts or not target_contacts:
        raise AssertionError("replayed disk lost an attachment")
    if any(triangles_intersect(first, second) for first in triangles for second in push_triangles):
        raise AssertionError("replayed disk meets its push-off")

    exact_checks = 0
    for component, (other_points, _, _) in other_states.items():
        if component == moved_component:
            continue
        for triangle in triangles + push_triangles:
            for other_segment in segments(other_points):
                for deck in candidate_deck_translations(triangle, other_segment):
                    exact_checks += 1
                    if segment_meets_triangle(translate_segment(other_segment, tuple(deck)), triangle):
                        raise AssertionError(
                            f"band {surface['band_index']} disk meets current {component}"
                        )
    hcs_xyz = point(ar_link["components"]["h_CS"]["section_point"])
    hcs = ((*hcs_xyz, Fraction(0)), (*hcs_xyz, Fraction(1)))
    if any(segment_meets_triangle(hcs, triangle) for triangle in triangles + push_triangles):
        raise AssertionError("band disk meets actual h_CS")
    # Every cross-section differs only in u, so the exact spatial projection
    # of each ribbon is its ordered sequence of even-indexed center vertices.
    dual_checks = verify_spatial_dual_clearance(
        [vertices[::2], pushed[::2]], ar_link
    )
    return source_contacts, target_contacts, exact_checks + dual_checks


def verify() -> dict:
    movie = json.loads(MOVIE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    lifts = json.loads(LIFTS.read_text(encoding="utf-8"))
    intervals = json.loads(INTERVALS.read_text(encoding="utf-8"))
    collars = json.loads(COLLARS.read_text(encoding="utf-8"))
    if movie["completion_status"] != "SIX_T_BAND_SEQUENTIAL_STATES_CONSTRUCTED_AWAITING_FULL_VERIFICATION":
        raise AssertionError("sequential movie status changed")
    bindings = {
        "ar_link_sha256": ar_link["sha256"],
        "universal_lifts_sha256": lifts["sha256"],
        "attachment_intervals_sha256": intervals["sha256"],
        "collar_surfaces_sha256": collars["sha256"],
    }
    if any(movie[field] != value for field, value in bindings.items()):
        raise AssertionError("sequential movie has a stale source binding")

    states = initial_states(ar_link, lifts)
    incremental_checks = 0
    stationary_clearance_checks = 0
    disk_checks = 0
    source_contacts = 0
    target_contacts = 0
    for expected_index, (record, interval, surface) in enumerate(
        zip(movie["transitions"], intervals["intervals"], collars["surfaces"])
    ):
        if record["band_index"] != expected_index or record["state_before"] != expected_index or record["state_after"] != expected_index + 1:
            raise AssertionError("sequential movie time order changed")
        component = interval["component"]
        initial_points = [point(value) for value in lifts["components"][component]["lifted_vertices"]]
        closing_deck = tuple(lifts["components"][component]["closing_deck_translation"])
        (
            old_points,
            old_normals,
            old_seams,
            new_points,
            new_normals,
            pushed,
            seam,
            ranges,
        ) = replay_transition(record, interval, surface, states, initial_points, closing_deck)
        incremental_checks += verify_incremental_curve(
            old_points, old_normals, new_points, new_normals, pushed, ranges, seam, closing_deck
        )
        stationary_clearance_checks += verify_changed_stationary_clearance(
            component,
            new_points,
            pushed,
            ranges,
            seam,
            states,
            ar_link,
        )
        current_source_contacts, current_target_contacts, current_disk_checks = verify_disk_contacts(
            surface,
            tuple(record["collar_placement_deck"]),
            component,
            old_points,
            states,
            ar_link,
        )
        source_contacts += current_source_contacts
        target_contacts += current_target_contacts
        disk_checks += current_disk_checks
        expected_manifest = {
            name: {
                "polyline_sha256": canonical_sha(encode_points(state[0])),
                "normal_field_sha256": canonical_sha(encode_points(state[1])),
                "vertex_count": len(state[0]),
                "mapping_torus_seam_segment_indices": sorted(state[2]),
            }
            for name, state in states.items()
        }
        if record["current_link_after"] != expected_manifest:
            raise AssertionError("current-link manifest does not describe the replayed state")
    return {
        "verdict": "PASS_SIX_T_BAND_SEQUENTIAL_FRAMED_KIRBY_SLIDES",
        "states": 7,
        "transitions": 6,
        "source_triangle_contacts": source_contacts,
        "target_triangle_contacts": target_contacts,
        "incremental_exact_segment_checks": incremental_checks,
        "changed_piece_stationary_and_dual_checks": stationary_clearance_checks,
        "disk_other_component_exact_checks": disk_checks,
        "final_vertex_counts": {
            name: len(state[0]) for name, state in states.items()
        },
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
