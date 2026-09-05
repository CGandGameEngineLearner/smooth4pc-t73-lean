#!/usr/bin/env python3
"""Independently replay all 1779 marked-disk point tracks."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_foot_to_dotted_disk_tracks.json"
SLOTS = ROOT / "geometry/t73_foot_to_dotted_slot_map.json"
FOOT_CHART = ROOT / "geometry/t73_unified_kirby_foot_chart.json"


def point(values):
    return tuple(Fraction(value) for value in values)


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


def matrix_apply(matrix, value):
    return tuple(
        sum(Fraction(entry) * coordinate for entry, coordinate in zip(row, value))
        for row in matrix
    )


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    slots = json.loads(SLOTS.read_text(encoding="utf-8"))
    foot_chart = json.loads(FOOT_CHART.read_text(encoding="utf-8"))
    if data["completion_status"] != "EXPLICIT_REFLECTION_PAIRED_MARKED_DISK_TRACKS_CONSTRUCTED":
        raise AssertionError("marked-disk track scope changed")
    if data["foot_to_dotted_slot_map_sha256"] != slots["sha256"] or data["unified_foot_chart_sha256"] != foot_chart["sha256"]:
        raise AssertionError("marked-disk tracks have stale sources")
    slot_by_handle = {item["handle"]: item for item in slots["handles"]}
    chart_by_name = {item["name"]: item for item in foot_chart["handles"]}
    moves = collision_checks = reflection_checks = 0
    for handle_tracks in data["handles"]:
        handle_name = handle_tracks["handle"]
        entries = slot_by_handle[handle_name]["entries"]
        current = {
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
        foot = chart_by_name[handle_name]["foot_pair"]
        matrix = foot["reflection_matrix"]
        for expected_index, track in enumerate(handle_tracks["tracks"]):
            passage_id = track["passage_id"]
            start = point(track["normalized_start"])
            waypoint = point(track["normalized_waypoint"])
            target = point(track["normalized_target"])
            if track["move_index"] != expected_index or start != current[passage_id] or target != targets[passage_id]:
                raise AssertionError("marked-disk track endpoint/state changed")
            if any(value[0] ** 2 + value[1] ** 2 >= 1 for value in (start, waypoint, target)):
                raise AssertionError("marked-disk track leaves the open normalized disk")
            obstacles = [
                value for other_id, value in current.items() if other_id != passage_id
            ]
            for obstacle in obstacles:
                collision_checks += 1
                if lies_on_segment(obstacle, start, waypoint) or lies_on_segment(
                    obstacle, waypoint, target
                ):
                    raise AssertionError("marked-disk track meets a fixed marked point")
            negative = point(track["negative_foot_endpoint"])
            positive = point(track["positive_foot_endpoint"])
            if matrix_apply(matrix, positive) != negative:
                raise AssertionError("paired physical disk tracks lost foot reflection")
            reflection_checks += 1
            current[passage_id] = target
            moves += 1
        if current != targets:
            raise AssertionError("marked-disk track replay missed a target")
    if moves != 1785 or data["move_count"] != moves:
        raise AssertionError("marked-disk move count changed")
    return {
        "verdict": "PASS_EXPLICIT_REFLECTION_PAIRED_MARKED_DISK_TRACKS",
        "moves": moves,
        "collision_checks": collision_checks,
        "reflection_checks": reflection_checks,
        "inverse_tracks": "reverse each two-segment path in reverse move order",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
