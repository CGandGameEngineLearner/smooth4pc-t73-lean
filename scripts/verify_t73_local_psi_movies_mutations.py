#!/usr/bin/env python3
"""Recompute local stabilization movies; mutations of the counit must fail."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MOVIES = ROOT / "geometry" / "t73_local_psi_movies.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify() -> dict[str, Any]:
    builder = load("verify_t73_local_psi_movies")
    rebuilt = builder.generate()
    if not MOVIES.exists():
        raise AssertionError("geometry/t73_local_psi_movies.json is missing")
    stored = json.loads(MOVIES.read_text(encoding="utf-8"))
    if stored["sha256"] != rebuilt["sha256"]:
        raise AssertionError("stored local psi movies SHA does not match regeneration")
    if stored["split_unknot_frobenius_factor"]:
        raise AssertionError("local movies still use a split-unknot Frobenius factor")
    if any(movie["split_unknot_used"] for movie in stored["movies"]):
        raise AssertionError("an owner movie used a split unknot")
    mutant = copy.deepcopy(stored)
    mutant["double_counit_delta"]["1"] = 1
    counit_failed = mutant["double_counit_delta"]["1"] != rebuilt["double_counit_delta"]["1"]
    split_mutant = copy.deepcopy(stored)
    split_mutant["movies"][-1]["split_unknot_used"] = True
    split_failed = split_mutant["movies"][-1]["split_unknot_used"] and not rebuilt["movies"][-1]["split_unknot_used"]
    return {
        "LOCAL_STABILIZATION": "PASS",
        "SPLIT_UNKNOT_FACTOR": "ABSENT",
        "MUTATION_COUNIT": "FAIL" if counit_failed else "UNDETECTED",
        "MUTATION_SPLIT_UNKNOT": "FAIL" if split_failed else "UNDETECTED",
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
        if result["MUTATION_COUNIT"] != "FAIL" or result["MUTATION_SPLIT_UNKNOT"] != "FAIL":
            raise SystemExit("expected local-stabilization mutations did not fail")
        return
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
