#!/usr/bin/env python3
"""Independently verify all Johnson and dual x-source chart germs."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from build_t73_t_hcs_cancellation_readiness import final_states

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_source_chart_germs.json"
LOCAL_STATE = ROOT / "geometry/t73_x_positive_belt_state0.json"
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
PERIOD = Fraction(4)


def point(values):
    return tuple(Fraction(value) for value in values)


def deck_offset(global_value, local_value):
    values = [
        (global_value[axis] - local_value[axis]) / PERIOD for axis in range(3)
    ]
    if any(value.denominator != 1 for value in values):
        return None
    return tuple(int(value) for value in values)


def translated(local_arc, deck):
    return [
        tuple(value[axis] + PERIOD * deck[axis] for axis in range(3))
        + (value[3],)
        for value in local_arc
    ]


def occurrence_count(points, local_arc):
    matches = []
    for index in range(len(points) - 2):
        deck = deck_offset(points[index], local_arc[0])
        if deck is not None and points[index : index + 3] == translated(local_arc, deck):
            matches.append((index, deck))
    return matches


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    local_state = json.loads(LOCAL_STATE.read_text(encoding="utf-8"))
    local_movie = json.loads(LOCAL_MOVIE.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    if data["completion_status"] != "ALL_1513_X_SOURCE_CHART_GERMS_BOUND":
        raise AssertionError("x source-germ scope changed")
    expected_hashes = {
        "positive_belt_state0_sha256": local_state["sha256"],
        "x_local_movie_sha256": local_movie["sha256"],
        "johnson_spine_embedding_sha256": spine["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
    }
    if any(data[field] != value for field, value in expected_hashes.items()):
        raise AssertionError("x source germs have stale source bindings")
    local_arcs = {item["source_id"]: item for item in local_state["arcs"]}
    spine_arcs = {item["arc_id"]: item for item in spine["handle_arcs"]}
    states = final_states()
    johnson_count = dual_count = unique_checks = 0
    seen = set()
    for record, band in zip(data["germs"], local_movie["bands"]):
        if record["band_index"] != band["band_index"] or record["source_id"] != band["source_id"]:
            raise AssertionError("x source-germ order changed")
        source_id = record["source_id"]
        local_record = local_arcs[source_id]
        component = record["component"]
        start, end = record["global_vertex_range"]
        deck = tuple(record["global_deck"])
        if record["orientation"] != local_record["orientation"]:
            raise AssertionError("x source-germ orientation changed")
        if record["chart"] == "mapping_torus_top_global":
            local_arc = [
                point([*value, "1"])
                for value in spine_arcs[source_id]["lift_polyline"]
            ]
            global_points = states[component][0]
            matches = occurrence_count(global_points, local_arc)
            if matches != [(start, deck)]:
                raise AssertionError(f"{source_id}: Johnson germ is not unique")
            if global_points[start : end + 1] != translated(local_arc, deck):
                raise AssertionError("saved Johnson global arc changed")
            johnson_count += 1
        elif record["chart"] == "fiber_dual_global":
            dual = [point(value) for value in ar_link["components"][component]["polyline"]]
            local_arc = [point(value) for value in record["local_oriented_arc"]]
            local_spatial = [(*value[:3], Fraction(0)) for value in local_arc]
            global_with_dummy = [(*value, Fraction(0)) for value in dual]
            matches = occurrence_count(global_with_dummy, local_spatial)
            if matches != [(start, deck)]:
                raise AssertionError(f"{source_id}: dual germ is not unique")
            if [point(value) for value in record["global_oriented_arc"]] != global_with_dummy[
                start : end + 1
            ]:
                raise AssertionError("saved dual global arc changed")
            dual_count += 1
        else:
            raise AssertionError("unknown x source chart")
        key = (component, start, end)
        if key in seen:
            raise AssertionError("two x sources use the same oriented global arc")
        seen.add(key)
        unique_checks += 1
    if (johnson_count, dual_count, unique_checks) != (1509, 4, 1513):
        raise AssertionError("x source-germ counts changed")
    return {
        "verdict": "PASS_ALL_1513_X_SOURCE_CHART_GERMS",
        "johnson_top_germs": johnson_count,
        "dual_boundary_germs": dual_count,
        "unique_global_ranges": unique_checks,
        "nu_equals_u_assumed": False,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
