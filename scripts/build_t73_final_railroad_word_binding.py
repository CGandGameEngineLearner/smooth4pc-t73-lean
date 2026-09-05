#!/usr/bin/env python3
"""Bind final geometric passage cycles to the compact railroad words."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
RAILROAD = ROOT / "audit/t73_reduced_link_pd.json"
CORE_CANDIDATE = ROOT / "geometry/t73_actual_kirby_core_embedding.json"
OUTPUT = ROOT / "geometry/t73_final_railroad_word_binding.json"


def load_compact():
    path = ROOT / "scripts/generate_t73_compact_kirby_ledger.py"
    spec = importlib.util.spec_from_file_location("compact_kirby", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_railroad_tools():
    path = ROOT / "scripts/certify_t73_e13_close.py"
    spec = importlib.util.spec_from_file_location("railroad_tools", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def reduce_with_ledger(word):
    stack = []
    cancellations = []
    for index, letter in enumerate(word):
        if stack and stack[-1][1] == -letter:
            previous_index, previous_letter = stack.pop()
            cancellations.append({
                "left_original_index": previous_index,
                "right_original_index": index,
                "letters": [previous_letter, letter],
            })
        else:
            stack.append((index, letter))
    return [letter for _, letter in stack], cancellations


def canonical_cyclic_word(word):
    if not word:
        return [], 0
    reduced = list(word)
    while len(reduced) > 1 and reduced[0] == -reduced[-1]:
        reduced = reduced[1:-1]
    rotations = [reduced[index:] + reduced[:index] for index in range(len(reduced))]
    canonical = min(rotations)
    return canonical, rotations.index(canonical)


def build() -> dict:
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    railroad = json.loads(RAILROAD.read_text(encoding="utf-8"))
    core = json.loads(CORE_CANDIDATE.read_text(encoding="utf-8"))
    compact = load_compact()
    railroad_tools = load_railroad_tools()
    letter_value = {"y": 2, "z": 3}
    value_letter = {2: "y", 3: "z", -2: "Y", -3: "Z"}
    raw_words = {
        component["component"]: [
            passage["orientation"] * letter_value[passage["handle"]]
            for passage in component["passages"]
        ]
        for component in cycles["components"]
    }
    expected_letters = {
        "m_2": compact.after_x_cancellation(1),
        "m_3": compact.after_x_cancellation(2),
        "r_xy": ["z", "y", "Z", "Y"],
        "r_yz": compact.commutator("y", "z"),
        "r_zx": [],
    }
    records = {}
    actual_words = {}
    for component, raw_word in raw_words.items():
        reduced, cancellations = reduce_with_ledger(raw_word)
        canonical_word, cycle_rotation = canonical_cyclic_word(reduced)
        canonical_letters = [value_letter[value] for value in canonical_word]
        expected_values = [
            {"y": 2, "z": 3, "Y": -2, "Z": -3}[value]
            for value in expected_letters[component]
        ]
        expected_canonical, _ = canonical_cyclic_word(expected_values)
        matches_old = canonical_word == expected_canonical
        actual_words[component] = reduced
        records[component] = {
            "raw_word": raw_word,
            "raw_length": len(raw_word),
            "free_reduction_cancellations": cancellations,
            "reduced_word": reduced,
            "reduced_length": len(reduced),
            "canonical_cycle_rotation": cycle_rotation,
            "canonical_word": canonical_word,
            "canonical_letters": canonical_letters,
            "actual_word_sha256": canonical_sha(canonical_word),
            "old_compact_word_matches_up_to_conjugacy": matches_old,
            "old_railroad_word_sha256": railroad["component_word_hashes"][component],
        }
    component_order = ["m_2", "m_3", "r_xy", "r_yz", "r_zx"]
    connectors = None
    crossings = None
    height_denominator = None
    for denominator in (10, 11, 13, 17, 19, 23, 29, 31, 1009):
        candidate_connectors = {}
        for index, component in enumerate(component_order):
            values = railroad_tools.word_connectors(actual_words[component], index)
            correction = Fraction(index, denominator) - Fraction(index, 10)
            for value in values:
                value["ha"] += correction
                value["hb"] += correction
            candidate_connectors[component] = values
        candidate_crossings = []
        try:
            for left_index, left in enumerate(component_order):
                for right in component_order[left_index + 1 :]:
                    candidate_crossings.extend(
                        railroad_tools.mixed_crossings(
                            left,
                            candidate_connectors[left],
                            right,
                            candidate_connectors[right],
                        )
                    )
        except AssertionError:
            continue
        connectors = candidate_connectors
        crossings = candidate_crossings
        height_denominator = denominator
        break
    if connectors is None or crossings is None or height_denominator is None:
        raise AssertionError("no generic rational railroad component-height perturbation found")
    result = {
        "schema": "t73_final_railroad_word_binding/v1",
        "final_component_passage_cycles_sha256": cycles["sha256"],
        "reduced_railroad_pd_sha256": canonical_sha(railroad),
        "source_bound_core_candidate_sha256": core["sha256"],
        "components": records,
        "old_railroad_crossing_count": len(railroad["crossings"]),
        "old_railroad_binding_verdict": "FAIL_M3_NONCOMMUTATIVE_ORDER_MISMATCH",
        "actual_component_order": component_order,
        "actual_connector_counts": {
            component: len(connectors[component]) for component in component_order
        },
        "actual_railroad_crossings": crossings,
        "actual_railroad_crossing_count": len(crossings),
        "actual_component_height_rule": f"letter_time + component_id/{height_denominator}",
        "actual_component_height_denominator": height_denominator,
        "r_zx_split_unknot_source": "geometry/t73_actual_kirby_core_embedding.json#/components/r_zx",
        "binding_scope": (
            "explicit free reductions and regenerated actual-word railroad crossings; "
            "dotted circles, standard PD rows, and framings still require verification"
        ),
        "completion_status": "ACTUAL_PASSAGE_WORD_RAILROAD_REGENERATED_OLD_M3_REJECTED",
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
        raise AssertionError("final railroad word binding is stale")
    print("T73_RAILROAD_WORD_BINDING=ACTUAL_PASSAGE_WORD_RAILROAD_REGENERATED_OLD_M3_REJECTED")


if __name__ == "__main__":
    main()
