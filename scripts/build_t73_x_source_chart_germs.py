#!/usr/bin/env python3
"""Locate all 1513 x-slide source arcs in their actual global component charts."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from build_t73_t_hcs_cancellation_readiness import final_states

ROOT = Path(__file__).resolve().parents[1]
LOCAL_STATE = ROOT / "geometry/t73_x_positive_belt_state0.json"
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
OUTPUT = ROOT / "geometry/t73_x_source_chart_germs.json"
PERIOD = Fraction(4)


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def deck_offset(global_value, local_value):
    quotients = [
        (global_value[axis] - local_value[axis]) / PERIOD for axis in range(3)
    ]
    if any(value.denominator != 1 for value in quotients):
        return None
    return tuple(int(value) for value in quotients)


def locate_top_arc(points, local_arc):
    matches = []
    for index in range(len(points) - 2):
        candidate = points[index : index + 3]
        deck = deck_offset(candidate[0], local_arc[0])
        if deck is None:
            continue
        translated = [
            tuple(value[axis] + PERIOD * deck[axis] for axis in range(3))
            + (value[3],)
            for value in local_arc
        ]
        if candidate == translated:
            matches.append((index, deck))
    if len(matches) != 1:
        raise AssertionError(f"Johnson x-arc has {len(matches)} global occurrences")
    return matches[0]


def locate_dual_arc(polyline, local_arc, orientation):
    oriented_local = local_arc if orientation == 1 else list(reversed(local_arc))
    matches = []
    for index in range(len(polyline) - 2):
        candidate = polyline[index : index + 3]
        deck = deck_offset(
            (*candidate[0], Fraction(0)), (*oriented_local[0][:3], Fraction(0))
        )
        if deck is None:
            continue
        translated = [
            tuple(value[axis] + PERIOD * deck[axis] for axis in range(3))
            for value in oriented_local
        ]
        if candidate == translated:
            matches.append((index, deck, oriented_local))
    if len(matches) != 1:
        raise AssertionError(f"dual x-arc has {len(matches)} global occurrences")
    return matches[0]


def build() -> dict:
    local_state = json.loads(LOCAL_STATE.read_text(encoding="utf-8"))
    local_movie = json.loads(LOCAL_MOVIE.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    local_arcs = {item["source_id"]: item for item in local_state["arcs"]}
    spine_arcs = {item["arc_id"]: item for item in spine["handle_arcs"]}
    states = final_states()
    germs = []
    for band in local_movie["bands"]:
        source_id = band["source_id"]
        local_record = local_arcs[source_id]
        local_arc = [point(value) for value in local_record["polyline"]]
        component = band["component"]
        if local_record["source_kind"] == "johnson_handle_lane":
            top_arc = [point([*value, "1"]) for value in spine_arcs[source_id]["lift_polyline"]]
            index, deck = locate_top_arc(states[component][0], top_arc)
            germs.append({
                "band_index": band["band_index"],
                "source_id": source_id,
                "component": component,
                "chart": "mapping_torus_top_global",
                "global_vertex_range": [index, index + 2],
                "global_deck": list(deck),
                "orientation": band["source_orientation"],
                "local_oriented_arc": [encode(value) for value in local_arc],
                "global_oriented_arc": [
                    encode(value) for value in states[component][0][index : index + 3]
                ],
                "status": "ACTUAL_JOHNSON_TOP_ARC_GERM",
            })
        else:
            dual = [point(value) for value in ar_link["components"][component]["polyline"]]
            local_spatial = [value[:3] for value in local_arc]
            index, deck, oriented_local = locate_dual_arc(
                dual, local_spatial, band["source_orientation"]
            )
            germs.append({
                "band_index": band["band_index"],
                "source_id": source_id,
                "component": component,
                "chart": "fiber_dual_global",
                "global_vertex_range": [index, index + 2],
                "global_deck": list(deck),
                "orientation": band["source_orientation"],
                "local_oriented_arc": [encode(value) for value in oriented_local],
                "global_oriented_arc": [
                    encode((*value, Fraction(0))) for value in dual[index : index + 3]
                ],
                "status": "ACTUAL_DUAL_DISK_BOUNDARY_GERM",
            })
    if len(germs) != 1513 or [item["band_index"] for item in germs] != list(range(1513)):
        raise AssertionError("x source chart germs do not cover the schedule")
    result = {
        "schema": "t73_x_source_chart_germs/v1",
        "positive_belt_state0_sha256": local_state["sha256"],
        "x_local_movie_sha256": local_movie["sha256"],
        "johnson_spine_embedding_sha256": spine["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "germs": germs,
        "counts": {
            "mapping_torus_top": sum(item["chart"] == "mapping_torus_top_global" for item in germs),
            "fiber_dual": sum(item["chart"] == "fiber_dual_global" for item in germs),
            "total": len(germs),
        },
        "completion_status": "ALL_1513_X_SOURCE_CHART_GERMS_BOUND",
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
        raise AssertionError("x source chart germs are stale")
    print("T73_X_SOURCE_GERMS=ALL_1513_X_SOURCE_CHART_GERMS_BOUND")


if __name__ == "__main__":
    main()
