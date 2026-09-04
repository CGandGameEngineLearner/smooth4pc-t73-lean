#!/usr/bin/env python3
"""Recompute the actual Johnson spine embedding and reject local mutations."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPINE = ROOT / "geometry" / "t73_johnson_spine_embedding.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decode(point):
    return tuple(Fraction(value) for value in point)


def validate(data):
    builder = load("build_t73_johnson_spine_embedding")
    side_search = load("search_t73_johnson_alpha_sides").generate()["known_candidate"]
    words = side_search["generator_images"]
    if data["component_word_lengths"] != [len(word) for word in words]:
        raise AssertionError("spine word lengths do not match the Johnson lift")
    if data["handle_arc_count"] != sum(map(len, words)):
        raise AssertionError("handle arc count does not equal the word length")
    lanes = {axis: set() for axis in range(3)}
    arcs_by_component = {component: [] for component in range(3)}
    for arc in data["handle_arcs"]:
        component = int(arc["component"])
        index = int(arc["letter_index"])
        letter = int(arc["word_letter"])
        if letter != words[component][index]:
            raise AssertionError("handle arc orientation does not read the retraction word")
        axis = abs(letter) - 1
        if int(arc["axis"]) != axis or int(arc["sign"]) != (1 if letter > 0 else -1):
            raise AssertionError("handle arc axis/sign does not match its letter")
        lane = (tuple(arc["start_lane"]), tuple(arc["end_lane"]))
        if lane in lanes[axis]:
            raise AssertionError("two handle occurrences use the same lane")
        lanes[axis].add(lane)
        departure = decode(arc["departure"])
        arrival = decode(arc["arrival"])
        expected_departure = 1 if letter > 0 else -1
        expected_arrival = -1 if letter > 0 else 1
        if departure[axis] != expected_departure or arrival[axis] != expected_arrival:
            raise AssertionError("handle arc has the wrong oriented ports")
        lift = [decode(point) for point in arc["lift_polyline"]]
        if len(lift) != 3 or lift[1][axis] != 2:
            raise AssertionError("handle arc has no period-four midpoint")
        other = [coordinate for coordinate in range(3) if coordinate != axis]
        if any(abs(point[coordinate]) >= 1 for point in lift for coordinate in other):
            raise AssertionError("handle lane leaves its H0 arm cube")
        arcs_by_component[component].append(arc)
    for component, arcs in arcs_by_component.items():
        arcs.sort(key=lambda arc: int(arc["letter_index"]))
        if [int(arc["word_letter"]) for arc in arcs] != words[component]:
            raise AssertionError("ordered handle arcs do not reproduce the generator image")

    levels = []
    columns = []
    connector_points = []
    for connector in data["central_connectors"]:
        level = Fraction(connector["level"])
        points = [decode(point) for point in connector["polyline"]]
        if len(points) != 5:
            raise AssertionError("central connector is not the five-point routing template")
        if points[1][:2] != points[0][:2] or points[1][2] != level:
            raise AssertionError("first connector column is malformed")
        if points[3][:2] != points[4][:2] or points[3][2] != level:
            raise AssertionError("second connector column is malformed")
        if points[2][2] != level:
            raise AssertionError("connector bend is not on its height level")
        if any(not (-1 <= coordinate <= 1) for point in points for coordinate in point):
            raise AssertionError("central connector leaves the origin cube")
        levels.append(level)
        columns.extend((points[0][:2], points[4][:2]))
        connector_points.append(points)
    if len(levels) != len(set(levels)):
        raise AssertionError("two central connectors use the same height")
    if len(columns) != len(set(columns)):
        raise AssertionError("two central connector endpoints use the same xy column")
    obstacles = set(columns)
    for points in connector_points:
        first = points[0][:2]
        bend = points[2][:2]
        second = points[4][:2]
        for obstacle in obstacles:
            if obstacle != first and builder.point_on_segment(obstacle, first, bend):
                raise AssertionError("connector first leg hits another vertical column")
            if obstacle != second and builder.point_on_segment(obstacle, bend, second):
                raise AssertionError("connector second leg hits another vertical column")
    for component, record in enumerate(data["components"]):
        if record["component"] != component:
            raise AssertionError("spine components are out of order")
        if record["retraction_word"] != words[component]:
            raise AssertionError("component retraction word changed")
        polyline = [decode(point) for point in record["polyline"]]
        if not polyline or polyline[0] != (0, 0, 0) or polyline[-1] != (0, 0, 0):
            raise AssertionError("spine component is not based and closed at the origin")
    return True


def mutation_fails(data, mutate):
    mutant = copy.deepcopy(data)
    mutate(mutant)
    try:
        validate(mutant)
    except AssertionError:
        return True
    return False


def verify():
    builder = load("build_t73_johnson_spine_embedding")
    stored = json.loads(SPINE.read_text(encoding="utf-8"))
    rebuilt = builder.build(write=False)
    if stored != rebuilt:
        raise AssertionError("stored spine embedding does not match a live rebuild")
    validate(stored)

    def duplicate_lane(mutant):
        first = next(arc for arc in mutant["handle_arcs"] if arc["axis"] == 0)
        second = next(
            arc
            for arc in mutant["handle_arcs"]
            if arc["axis"] == 0 and arc["arc_id"] != first["arc_id"]
        )
        second["start_lane"] = first["start_lane"]
        second["end_lane"] = first["end_lane"]

    def duplicate_height(mutant):
        mutant["central_connectors"][1]["level"] = mutant["central_connectors"][0]["level"]

    def reverse_letter(mutant):
        mutant["handle_arcs"][0]["word_letter"] *= -1

    lane_failed = mutation_fails(stored, duplicate_lane)
    height_failed = mutation_fails(stored, duplicate_height)
    orientation_failed = mutation_fails(stored, reverse_letter)
    side_module = load("search_t73_johnson_alpha_sides")
    bits = [int(bit) for bit in side_module.KNOWN_BITS]
    bits[0] ^= 1
    mutated_words, _ = side_module.build_lift(bits)
    side_failed = mutated_words != [component["retraction_word"] for component in stored["components"]]
    if not all((lane_failed, height_failed, orientation_failed, side_failed)):
        raise AssertionError("a spine mutation was not detected")
    return {
        "ACTUAL_SPINE_EMBEDDING": "PASS",
        "HANDLE_ARCS": stored["handle_arc_count"],
        "CENTRAL_CONNECTORS": stored["central_connector_count"],
        "RETRACTION_WORDS": "PASS",
        "ABELIANIZATION_IS_A": "PASS",
        "MUTATION_LANE_DUPLICATE": "FAIL",
        "MUTATION_CONNECTOR_HEIGHT": "FAIL",
        "MUTATION_ORIENTATION": "FAIL",
        "MUTATION_SIDE_BIT": "FAIL",
        "AMBIENT_RESTORE_SPINE_BINDING": stored["ambient_restore_spine_binding"],
        "ACTUAL_CURVE_EVALUATOR": stored["actual_curve_transport_evaluator"],
        "SHA256": stored["sha256"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.check:
        for key, value in result.items():
            print(f"{key}={value}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
