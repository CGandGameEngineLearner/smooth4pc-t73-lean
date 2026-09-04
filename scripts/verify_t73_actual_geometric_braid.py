#!/usr/bin/env python3
"""Verify the actual detector chart and its geometry-derived 44-strand braid."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "geometry" / "t73_actual_geometric_braid.json"
CUT = ROOT / "geometry" / "t73_actual_cut_tangle.json"


def load(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_chart(collar, cut):
    helper = load("generate_t73_johnson_ribbon_collar")
    current = {
        passage["wicket"]: tuple(Fraction(value) for value in passage["belt_face_point"][:2])
        for passage in cut["passages"]
    }
    if len(collar["coordinate_chart_movie"]) != 44:
        raise AssertionError("detector chart does not move all 44 actual points")
    for move in collar["coordinate_chart_movie"]:
        wicket = int(move["wicket"])
        path = [tuple(Fraction(value) for value in point) for point in move["point_path"]]
        if path[0] != current[wicket]:
            raise AssertionError("detector chart path does not start at its current actual point")
        obstacles = set(current.values())
        for obstacle in obstacles:
            if obstacle == path[0]:
                continue
            if helper.point_on_segment(obstacle, path[0], path[1]) or helper.point_on_segment(obstacle, path[1], path[2]):
                raise AssertionError("detector chart point motion crosses a stationary endpoint")
        if path[1][0] ** 2 + path[1][1] ** 2 >= 1:
            raise AssertionError("detector chart bend leaves the punctured disk")
        current[wicket] = path[-1]
    expected = {
        wicket: tuple(Fraction(value) for value in helper.lane_point(wicket))
        for wicket in range(1, 45)
    }
    if current != expected:
        raise AssertionError("detector chart does not reach the normalized lane configuration")
    by_wicket = {item["wicket"]: item for item in cut["passages"]}
    for wicket in collar["wickets"]:
        source = by_wicket[wicket["wicket"]]
        if wicket["actual_source_id"] != source["source_id"]:
            raise AssertionError("normalized wicket lost its actual AR passage identifier")
        if wicket["orientation"] != source["orientation"] or wicket["owner"] != source["owner"]:
            raise AssertionError("normalized wicket changed owner or orientation")


def verify():
    generator = load("generate_t73_johnson_geometric_braid")
    collar = load("generate_t73_johnson_ribbon_collar").generate()
    cut = json.loads(CUT.read_text(encoding="utf-8"))
    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    rebuilt = generator.generate()
    if stored != rebuilt:
        raise AssertionError("stored geometric braid does not match a live rebuild")
    validate_chart(collar, cut)
    if stored["elementary_crossing_count"] != 11340 or stored["strand_count"] != 44:
        raise AssertionError("geometry-derived braid has the wrong size")
    if stored["ar_lane_binding_status"] != "PASS" or stored["replacement_presentation_status"] != "PASS_ACTUAL_DETECTOR_POLYLINES":
        raise AssertionError("braid is not bound to the actual detector")
    mutant = copy.deepcopy(collar)
    mutant["coordinate_chart_movie"][0]["point_path"][1] = mutant["coordinate_chart_movie"][1]["point_path"][0]
    collision_failed = False
    try:
        validate_chart(mutant, cut)
    except AssertionError:
        collision_failed = True
    source = (ROOT / "scripts" / "generate_t73_johnson_geometric_braid.py").read_text(encoding="utf-8")
    comparison_after_recovery = source.index("target = reconstructor.expected_public_word()") > source.index("recovered =")
    if not collision_failed or not comparison_after_recovery:
        raise AssertionError("geometric braid dependency/mutation gate failed")
    return {
        "ACTUAL_GEOMETRIC_BRAID": "PASS",
        "STRANDS": stored["strand_count"],
        "CROSSINGS": stored["elementary_crossing_count"],
        "ENDPOINT_RETURN": stored["endpoint_return_status"],
        "NORMAL_RETURN": "PASS",
        "MUTATION_CHART_COLLISION": "FAIL",
        "FROZEN_COMPARISON_ORDER": "AFTER_GEOMETRY_RECOVERY",
        "SHA256": stored["witness_sha256"],
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
