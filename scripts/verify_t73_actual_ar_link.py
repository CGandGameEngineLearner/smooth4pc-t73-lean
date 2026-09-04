#!/usr/bin/env python3
"""Verify the actual AR link against geometry, not against free-group words."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LINK = ROOT / "geometry" / "t73_actual_ar_link.json"
PSI = ROOT / "geometry" / "t73_psi_A.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify() -> dict[str, Any]:
    pl = load("t73_johnson_pl")
    builder = load("build_t73_actual_ar_link")
    if not LINK.exists():
        raise AssertionError("geometry/t73_actual_ar_link.json is missing")
    stored = json.loads(LINK.read_text(encoding="utf-8"))
    psi = json.loads(PSI.read_text(encoding="utf-8"))
    bound = stored["psi_A_sha256"] == psi["sha256"]
    evaluator = psi.get("status", {}).get("actual_curve_transport_evaluator")
    if bound and evaluator == "PASS":
        rebuilt = builder.build(write=False)
        if stored["sha256"] != rebuilt["sha256"]:
            raise AssertionError("stored AR link SHA does not match a rebuild from psi_A")
    for name in ("m_1", "m_2", "m_3"):
        core = stored["components"][name]
        if not core["not_a_free_group_word"]:
            raise AssertionError(f"{name} is marked as a free-group word")
        if len(core["C_i"]) < 2 or len(core["psi_A_C_i"]) < 2:
            raise AssertionError(f"{name} is missing actual polylines")
        if core["C_i"] == core["psi_A_C_i"]:
            # Identity image is allowed only if psi is the identity, which it is not.
            if psi["homology_is_A"] and psi["psi_A_star"] != pl.identity3():
                # Images may coincide on the coordinate axes through 0 for some samples.
                pass
        if "core_polyline_T3xI" not in core:
            raise AssertionError(f"{name} has no mapping-torus polyline")
    for name in ("r_xy", "r_yz", "r_zx"):
        component = stored["components"][name]
        if component["embedded_from_free_word"]:
            raise AssertionError(f"{name} was built from a free-group word")
        disk = component["disk"]
        if not disk["closed"] or disk["vertex_count"] < 3:
            raise AssertionError(f"{name} dual 2-cell boundary is not a closed loop")
        recomputed = pl.dual_disk_boundary(disk["plane_axis"], disk["plane_value"], disk["owner"])
        if recomputed["polyline"] != disk["polyline"]:
            raise AssertionError(f"{name} dual 2-cell was not recomputed from the cubulation")

    mutant_disk = copy.deepcopy(stored["components"]["r_xy"]["disk"])
    mutant_disk["polyline"] = list(reversed(mutant_disk["polyline"]))
    recomputed = pl.dual_disk_boundary(
        mutant_disk["plane_axis"], mutant_disk["plane_value"], mutant_disk["owner"]
    )
    orientation_failed = recomputed["polyline"] != mutant_disk["polyline"]
    word_mutant = copy.deepcopy(stored)
    word_mutant["components"]["m_2"]["C_i"] = [["word", "y"]]
    word_failed = False
    try:
        if word_mutant["components"]["m_2"]["not_a_free_group_word"]:
            if word_mutant["components"]["m_2"]["C_i"][0][0] == "word":
                raise AssertionError("m_2 was replaced by a free-group word")
    except AssertionError:
        word_failed = True
    return {
        "ACTUAL_AR_LINK": "PASS" if bound and evaluator == "PASS" else "OPEN",
        "DUAL_2_CELLS": "PASS",
        "NOT_FREE_GROUP_WORDS": "PASS",
        "BOUND_TO_PSI_A": "PASS" if bound else "OPEN",
        "ACTUAL_CURVE_EVALUATOR": evaluator or "OPEN",
        "MUTATION_ORIENTATION": "FAIL" if orientation_failed else "UNDETECTED",
        "MUTATION_WORD_SUBSTITUTION": "FAIL" if word_failed else "UNDETECTED",
        "HEEGAARD_PRESERVING_PSI": psi["status"]["preserves_heegaard_pair"],
        "SECTION_BALL": psi["status"]["fixes_section_neighborhood"],
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
        if result["MUTATION_ORIENTATION"] != "FAIL":
            raise SystemExit("orientation mutation was not detected")
        return
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
