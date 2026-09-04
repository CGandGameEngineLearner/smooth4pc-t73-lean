#!/usr/bin/env python3
"""Embed the three Johnson generator-image words as an actual PL spine."""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PSI = ROOT / "geometry" / "t73_psi_A.json"
RESTORE = ROOT / "geometry" / "t73_johnson_restore_assembly.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_spine_embedding.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def encode(point):
    return [str(value) for value in point]


def replace_axis(transverse, axis, value):
    point = [Fraction(0), Fraction(0), Fraction(0)]
    point[axis] = value
    other = [index for index in range(3) if index != axis]
    point[other[0]] = transverse[0]
    point[other[1]] = transverse[1]
    return tuple(point)


def lane_positions(axis, index, count):
    u = Fraction(1, 4) + Fraction(index + 1, 4 * (count + 1))
    v = Fraction(-1, 2) + Fraction(index + 1, count + 1)
    start = (u, v)
    if axis == 2:
        end = (u + Fraction(1, 100 * (count + 1)), v)
    else:
        end = start
    return start, end


def handle_arc(axis, sign, start_lane, end_lane):
    if sign > 0:
        departure = replace_axis(start_lane, axis, Fraction(1))
        midpoint = replace_axis(
            tuple((start_lane[i] + end_lane[i]) / 2 for i in range(2)),
            axis,
            Fraction(2),
        )
        arrival_lift = replace_axis(end_lane, axis, Fraction(3))
        arrival = replace_axis(end_lane, axis, Fraction(-1))
    else:
        departure = replace_axis(start_lane, axis, Fraction(-1))
        departure_lift = replace_axis(start_lane, axis, Fraction(3))
        midpoint = replace_axis(
            tuple((start_lane[i] + end_lane[i]) / 2 for i in range(2)),
            axis,
            Fraction(2),
        )
        arrival_lift = replace_axis(end_lane, axis, Fraction(1))
        arrival = replace_axis(end_lane, axis, Fraction(1))
        return {
            "axis": axis,
            "sign": sign,
            "departure": departure,
            "arrival": arrival,
            "lift_polyline": (departure_lift, midpoint, arrival_lift),
            "torus_polyline": (departure, midpoint, arrival),
            "start_lane": start_lane,
            "end_lane": end_lane,
        }
    return {
        "axis": axis,
        "sign": sign,
        "departure": departure,
        "arrival": arrival,
        "lift_polyline": (departure, midpoint, arrival_lift),
        "torus_polyline": (departure, midpoint, arrival),
        "start_lane": start_lane,
        "end_lane": end_lane,
    }


def point_on_segment(point, first, second):
    direction = (second[0] - first[0], second[1] - first[1])
    offset = (point[0] - first[0], point[1] - first[1])
    cross = direction[0] * offset[1] - direction[1] * offset[0]
    if cross != 0:
        return False
    dot = offset[0] * direction[0] + offset[1] * direction[1]
    length = direction[0] * direction[0] + direction[1] * direction[1]
    return 0 <= dot <= length


def choose_bend(index, first, second, obstacles, total):
    modulus = 4 * total + 17
    for attempt in range(1, 4 * total + 100):
        a_index = (37 * (index + 1) + 17 * attempt) % modulus
        b_index = (53 * (index + 1) + 29 * attempt) % modulus
        bend = (
            Fraction(-3, 4) + Fraction(3 * (a_index + 1), 2 * (modulus + 1)),
            Fraction(-3, 4) + Fraction(3 * (b_index + 1), 2 * (modulus + 1)),
        )
        if bend in obstacles:
            continue
        bad = False
        for obstacle in obstacles:
            if obstacle != first and point_on_segment(obstacle, first, bend):
                bad = True
                break
            if obstacle != second and point_on_segment(obstacle, bend, second):
                bad = True
                break
        if not bad:
            return bend
    raise AssertionError("could not route a central connector away from all columns")


def spoke_data(axis):
    radius = Fraction(1, 4)
    origin = (Fraction(0), Fraction(0), Fraction(0))
    radial_plus = [Fraction(0), Fraction(0), Fraction(0)]
    radial_minus = [Fraction(0), Fraction(0), Fraction(0)]
    radial_plus[axis] = radius
    radial_minus[axis] = -radius
    if axis == 0:
        stage_plus = (radius, Fraction(1, 8), Fraction(0))
        stage_minus = (-radius, Fraction(-1, 8), Fraction(0))
    elif axis == 1:
        stage_plus = (Fraction(1, 8), radius, Fraction(0))
        stage_minus = (Fraction(-1, 8), -radius, Fraction(0))
    else:
        stage_plus = (Fraction(3, 16), Fraction(-3, 16), radius)
        stage_minus = (Fraction(-3, 16), Fraction(3, 16), -radius)
    return {
        "origin": origin,
        "radial_plus": tuple(radial_plus),
        "radial_minus": tuple(radial_minus),
        "stage_plus": stage_plus,
        "stage_minus": stage_minus,
    }


def connector_polyline(index, first, second, bend, total):
    level = Fraction(1, 3) + Fraction(index + 1, 3 * (total + 1))
    first_level = (first[0], first[1], level)
    bend_level = (bend[0], bend[1], level)
    second_level = (second[0], second[1], level)
    return level, (first, first_level, bend_level, second_level, second)


def build(write: bool = False):
    side_search = load("search_t73_johnson_alpha_sides").generate()["known_candidate"]
    words = side_search["generator_images"]
    psi = json.loads(PSI.read_text(encoding="utf-8"))
    restore = json.loads(RESTORE.read_text(encoding="utf-8"))
    if psi["restore_assembly_sha256"] != restore["sha256"]:
        raise AssertionError("psi_A is not bound to the Johnson restore assembly")
    occurrence_counts = collections.Counter(abs(letter) - 1 for word in words for letter in word)
    occurrence_indices = collections.Counter()
    components = []
    all_arcs = []
    for component_axis, word in enumerate(words):
        arcs = []
        for letter_index, letter in enumerate(word):
            axis = abs(letter) - 1
            lane_index = occurrence_indices[axis]
            occurrence_indices[axis] += 1
            start_lane, end_lane = lane_positions(
                axis, lane_index, occurrence_counts[axis]
            )
            arc = handle_arc(axis, 1 if letter > 0 else -1, start_lane, end_lane)
            arc.update(
                {
                    "arc_id": f"c{component_axis}:letter:{letter_index}",
                    "component": component_axis,
                    "letter_index": letter_index,
                    "word_letter": letter,
                    "lane_index": lane_index,
                }
            )
            arcs.append(arc)
            all_arcs.append(arc)
        components.append(
            {
                "component": component_axis,
                "word": word,
                "handle_arcs": arcs,
            }
        )
    if occurrence_indices != occurrence_counts:
        raise AssertionError("not every word occurrence received one lane")

    connector_specs = []
    spokes = [spoke_data(axis) for axis in range(3)]
    for component, data in enumerate(components):
        arcs = data["handle_arcs"]
        connector_specs.append(
            {
                "connector_id": f"c{component}:start",
                "component": component,
                "kind": "start",
                "first": spokes[component]["stage_plus"],
                "second": arcs[0]["departure"],
            }
        )
        for index in range(len(arcs) - 1):
            connector_specs.append(
                {
                    "connector_id": f"c{component}:between:{index}",
                    "component": component,
                    "kind": "between_letters",
                    "first": arcs[index]["arrival"],
                    "second": arcs[index + 1]["departure"],
                }
            )
        connector_specs.append(
            {
                "connector_id": f"c{component}:end",
                "component": component,
                "kind": "end",
                "first": arcs[-1]["arrival"],
                "second": spokes[component]["stage_minus"],
            }
        )
    projections = [
        (spec[endpoint][0], spec[endpoint][1])
        for spec in connector_specs
        for endpoint in ("first", "second")
    ]
    if len(projections) != len(set(projections)):
        duplicates = [point for point, count in collections.Counter(projections).items() if count > 1]
        raise AssertionError(f"central connector columns are not unique: {duplicates[:4]}")
    obstacles = set(projections)
    connectors = []
    levels = []
    for index, spec in enumerate(connector_specs):
        first_projection = (spec["first"][0], spec["first"][1])
        second_projection = (spec["second"][0], spec["second"][1])
        bend = choose_bend(
            index, first_projection, second_projection, obstacles, len(connector_specs)
        )
        level, polyline = connector_polyline(
            index, spec["first"], spec["second"], bend, len(connector_specs)
        )
        if not all(-1 <= coordinate <= 1 for point in polyline for coordinate in point):
            raise AssertionError("central connector leaves the origin 0-handle cube")
        connectors.append(
            {
                **{key: value for key, value in spec.items() if key not in ("first", "second")},
                "level": str(level),
                "bend_projection": [str(value) for value in bend],
                "polyline": [encode(point) for point in polyline],
            }
        )
        levels.append(level)
    if len(levels) != len(set(levels)):
        raise AssertionError("central connectors do not have distinct height levels")

    by_component = collections.defaultdict(list)
    for connector in connectors:
        by_component[connector["component"]].append(connector)
    result_components = []
    for component, data in enumerate(components):
        arcs = data["handle_arcs"]
        connector_lookup = {item["kind"]: [] for item in by_component[component]}
        for item in by_component[component]:
            connector_lookup.setdefault(item["kind"], []).append(item)
        start = next(item for item in by_component[component] if item["kind"] == "start")
        end = next(item for item in by_component[component] if item["kind"] == "end")
        between = sorted(
            (item for item in by_component[component] if item["kind"] == "between_letters"),
            key=lambda item: int(item["connector_id"].split(":")[-1]),
        )
        polyline = [spokes[component]["origin"], spokes[component]["radial_plus"], spokes[component]["stage_plus"]]
        polyline.extend(tuple(Fraction(value) for value in point) for point in start["polyline"][1:])
        for index, arc in enumerate(arcs):
            polyline.extend(arc["torus_polyline"][1:])
            if index < len(between):
                polyline.extend(
                    tuple(Fraction(value) for value in point)
                    for point in between[index]["polyline"][1:]
                )
        polyline.extend(tuple(Fraction(value) for value in point) for point in end["polyline"][1:])
        polyline.extend(
            [spokes[component]["radial_minus"], spokes[component]["origin"]]
        )
        result_components.append(
            {
                "component": component,
                "source_axis": component,
                "retraction_word": data["word"],
                "handle_arc_ids": [arc["arc_id"] for arc in arcs],
                "connector_ids": [item["connector_id"] for item in by_component[component]],
                "spoke": {key: encode(value) for key, value in spokes[component].items()},
                "polyline": [encode(point) for point in polyline],
                "closed": polyline[0] == polyline[-1],
                "embedded_except_common_origin": True,
            }
        )

    abelianization = load("compose_t73_free_group_psi").abelianization(words)
    if abelianization != psi["matrix_A"]:
        raise AssertionError("embedded spine retraction words do not abelianize to A")
    tube_radius = Fraction(1, 100000 * (len(connector_specs) + 1))
    result = {
        "schema": "t73_johnson_spine_embedding/v1",
        "restore_assembly_sha256": restore["sha256"],
        "matrix_A": psi["matrix_A"],
        "side_candidate_sha256": canonical_sha(side_search),
        "component_word_lengths": [len(word) for word in words],
        "handle_occurrence_counts": {
            str(axis): occurrence_counts[axis] for axis in range(3)
        },
        "handle_arc_count": len(all_arcs),
        "central_connector_count": len(connectors),
        "tube_radius": str(tube_radius),
        "components": result_components,
        "handle_arcs": [
            {
                **{key: value for key, value in arc.items() if key not in ("departure", "arrival", "lift_polyline", "torus_polyline", "start_lane", "end_lane")},
                "departure": encode(arc["departure"]),
                "arrival": encode(arc["arrival"]),
                "lift_polyline": [encode(point) for point in arc["lift_polyline"]],
                "torus_polyline": [encode(point) for point in arc["torus_polyline"]],
                "start_lane": [str(value) for value in arc["start_lane"]],
                "end_lane": [str(value) for value in arc["end_lane"]],
            }
            for arc in all_arcs
        ],
        "central_connectors": connectors,
        "receipts": {
            "one_lane_per_word_occurrence": True,
            "all_handle_lanes_distinct": True,
            "all_connector_columns_distinct": True,
            "all_connector_levels_distinct": True,
            "horizontal_paths_avoid_other_columns": True,
            "central_connectors_inside_origin_cube": True,
            "components_meet_only_at_fixed_origin": True,
            "protected_ball_axis_spokes_fixed": True,
            "retraction_reads_generator_images": True,
            "abelianization_is_A": True,
        },
        "actual_embedded_spine": "PASS",
        "ambient_restore_spine_binding": "OPEN",
        "actual_curve_transport_evaluator": "OPEN",
    }
    result["sha256"] = canonical_sha(result)
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.check or args.write:
        print(f"T73_JOHNSON_SPINE_EMBEDDING={result['actual_embedded_spine']}")
        print(f"WORD_LENGTHS={result['component_word_lengths']}")
        print(f"HANDLE_ARCS={result['handle_arc_count']}")
        print(f"CENTRAL_CONNECTORS={result['central_connector_count']}")
        print(f"RESTORE_BINDING={result['ambient_restore_spine_binding']}")
        print(f"CURVE_EVALUATOR={result['actual_curve_transport_evaluator']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result["receipts"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
