#!/usr/bin/env python3
"""Build a generic rational railroad coordinate model for the five reduced words."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from export_t73_full_handle_diagram import (
    curve_crossings,
    pairwise_linking_matrix,
)

ROOT = Path(__file__).resolve().parents[1]
RAILROAD = ROOT / "geometry/t73_final_railroad_word_binding.json"
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
OUTPUT = ROOT / "geometry/t73_actual_railroad_core_coordinates.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def encode(value):
    return [str(coordinate) for coordinate in value]


def reduce_with_survivors(word):
    stack = []
    cancellations = []
    for index, value in enumerate(word):
        if stack and stack[-1][1] == -value:
            previous = stack.pop()
            cancellations.append([previous[0], index])
        else:
            stack.append((index, value))
    return [value for _, value in stack], [index for index, _ in stack], cancellations


def railroad_polyline(word, component_index):
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
    vertices = []
    for index, letter in enumerate(word):
        time = Fraction(index, length)
        rail = Fraction(0 if abs(letter) == 2 else 1)
        x_coordinate = rail + Fraction(component_index, 1000)
        height = (
            time
            + Fraction(component_index, 11)
            + Fraction(index * index, 1000003 * length * length)
        )
        vertices.append((x_coordinate, time, height))
    closure_x = Fraction(2) + Fraction(component_index, 10)
    upper_y = Fraction(11, 10) + Fraction(component_index, 100)
    lower_y = Fraction(-1, 10) - Fraction(component_index, 100)
    vertices.extend([
        (closure_x, upper_y, Fraction(2) + Fraction(component_index, 11)),
        (closure_x, lower_y, Fraction(-1) + Fraction(component_index, 11)),
        vertices[0],
    ])
    return vertices


def build() -> dict:
    railroad = json.loads(RAILROAD.read_text(encoding="utf-8"))
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    cycles_by_name = {item["component"]: item for item in cycles["components"]}
    order = railroad["actual_component_order"]
    components = []
    curves = []
    for component_index, name in enumerate(order):
        raw_word = railroad["components"][name]["raw_word"]
        reduced = raw_word
        survivor_indices = list(range(len(raw_word)))
        cancellations = []
        passage_ids = cycles_by_name[name]["passage_ids"]
        survivor_passage_ids = [passage_ids[index] for index in survivor_indices]
        vertices = railroad_polyline(raw_word, component_index)
        components.append({
            "name": name,
            "raw_passage_count": len(raw_word),
            "target_word": raw_word,
            "survivor_original_indices": survivor_indices,
            "survivor_passage_ids": survivor_passage_ids,
            "cancelled_original_index_pairs": cancellations,
            "vertices": [encode(value) for value in vertices],
            "closed": True,
        })
        curves.append({"name": name, "points": vertices})
    basis = [
        (Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1), Fraction(0)),
    ]
    height = (Fraction(0), Fraction(0), Fraction(1))
    crossings = curve_crossings(
        curves,
        basis,
        height,
        include_self=True,
        require_unique_projection_points=True,
    )
    pairwise = pairwise_linking_matrix(order, crossings)
    result = {
        "schema": "t73_actual_railroad_core_coordinates/v1",
        "actual_railroad_word_binding_sha256": railroad["sha256"],
        "final_component_passage_cycles_sha256": cycles["sha256"],
        "component_order": order,
        "components": components,
        "ambient": {
            "chart": "oriented_affine_Q3",
            "projection_basis": [["1", "0", "0"], ["0", "1", "0"]],
            "height_direction": ["0", "0", "1"],
        },
        "crossings": crossings,
        "crossing_count": len(crossings),
        "pairwise_linking_matrix": pairwise,
        "coordinate_rule": (
            "actual reduced letters on y/z rails with component x-offset, "
            "quadratic rational height perturbation, and two-vertex outer closure"
        ),
        "completion_status": "SOURCE_BOUND_RAW_PASSAGE_RAILROAD_CORE_COORDINATES_CANDIDATE",
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
        raise AssertionError("actual railroad core coordinates are stale")
    print(f"T73_RAILROAD_CORE={result['completion_status']} crossings={result['crossing_count']}")


if __name__ == "__main__":
    main()
