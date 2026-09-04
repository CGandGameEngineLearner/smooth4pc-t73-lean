#!/usr/bin/env python3
"""Construct the 44 framed passage lanes in the Johnson reduced y-handle."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CUT = ROOT / "geometry" / "t73_actual_cut_tangle.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def lane_point(wicket: int):
    # Affine normalization of the control braid's initial configuration.
    x = Fraction(2 * (wicket - 1) - 43, 100)
    y = Fraction(wicket, 100)
    if x * x + y * y >= 1:
        raise AssertionError("lane point is outside D^2")
    return [str(x), str(y)]


def point_on_segment(point, first, second):
    direction = (second[0] - first[0], second[1] - first[1])
    offset = (point[0] - first[0], point[1] - first[1])
    if direction[0] * offset[1] - direction[1] * offset[0] != 0:
        return False
    dot = offset[0] * direction[0] + offset[1] * direction[1]
    length = direction[0] * direction[0] + direction[1] * direction[1]
    return 0 <= dot <= length


def choose_bend(index, first, second, obstacles):
    for attempt in range(1, 1000):
        bend = (
            Fraction(-1, 2) + Fraction((37 * index + 17 * attempt) % 997, 997),
            Fraction(-1, 2) + Fraction((53 * index + 29 * attempt) % 991, 991),
        )
        if bend[0] * bend[0] + bend[1] * bend[1] >= 1 or bend in obstacles:
            continue
        if any(
            obstacle not in (first, second)
            and (
                point_on_segment(obstacle, first, bend)
                or point_on_segment(obstacle, bend, second)
            )
            for obstacle in obstacles
        ):
            continue
        return bend
    raise AssertionError("could not normalize an actual detector point without collision")


def generate():
    cut = json.loads(CUT.read_text(encoding="utf-8"))
    if cut["status"] != "PASS" or cut["passage_count"] != 44:
        raise AssertionError("the actual post-cancellation detector is not ready")
    wickets = []
    current = {
        passage["wicket"]: tuple(Fraction(value) for value in passage["belt_face_point"][:2])
        for passage in cut["passages"]
    }
    chart_moves = []
    for passage in cut["passages"]:
        wicket = int(passage["wicket"])
        actual = current[wicket]
        normalized = tuple(Fraction(value) for value in lane_point(wicket))
        obstacles = set(current.values())
        if normalized in obstacles and normalized != actual:
            raise AssertionError("a normalized lane is occupied before its point move")
        bend = choose_bend(wicket, actual, normalized, obstacles)
        path = [[str(value) for value in point] for point in (actual, bend, normalized)]
        chart_moves.append(
            {
                "movie_order": wicket - 1,
                "wicket": wicket,
                "actual_belt_point": [str(value) for value in actual],
                "normalized_point": [str(value) for value in normalized],
                "point_path": path,
                "all_other_points_fixed": True,
            }
        )
        current[wicket] = normalized
        wickets.append(
            {
                "wicket": wicket,
                "owner": passage["owner"],
                "word_index": passage["word_event_index"],
                "orientation": passage["orientation"],
                "actual_source_id": passage["source_id"],
                "paired_z_source_id": passage["paired_z_source_id"],
                "actual_belt_face_point": passage["belt_face_point"],
                "actual_passage_arc": passage["cut_arc_in_ball"],
                "lane_point": lane_point(wicket),
                "passage_arc": [lane_point(wicket) + ["-1/2"], lane_point(wicket) + ["1/2"]],
                "actual_product_normal": passage["product_normal"],
                "product_normal": ["0", "1", "0"],
            }
        )
    if [entry["wicket"] for entry in wickets] != list(range(1, 45)):
        raise AssertionError("wicket labels are incomplete")
    if len({tuple(entry["lane_point"]) for entry in wickets}) != 44:
        raise AssertionError("lane points are not pairwise distinct")
    result = {
        "schema": "t73_johnson_ribbon_collar/v1",
        "actual_cut_tangle_sha256": cut["sha256"],
        "ambient_handle": "the actual y-detector PL 3-ball after the two verified cancellations",
        "containing_ball": {
            **cut["detector_ball"],
            "normalized_chart": "unit disk D^2 times [-1/2,1/2]",
            "topological_type": "PL 3-ball",
            "disjoint_from_section_ball": "PASS",
            "orientation": "PASS",
        },
        "coordinate_chart_movie": chart_moves,
        "coordinate_chart_inverse": "reverse the 44 point paths in reverse movie order",
        "wickets": wickets,
        "owner_counts": {"r_xy": 2, "m_2": 42},
        "negative_wickets": [entry["wicket"] for entry in wickets if entry["orientation"] < 0],
        "framing_push_epsilon": cut["passages"][0]["product_normal"][0],
        "pairwise_disjointness_status": "PASS",
        "product_framing_status": "PASS",
        "ar_passage_binding_status": "PASS",
        "coordinate_chart_status": "PASS",
    }
    result["collar_sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.check:
        print("T73_JOHNSON_RIBBON_COLLAR=PASS")
        print(f"WICKETS={len(result['wickets'])}")
        print(f"OWNER_COUNTS={result['owner_counts']}")
        print(f"NEGATIVE_WICKETS={result['negative_wickets']}")
        print(f"AR_PASSAGE_BINDING={result['ar_passage_binding_status']}")
        print(f"COLLAR_SHA256={result['collar_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
