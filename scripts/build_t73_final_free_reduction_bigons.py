#!/usr/bin/env python3
"""Build the three local bigon isotopies realizing the final free reductions."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
FOOT_STATE = ROOT / "geometry/t73_final_yz_foot_state.json"
RAILROAD_CORE = ROOT / "geometry/t73_actual_railroad_core_coordinates.json"
OUTPUT = ROOT / "geometry/t73_final_free_reduction_bigons.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def distance_squared(first, second):
    return sum((left - right) ** 2 for left, right in zip(first, second))


def passage_lookup(foot_state):
    return {
        passage["passage_id"]: {**passage, "handle": handle["name"]}
        for handle in foot_state["handles"]
        for passage in handle["passages"]
    }


def bigon_record(component, move_index, first_id, second_id, passages, state_before, state_after):
    first = passages[first_id]
    second = passages[second_id]
    if first["handle"] != second["handle"] or first["orientation"] != -second["orientation"]:
        raise AssertionError("free-reduction passages are not inverse handle letters")
    all_endpoints = [
        point(passage[field])
        for passage in passages.values()
        if passage["handle"] == first["handle"]
        for field in ("negative_foot_endpoint", "positive_foot_endpoint")
    ]
    selected = {
        point(first["negative_foot_endpoint"]),
        point(first["positive_foot_endpoint"]),
        point(second["negative_foot_endpoint"]),
        point(second["positive_foot_endpoint"]),
    }
    separation = min(
        distance_squared(chosen, other)
        for chosen in selected
        for other in all_endpoints
        if other not in selected
    )
    return {
        "component": component,
        "move_index": move_index,
        "first_passage_id": first_id,
        "second_passage_id": second_id,
        "handle": first["handle"],
        "orientations": [first["orientation"], second["orientation"]],
        "state_before_passage_ids": state_before,
        "state_after_passage_ids": state_after,
        "state_before_sha256": canonical_sha(state_before),
        "state_after_sha256": canonical_sha(state_after),
        "standard_bigon": {
            "vertices": [["0", "0"], ["1", "0"], ["1", "1"], ["0", "1"]],
            "triangles": [[0, 1, 2], [0, 2, 3]],
            "boundary_roles": [
                "first_handle_passage",
                "positive_or_negative_foot_connector",
                "inverse_second_handle_passage",
                "opposite_foot_connector",
            ],
        },
        "minimum_other_endpoint_distance_squared": str(separation),
        "tube_radius_squared": str(separation / 16),
        "inverse_move": {
            "kind": "insert_inverse_passage_pair_in_same_regular_neighborhood",
            "restores_state_sha256": canonical_sha(state_before),
        },
        "status": "LOCAL_PRODUCT_BIGON_WITH_DISJOINT_ENDPOINT_TUBE",
    }


def build() -> dict:
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    foot_state = json.loads(FOOT_STATE.read_text(encoding="utf-8"))
    railroad = json.loads(RAILROAD_CORE.read_text(encoding="utf-8"))
    passages = passage_lookup(foot_state)
    cycles_by_name = {
        item["component"]: list(item["passage_ids"])
        for item in cycles["components"]
    }
    moves = []
    m3_before = cycles_by_name["m_3"]
    m3_after = m3_before[2:]
    moves.append(
        bigon_record(
            "m_3", 0, m3_before[0], m3_before[1], passages, m3_before, m3_after
        )
    )
    rzx_before = cycles_by_name["r_zx"]
    rzx_middle = [rzx_before[0], rzx_before[3]]
    moves.append(
        bigon_record(
            "r_zx",
            1,
            rzx_before[1],
            rzx_before[2],
            passages,
            rzx_before,
            rzx_middle,
        )
    )
    moves.append(
        bigon_record(
            "r_zx",
            2,
            rzx_middle[0],
            rzx_middle[1],
            passages,
            rzx_middle,
            [],
        )
    )
    reduced_by_name = {
        item["name"]: item["survivor_passage_ids"]
        for item in railroad["components"]
    }
    if m3_after != reduced_by_name["m_3"] or reduced_by_name["r_zx"]:
        raise AssertionError("bigon outputs do not equal railroad survivor passage states")
    result = {
        "schema": "t73_final_free_reduction_bigons/v1",
        "final_component_passage_cycles_sha256": cycles["sha256"],
        "final_yz_foot_state_sha256": foot_state["sha256"],
        "railroad_core_coordinates_sha256": railroad["sha256"],
        "moves": moves,
        "move_count": len(moves),
        "completion_status": "THREE_FINAL_FREE_REDUCTION_BIGONS_CONSTRUCTED",
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
        raise AssertionError("final free-reduction bigons are stale")
    print("T73_FINAL_BIGONS=THREE_FINAL_FREE_REDUCTION_BIGONS_CONSTRUCTED")


if __name__ == "__main__":
    main()
