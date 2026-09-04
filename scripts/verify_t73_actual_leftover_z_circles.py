#!/usr/bin/env python3
"""Verify the 227 actual leftover-circle transports and mutations."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "geometry" / "t73_actual_leftover_z_circles.json"


def load(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(data):
    if data["circle_count"] != 227 or len(data["circles"]) != 227:
        raise AssertionError("leftover circle count changed")
    supports = []
    for order, item in enumerate(data["circles"]):
        if not item["actual_z_source_id"] or not item["source_geometry"]:
            raise AssertionError("leftover circle lost its actual z source")
        if item["closure_band"]["movie_order"] != order or item["closure_band"]["relative_twist"] != 0:
            raise AssertionError("leftover closure movie order or framing changed")
        if item["target_meridian"][0] != item["target_meridian"][-1]:
            raise AssertionError("leftover target is not a circle")
        interval = tuple(Fraction(value) for value in item["closure_band"]["support_x_interval"])
        if interval[0] <= 2 or interval[1] <= interval[0]:
            raise AssertionError("leftover closure support meets the detector")
        supports.append(interval)
    for index, left in enumerate(supports):
        for right in supports[index + 1 :]:
            if not (left[1] < right[0] or right[1] < left[0]):
                raise AssertionError("two leftover closure supports overlap")


def verify():
    builder = load("build_t73_actual_leftover_z_circles")
    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    rebuilt = builder.build(write=False)
    if stored != rebuilt:
        raise AssertionError("stored leftover circles do not match a live rebuild")
    validate(stored)
    mutant = copy.deepcopy(stored)
    mutant["circles"][0]["closure_band"]["relative_twist"] = 1
    failed = False
    try:
        validate(mutant)
    except AssertionError:
        failed = True
    if not failed:
        raise AssertionError("leftover framing mutation was not detected")
    return {
        "ACTUAL_LEFTOVER_Z_CIRCLES": "PASS",
        "CIRCLES": stored["circle_count"],
        "MUTATION_RELATIVE_TWIST": "FAIL",
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
