#!/usr/bin/env python3
"""Independently verify the hybrid global/local x-state 0-to-1."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from build_t73_t_hcs_cancellation_readiness import final_states
from verify_t73_t_hcs_framing_exteriorization import verify_changed_push_clearance
from verify_t73_x_band0_attachment_surface import verify as verify_surface
from verify_t73_x_band0_chart_transitions import verify as verify_charts
from verify_t73_x_band0_current_link_clearance import verify as verify_clearance
from verify_t73_x_band0_m1_parallel import verify as verify_parallel

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_band_hybrid_state_0000_0001.json"
SURFACE = ROOT / "geometry/t73_x_band0_attachment_surface.json"
PARALLEL = ROOT / "geometry/t73_x_band0_m1_parallel.json"
EXTERIOR = ROOT / "geometry/t73_t_hcs_framing_exteriorization.json"
PERIOD = Fraction(4)


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode_points(values):
    return [[str(coordinate) for coordinate in value] for value in values]


def translate(value, deck):
    return tuple(value[axis] + PERIOD * deck[axis] for axis in range(3)) + (value[3],)


def interpolate(value, start, end, start_value, end_value):
    parameter = (value[0] - start[0]) / (end[0] - start[0])
    return tuple(
        start_value[axis] + parameter * (end_value[axis] - start_value[axis])
        for axis in range(4)
    )


def cut_complement(points, normals, center_index, before, after, deck):
    before_normal = interpolate(
        before, points[center_index - 1], points[center_index], normals[center_index - 1], normals[center_index]
    )
    after_normal = interpolate(
        after, points[center_index], points[center_index + 1], normals[center_index], normals[center_index + 1]
    )
    values = [
        after,
        *points[center_index + 1 :],
        *[translate(points[index], deck) for index in range(1, center_index)],
        translate(before, deck),
    ]
    value_normals = [
        after_normal,
        *normals[center_index + 1 :],
        *normals[1:center_index],
        before_normal,
    ]
    return values, value_normals


def exteriorized_normals(component, normals, exterior):
    replacements = {
        item["vertex_index"]: point(item["new_normal"])
        for item in exterior["components"][component]["normal_replacements"]
    }
    return [replacements.get(index, value) for index, value in enumerate(normals)]


def source_local_to_global(value, cycle):
    return (
        value[0] + 1076 + cycle * 1076,
        value[1] + 160 + cycle * 160,
        value[2],
        Fraction(1),
    )


def target_local_to_global(value, cycle):
    return (
        -value[0] - cycle * 4,
        value[1],
        value[2] + 4 + cycle * 4,
        Fraction(0),
    )


def verify() -> dict:
    prerequisite_verdicts = [
        verify_surface()["verdict"],
        verify_charts()["verdict"],
        verify_clearance()["verdict"],
        verify_parallel()["verdict"],
    ]
    data = json.loads(DATA.read_text(encoding="utf-8"))
    surface = json.loads(SURFACE.read_text(encoding="utf-8"))
    parallel_data = json.loads(PARALLEL.read_text(encoding="utf-8"))
    exterior = json.loads(EXTERIOR.read_text(encoding="utf-8"))
    if data["completion_status"] != "X_BAND0_HYBRID_FRAMED_STATE_TRANSITION_CONSTRUCTED":
        raise AssertionError("hybrid x-state scope changed")
    states = final_states()
    m2_points, m2_original_normals, m2_seams = states["m_2"]
    m2_normals = exteriorized_normals("m_2", m2_original_normals, exterior)
    source_start, source_end = surface["source_arc_current_state_vertex_range"]
    source_normal = point(surface["source_normal_mod_x_tangent"])
    for index in range(source_start, source_end + 1):
        m2_normals[index] = source_normal
    source_interval = [point(value) for value in surface["source_interval_current_state"]]
    m2_deck = (269, 40, 0)
    m2_complement, m2_complement_normals = cut_complement(
        m2_points, m2_normals, source_start + 1, source_interval[0], source_interval[1], m2_deck
    )

    parallel = [point(value) for value in parallel_data["parallel_vertices"]]
    parallel_normals = [
        tuple(value / parallel_data["parallel_coefficient"] for value in point(offset))
        for offset in parallel_data["framing_offsets"]
    ]
    target_interval = [point(value) for value in parallel_data["target_interval_global"]]
    m1_complement, m1_complement_normals = cut_complement(
        parallel, parallel_normals, 3, target_interval[0], target_interval[1], (-1, 0, 1)
    )
    pieces = {item["name"]: item for item in data["pieces"]}
    expected_hashes = {
        "retained_m2_complement": (
            canonical_sha(encode_points(m2_complement)),
            canonical_sha(encode_points(m2_complement_normals)),
        ),
        "oriented_m1_parallel_complement": (
            canonical_sha(encode_points(m1_complement)),
            canonical_sha(encode_points(m1_complement_normals)),
        ),
    }
    for name, (vertices_sha, normals_sha) in expected_hashes.items():
        if pieces[name]["vertices_sha256"] != vertices_sha or pieces[name]["normals_sha256"] != normals_sha:
            raise AssertionError(f"hybrid piece {name} changed")

    vertices = [point(value) for value in surface["vertices"]]
    surface_normals = [point(value) for value in surface["normal_field"]]
    negative = [vertices[index] for index in surface["boundary"]["negative_x_lane"]]
    positive = [vertices[index] for index in surface["boundary"]["positive_x_lane"]]
    negative_normals = [
        surface_normals[index] for index in surface["boundary"]["negative_x_lane"]
    ]
    positive_normals = [
        surface_normals[index] for index in surface["boundary"]["positive_x_lane"]
    ]
    if pieces["negative_band_lane"]["vertices"] != encode_points(negative) or pieces[
        "negative_band_lane"
    ]["normals"] != encode_points(negative_normals):
        raise AssertionError("saved negative local band lane changed")
    if pieces["positive_band_lane"]["vertices"] != encode_points(positive) or pieces[
        "positive_band_lane"
    ]["normals"] != encode_points(positive_normals):
        raise AssertionError("saved positive local band lane changed")
    if source_local_to_global(negative[0], 1) != m2_complement[-1]:
        raise AssertionError("negative lane does not glue to the retained m2 end")
    if target_local_to_global(negative[-1], 0) != m1_complement[0]:
        raise AssertionError("negative lane does not glue to the oriented m1 parallel")
    if target_local_to_global(positive[0], 1) != m1_complement[-1]:
        raise AssertionError("positive lane does not glue to the translated m1 endpoint")
    if source_local_to_global(positive[-1], 1) != translate(m2_complement[0], m2_deck):
        raise AssertionError("positive lane does not close the m2 deck cycle")
    if negative_normals[0] != m2_complement_normals[-1]:
        raise AssertionError("negative lane source framing does not glue")
    if negative_normals[-1] != m1_complement_normals[0]:
        raise AssertionError("negative lane target framing does not glue")
    if positive_normals[0] != m1_complement_normals[-1]:
        raise AssertionError("positive lane target framing does not glue")
    if positive_normals[-1] != m2_complement_normals[0]:
        raise AssertionError("positive lane source framing does not glue")
    if data["intersection_orientation_check"] != {
        "removed_source_x_intersection": 1,
        "inserted_m1_x_intersection": -1,
        "sum": 0,
    }:
        raise AssertionError("x-handle intersection does not cancel algebraically")

    recovered = [
        *m2_complement,
        translate(m2_points[source_start + 1], m2_deck),
        translate(source_interval[1], m2_deck),
    ]
    if data["inverse_move"]["recovered_previous_refined_m2_sha256"] != canonical_sha(
        encode_points(recovered)
    ):
        raise AssertionError("inverse hybrid move does not recover m2")
    adjusted_push = [
        tuple(value[axis] + normal[axis] for axis in range(4))
        for value, normal in zip(m2_points, m2_normals)
    ]
    adjustment_checks = verify_changed_push_clearance(
        "m_2",
        m2_points,
        adjusted_push,
        m2_seams,
        [source_start, source_start + 1, source_end],
        states,
    )
    return {
        "verdict": "PASS_X_BAND0_HYBRID_FRAMED_STATE_0_TO_1",
        "prerequisite_verdicts": prerequisite_verdicts,
        "hybrid_pieces": len(data["pieces"]),
        "chart_gluings": len(data["chart_gluings"]),
        "source_framing_adjustment_checks": adjustment_checks,
        "inverse_recovers_m2": True,
        "x_intersection_after": 0,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
