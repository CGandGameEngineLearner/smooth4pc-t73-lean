#!/usr/bin/env python3
"""GMP exact verifier for transition/stub common-displacement ribbons."""

from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from verify_t73_x_m1_transition_transition_ribbon_clearance_gmp import (
    constant_intersection,
    load_geometry,
    point,
    rectangle,
    resolve,
    subtract,
)


ROOT = Path(__file__).resolve().parents[1]
TRANSITIONS = ROOT / "audit/t73_x_m1_negative_transition_push_paths_v3_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
CANDIDATES = ROOT / "audit/t73_x_m1_transition_stub_ribbon_exact_candidates.json"


def load_stub_rectangles(path):
    output = []
    with gzip.open(path, "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            for name, stub in record["stubs"].items():
                core = [point(value) for value in stub["core_vertices"]]
                push = [point(value) for value in stub["push_vertices"]]
                for index in range(len(core) - 1):
                    output.append(((core[index], core[index + 1]), (push[index], push[index + 1]), (record["band_index"], name, index)))
    return output


def verify():
    transition_receipt = json.loads(TRANSITIONS.read_text())
    stub_receipt = json.loads(STUBS.read_text())
    candidate_receipt = json.loads(CANDIDATES.read_text())
    transitions = load_geometry(resolve(transition_receipt["cache_path"]))
    stubs = load_stub_rectangles(resolve(stub_receipt["cache_path"]))
    displacement = point(stub_receipt["push_displacement"])
    delta = displacement[0]
    checks = 0
    with gzip.open(resolve(candidate_receipt["candidate_path"]), "rt", encoding="utf-8") as source:
        if source.readline().strip() != "transition_stub_rectangle_pairs/v1":
            raise AssertionError("transition/stub exact candidate schema changed")
        for line in source:
            transition_index, stub_index = (int(value) for value in line.split(","))
            transition_core, transition_push = rectangle(transitions, transition_index)
            stub_core, stub_push, stub_owner = stubs[stub_index]
            if any(subtract(pushed, core) != displacement for core, pushed in zip(transition_core + stub_core, transition_push + stub_push)):
                raise AssertionError("transition/stub candidate is not common-displacement")
            checks += 1
            if checks % 100_000 == 0:
                print(f"transition/stub rectangles {checks}/{candidate_receipt['exact_rectangle_pair_count']}", file=sys.stderr, flush=True)
            if constant_intersection(transition_core, stub_core, delta):
                return {
                    "verdict": "REFUTED_TRANSITION_STUB_RIBBON_CLEARANCE",
                    "transition_rectangle": transition_index,
                    "stub_rectangle": stub_index,
                    "stub_owner": list(stub_owner),
                    "checks_before_collision": checks,
                }
    if checks != candidate_receipt["exact_rectangle_pair_count"]:
        raise AssertionError("transition/stub exact candidate count changed")
    return {
        "verdict": "PASS_TRANSITION_STUB_RIBBON_EXACT_CLEARANCE",
        "exact_rectangle_checks": checks,
        "permitted_port_triangle_pairs": candidate_receipt["permitted_port_triangle_pair_count"],
        "intersections": 0,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
