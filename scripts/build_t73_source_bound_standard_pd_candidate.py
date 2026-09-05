#!/usr/bin/env python3
"""Insert dotted-handle clasps into the exact railroad core diagram."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from export_t73_full_handle_diagram import pairwise_linking_matrix, pd_and_cycles

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "geometry/t73_actual_railroad_core_coordinates.json"
RAILROAD = ROOT / "geometry/t73_final_railroad_word_binding.json"
FOOT_STATE = ROOT / "geometry/t73_final_yz_foot_state.json"
FRAMINGS = ROOT / "geometry/t73_railroad_product_framings.json"
SLOT_MAP = ROOT / "geometry/t73_foot_to_dotted_slot_map.json"
OUTPUT = ROOT / "geometry/t73_source_bound_standard_pd_candidate.json"

COMPONENT_ORDER = ["m_2", "m_3", "r_xy", "r_yz", "r_zx", "dotted_y", "dotted_z"]


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def abstract_connector_segment(coordinate_segment, word_length):
    if coordinate_segment < word_length - 1:
        return 2 * coordinate_segment + 1
    return 2 * word_length + coordinate_segment - (word_length - 1)


def build() -> dict:
    core = json.loads(CORE.read_text(encoding="utf-8"))
    railroad = json.loads(RAILROAD.read_text(encoding="utf-8"))
    foot_state = json.loads(FOOT_STATE.read_text(encoding="utf-8"))
    framings = json.loads(FRAMINGS.read_text(encoding="utf-8"))
    slot_map = json.loads(SLOT_MAP.read_text(encoding="utf-8"))
    slot_by_passage = {
        entry["passage_id"]: entry
        for handle in slot_map["handles"]
        for entry in handle["entries"]
    }
    words = {
        record["name"]: record["reduced_word"] for record in core["components"]
    }
    crossings = []
    for crossing in core["crossings"]:
        value = dict(crossing)
        value["over_segment"] = abstract_connector_segment(
            crossing["over_segment"], len(words[crossing["over_owner"]])
        )
        value["under_segment"] = abstract_connector_segment(
            crossing["under_segment"], len(words[crossing["under_owner"]])
        )
        value["kind"] = "exact_railroad_core_crossing"
        crossings.append(value)
    dotted_insertions = []
    for component in core["components"]:
        name = component["name"]
        for letter_index, (letter, passage_id) in enumerate(
            zip(component["reduced_word"], component["survivor_passage_ids"])
        ):
            handle = "y" if abs(letter) == 2 else "z"
            dotted = f"dotted_{handle}"
            sign = 1 if letter > 0 else -1
            dotted_start = slot_by_passage[passage_id]["dotted_segment_pair"][0]
            insertion_index = len(dotted_insertions)
            first = {
                "projection_point": [str(-2 if handle == "y" else -3), str(Fraction(2 * insertion_index + 1, 100000))],
                "over_owner": name,
                "under_owner": dotted,
                "over_segment": 2 * letter_index,
                "under_segment": dotted_start,
                "over_parameter": "1/3",
                "under_parameter": "1/2",
                "over_height": "1",
                "under_height": "0",
                "sign": sign,
                "kind": "local_dotted_hopf_clasp_first",
                "source_passage_id": passage_id,
            }
            second = {
                "projection_point": [str(-2 if handle == "y" else -3), str(Fraction(2 * insertion_index + 2, 100000))],
                "over_owner": dotted,
                "under_owner": name,
                "over_segment": dotted_start + 1,
                "under_segment": 2 * letter_index,
                "over_parameter": "1/2",
                "under_parameter": "2/3",
                "over_height": "1",
                "under_height": "0",
                "sign": sign,
                "kind": "local_dotted_hopf_clasp_second",
                "source_passage_id": passage_id,
            }
            crossings.extend([first, second])
            dotted_insertions.append({
                "component": name,
                "letter_index": letter_index,
                "letter": letter,
                "source_passage_id": passage_id,
                "dotted_component": dotted,
                "dotted_segment_pair": slot_by_passage[passage_id][
                    "dotted_segment_pair"
                ],
            })
    crossings.append({
        "projection_point": ["4", "2"],
        "over_owner": "r_zx",
        "under_owner": "r_zx",
        "over_segment": 0,
        "under_segment": 1,
        "over_parameter": "1/3",
        "under_parameter": "2/3",
        "over_height": "1",
        "under_height": "0",
        "sign": 1,
        "kind": "split_unknot_reidemeister_I",
    })
    for index, crossing in enumerate(crossings):
        crossing["id"] = f"X{index}"
    pd, cycles, crossingless = pd_and_cycles(COMPONENT_ORDER, crossings)
    if crossingless:
        raise AssertionError(f"PD insertion lost components: {crossingless}")
    pairwise = pairwise_linking_matrix(COMPONENT_ORDER, crossings)
    if len(crossings) != 4727:
        raise AssertionError("source-bound standard PD crossing count changed")
    exponent_sums = {
        name: {
            "y": sum(1 if value > 0 else -1 for value in word if abs(value) == 2),
            "z": sum(1 if value > 0 else -1 for value in word if abs(value) == 3),
        }
        for name, word in words.items()
    }
    for name in words:
        row = COMPONENT_ORDER.index(name)
        if pairwise[row][COMPONENT_ORDER.index("dotted_y")] != exponent_sums[name]["y"] or pairwise[row][COMPONENT_ORDER.index("dotted_z")] != exponent_sums[name]["z"]:
            raise AssertionError("PD dotted linking differs from actual word exponent sum")
    result = {
        "schema": "t73_source_bound_standard_pd_candidate/v1",
        "railroad_core_coordinates_sha256": core["sha256"],
        "actual_railroad_word_binding_sha256": railroad["sha256"],
        "final_yz_foot_state_sha256": foot_state["sha256"],
        "railroad_product_framings_sha256": framings["sha256"],
        "foot_to_dotted_slot_map_sha256": slot_map["sha256"],
        "component_order": COMPONENT_ORDER,
        "crossing_count": len(crossings),
        "crossings": crossings,
        "standard_pd_code": pd,
        "component_halfedge_cycles": cycles,
        "pairwise_linking_matrix": pairwise,
        "dotted_insertion_count": len(dotted_insertions),
        "dotted_insertions": dotted_insertions,
        "word_exponent_sums": exponent_sums,
        "blackboard_writhe": {
            name: sum(
                crossing["sign"]
                for crossing in crossings
                if crossing["over_owner"] == crossing["under_owner"] == name
            )
            for name in COMPONENT_ORDER
        },
        "integer_surgery_framings": framings["integer_surgery_framings"],
        "framing_linking_receipts": framings["framing_linking_receipts"],
        "framing_status": "PASS_RAILROAD_TARGET_PRODUCT_PUSH_OFF_LINKING",
        "source_isotopy_status": "OPEN_HYBRID_TO_RAILROAD_CELL_MAP_REQUIRED",
        "completion_status": "SOURCE_BOUND_STANDARD_PD_CANDIDATE_CONSTRUCTED",
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
        raise AssertionError("source-bound standard PD candidate is stale")
    print(f"T73_STANDARD_PD_CANDIDATE={result['completion_status']} crossings={result['crossing_count']}")


if __name__ == "__main__":
    main()
