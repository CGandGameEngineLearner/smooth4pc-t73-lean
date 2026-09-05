#!/usr/bin/env python3
"""Verify the actual-word railroad ledger and reject the old m3 surrogate."""

from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_final_railroad_word_binding.json"
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
OLD_RAILROAD = ROOT / "audit/t73_reduced_link_pd.json"
CORE = ROOT / "geometry/t73_actual_kirby_core_embedding.json"


def load(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reduce_word(word):
    stack = []
    for value in word:
        if stack and stack[-1] == -value:
            stack.pop()
        else:
            stack.append(value)
    return stack


def canonical_cycle(word):
    if not word:
        return []
    reduced = list(word)
    while len(reduced) > 1 and reduced[0] == -reduced[-1]:
        reduced = reduced[1:-1]
    return min(reduced[index:] + reduced[:index] for index in range(len(reduced)))


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    old = json.loads(OLD_RAILROAD.read_text(encoding="utf-8"))
    core = json.loads(CORE.read_text(encoding="utf-8"))
    compact = load("generate_t73_compact_kirby_ledger")
    railroad = load("certify_t73_e13_close")
    if data["completion_status"] != "ACTUAL_PASSAGE_WORD_RAILROAD_REGENERATED_OLD_M3_REJECTED":
        raise AssertionError("actual railroad binding scope changed")
    if data["final_component_passage_cycles_sha256"] != cycles["sha256"] or data["source_bound_core_candidate_sha256"] != core["sha256"]:
        raise AssertionError("actual railroad binding has stale sources")
    values = {"y": 2, "z": 3}
    letters = {2: "y", 3: "z", -2: "Y", -3: "Z"}
    raw_words = {
        component["component"]: [
            passage["orientation"] * values[passage["handle"]]
            for passage in component["passages"]
        ]
        for component in cycles["components"]
    }
    old_expected = {
        "m_2": compact.after_x_cancellation(1),
        "m_3": compact.after_x_cancellation(2),
        "r_xy": ["z", "y", "Z", "Y"],
        "r_yz": compact.commutator("y", "z"),
        "r_zx": [],
    }
    actual_words = {}
    direct_matches = {}
    inverse_matches = {}
    for component, raw in raw_words.items():
        reduced = reduce_word(raw)
        record = data["components"][component]
        if record["raw_word"] != raw or record["reduced_word"] != reduced:
            raise AssertionError(f"{component}: saved free reduction changed")
        actual_words[component] = reduced
        expected_values = [
            {"y": 2, "z": 3, "Y": -2, "Z": -3}[value]
            for value in old_expected[component]
        ]
        direct = canonical_cycle(reduced) == canonical_cycle(expected_values)
        inverse = canonical_cycle(reduced) == canonical_cycle(
            [-value for value in reversed(expected_values)]
        )
        if record["old_compact_word_matches_up_to_conjugacy"] != direct or record[
            "old_compact_word_matches_after_orientation_reversal"
        ] != inverse or record["old_compact_unoriented_attaching_circle_matches"] != (
            direct or inverse
        ):
            raise AssertionError("old railroad comparison flag changed")
        direct_matches[component] = direct
        inverse_matches[component] = inverse
        if record["canonical_letters"] != [letters[value] for value in canonical_cycle(reduced)]:
            raise AssertionError("canonical actual word changed")
    if direct_matches != {
        "m_2": True,
        "m_3": False,
        "r_xy": False,
        "r_yz": False,
        "r_zx": True,
    }:
        raise AssertionError("old railroad direct-orientation comparison changed")
    if not inverse_matches["r_xy"] or not inverse_matches["r_yz"]:
        raise AssertionError("dual words no longer match after orientation reversal")

    order = data["actual_component_order"]
    denominator = data["actual_component_height_denominator"]
    connectors = {}
    for index, component in enumerate(order):
        values_for_component = railroad.word_connectors(actual_words[component], index)
        correction = Fraction(index, denominator) - Fraction(index, 10)
        for value in values_for_component:
            value["ha"] += correction
            value["hb"] += correction
        connectors[component] = values_for_component
    crossings = []
    for left_index, left in enumerate(order):
        for right in order[left_index + 1 :]:
            crossings.extend(
                railroad.mixed_crossings(
                    left, connectors[left], right, connectors[right]
                )
            )
    if crossings != data["actual_railroad_crossings"]:
        raise AssertionError("actual railroad crossing ledger changed")
    if len(crossings) != 1878 or data["old_railroad_crossing_count"] != 1958:
        raise AssertionError("actual/old railroad crossing counts changed")
    rzx = next(item for item in core["components"] if item["name"] == "r_zx")
    if rzx["vertices"][0] != rzx["vertices"][-1]:
        raise AssertionError("source-bound r_zx split-unknot candidate is not closed")
    return {
        "verdict": "PASS_ACTUAL_1878_RAILROAD_LEDGER_OLD_M3_REJECTED",
        "actual_crossings": len(crossings),
        "old_crossings": len(old["crossings"]),
        "old_word_direct_matches": direct_matches,
        "old_word_inverse_matches": inverse_matches,
        "component_connector_counts": {
            component: len(connectors[component]) for component in order
        },
        "r_zx_reduced_word_length": len(actual_words["r_zx"]),
        "standard_pd_status": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
