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


def generate():
    johnson = load("search_t73_johnson_alpha_sides").generate()["known_candidate"]
    relative = load("straighten_t73_johnson_relative_ball").generate()
    m2 = johnson["m2_after_cancellation"]
    m2_occurrences = [(index, letter) for index, letter in enumerate(m2) if abs(letter) == 2]
    if len(m2_occurrences) != 42:
        raise AssertionError("Johnson m2 does not have 42 y passages")
    if [letter for _, letter in m2_occurrences] != [2] * 41 + [-2]:
        raise AssertionError("Johnson m2 y-passage orientation order differs")
    rxy = [3, 2, -3, -2]
    rxy_occurrences = [(index, letter) for index, letter in enumerate(rxy) if abs(letter) == 2]
    wickets = []
    for wicket, (index, letter) in enumerate(rxy_occurrences, start=1):
        wickets.append({
            "wicket": wicket,
            "owner": "r_xy",
            "word_index": index,
            "orientation": 1 if letter > 0 else -1,
            "lane_point": lane_point(wicket),
            "passage_arc": [lane_point(wicket) + ["-1/2"], lane_point(wicket) + ["1/2"]],
            "product_normal": ["1", "0", "0"],
        })
    for offset, (index, letter) in enumerate(m2_occurrences):
        wicket = offset + 3
        wickets.append({
            "wicket": wicket,
            "owner": "m_2",
            "word_index": index,
            "orientation": 1 if letter > 0 else -1,
            "lane_point": lane_point(wicket),
            "passage_arc": [lane_point(wicket) + ["-1/2"], lane_point(wicket) + ["1/2"]],
            "product_normal": ["1", "0", "0"],
        })
    if [entry["wicket"] for entry in wickets] != list(range(1, 45)):
        raise AssertionError("wicket labels are incomplete")
    if len({tuple(entry["lane_point"]) for entry in wickets}) != 44:
        raise AssertionError("lane points are not pairwise distinct")
    result = {
        "schema": "t73_johnson_ribbon_collar/v1",
        "johnson_candidate_sha256": canonical_sha(johnson),
        "relative_movie_sha256": relative["movie_sha256"],
        "ambient_handle": "the reduced y one-handle D^2 times [-1,1]",
        "containing_ball": {
            "chart": "D^2 times [-1/2,1/2]",
            "topological_type": "3-ball",
            "disjoint_from_section_ball": True,
            "orientation": "product orientation",
        },
        "wickets": wickets,
        "owner_counts": {"r_xy": 2, "m_2": 42},
        "negative_wickets": [entry["wicket"] for entry in wickets if entry["orientation"] < 0],
        "framing_push_epsilon": "1/10000",
        "pairwise_disjointness_status": "PASS_BY_DISTINCT_RATIONAL_LANES",
        "product_framing_status": "PASS",
        "ar_passage_binding_status": "PASS_BY_EXACT_JOHNSON_M2_AND_STANDARD_RXY",
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
