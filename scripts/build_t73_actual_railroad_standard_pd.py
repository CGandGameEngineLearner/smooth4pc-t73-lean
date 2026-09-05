#!/usr/bin/env python3
"""Build a standard seven-component PD from the actual-word railroad ledger."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAILROAD = ROOT / "geometry/t73_final_railroad_word_binding.json"
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
FOOT_STATE = ROOT / "geometry/t73_final_yz_foot_state.json"
OUTPUT = ROOT / "audit/t73_actual_railroad_standard_pd_gap.json"

COMPONENT_ORDER = ["m_2", "m_3", "r_xy", "r_yz", "r_zx", "dotted_y", "dotted_z"]


def load_railroad_tools():
    path = ROOT / "scripts/certify_t73_e13_close.py"
    spec = importlib.util.spec_from_file_location("railroad_pd_tools", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def enc(value):
    return str(value)


def railroad_connectors(words, order, denominator, tools):
    result = {}
    for component_index, component in enumerate(order):
        connectors = tools.word_connectors(words[component], component_index)
        correction = Fraction(component_index, denominator) - Fraction(component_index, 10)
        for connector in connectors:
            connector["ha"] += correction
            connector["hb"] += correction
        result[component] = connectors
    return result


def enhanced_mixed_crossings(left_name, left_connectors, right_name, right_connectors, tools):
    crossings = []
    for left_index, left in enumerate(left_connectors):
        for right_index, right in enumerate(right_connectors):
            parameter = tools.crossing_parameter(left, right)
            if parameter is None:
                continue
            left_height = left["ha"] + parameter * (left["hb"] - left["ha"])
            right_height = right["ha"] + parameter * (right["hb"] - right["ha"])
            if left_height == right_height:
                raise AssertionError("actual railroad height perturbation is not generic")
            left_dy = left["t"] - left["s"] if left["dx"] == 1 else left["s"] - left["t"]
            right_dy = right["t"] - right["s"] if right["dx"] == 1 else right["s"] - right["t"]
            determinant = left["dx"] * right_dy - left_dy * right["dx"]
            raw_sign = 1 if determinant > 0 else -1
            if right_height > left_height:
                over_name, under_name = right_name, left_name
                over_connector, under_connector = right, left
                sign = raw_sign
            else:
                over_name, under_name = left_name, right_name
                over_connector, under_connector = left, right
                sign = -raw_sign
            if left["dx"] == 1:
                projection_x = parameter
                projection_y = left["s"] + parameter * (left["t"] - left["s"])
            else:
                projection_x = 1 - parameter
                projection_y = left["t"] + parameter * (left["s"] - left["t"])
            crossings.append({
                "projection_point": [enc(projection_x), enc(projection_y)],
                "over_owner": over_name,
                "under_owner": under_name,
                "over_segment": 2 * over_connector["start_index"] + 1,
                "under_segment": 2 * under_connector["start_index"] + 1,
                "over_parameter": enc(parameter),
                "under_parameter": enc(parameter),
                "over_height": enc(max(left_height, right_height)),
                "under_height": enc(min(left_height, right_height)),
                "sign": sign,
                "kind": "actual_word_railroad_mixed",
            })
    return crossings


def build() -> dict:
    railroad = json.loads(RAILROAD.read_text(encoding="utf-8"))
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    foot_state = json.loads(FOOT_STATE.read_text(encoding="utf-8"))
    tools = load_railroad_tools()
    words = {
        component: railroad["components"][component]["reduced_word"]
        for component in railroad["actual_component_order"]
    }
    order = railroad["actual_component_order"]
    connectors = railroad_connectors(
        words, order, railroad["actual_component_height_denominator"], tools
    )
    crossings = []
    for left_index, left in enumerate(order):
        for right in order[left_index + 1 :]:
            crossings.extend(
                enhanced_mixed_crossings(
                    left, connectors[left], right, connectors[right], tools
                )
            )
    if len(crossings) != 1878:
        raise AssertionError("actual railroad mixed crossing count changed")

    dotted_event_counts = {"dotted_y": 0, "dotted_z": 0}
    letter_handles = {2: "y", 3: "z", -2: "y", -3: "z"}
    for component in order:
        for letter_index, letter in enumerate(words[component]):
            handle = letter_handles[letter]
            dotted = f"dotted_{handle}"
            sign = 1 if letter > 0 else -1
            first_dotted_segment = dotted_event_counts[dotted]
            dotted_event_counts[dotted] += 2
            base_x = Fraction(-2 if handle == "y" else -3)
            point_index = dotted_event_counts[dotted]
            crossings.extend([
                {
                    "projection_point": [enc(base_x), enc(Fraction(point_index * 2 - 1, 10000))],
                    "over_owner": component,
                    "under_owner": dotted,
                    "over_segment": 2 * letter_index,
                    "under_segment": first_dotted_segment,
                    "over_parameter": "1/3",
                    "under_parameter": "1/2",
                    "over_height": "1",
                    "under_height": "0",
                    "sign": sign,
                    "kind": "dotted_handle_pair_first",
                },
                {
                    "projection_point": [enc(base_x), enc(Fraction(point_index * 2, 10000))],
                    "over_owner": dotted,
                    "under_owner": component,
                    "over_segment": first_dotted_segment + 1,
                    "under_segment": 2 * letter_index,
                    "over_parameter": "1/2",
                    "under_parameter": "2/3",
                    "over_height": "1",
                    "under_height": "0",
                    "sign": sign,
                    "kind": "dotted_handle_pair_second",
                },
            ])
    crossings.append({
        "projection_point": ["2", "0"],
        "over_owner": "r_zx",
        "under_owner": "r_zx",
        "over_segment": 0,
        "under_segment": 1,
        "over_parameter": "1/3",
        "under_parameter": "2/3",
        "over_height": "1",
        "under_height": "0",
        "sign": 1,
        "kind": "explicit_split_unknot_reidemeister_I",
    })
    for index, crossing in enumerate(crossings):
        crossing["id"] = f"X{index}"
    expected_exponent_sums = {
        component: {
            handle: sum(
                1 if letter > 0 else -1
                for letter in words[component]
                if abs(letter) == value
            )
            for handle, value in (("y", 2), ("z", 3))
        }
        for component in order
    }
    mixed_sums = Counter()
    for crossing in crossings:
        if crossing["over_owner"] == crossing["under_owner"]:
            continue
        pair = tuple(sorted((crossing["over_owner"], crossing["under_owner"])))
        mixed_sums[pair] += crossing["sign"]
    odd_pairs = {
        "/".join(pair): value
        for pair, value in sorted(mixed_sums.items())
        if value % 2
    }
    if odd_pairs != {"m_2/m_3": -3, "m_3/r_xy": 1}:
        raise AssertionError(f"unexpected railroad closure parity gap: {odd_pairs}")
    result = {
        "schema": "t73_actual_railroad_standard_pd_gap/v1",
        "actual_railroad_word_binding_sha256": railroad["sha256"],
        "final_component_passage_cycles_sha256": cycles["sha256"],
        "final_yz_foot_state_sha256": foot_state["sha256"],
        "component_order": COMPONENT_ORDER,
        "actual_railroad_mixed_crossing_count": 1878,
        "candidate_dotted_crossing_count": 2 * sum(len(word) for word in words.values()),
        "candidate_split_unknot_self_crossings": 1,
        "candidate_total_crossing_occurrences": len(crossings),
        "mixed_crossing_sign_sums": {
            "/".join(pair): value for pair, value in sorted(mixed_sums.items())
        },
        "odd_mixed_pairs_blocking_planar_pd": odd_pairs,
        "word_exponent_sums": expected_exponent_sums,
        "blackboard_writhe": {
            component: sum(
                crossing["sign"]
                for crossing in crossings
                if crossing["over_owner"] == crossing["under_owner"] == component
            )
            for component in COMPONENT_ORDER
        },
        "standard_pd_code": None,
        "framing_status": "OPEN_PUSH_OFFS_NOT_YET_ATTACHED",
        "coordinate_realization_status": "OPEN_ACTUAL_CUT_HANDLEBODY_CONNECTOR_TRANSPORT_REQUIRED",
        "next_required_witness": (
            "transport the actual Johnson central connectors and hybrid replacement "
            "connectors into the y/z foot-ball complement; their closure crossings "
            "must make every mixed sign sum even before standard PD rows are emitted"
        ),
        "completion_status": "OPEN_RAILROAD_CLOSURE_CROSSINGS_MISSING",
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
        raise AssertionError("actual railroad standard-PD gap report is stale")
    print(f"T73_RAILROAD_STANDARD_PD={result['completion_status']}")


if __name__ == "__main__":
    main()
