#!/usr/bin/env python3
"""Independently verify the first framed t-slide and its inverse recovery."""

from __future__ import annotations

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
STATE = ROOT / "geometry/t73_t_band_sequential_state_01.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
LIFTS = ROOT / "geometry/t73_ar_core_universal_lifts.json"
INTERVALS = ROOT / "geometry/t73_t_band_attachment_intervals.json"
COLLARS = ROOT / "geometry/t73_t_band_collar_surfaces.json"
PERIOD = Fraction(4)


def point(values):
    return tuple(Fraction(value) for value in values)


def translate(value, deck):
    return tuple(value[axis] + PERIOD * deck[axis] for axis in range(3)) + (value[3],)


def segments(points):
    return list(zip(points, points[1:]))


def interpolate(origin, neighbour, parameter):
    return tuple(
        origin[axis] + parameter * (neighbour[axis] - origin[axis])
        for axis in range(4)
    )


def verify_hash_bindings(state, ar_link, lifts, intervals, collars):
    expected = {
        "ar_link_sha256": ar_link["sha256"],
        "universal_lifts_sha256": lifts["sha256"],
        "attachment_intervals_sha256": intervals["sha256"],
        "collar_surfaces_sha256": collars["sha256"],
    }
    for field, value in expected.items():
        if state[field] != value:
            raise AssertionError(f"band-0 state has stale {field}")


def verify_piece_bindings(state, lifts, intervals, surface, points, normals):
    attachment = intervals["intervals"][0]
    source_points = [
        point(value) for value in lifts["components"]["m_1"]["lifted_vertices"]
    ]
    deck = tuple(state["closing_deck_translation"])
    index = attachment["source_core_vertex_index"]
    width = Fraction(attachment["source_parameter_from_vertex"])
    before = interpolate(source_points[index], source_points[index - 1], width)
    after = interpolate(source_points[index], source_points[index + 1], width)
    source_complement = [
        after,
        *source_points[index + 1 :],
        *[translate(value, deck) for value in source_points[1:index]],
        translate(before, deck),
    ]

    surface_vertices = [point(value) for value in surface["vertices"]]
    surface_normals = [point(value) for value in surface["normal_field"]]
    boundary = surface["boundary"]
    negative_ids = boundary["negative_u_lane"]
    positive_ids = boundary["positive_u_lane"]
    negative_lane = [translate(surface_vertices[item], deck) for item in negative_ids]
    positive_lane = [translate(surface_vertices[item], deck) for item in positive_ids]
    target_start, target_end = negative_lane[-1], positive_lane[0]
    target_complement = [
        target_start,
        (*target_start[:3], Fraction(0)),
        (*target_start[:3], Fraction(1)),
        target_end,
    ]
    expected_pieces = {
        "retained_m1_complement": source_complement,
        "negative_band_lane": negative_lane,
        "parallel_hcs_complement": target_complement,
        "positive_band_lane": positive_lane,
    }
    source_normal = surface_normals[boundary["source_attachment"][0]]
    target_normal = surface_normals[boundary["target_attachment"][0]]
    expected_normals = {
        "retained_m1_complement": [source_normal] * len(source_complement),
        "negative_band_lane": [surface_normals[item] for item in negative_ids],
        "parallel_hcs_complement": [target_normal] * len(target_complement),
        "positive_band_lane": [surface_normals[item] for item in positive_ids],
    }
    for name, expected in expected_pieces.items():
        start, end = state["piece_vertex_ranges"][name]
        if points[start : end + 1] != expected:
            raise AssertionError(f"post-slide {name} is not the independently rebuilt piece")
        if normals[start : end + 1] != expected_normals[name]:
            raise AssertionError(f"post-slide {name} framing changed")


def verify_quotient_framed_curve(points, push_points, seam, deck):
    curve_segments = segments(points)
    push_segments = segments(push_points)
    expected_end = translate(points[0], deck)
    if points[-1] != expected_end or push_points[-1] != translate(push_points[0], deck):
        raise AssertionError("post-slide framed curve has the wrong deck closure")

    self_checks = 0
    for curve_kind, current_segments in (("core", curve_segments), ("push", push_segments)):
        for first_index, first in enumerate(current_segments):
            for second_index in range(first_index, len(current_segments)):
                if first_index in seam or second_index in seam:
                    continue
                second = current_segments[second_index]
                for translation in candidate_deck_translations(first, second):
                    translation = tuple(translation)
                    if first_index == second_index and translation == (0, 0, 0):
                        continue
                    if second_index == first_index + 1 and translation == (0, 0, 0):
                        continue
                    if (
                        first_index == 0
                        and second_index == len(current_segments) - 1
                        and translation == tuple(-value for value in deck)
                    ):
                        continue
                    self_checks += 1
                    if exact_segment_intersection(first, translate_segment(second, translation)):
                        raise AssertionError(
                            f"post-slide {curve_kind} has a quotient self-intersection"
                        )

    core_push_checks = 0
    for core_index, core_segment in enumerate(curve_segments):
        if core_index in seam:
            continue
        for push_index, push_segment in enumerate(push_segments):
            if push_index in seam:
                continue
            for translation in candidate_deck_translations(core_segment, push_segment):
                core_push_checks += 1
                if exact_segment_intersection(
                    core_segment, translate_segment(push_segment, tuple(translation))
                ):
                    raise AssertionError("post-slide core meets its framed push-off")
    return self_checks, core_push_checks


def verify_disk_and_current_link(surface, ar_link, lifts):
    vertices = [point(value) for value in surface["vertices"]]
    pushed = [point(value) for value in surface["push_off_vertices"]]
    triangle_ids = surface["triangles"]
    triangles = [tuple(vertices[index] for index in ids) for ids in triangle_ids]
    push_triangles = [tuple(pushed[index] for index in ids) for ids in triangle_ids]
    boundary = surface["boundary"]
    source_edge = tuple(vertices[index] for index in boundary["source_attachment"])
    target_edge = tuple(vertices[index] for index in boundary["target_attachment"])

    m1_points = [point(value) for value in lifts["components"]["m_1"]["lifted_vertices"]]
    source_contacts = verify_contacts(triangles, segments(m1_points), source_edge, True)
    target_xyz = target_edge[0][:3]
    target_parallel = ((*target_xyz, Fraction(0)), (*target_xyz, Fraction(1)))
    target_contacts = verify_contacts(triangles, [target_parallel], target_edge, False)
    if not source_contacts or not target_contacts:
        raise AssertionError("band-0 disk lost one of its two attachments")

    actual_hcs_xyz = point(ar_link["components"]["h_CS"]["section_point"])
    actual_hcs = ((*actual_hcs_xyz, Fraction(0)), (*actual_hcs_xyz, Fraction(1)))
    if any(segment_meets_triangle(actual_hcs, triangle) for triangle in triangles + push_triangles):
        raise AssertionError("band-0 disk or push-off meets the actual h_CS core")

    exact_other_checks = 0
    for disk_triangles in (triangles, push_triangles):
        for triangle in disk_triangles:
            for component in ("m_2", "m_3"):
                other_points = [
                    point(value) for value in lifts["components"][component]["lifted_vertices"]
                ]
                for other_segment in segments(other_points):
                    for deck in candidate_deck_translations(triangle, other_segment):
                        exact_other_checks += 1
                        if segment_meets_triangle(
                            translate_segment(other_segment, tuple(deck)), triangle
                        ):
                            raise AssertionError(f"band-0 disk meets actual {component}")

    for triangle in triangles:
        for pushed_triangle in push_triangles:
            if triangles_intersect(triangle, pushed_triangle):
                raise AssertionError("band-0 disk meets its push-off")

    centerline = [point(value)[:3] for value in surface["centerline"]]
    for component in ("r_xy", "r_yz", "r_zx"):
        dual = [point(value) for value in ar_link["components"][component]["polyline"]]
        if any(
            exact_segment_intersection(band_segment, dual_segment)
            for band_segment in segments(centerline)
            for dual_segment in segments(dual)
        ):
            raise AssertionError(f"band-0 spatial projection meets actual {component}")
    return source_contacts, target_contacts, exact_other_checks


def quotient_coordinate(value):
    return value - PERIOD * (value // PERIOD)


def lies_on_segment(value, segment):
    start, end = segment
    direction = tuple(end[axis] - start[axis] for axis in range(len(start)))
    delta = tuple(value[axis] - start[axis] for axis in range(len(start)))
    axis = next((index for index, coordinate in enumerate(direction) if coordinate), None)
    if axis is None:
        return value == start
    parameter = delta[axis] / direction[axis]
    return 0 <= parameter <= 1 and all(
        delta[index] == parameter * direction[index] for index in range(len(start))
    )


def verify_changed_piece_clearance(state, points, pushed, ar_link, lifts):
    start = state["piece_vertex_ranges"]["negative_band_lane"][0]
    end = state["piece_vertex_ranges"]["positive_band_lane"][1]
    seam = set(state["mapping_torus_seam_segment_indices"])
    exact_checks = 0
    for curve_kind, curve in (("core", points), ("push", pushed)):
        changed_segments = list(enumerate(segments(curve)[start:end], start=start))
        for component in ("m_2", "m_3"):
            stationary = [
                point(value) for value in lifts["components"][component]["lifted_vertices"]
            ]
            for changed_index, changed in changed_segments:
                if changed_index in seam:
                    continue
                for stationary_segment in segments(stationary):
                    for deck in candidate_deck_translations(changed, stationary_segment):
                        exact_checks += 1
                        if exact_segment_intersection(
                            changed, translate_segment(stationary_segment, tuple(deck))
                        ):
                            raise AssertionError(
                                f"new {curve_kind} piece meets actual {component}"
                            )

        hcs_xyz = point(ar_link["components"]["h_CS"]["section_point"])
        hcs_segment = ((*hcs_xyz, Fraction(0)), (*hcs_xyz, Fraction(1)))
        for changed_index, changed in changed_segments:
            if changed_index in seam:
                continue
            for deck in candidate_deck_translations(changed, hcs_segment):
                exact_checks += 1
                if exact_segment_intersection(
                    changed, translate_segment(hcs_segment, tuple(deck))
                ):
                    raise AssertionError(f"new {curve_kind} piece meets actual h_CS")

        spatial = [
            tuple(quotient_coordinate(coordinate) for coordinate in value[:3])
            for value in curve[start : end + 1]
        ]
        for component in ("r_xy", "r_yz", "r_zx"):
            dual = [point(value) for value in ar_link["components"][component]["polyline"]]
            for changed in segments(spatial):
                for dual_segment in segments(dual):
                    exact_checks += 1
                    if changed[0] == changed[1]:
                        meets = lies_on_segment(changed[0], dual_segment)
                    else:
                        meets = exact_segment_intersection(changed, dual_segment)
                    if meets:
                        raise AssertionError(
                            f"new {curve_kind} spatial projection meets actual {component}"
                        )
    return exact_checks


def verify_inverse(state, lifts, intervals):
    attachment = intervals["intervals"][0]
    source_points = [
        point(value) for value in lifts["components"]["m_1"]["lifted_vertices"]
    ]
    deck = tuple(state["closing_deck_translation"])
    index = attachment["source_core_vertex_index"]
    width = Fraction(attachment["source_parameter_from_vertex"])
    before = interpolate(source_points[index], source_points[index - 1], width)
    after = interpolate(source_points[index], source_points[index + 1], width)
    expected = [
        after,
        *source_points[index + 1 :],
        *[translate(value, deck) for value in source_points[1:index]],
        translate(before, deck),
        translate(source_points[index], deck),
        translate(after, deck),
    ]
    recovered = [point(value) for value in state["inverse_move"]["recovered_source_lift"]]
    if recovered != expected or recovered[-1] != translate(recovered[0], deck):
        raise AssertionError("inverse band cut does not recover the refined actual m1 lift")
    return len(recovered) - 1


def verify() -> dict:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    lifts = json.loads(LIFTS.read_text(encoding="utf-8"))
    intervals = json.loads(INTERVALS.read_text(encoding="utf-8"))
    collars = json.loads(COLLARS.read_text(encoding="utf-8"))
    if state["completion_status"] != "BAND0_SEQUENTIAL_FRAMED_SLIDE_GEOMETRY_CONSTRUCTED":
        raise AssertionError("band-0 sequential-state status changed")
    verify_hash_bindings(state, ar_link, lifts, intervals, collars)

    points = [point(value) for value in state["post_slide_lifted_polyline"]]
    normals = [point(value) for value in state["post_slide_normal_field"]]
    pushed = [point(value) for value in state["post_slide_push_off"]]
    if len(points) != len(normals) or len(points) != len(pushed):
        raise AssertionError("post-slide framing arrays have incompatible lengths")
    if any(
        tuple(value[axis] + normal[axis] for axis in range(4)) != push
        for value, normal, push in zip(points, normals, pushed)
    ):
        raise AssertionError("post-slide push-off is not core plus normal")
    verify_piece_bindings(
        state, lifts, intervals, collars["surfaces"][0], points, normals
    )
    seam = set(state["mapping_torus_seam_segment_indices"])
    if len(seam) != 1:
        raise AssertionError("post-slide state must contain exactly one seam cell")
    seam_start, seam_end = segments(points)[next(iter(seam))]
    if seam_start[:3] != seam_end[:3] or (seam_start[3], seam_end[3]) != (0, 1):
        raise AssertionError("post-slide seam cell has incompatible endpoints")

    self_checks, core_push_checks = verify_quotient_framed_curve(
        points, pushed, seam, tuple(state["closing_deck_translation"])
    )
    source_contacts, target_contacts, other_checks = verify_disk_and_current_link(
        collars["surfaces"][0], ar_link, lifts
    )
    changed_clearance_checks = verify_changed_piece_clearance(
        state, points, pushed, ar_link, lifts
    )
    inverse_segments = verify_inverse(state, lifts, intervals)
    return {
        "verdict": "PASS_T_BAND0_SEQUENTIAL_FRAMED_KIRBY_SLIDE",
        "state_transition": [0, 1],
        "post_slide_segments": len(points) - 1,
        "quotient_self_checks": self_checks,
        "core_push_checks": core_push_checks,
        "disk_source_contacts": source_contacts,
        "disk_target_parallel_contacts": target_contacts,
        "disk_actual_m2_m3_checks": other_checks,
        "changed_piece_stationary_clearance_checks": changed_clearance_checks,
        "dual_clearance": "EXACT_SPATIAL_PROJECTION_DISJOINT_INDEPENDENT_OF_U",
        "inverse_recovered_source_segments": inverse_segments,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
