#!/usr/bin/env python3
"""Move all surviving marked foot points to dotted slots by explicit disk paths."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLOTS = ROOT / "geometry/t73_foot_to_dotted_slot_map.json"
FOOT_CHART = ROOT / "geometry/t73_unified_kirby_foot_chart.json"
OUTPUT = ROOT / "geometry/t73_foot_to_dotted_disk_tracks.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def lies_on_segment(value, start, end):
    direction = (end[0] - start[0], end[1] - start[1])
    delta = (value[0] - start[0], value[1] - start[1])
    axis = next((index for index, coordinate in enumerate(direction) if coordinate), None)
    if axis is None:
        return value == start
    parameter = delta[axis] / direction[axis]
    return 0 <= parameter <= 1 and all(
        delta[index] == parameter * direction[index] for index in range(2)
    )


def choose_waypoint(start, target, obstacles, rank, count):
    for attempt in range(2 * count + 20):
        x_coordinate = Fraction(1, 2) if attempt % 2 == 0 else Fraction(-1, 2)
        y_index = (rank + attempt) % (count + 1)
        y_coordinate = Fraction(-1, 2) + Fraction(y_index + 1, count + 2)
        waypoint = (x_coordinate, y_coordinate)
        if waypoint[0] ** 2 + waypoint[1] ** 2 >= 1:
            continue
        if any(
            lies_on_segment(obstacle, start, waypoint)
            or lies_on_segment(obstacle, waypoint, target)
            for obstacle in obstacles
        ):
            continue
        return waypoint, attempt
    raise AssertionError("no rational marked-disk waypoint avoids the fixed configuration")


def build() -> dict:
    slots = json.loads(SLOTS.read_text(encoding="utf-8"))
    foot_chart = json.loads(FOOT_CHART.read_text(encoding="utf-8"))
    handles = []
    for handle in slots["handles"]:
        entries = handle["entries"]
        actual = {
            entry["passage_id"]: (
                point(entry["belt_point"])[0] / 4,
                point(entry["belt_point"])[1] / 4,
            )
            for entry in entries
        }
        targets = {
            entry["passage_id"]: point(entry["target_disk_slot"])
            for entry in entries
        }
        current = dict(actual)
        tracks = []
        for move_index, entry in enumerate(entries):
            passage_id = entry["passage_id"]
            start = current[passage_id]
            target = targets[passage_id]
            obstacles = [
                value for other_id, value in current.items() if other_id != passage_id
            ]
            waypoint, attempt = choose_waypoint(
                start, target, obstacles, move_index, len(entries)
            )
            tracks.append({
                "move_index": move_index,
                "passage_id": passage_id,
                "normalized_start": encode(start),
                "normalized_waypoint": encode(waypoint),
                "normalized_target": encode(target),
                "waypoint_attempt": attempt,
                "negative_foot_endpoint": entry["negative_foot_endpoint"],
                "positive_foot_endpoint": entry["positive_foot_endpoint"],
                "paired_track_rule": (
                    "apply the same normalized path in both foot disks; the "
                    "Figure-2a reflection exchanges the two physical tracks"
                ),
            })
            current[passage_id] = target
        if current != targets:
            raise AssertionError("marked disk tracks did not reach every dotted slot")
        handles.append({
            "handle": handle["handle"],
            "move_count": len(tracks),
            "tracks": tracks,
            "initial_configuration_sha256": canonical_sha(
                {key: encode(value) for key, value in sorted(actual.items())}
            ),
            "final_configuration_sha256": canonical_sha(
                {key: encode(value) for key, value in sorted(targets.items())}
            ),
        })
    result = {
        "schema": "t73_foot_to_dotted_disk_tracks/v1",
        "foot_to_dotted_slot_map_sha256": slots["sha256"],
        "unified_foot_chart_sha256": foot_chart["sha256"],
        "handles": handles,
        "move_count": sum(handle["move_count"] for handle in handles),
        "completion_status": "EXPLICIT_REFLECTION_PAIRED_MARKED_DISK_TRACKS_CONSTRUCTED",
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
        raise AssertionError("foot-to-dotted disk tracks are stale")
    print("T73_DOTTED_DISK_TRACKS=EXPLICIT_REFLECTION_PAIRED_MARKED_DISK_TRACKS_CONSTRUCTED")


if __name__ == "__main__":
    main()
