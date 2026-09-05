#!/usr/bin/env python3
"""Verify the surviving marked-foot ordering and dotted slot assignment."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from verify_t73_final_yz_foot_state import verify as verify_foot_state

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_foot_to_dotted_slot_map.json"
FOOT_STATE = ROOT / "geometry/t73_final_yz_foot_state.json"
RAILROAD = ROOT / "geometry/t73_actual_railroad_core_coordinates.json"
FOOT_CHART = ROOT / "geometry/t73_unified_kirby_foot_chart.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def verify() -> dict:
    if verify_foot_state()["verdict"] != "PASS_FINAL_YZ_FOOT_AND_PASSAGE_STATE":
        raise AssertionError("final foot state did not verify")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    foot_state = json.loads(FOOT_STATE.read_text(encoding="utf-8"))
    railroad = json.loads(RAILROAD.read_text(encoding="utf-8"))
    foot_chart = json.loads(FOOT_CHART.read_text(encoding="utf-8"))
    if data["completion_status"] != "FOOT_MARKED_POINTS_ORDERED_AND_DOTTED_SLOTS_ASSIGNED":
        raise AssertionError("dotted slot-map scope changed")
    if data["final_yz_foot_state_sha256"] != foot_state["sha256"] or data["railroad_core_coordinates_sha256"] != railroad["sha256"] or data["unified_foot_chart_sha256"] != foot_chart["sha256"]:
        raise AssertionError("dotted slot map has stale sources")
    passages = {
        passage["passage_id"]: {**passage, "handle": handle["name"]}
        for handle in foot_state["handles"]
        for passage in handle["passages"]
    }
    survivors = {
        passage_id
        for component in railroad["components"]
        for passage_id in component["survivor_passage_ids"]
    }
    total = 0
    for handle in data["handles"]:
        name = handle["handle"]
        denominator = handle["ordering_denominator"]
        expected = sorted(
            (
                point(passages[passage_id]["belt_point"])[0]
                + point(passages[passage_id]["belt_point"])[1] / denominator,
                passage_id,
            )
            for passage_id in survivors
            if passages[passage_id]["handle"] == name
        )
        if len({value for value, _ in expected}) != len(expected):
            raise AssertionError("saved dotted ordering functional is not generic")
        entries = handle["entries"]
        if [item["passage_id"] for item in entries] != [item[1] for item in expected]:
            raise AssertionError("dotted slot marked-point order changed")
        used_segments = set()
        for rank, ((key, passage_id), entry) in enumerate(zip(expected, entries)):
            source = passages[passage_id]
            if entry["ordering_key"] != str(key) or entry["rank"] != rank:
                raise AssertionError("dotted slot rank/key changed")
            if entry["negative_foot_endpoint"] != source["negative_foot_endpoint"] or entry["positive_foot_endpoint"] != source["positive_foot_endpoint"]:
                raise AssertionError("dotted slot lost its reflected foot endpoints")
            expected_pair = [2 * rank, 2 * rank + 1]
            if entry["dotted_segment_pair"] != expected_pair:
                raise AssertionError("dotted segment-pair assignment changed")
            if used_segments & set(expected_pair):
                raise AssertionError("two passages share a dotted segment")
            used_segments.update(expected_pair)
            expected_slot = ["0", str(Fraction(rank + 1, len(entries) + 1))]
            if entry["target_disk_slot"] != expected_slot:
                raise AssertionError("target dotted-disk slot changed")
        if used_segments != set(range(2 * len(entries))):
            raise AssertionError("dotted segments are not an exhaustive partition")
        total += len(entries)
    if total != 1785 or data["disk_track_status"] != "OPEN_EXPLICIT_MARKED_CONFIGURATION_ISOTOPY":
        raise AssertionError("dotted slot map overstates its track completion")
    return {
        "verdict": "PASS_FOOT_MARKED_ORDER_AND_DOTTED_SLOT_ASSIGNMENT_ONLY",
        "y_slots": 235,
        "z_slots": 1550,
        "surviving_marked_points": total,
        "dotted_segments": 2 * total,
        "explicit_disk_tracks": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
