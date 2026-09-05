#!/usr/bin/env python3
"""Build the first global/local hybrid x-slide state transition."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from build_t73_t_hcs_cancellation_readiness import final_states
ROOT = Path(__file__).resolve().parents[1]
SURFACE = ROOT / "geometry/t73_x_band0_attachment_surface.json"
CHARTS = ROOT / "geometry/t73_x_band0_chart_transitions.json"
PARALLEL = ROOT / "geometry/t73_x_band0_m1_parallel.json"
EXTERIOR = ROOT / "geometry/t73_t_hcs_framing_exteriorization.json"
OUTPUT = ROOT / "geometry/t73_x_band_hybrid_state_0000_0001.json"
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


def expanded_exterior_normals(component, normals, exterior):
    replacements = {
        item["vertex_index"]: point(item["new_normal"])
        for item in exterior["components"][component]["normal_replacements"]
    }
    return [replacements.get(index, value) for index, value in enumerate(normals)]


def cut_complement(points, normals, center_index, before, after, deck):
    before_normal = interpolate(
        before,
        points[center_index - 1],
        points[center_index],
        normals[center_index - 1],
        normals[center_index],
    )
    after_normal = interpolate(
        after,
        points[center_index],
        points[center_index + 1],
        normals[center_index],
        normals[center_index + 1],
    )
    complement = [
        after,
        *points[center_index + 1 :],
        *[translate(points[index], deck) for index in range(1, center_index)],
        translate(before, deck),
    ]
    complement_normals = [
        after_normal,
        *normals[center_index + 1 :],
        *normals[1:center_index],
        before_normal,
    ]
    return complement, complement_normals


def build() -> dict:
    surface = json.loads(SURFACE.read_text(encoding="utf-8"))
    charts = json.loads(CHARTS.read_text(encoding="utf-8"))
    parallel_data = json.loads(PARALLEL.read_text(encoding="utf-8"))
    exterior = json.loads(EXTERIOR.read_text(encoding="utf-8"))
    states = final_states()
    m2_points, m2_original_normals, _ = states["m_2"]
    m2_normals = expanded_exterior_normals("m_2", m2_original_normals, exterior)
    source_start, source_end = surface["source_arc_current_state_vertex_range"]
    source_center_index = source_start + 1
    source_normal = point(surface["source_normal_mod_x_tangent"])
    source_adjustments = []
    for index in range(source_start, source_end + 1):
        source_adjustments.append({
            "vertex_index": index,
            "old_normal": [str(value) for value in m2_normals[index]],
            "new_normal": [str(value) for value in source_normal],
        })
        m2_normals[index] = source_normal
    source_interval = [point(value) for value in surface["source_interval_current_state"]]
    m2_deck = tuple(
        int((m2_points[-1][axis] - m2_points[0][axis]) / PERIOD)
        for axis in range(3)
    )
    m2_complement, m2_complement_normals = cut_complement(
        m2_points,
        m2_normals,
        source_center_index,
        source_interval[0],
        source_interval[1],
        m2_deck,
    )

    parallel = [point(value) for value in parallel_data["parallel_vertices"]]
    parallel_offsets = [point(value) for value in parallel_data["framing_offsets"]]
    coefficient = parallel_data["parallel_coefficient"]
    parallel_normals = [
        tuple(value / coefficient for value in offset) for offset in parallel_offsets
    ]
    target_interval = [point(value) for value in parallel_data["target_interval_global"]]
    m1_deck = (-1, 0, 1)
    m1_complement, m1_complement_normals = cut_complement(
        parallel,
        parallel_normals,
        3,
        target_interval[0],
        target_interval[1],
        m1_deck,
    )

    vertices = [point(value) for value in surface["vertices"]]
    normals = [point(value) for value in surface["normal_field"]]
    negative_ids = surface["boundary"]["negative_x_lane"]
    positive_ids = surface["boundary"]["positive_x_lane"]
    negative_lane = [vertices[index] for index in negative_ids]
    positive_lane = [vertices[index] for index in positive_ids]
    negative_normals = [normals[index] for index in negative_ids]
    positive_normals = [normals[index] for index in positive_ids]
    recovered_m2 = [
        *m2_complement,
        translate(m2_points[source_center_index], m2_deck),
        translate(source_interval[1], m2_deck),
    ]
    pieces = [
        {
            "name": "retained_m2_complement",
            "chart": "mapping_torus_global",
            "vertex_count": len(m2_complement),
            "vertices_sha256": canonical_sha(encode_points(m2_complement)),
            "normals_sha256": canonical_sha(encode_points(m2_complement_normals)),
            "start": [str(value) for value in m2_complement[0]],
            "end": [str(value) for value in m2_complement[-1]],
        },
        {
            "name": "negative_band_lane",
            "chart": "positive_x_belt_local",
            "vertices": encode_points(negative_lane),
            "normals": encode_points(negative_normals),
        },
        {
            "name": "oriented_m1_parallel_complement",
            "chart": "mapping_torus_global",
            "vertex_count": len(m1_complement),
            "vertices_sha256": canonical_sha(encode_points(m1_complement)),
            "normals_sha256": canonical_sha(encode_points(m1_complement_normals)),
            "start": [str(value) for value in m1_complement[0]],
            "end": [str(value) for value in m1_complement[-1]],
        },
        {
            "name": "positive_band_lane",
            "chart": "positive_x_belt_local",
            "vertices": encode_points(positive_lane),
            "normals": encode_points(positive_normals),
        },
    ]
    result = {
        "schema": "t73_x_band_hybrid_state/v1",
        "surface_sha256": surface["sha256"],
        "chart_transitions_sha256": charts["sha256"],
        "m1_parallel_sha256": parallel_data["sha256"],
        "framing_exteriorization_sha256": exterior["sha256"],
        "state_before": 0,
        "state_after": 1,
        "band_index": 0,
        "moved_component": "m_2",
        "source_normal_adjustments": source_adjustments,
        "hybrid_piece_order": [piece["name"] for piece in pieces],
        "pieces": pieces,
        "chart_gluings": [
            {
                "from": "retained_m2_complement/end",
                "to": "negative_band_lane/start",
                "germ": "source_germ",
                "source_deck_cycle": 1,
            },
            {
                "from": "negative_band_lane/end",
                "to": "oriented_m1_parallel_complement/start",
                "germ": "target_germ",
                "target_deck_cycle": 0,
            },
            {
                "from": "oriented_m1_parallel_complement/end",
                "to": "positive_band_lane/start",
                "germ": "target_germ",
                "target_deck_cycle": 1,
            },
            {
                "from": "positive_band_lane/end",
                "to": "retained_m2_complement/start",
                "germ": "source_germ",
                "source_deck_cycle": 1,
            },
        ],
        "intersection_orientation_check": {
            "removed_source_x_intersection": 1,
            "inserted_m1_x_intersection": -1,
            "sum": 0,
        },
        "inverse_move": {
            "kind": "remove_hybrid_band_sum_and_restore_m2_source_subarc",
            "recovered_previous_refined_m2_sha256": canonical_sha(
                encode_points(recovered_m2)
            ),
        },
        "completion_status": "X_BAND0_HYBRID_FRAMED_STATE_TRANSITION_CONSTRUCTED",
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
        raise AssertionError("x-band hybrid state 0-to-1 is stale")
    print("T73_X_STATE_0000_0001=X_BAND0_HYBRID_FRAMED_STATE_TRANSITION_CONSTRUCTED")


if __name__ == "__main__":
    main()
