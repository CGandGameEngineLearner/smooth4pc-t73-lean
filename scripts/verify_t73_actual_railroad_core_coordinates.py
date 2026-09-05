#!/usr/bin/env python3
"""Independently verify the source-bound five-component railroad coordinates."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from export_t73_full_handle_diagram import curve_crossings, pairwise_linking_matrix

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_actual_railroad_core_coordinates.json"
RAILROAD = ROOT / "geometry/t73_final_railroad_word_binding.json"
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def reduce_survivors(word):
    stack = []
    cancelled = []
    for index, value in enumerate(word):
        if stack and stack[-1][1] == -value:
            previous = stack.pop()
            cancelled.append([previous[0], index])
        else:
            stack.append((index, value))
    return [value for _, value in stack], [index for index, _ in stack], cancelled


def expected_polyline(word, component_index):
    if not word:
        height = Fraction(component_index, 11)
        return [
            (Fraction(4), Fraction(19, 10), height),
            (Fraction(41, 10), Fraction(2), height + Fraction(1, 100)),
            (Fraction(4), Fraction(21, 10), height),
            (Fraction(39, 10), Fraction(2), height - Fraction(1, 100)),
            (Fraction(4), Fraction(19, 10), height),
        ]
    length = len(word)
    points = []
    for index, letter in enumerate(word):
        time = Fraction(index, length)
        points.append((
            Fraction(0 if abs(letter) == 2 else 1) + Fraction(component_index, 1000),
            time,
            time
            + Fraction(component_index, 11)
            + Fraction(index * index, 1000003 * length * length),
        ))
    closure_x = Fraction(2) + Fraction(component_index, 10)
    upper_y = Fraction(11, 10) + Fraction(component_index, 100)
    lower_y = Fraction(-1, 10) - Fraction(component_index, 100)
    points.extend([
        (closure_x, upper_y, Fraction(2) + Fraction(component_index, 11)),
        (closure_x, lower_y, Fraction(-1) + Fraction(component_index, 11)),
        points[0],
    ])
    return points


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    railroad = json.loads(RAILROAD.read_text(encoding="utf-8"))
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    if data["completion_status"] != "SOURCE_BOUND_RAILROAD_CORE_COORDINATES_CANDIDATE":
        raise AssertionError("railroad coordinate scope changed")
    if data["actual_railroad_word_binding_sha256"] != railroad["sha256"] or data["final_component_passage_cycles_sha256"] != cycles["sha256"]:
        raise AssertionError("railroad coordinates have stale sources")
    cycles_by_name = {item["component"]: item for item in cycles["components"]}
    curves = []
    cancellation_pairs = 0
    for component_index, record in enumerate(data["components"]):
        name = record["name"]
        raw = railroad["components"][name]["raw_word"]
        reduced, survivors, cancelled = reduce_survivors(raw)
        if record["reduced_word"] != reduced or record["survivor_original_indices"] != survivors or record["cancelled_original_index_pairs"] != cancelled:
            raise AssertionError("railroad survivor/cancellation map changed")
        expected_ids = [cycles_by_name[name]["passage_ids"][index] for index in survivors]
        if record["survivor_passage_ids"] != expected_ids:
            raise AssertionError("railroad event-to-passage binding changed")
        points = [point(value) for value in record["vertices"]]
        if points != expected_polyline(reduced, component_index):
            raise AssertionError("railroad rational coordinates changed")
        curves.append({"name": name, "points": points})
        cancellation_pairs += len(cancelled)
    basis = [(Fraction(1), Fraction(0), Fraction(0)), (Fraction(0), Fraction(1), Fraction(0))]
    height = (Fraction(0), Fraction(0), Fraction(1))
    crossings = curve_crossings(
        curves, basis, height, include_self=True, require_unique_projection_points=True
    )
    if crossings != data["crossings"] or len(crossings) != 1168:
        raise AssertionError("railroad exact coordinate crossings changed")
    pairwise = pairwise_linking_matrix(data["component_order"], crossings)
    if pairwise != [[0] * 5 for _ in range(5)] or data["pairwise_linking_matrix"] != pairwise:
        raise AssertionError("railroad pairwise linking matrix changed")
    return {
        "verdict": "PASS_SOURCE_BOUND_RAILROAD_CORE_COORDINATES_CANDIDATE",
        "components": 5,
        "crossings": len(crossings),
        "pairwise_linking_matrix": pairwise,
        "explicit_free_reduction_pairs": cancellation_pairs,
        "surviving_passage_events": sum(
            len(record["survivor_passage_ids"]) for record in data["components"]
        ),
        "actual_isotopy_to_hybrid_state": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
