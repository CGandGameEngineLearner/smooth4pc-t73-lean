#!/usr/bin/env python3
"""Verify the 4727-row source-bound PD candidate without claiming framings."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_source_bound_standard_pd_candidate.json"
CORE = ROOT / "geometry/t73_actual_railroad_core_coordinates.json"
RAILROAD = ROOT / "geometry/t73_final_railroad_word_binding.json"
FOOT_STATE = ROOT / "geometry/t73_final_yz_foot_state.json"
FRAMINGS = ROOT / "geometry/t73_railroad_product_framings.json"
SLOT_MAP = ROOT / "geometry/t73_foot_to_dotted_slot_map.json"


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    core = json.loads(CORE.read_text(encoding="utf-8"))
    railroad = json.loads(RAILROAD.read_text(encoding="utf-8"))
    foot_state = json.loads(FOOT_STATE.read_text(encoding="utf-8"))
    framings = json.loads(FRAMINGS.read_text(encoding="utf-8"))
    slot_map = json.loads(SLOT_MAP.read_text(encoding="utf-8"))
    if data["completion_status"] != "SOURCE_BOUND_STANDARD_PD_CANDIDATE_CONSTRUCTED":
        raise AssertionError("standard PD candidate scope changed")
    if data["railroad_core_coordinates_sha256"] != core["sha256"] or data["actual_railroad_word_binding_sha256"] != railroad["sha256"] or data["final_yz_foot_state_sha256"] != foot_state["sha256"] or data["railroad_product_framings_sha256"] != framings["sha256"] or data["foot_to_dotted_slot_map_sha256"] != slot_map["sha256"]:
        raise AssertionError("standard PD candidate has stale sources")
    crossings = data["crossings"]
    if len(crossings) != 4748 or len(data["standard_pd_code"]) != 4748:
        raise AssertionError("standard PD crossing/row count changed")
    kinds = Counter(crossing["kind"] for crossing in crossings)
    if kinds != {
        "exact_railroad_core_crossing": 1178,
        "local_dotted_hopf_clasp_first": 1785,
        "local_dotted_hopf_clasp_second": 1785,
    }:
        raise AssertionError("standard PD crossing provenance changed")
    arc_incidence = Counter(
        label for row in data["standard_pd_code"] for label in row
    )
    if set(arc_incidence.values()) != {2}:
        raise AssertionError("a standard PD arc label does not occur twice")
    component_events = {
        component: events
        for component, events in data["component_halfedge_cycles"].items()
    }
    if set(component_events) != set(data["component_order"]) or any(
        not events for events in component_events.values()
    ):
        raise AssertionError("standard PD does not recover all seven cycles")
    crossing_ids = {crossing["id"] for crossing in crossings}
    for component, events in component_events.items():
        if {event["crossing"] for event in events} - crossing_ids:
            raise AssertionError(f"{component}: halfedge cycle cites an unknown crossing")
        for index, event in enumerate(events):
            successor = events[(index + 1) % len(events)]
            if event["successor_crossing"] != successor["crossing"] or event[
                "successor_role"
            ] != successor["role"]:
                raise AssertionError(f"{component}: halfedge successor chain changed")

    by_passage = {}
    slot_by_passage = {
        entry["passage_id"]: entry
        for handle in slot_map["handles"]
        for entry in handle["entries"]
    }
    for crossing in crossings:
        passage_id = crossing.get("source_passage_id")
        if passage_id is not None:
            by_passage.setdefault(passage_id, []).append(crossing)
    if len(by_passage) != 1785:
        raise AssertionError("dotted clasp insertions lost a surviving passage")
    for insertion in data["dotted_insertions"]:
        pair = by_passage[insertion["source_passage_id"]]
        if len(pair) != 2 or pair[0]["sign"] != pair[1]["sign"]:
            raise AssertionError("a dotted handle insertion is not a same-sign Hopf clasp")
        owners = {
            pair[0]["over_owner"],
            pair[0]["under_owner"],
            pair[1]["over_owner"],
            pair[1]["under_owner"],
        }
        if owners != {insertion["component"], insertion["dotted_component"]}:
            raise AssertionError("dotted clasp owner binding changed")
        expected_segments = slot_by_passage[insertion["source_passage_id"]][
            "dotted_segment_pair"
        ]
        if insertion["dotted_segment_pair"] != expected_segments:
            raise AssertionError("dotted insertion lost its marked-foot slot")
        actual_segments = sorted(
            crossing["under_segment"]
            if crossing["under_owner"] == insertion["dotted_component"]
            else crossing["over_segment"]
            for crossing in pair
        )
        if actual_segments != expected_segments:
            raise AssertionError("PD dotted crossing order differs from foot slots")

    names = data["component_order"]
    matrix = [[0 for _ in names] for _ in names]
    for first_index, first in enumerate(names):
        for second_index in range(first_index + 1, len(names)):
            second = names[second_index]
            signed_sum = sum(
                crossing["sign"]
                for crossing in crossings
                if {crossing["over_owner"], crossing["under_owner"]}
                == {first, second}
            )
            if signed_sum % 2:
                raise AssertionError("standard PD has an odd mixed crossing sum")
            matrix[first_index][second_index] = signed_sum // 2
            matrix[second_index][first_index] = signed_sum // 2
    if matrix != data["pairwise_linking_matrix"]:
        raise AssertionError("standard PD linking matrix changed")
    if data["framing_status"] != "PASS_RAILROAD_TARGET_PRODUCT_PUSH_OFF_LINKING" or data[
        "source_isotopy_status"
    ] != "OPEN_HYBRID_TO_RAILROAD_CELL_MAP_REQUIRED":
        raise AssertionError("standard PD candidate overstates its scope")
    if data["integer_surgery_framings"] != {
        "m_2": 0,
        "m_3": 0,
        "r_xy": 0,
        "r_yz": 0,
        "r_zx": 0,
    }:
        raise AssertionError("standard PD target framings changed")
    return {
        "verdict": "PASS_SOURCE_BOUND_STANDARD_PD_COMBINATORICS_ONLY",
        "components": 7,
        "crossings": 4748,
        "pd_rows": 4748,
        "arc_labels": len(arc_incidence),
        "dotted_hopf_clasps": 1785,
        "pairwise_linking_matrix": matrix,
        "framing_status": "PASS_TARGET_ONLY",
        "hybrid_to_railroad_isotopy": "OPEN",
        "spherogram_status": "OPEN_RESOURCE_LIMIT_AT_4748_CROSSINGS",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
