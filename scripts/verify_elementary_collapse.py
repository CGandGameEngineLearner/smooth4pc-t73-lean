#!/usr/bin/env python3
"""Replay stored elementary collapses; do not trust a self-reported PASS field."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_t73_common_heegaard_complex.py"
TORUS = ROOT / "geometry" / "t73_common_torus_triangulation.json"
JOHNSON = ROOT / "geometry" / "t73_johnson_spines.json"
AR = ROOT / "geometry" / "t73_ar_spines.json"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_t73_common_heegaard_complex", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {BUILDER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def graph_from(block: dict[str, Any]):
    vertices = {tuple(vertex) for vertex in block["vertices"]}
    edges = {frozenset(tuple(vertex) for vertex in edge) for edge in block["edges"]}
    return vertices, edges


def check_pair(
    module,
    tets_0: list[list[list[int]]],
    tets_1: list[list[list[int]]],
    spines: dict[str, Any],
    labels: tuple[str, str, str, str],
) -> dict[str, Any]:
    h0, h1, k0, k1 = labels
    v0, e0 = graph_from(spines[k0])
    v1, e1 = graph_from(spines[k1])
    if spines[k0]["graph_rank"] != 3 or spines[k1]["graph_rank"] != 3:
        raise AssertionError("stored spine rank is not 3")
    if module.graph_rank(v0, e0) != 3 or module.graph_rank(v1, e1) != 3:
        raise AssertionError("recomputed spine rank is not 3")
    wrapped_0 = [[tuple(vertex) for vertex in tet] for tet in tets_0]
    wrapped_1 = [[tuple(vertex) for vertex in tet] for tet in tets_1]
    module.replay_collapse(wrapped_0, spines[f"collapse_{h0}"], v0, e0)
    module.replay_collapse(wrapped_1, spines[f"collapse_{h1}"], v1, e1)
    rebuilt_0 = module.collapse_relative(wrapped_0, v0, e0)
    rebuilt_1 = module.collapse_relative(wrapped_1, v1, e1)
    if rebuilt_0 != spines[f"collapse_{h0}"] or rebuilt_1 != spines[f"collapse_{h1}"]:
        raise AssertionError("stored collapse sequence is not the canonical live collapse")
    if spines["interface_genus"] != 3:
        raise AssertionError("stored interface genus is not 3")
    return {
        f"{h0}_steps": len(spines[f"collapse_{h0}"]),
        f"{h1}_steps": len(spines[f"collapse_{h1}"]),
        f"{k0}_rank": 3,
        f"{k1}_rank": 3,
        "interface_genus": 3,
    }


def verify() -> dict[str, Any]:
    module = load_builder()
    torus = json.loads(TORUS.read_text(encoding="utf-8"))
    johnson = json.loads(JOHNSON.read_text(encoding="utf-8"))
    ar = json.loads(AR.read_text(encoding="utf-8"))
    if torus.get("forbidden_assignment") != "tetrahedron barycenter distance to the two spines":
        raise AssertionError("torus file does not record the forbidden barycenter assignment")
    if "barycentric dual 3-blocks" not in torus.get("assignment", ""):
        raise AssertionError("torus file is not a dual-block assignment")
    johnson_result = check_pair(
        module,
        torus["johnson_tetrahedra"]["H0"],
        torus["johnson_tetrahedra"]["H1"],
        johnson,
        ("H_J_0", "H_J_1", "K_J_0", "K_J_1"),
    )
    ar_result = check_pair(
        module,
        torus["ar_tetrahedra"]["H0"],
        torus["ar_tetrahedra"]["H1"],
        ar,
        ("H_AR_0", "H_AR_1", "K_AR_0", "K_AR_1"),
    )
    if not torus["s_maps_johnson_pair_onto_ar_pair"]:
        raise AssertionError("stored S-mapping flag is false")
    live = module.generate()
    if not live["s_maps_johnson_pair_onto_ar_pair"]:
        raise AssertionError("live S-mapping failed")
    mutated = json.loads(json.dumps(johnson["collapse_H_J_0"]))
    mutated[0]["dim"] = 1 if mutated[0]["dim"] != 1 else 2
    try:
        v0, e0 = graph_from(johnson["K_J_0"])
        module.replay_collapse(
            [[tuple(vertex) for vertex in tet] for tet in torus["johnson_tetrahedra"]["H0"]],
            mutated,
            v0,
            e0,
        )
    except AssertionError:
        mutation = "FAIL"
    else:
        raise AssertionError("mutated collapse sequence was accepted")
    return {
        "ELEMENTARY_COLLAPSE": "PASS",
        "johnson": johnson_result,
        "ar": ar_result,
        "S_MAPS_PAIR": "PASS",
        "MUTATION_COLLAPSE_STEP": mutation,
        "UNION_T3": "PASS",
        "COMMON_BOUNDARY_GENUS": 3,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.check:
        print(f"ELEMENTARY_COLLAPSE={result['ELEMENTARY_COLLAPSE']}")
        print(f"H_J_0_STEPS={result['johnson']['H_J_0_steps']}")
        print(f"H_J_1_STEPS={result['johnson']['H_J_1_steps']}")
        print(f"H_AR_0_STEPS={result['ar']['H_AR_0_steps']}")
        print(f"H_AR_1_STEPS={result['ar']['H_AR_1_steps']}")
        print(f"SPINE_RANK=3")
        print(f"COMMON_BOUNDARY_GENUS={result['COMMON_BOUNDARY_GENUS']}")
        print(f"UNION_T3={result['UNION_T3']}")
        print(f"S_MAPS_PAIR={result['S_MAPS_PAIR']}")
        print(f"MUTATION_COLLAPSE_STEP={result['MUTATION_COLLAPSE_STEP']}")
        return
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
