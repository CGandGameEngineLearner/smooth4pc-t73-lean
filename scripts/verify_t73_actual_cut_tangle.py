#!/usr/bin/env python3
"""Rebuild the post-cancellation y-detector directly from AR geometry."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TANGLE = ROOT / "geometry" / "t73_actual_cut_tangle.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(data):
    if data["derived_from_expected_B44"] or data["status"] != "PASS":
        raise AssertionError("actual cut tangle is not an independent passing construction")
    passages = data["passages"]
    if data["passage_count"] != 44 or len(passages) != 44:
        raise AssertionError("detector does not contain 44 cut passages")
    if [item["wicket"] for item in passages] != list(range(1, 45)):
        raise AssertionError("detector wicket order is incomplete")
    points = [tuple(item["belt_face_point"]) for item in passages]
    if len(points) != len(set(points)):
        raise AssertionError("two actual passages occupy the same y-belt point")
    owner_counts = {
        owner: sum(item["owner"] == owner for item in passages)
        for owner in ("r_xy", "m_2")
    }
    if owner_counts != {"r_xy": 2, "m_2": 42}:
        raise AssertionError("detector owner counts changed")
    if sum(item["orientation"] < 0 for item in passages) != 2:
        raise AssertionError("detector orientation multiset changed")
    for item in passages:
        start, end = item["cut_arc_in_ball"]
        if start[:2] != list(item["belt_face_point"][:2]) or end[:2] != list(item["belt_face_point"][:2]):
            raise AssertionError("cut arc is not over its actual belt point")
        if start[2] != "-1" or end[2] != "1":
            raise AssertionError("cut arc is not height-monotone across the detector ball")
    paired = {(item["owner"], item["z_source_id"]) for item in data["product_rectangle_pairings"]}
    leftover = {(item["owner"], item["source_id"]) for item in data["leftover_z_circles"]}
    if paired & leftover:
        raise AssertionError("a z event is both paired and leftover")
    all_z = {
        (owner, event["source_id"])
        for owner, events in data["post_x_event_lists"].items()
        for event in events
        if event["label"] == "z"
    }
    if paired | leftover != all_z:
        raise AssertionError("product rectangles do not partition all actual z events")
    if data["leftover_circle_count"] != 227 or len(leftover) != 227:
        raise AssertionError("actual cut has the wrong leftover z-circle count")
    circle_centers = set()
    for item in data["leftover_z_circles"]:
        circle = item["circle_in_complement_chart"]
        if circle[0] != circle[-1] or len(circle) != 5:
            raise AssertionError("a leftover z component is not a closed PL meridian")
        center = circle[0][0]
        if center in circle_centers or Fraction(center) <= 2:
            raise AssertionError("leftover z meridians meet each other or the detector chart")
        circle_centers.add(center)


def verify():
    builder = load("build_t73_actual_cut_tangle")
    stored = json.loads(TANGLE.read_text(encoding="utf-8"))
    rebuilt = builder.build(write=False)
    if stored != rebuilt:
        raise AssertionError("stored cut tangle does not match a live geometry rebuild")
    validate(stored)
    mutant = copy.deepcopy(stored)
    mutant["passages"][1]["belt_face_point"] = mutant["passages"][0]["belt_face_point"]
    duplicate_failed = False
    try:
        validate(mutant)
    except AssertionError:
        duplicate_failed = True
    source = (ROOT / "scripts" / "build_t73_actual_cut_tangle.py").read_text(encoding="utf-8")
    forbidden_absent = all(
        token not in source
        for token in ("expected_public_word", "T73_DELTA3_PUBLIC_RECEIPT", "FROZEN")
    )
    if not duplicate_failed or not forbidden_absent:
        raise AssertionError("cut-tangle mutation or dependency gate failed")
    return {
        "ACTUAL_CUT_TANGLE": "PASS",
        "PASSAGES": stored["passage_count"],
        "LEFTOVER_Z_CIRCLES": stored["leftover_circle_count"],
        "OWNER_COUNTS": {"r_xy": 2, "m_2": 42},
        "MUTATION_DUPLICATE_PASSAGE": "FAIL",
        "FROZEN_B44_SOURCE_DEPENDENCY": "ABSENT",
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
