#!/usr/bin/env python3
"""Order surviving marked foot points and assign compatible dotted-clasp slots."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOOT_STATE = ROOT / "geometry/t73_final_yz_foot_state.json"
RAILROAD = ROOT / "geometry/t73_actual_railroad_core_coordinates.json"
FOOT_CHART = ROOT / "geometry/t73_unified_kirby_foot_chart.json"
OUTPUT = ROOT / "geometry/t73_foot_to_dotted_slot_map.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def build() -> dict:
    foot_state = json.loads(FOOT_STATE.read_text(encoding="utf-8"))
    railroad = json.loads(RAILROAD.read_text(encoding="utf-8"))
    foot_chart = json.loads(FOOT_CHART.read_text(encoding="utf-8"))
    passages = {
        passage["passage_id"]: {**passage, "handle": handle["name"]}
        for handle in foot_state["handles"]
        for passage in handle["passages"]
    }
    surviving_ids = {
        passage_id
        for component in railroad["components"]
        for passage_id in component["survivor_passage_ids"]
    }
    handles = []
    for handle_name in ("y", "z"):
        handle_ids = sorted(
            passage_id
            for passage_id in surviving_ids
            if passages[passage_id]["handle"] == handle_name
        )
        denominator = None
        keyed = None
        for candidate in (1009, 1013, 1019, 1021, 1031, 10007):
            values = [
                (
                    point(passages[passage_id]["belt_point"])[0]
                    + point(passages[passage_id]["belt_point"])[1]
                    / candidate,
                    passage_id,
                )
                for passage_id in handle_ids
            ]
            if len({value for value, _ in values}) == len(values):
                denominator = candidate
                keyed = sorted(values)
                break
        if denominator is None or keyed is None:
            raise AssertionError(f"no generic marked-point ordering for {handle_name}")
        entries = []
        count = len(keyed)
        for rank, (key, passage_id) in enumerate(keyed):
            passage = passages[passage_id]
            slot = Fraction(rank + 1, count + 1)
            entries.append({
                "passage_id": passage_id,
                "component": passage["component"],
                "orientation": passage["orientation"],
                "belt_point": passage["belt_point"],
                "negative_foot_endpoint": passage["negative_foot_endpoint"],
                "positive_foot_endpoint": passage["positive_foot_endpoint"],
                "ordering_key": str(key),
                "rank": rank,
                "dotted_segment_pair": [2 * rank, 2 * rank + 1],
                "target_disk_slot": ["0", str(slot)],
            })
        handles.append({
            "handle": handle_name,
            "ordering_functional": f"lane_0 + lane_1/{denominator}",
            "ordering_denominator": denominator,
            "surviving_passage_count": count,
            "entries": entries,
            "target_slot_rule": "rank r maps to (0,(r+1)/(N+1)) in the standard dotted disk",
            "reflection_compatibility": (
                "negative and positive foot endpoints of one passage share one target slot"
            ),
        })
    if [item["surviving_passage_count"] for item in handles] != [235, 1544]:
        raise AssertionError("surviving y/z dotted slot counts changed")
    result = {
        "schema": "t73_foot_to_dotted_slot_map/v1",
        "final_yz_foot_state_sha256": foot_state["sha256"],
        "railroad_core_coordinates_sha256": railroad["sha256"],
        "unified_foot_chart_sha256": foot_chart["sha256"],
        "handles": handles,
        "surviving_marked_points": sum(
            item["surviving_passage_count"] for item in handles
        ),
        "disk_track_status": "OPEN_EXPLICIT_MARKED_CONFIGURATION_ISOTOPY",
        "completion_status": "FOOT_MARKED_POINTS_ORDERED_AND_DOTTED_SLOTS_ASSIGNED",
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
        raise AssertionError("foot-to-dotted slot map is stale")
    print("T73_DOTTED_SLOTS=FOOT_MARKED_POINTS_ORDERED_AND_DOTTED_SLOTS_ASSIGNED")


if __name__ == "__main__":
    main()
