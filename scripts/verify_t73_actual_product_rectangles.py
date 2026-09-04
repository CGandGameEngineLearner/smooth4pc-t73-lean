#!/usr/bin/env python3
"""Verify all actual detector product rectangles and a source mutation."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECTANGLES = ROOT / "geometry" / "t73_actual_product_rectangles.json"


def load(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(data):
    if data["rectangle_count"] != 44 or len(data["rectangles"]) != 44:
        raise AssertionError("actual rectangle count is not 44")
    if [item["wicket"] for item in data["rectangles"]] != list(range(1, 45)):
        raise AssertionError("actual rectangle wicket order changed")
    for item in data["rectangles"]:
        if not item["actual_y_source_id"] or not item["actual_z_source_id"]:
            raise AssertionError("product rectangle lost an actual side source")
        if not item["between_y_and_z"] or not item["coordinate_chart_move_sha256"]:
            raise AssertionError("product rectangle lost its connector or chart move")
        if item["z_side"]["kind"] == "x_slide_replacement_by_actual_m1_z_lane" and not item["z_side"]["x_slide_band_sha256"]:
            raise AssertionError("x-replaced z side lost its Kirby band")
    if not data["all_y_z_sources_actual"] or not data["all_connectors_actual"]:
        raise AssertionError("actual rectangle source receipts are not closed")


def verify():
    builder = load("build_t73_actual_product_rectangles")
    stored = json.loads(RECTANGLES.read_text(encoding="utf-8"))
    rebuilt = builder.build(write=False)
    if stored != rebuilt:
        raise AssertionError("stored product rectangles do not match a live rebuild")
    validate(stored)
    mutant = copy.deepcopy(stored)
    mutant["rectangles"][0]["actual_z_source_id"] = ""
    failed = False
    try:
        validate(mutant)
    except AssertionError:
        failed = True
    if not failed:
        raise AssertionError("product rectangle source mutation was not detected")
    return {
        "ACTUAL_PRODUCT_RECTANGLES": "PASS",
        "RECTANGLES": stored["rectangle_count"],
        "MUTATION_Z_SOURCE": "FAIL",
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
