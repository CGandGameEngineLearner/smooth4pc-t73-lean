#!/usr/bin/env python3
"""Recompute the Johnson ambient-restore/spine binding and reject mutations."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BINDING = ROOT / "geometry" / "t73_johnson_spine_binding.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(data: dict[str, Any]) -> None:
    canonical_sha = load("build_t73_johnson_spine_binding").canonical_sha
    restore = json.loads(
        (ROOT / "geometry" / "t73_johnson_restore_assembly.json").read_text(
            encoding="utf-8"
        )
    )
    spine = json.loads(
        (ROOT / "geometry" / "t73_johnson_spine_embedding.json").read_text(
            encoding="utf-8"
        )
    )
    movie = load("generate_t73_johnson_alpha_movie").generate()
    factors = restore["full_93_factor_assembly"]["factors"]
    if data["factor_count"] != 93 or len(data["factors"]) != 93:
        raise AssertionError("binding does not contain all 93 Johnson factors")
    for index, (record, move, factor) in enumerate(
        zip(data["factors"], movie["moves"], factors)
    ):
        expected = (
            index,
            int(move["alpha_target"]),
            int(move["alpha_prefix"]),
            int(move["power"]),
            move["side"],
        )
        actual = (
            int(record["index"]),
            int(record["source_axis"]),
            int(record["prefix_axis"]),
            int(record["power"]),
            record["side"],
        )
        if actual != expected:
            raise AssertionError("factor record changed its Johnson slide")
        if record["ambient_restore_factor_sha256"] != canonical_sha(factor):
            raise AssertionError("factor record is not bound to the ambient restore")
        if not record["ambient_extension_maps_both_owners"]:
            raise AssertionError("ambient factor lost the two-owner extension")
        if not record["ambient_extension_fixes_protected_ball"]:
            raise AssertionError("ambient factor no longer fixes the protected ball")

    arcs = {arc["arc_id"]: arc for arc in spine["handle_arcs"]}
    if data["leaf_binding_count"] != len(data["leaf_bindings"]):
        raise AssertionError("leaf binding count is inconsistent")
    if data["leaf_binding_count"] != spine["handle_arc_count"]:
        raise AssertionError("not every actual handle lane has a word leaf")
    seen = set()
    for leaf in data["leaf_bindings"]:
        key = (int(leaf["component"]), int(leaf["letter_index"]))
        if key in seen:
            raise AssertionError("a word leaf is bound twice")
        seen.add(key)
        arc = arcs.get(leaf["arc_id"])
        if arc is None:
            raise AssertionError("word leaf names a nonexistent lane")
        if (
            int(arc["component"]),
            int(arc["letter_index"]),
            int(arc["word_letter"]),
            int(arc["lane_index"]),
        ) != (
            key[0],
            key[1],
            int(leaf["letter"]),
            int(leaf["lane_index"]),
        ):
            raise AssertionError("word leaf is bound to the wrong oriented lane")
    if data["connector_binding_count"] != spine["central_connector_count"]:
        raise AssertionError("successive word leaves are not all joined")
    if data["ambient_restore_spine_binding"] != "PASS":
        raise AssertionError("ambient restore/spine binding is not closed")
    if data["coordinate_spine_curve_transport"] != "PASS":
        raise AssertionError("coordinate-spine transport is not closed")


def mutation_fails(data: dict[str, Any], mutate) -> bool:
    mutant = copy.deepcopy(data)
    mutate(mutant)
    try:
        validate(mutant)
    except AssertionError:
        return True
    return False


def verify() -> dict[str, Any]:
    builder = load("build_t73_johnson_spine_binding")
    stored = json.loads(BINDING.read_text(encoding="utf-8"))
    rebuilt = builder.build(write=False)
    if stored != rebuilt:
        raise AssertionError("stored spine binding does not match a live rebuild")
    validate(stored)

    side_failed = mutation_fails(
        stored,
        lambda mutant: mutant["factors"][0].__setitem__(
            "side",
            "source-first"
            if mutant["factors"][0]["side"] == "prefix-first"
            else "prefix-first",
        ),
    )
    leaf_failed = mutation_fails(
        stored,
        lambda mutant: mutant["leaf_bindings"][0].__setitem__(
            "letter", -int(mutant["leaf_bindings"][0]["letter"])
        ),
    )
    connector_failed = mutation_fails(
        stored,
        lambda mutant: mutant.__setitem__(
            "connector_binding_count", int(mutant["connector_binding_count"]) - 1
        ),
    )
    if not all((side_failed, leaf_failed, connector_failed)):
        raise AssertionError("a Johnson spine-binding mutation was not detected")
    return {
        "T73_JOHNSON_SPINE_BINDING": "PASS",
        "FACTORS": stored["factor_count"],
        "LEAF_BINDINGS": stored["leaf_binding_count"],
        "CONNECTOR_BINDINGS": stored["connector_binding_count"],
        "CURVE_TRANSPORT": stored["coordinate_spine_curve_transport"],
        "GENERAL_POINT_EVALUATOR": stored["general_point_evaluator"],
        "MUTATION_FACTOR_SIDE": "FAIL",
        "MUTATION_LEAF_ORIENTATION": "FAIL",
        "MUTATION_CONNECTOR_COUNT": "FAIL",
        "SHA256": stored["sha256"],
    }


def main() -> None:
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
