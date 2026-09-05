#!/usr/bin/env python3
"""Independently verify the three final free-reduction bigon tubes."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_final_free_reduction_bigons.json"
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
FOOT_STATE = ROOT / "geometry/t73_final_yz_foot_state.json"
RAILROAD = ROOT / "geometry/t73_actual_railroad_core_coordinates.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def distance_squared(first, second):
    return sum((left - right) ** 2 for left, right in zip(first, second))


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    foot_state = json.loads(FOOT_STATE.read_text(encoding="utf-8"))
    railroad = json.loads(RAILROAD.read_text(encoding="utf-8"))
    if data["completion_status"] != "CANDIDATE_FREE_REDUCTION_ENDPOINT_TUBES_CONNECTOR_SURFACES_OPEN":
        raise AssertionError("free-reduction bigon scope changed")
    if data["final_component_passage_cycles_sha256"] != cycles["sha256"] or data["final_yz_foot_state_sha256"] != foot_state["sha256"] or data["railroad_core_coordinates_sha256"] != railroad["sha256"]:
        raise AssertionError("free-reduction bigons have stale sources")
    passages = {
        passage["passage_id"]: {**passage, "handle": handle["name"]}
        for handle in foot_state["handles"]
        for passage in handle["passages"]
    }
    z_endpoints = [
        point(passage[field])
        for passage in passages.values()
        if passage["handle"] == "z"
        for field in ("negative_foot_endpoint", "positive_foot_endpoint")
    ]
    state_by_component = {
        item["component"]: list(item["passage_ids"])
        for item in cycles["components"]
    }
    minimum_radius_squared = None
    for move in data["moves"]:
        component = move["component"]
        current = state_by_component[component]
        if move["state_before_passage_ids"] != current or move["state_before_sha256"] != canonical_sha(current):
            raise AssertionError("bigon state-before changed")
        first_id = move["first_passage_id"]
        second_id = move["second_passage_id"]
        first_index = current.index(first_id)
        if current[(first_index + 1) % len(current)] != second_id:
            raise AssertionError("bigon passages are not cyclically adjacent")
        first = passages[first_id]
        second = passages[second_id]
        if first["handle"] != "z" or second["handle"] != "z" or first["orientation"] != -second["orientation"]:
            raise AssertionError("bigon does not cancel inverse z passages")
        output = current[:first_index] + current[first_index + 2 :]
        if move["state_after_passage_ids"] != output or move["state_after_sha256"] != canonical_sha(output):
            raise AssertionError("bigon state-after changed")
        if move["inverse_move"]["restores_state_sha256"] != canonical_sha(current):
            raise AssertionError("inverse bigon does not restore its input")
        selected = {
            point(first["negative_foot_endpoint"]),
            point(first["positive_foot_endpoint"]),
            point(second["negative_foot_endpoint"]),
            point(second["positive_foot_endpoint"]),
        }
        separation = min(
            distance_squared(chosen, other)
            for chosen in selected
            for other in z_endpoints
            if other not in selected
        )
        if Fraction(move["minimum_other_endpoint_distance_squared"]) != separation or Fraction(move["tube_radius_squared"]) != separation / 16 or separation <= 0:
            raise AssertionError("bigon endpoint tube radius changed")
        minimum_radius_squared = (
            separation / 16
            if minimum_radius_squared is None
            else min(minimum_radius_squared, separation / 16)
        )
        bigon = move["standard_bigon"]
        edge_counts = Counter(
            tuple(sorted((triangle[index], triangle[(index + 1) % 3])))
            for triangle in bigon["triangles"]
            for index in range(3)
        )
        if 4 - len(edge_counts) + len(bigon["triangles"]) != 1 or sum(
            count == 1 for count in edge_counts.values()
        ) != 4:
            raise AssertionError("standard reduction bigon is not a disk")
        state_by_component[component] = output
    if len(state_by_component["m_3"]) != 1460 or state_by_component["r_zx"]:
        raise AssertionError("candidate bigon word reductions changed")
    return {
        "verdict": "PASS_FREE_REDUCTION_ENDPOINT_TUBES_ONLY",
        "moves": len(data["moves"]),
        "m3_removed_passages": 2,
        "rzx_removed_passages": 4,
        "minimum_tube_radius_squared": str(minimum_radius_squared),
        "all_inverse_moves": True,
        "connector_spanning_surfaces": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
