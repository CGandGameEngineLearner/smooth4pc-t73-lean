#!/usr/bin/env python3
"""Verify the stage-0 AR source atlas against live coordinate artifacts."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "geometry" / "t73_ar_source_coordinate_atlas.json"


def load_builder():
    path = ROOT / "scripts" / "build_t73_ar_source_coordinate_atlas.py"
    spec = importlib.util.spec_from_file_location("t73_ar_source_atlas_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pointer(document: Any, value: str) -> Any:
    current = document
    for token in value.split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def validate(data: dict[str, Any]) -> dict[str, Any]:
    builder = load_builder()
    ar = json.loads(builder.AR_PATH.read_text(encoding="utf-8"))
    belts = json.loads(builder.BELT_PATH.read_text(encoding="utf-8"))
    cancel_t = json.loads(builder.T_CANCEL_PATH.read_text(encoding="utf-8"))
    cancel_x = json.loads(builder.X_CANCEL_PATH.read_text(encoding="utf-8"))
    pair = json.loads(builder.PAIR_PATH.read_text(encoding="utf-8"))
    if data.get("schema") != "t73_ar_source_coordinate_atlas/v1":
        raise AssertionError("wrong AR source atlas schema")
    expected_bindings = {
        "actual_ar_link_sha256": ar["sha256"],
        "belt_spheres_sha256": belts["sha256"],
        "t_cancellation_sha256": cancel_t["sha256"],
        "x_cancellation_sha256": cancel_x["sha256"],
        "p0a_handlebody_pair_sha256": pair["pair_sha256"],
    }
    if data.get("source_bindings") != expected_bindings:
        raise AssertionError("atlas source bindings are stale")

    required_cores = {"m_1", "m_2", "m_3", "h_CS", "r_xy", "r_yz", "r_zx"}
    records = data.get("pre_cancellation_cores", {})
    if set(records) != required_cores:
        raise AssertionError("atlas does not reference exactly seven pre-cancellation cores")
    for name, record in records.items():
        source = pointer(ar, record["source_pointer"])
        if builder.canonical_sha(source) != record["core_sha256"]:
            raise AssertionError(f"{name} core pointer/hash is stale")
        if builder.dimensions(source) != record["coordinate_dimension"]:
            raise AssertionError(f"{name} coordinate dimension is false")
        if len(source) != record["vertex_count"]:
            raise AssertionError(f"{name} vertex count is false")
        if not record["closed_verified"]:
            raise AssertionError(f"{name} closure is not verified")

    charts = data["source_charts"]
    if charts["mapping_torus_T3xI"]["coordinate_names"] != ["x", "y", "z", "u"]:
        raise AssertionError("mapping-torus coordinate semantics changed")
    if charts["fiber_dual_H2_T3"]["coordinate_names"] != ["x", "y", "z"]:
        raise AssertionError("dual-cell coordinate semantics changed")
    if charts["x_belt_local"]["coordinate_names"] != ["y", "z", "nu"]:
        raise AssertionError("x-belt normal coordinate was relabelled as mapping-torus u")
    t_vertices = belts["t_handle"]["belt_sphere"]["vertices"]
    if any(len(vertex) != 4 or Fraction(vertex[3]) != Fraction(1, 2) for vertex in t_vertices):
        raise AssertionError("t-belt vertices do not lie in the stored u=1/2 slice")
    if any(
        len(point) != 3
        for band in cancel_t["slide_bands"]
        for point in band["band_core_on_belt_sphere"]
    ):
        raise AssertionError("t-band center cannot use the recorded constant-u lift")
    x_vertices = belts["x_handle"]["belt_sphere"]["vertices"]
    if any(len(vertex) != 4 or Fraction(vertex[0]) != 2 for vertex in x_vertices):
        raise AssertionError("x-belt vertices do not lie in the local x=2 chart")
    if any(
        len(point) != 3 or Fraction(point[2]) != 1
        for band in cancel_x["slide_bands"]
        for point in band["band_core_on_positive_belt_face"]
    ):
        raise AssertionError("x-slide band center left the recorded positive nu face")
    normal_values = {Fraction(vertex[3]) for vertex in x_vertices}
    if normal_values != {Fraction(-1), Fraction(1)}:
        raise AssertionError("unexpected x-belt normal-coordinate boundary")
    u_interval = tuple(Fraction(value) for value in charts["mapping_torus_T3xI"]["u_interval"])
    naive_coordinatewise_inclusion_fails = any(
        normal < u_interval[0] or normal > u_interval[1]
        for normal in normal_values
    )
    if not naive_coordinatewise_inclusion_fails:
        raise AssertionError("expected x-belt nu/u semantic mismatch disappeared")

    snapshots = data["presentation_snapshots"]
    if cancel_t["handle_counts_before"][1:3] != [4, 7]:
        raise AssertionError("live pre-cancellation handle counts changed")
    if cancel_x["handle_counts_after"][1:3] != [2, 5]:
        raise AssertionError("live post-cancellation handle counts changed")
    if snapshots["pre_cancellation"]["required_dotted_meridians"] != 4:
        raise AssertionError("seven pre-cancellation cores require four dotted meridians")
    if snapshots["pre_cancellation"]["required_two_handle_cores"] != 7:
        raise AssertionError("wrong pre-cancellation two-handle count")
    if snapshots["post_cancellation"]["required_dotted_meridians"] != 2:
        raise AssertionError("post-cancellation diagram requires two dotted meridians")
    if snapshots["post_cancellation"]["required_two_handle_cores"] != 5:
        raise AssertionError("wrong post-cancellation two-handle count")

    missing = data["missing_transitions_in_order"]
    expected_missing_ids = [
        "fiber_dual_H2_to_mapping_torus",
        "x_belt_local_to_mapping_torus_or_cut_handlebody",
        "cut_handlebody_to_dotted_S3_presentation",
        "full_band_rectangles_and_surgery_splices",
    ]
    if [item["id"] for item in missing] != expected_missing_ids:
        raise AssertionError("missing transition order changed")
    if any(item["status"] != "OPEN" for item in missing):
        raise AssertionError("an absent transition was promoted without a witness")
    if data["status"]["common_kirby_presentation"] != "OPEN":
        raise AssertionError("source atlas cannot claim a completed Kirby presentation")
    if data["status"]["complete_pre_cancellation_framing_ribbons"] != "OPEN":
        raise AssertionError("three dual-cell framing ribbons are still missing")
    if data["status"]["upstream_actual_framed_ar_link_claim"] != "PASS":
        raise AssertionError("upstream framed-link status changed")
    if data["status"]["explicit_dual_cell_ribbon_count"] != 0:
        raise AssertionError("dual-cell ribbon count is not supported by coordinates")
    if data["status"]["explicit_pre_cancellation_dotted_meridian_count"] != 0:
        raise AssertionError("dotted-meridian count is not supported by coordinates")
    if any(name in ar["components"] for name in ("dotted_x", "dotted_y", "dotted_z", "dotted_t")):
        raise AssertionError("dotted meridian inventory must be updated")

    digest = data.get("sha256")
    payload = {key: value for key, value in data.items() if key != "sha256"}
    if digest != builder.canonical_sha(payload):
        raise AssertionError("AR source atlas SHA is stale")
    live = builder.build(write=False)
    if data != live:
        raise AssertionError("stored AR source atlas differs from live reconstruction")
    return {
        "schema": "t73_ar_source_coordinate_atlas_verification/v1",
        "source_bindings": "PASS",
        "seven_pre_cancellation_cores": "PASS",
        "core_pointer_hashes": "PASS",
        "chart_coordinate_semantics": "PASS",
        "t_belt_constant_u_lift": "PASS",
        "x_belt_positive_normal_face": "PASS",
        "naive_x_normal_equals_u_rejected": "PASS",
        "pre_snapshot_4_dotted_7_two_handles": "PASS",
        "post_snapshot_2_dotted_5_two_handles": "PASS",
        "common_kirby_presentation": "OPEN",
        "upstream_PASS_does_not_supply_missing_coordinates": "PASS",
        "verdict": "PASS_PREFIX_ONLY",
    }


def mutation_checks(data: dict[str, Any]) -> dict[str, str]:
    checks = {}
    mutations = {
        "SOURCE_HASH": ("source_bindings", "actual_ar_link_sha256", "0" * 64),
        "CORE_HASH": ("pre_cancellation_cores", "m_2", "core_sha256", "0" * 64),
        "X_NORMAL_LABEL": ("source_charts", "x_belt_local", "coordinate_names", ["y", "z", "u"]),
        "FALSE_COMMON_PASS": ("status", "common_kirby_presentation", "PASS"),
    }
    for name, path in mutations.items():
        mutant = copy.deepcopy(data)
        current = mutant
        for token in path[:-2]:
            current = current[token]
        current[path[-2]] = path[-1]
        try:
            validate(mutant)
        except AssertionError:
            checks[name] = "FAIL_DETECTED"
        else:
            checks[name] = "UNDETECTED"
    return checks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    data = json.loads(ATLAS.read_text(encoding="utf-8"))
    result = validate(data)
    print("T73_AR_SOURCE_ATLAS_VERIFY=PASS_PREFIX_ONLY")
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.mutations:
        checks = mutation_checks(data)
        if set(checks.values()) != {"FAIL_DETECTED"}:
            raise AssertionError(f"undetected source-atlas mutation: {checks}")
        print(json.dumps(checks, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
