#!/usr/bin/env python3
"""Verify the actual three-handle surface transport and mutations."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SURFACES = ROOT / "geometry" / "t73_three_handle_surface_transport.json"


def load(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(data):
    if data["surface_count"] != 3 or len(data["surfaces"]) != 3:
        raise AssertionError("three-handle transport does not contain three surfaces")
    if not data["pairwise_disjoint_before"] or not data["pairwise_disjoint_after"]:
        raise AssertionError("three-handle surface transport loses disjointness")
    for surface in data["surfaces"]:
        if len(surface["disk_track_factor_indices"]) != 93 or surface["disk_track_factor_indices"] != list(range(93)):
            raise AssertionError("surface omits a Johnson disk-track factor")
        if len(surface["t_cancellation_band_hashes"]) != 6 or len(surface["x_cancellation_band_hashes"]) != 1513:
            raise AssertionError("surface omits a Kirby boundary-map band")
        profile_count = sum(item["copy_count"] for item in surface["core_disk_boundary_profile"])
        if profile_count != surface["core_disk_count_b"]:
            raise AssertionError("surface boundary copies disagree with b")
        if surface["punctured_surface"]["euler_characteristic"] != 2 - profile_count:
            raise AssertionError("punctured sphere has the wrong Euler characteristic")
        if surface["relative_surface_map"] != "PASS":
            raise AssertionError("surface relative map is not closed")
    if data["core_disk_counts"] != [12578, 1824, 409]:
        raise AssertionError("actual three-handle b counts changed")


def verify():
    builder = load("build_t73_three_handle_surface_transport")
    stored = json.loads(SURFACES.read_text(encoding="utf-8"))
    rebuilt = builder.build(write=False)
    if stored != rebuilt:
        raise AssertionError("stored surface transport does not match a live rebuild")
    validate(stored)
    mutant = copy.deepcopy(stored)
    mutant["surfaces"][0]["x_cancellation_band_hashes"].pop()
    failed = False
    try:
        validate(mutant)
    except AssertionError:
        failed = True
    if not failed:
        raise AssertionError("missing Kirby-band mutation was not detected")
    return {
        "ACTUAL_THREE_HANDLE_SURFACE_TRANSPORT": "PASS",
        "SURFACES": stored["surface_count"],
        "CORE_DISK_COUNTS": stored["core_disk_counts"],
        "T_BANDS_PER_SURFACE": 6,
        "X_BANDS_PER_SURFACE": 1513,
        "MUTATION_MISSING_X_BAND": "FAIL",
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
