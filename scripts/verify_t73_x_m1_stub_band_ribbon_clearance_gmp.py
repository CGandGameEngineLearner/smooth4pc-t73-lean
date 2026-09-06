#!/usr/bin/env python3
"""GMP exact verifier for all nonincident stub/band framing rectangles."""

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
    point,
    resolve,
    subtract,
)

ROOT = Path(__file__).resolve().parents[1]
STUBS = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
BANDS = ROOT / "audit/t73_x_band_global_r3_lane_push_paths_receipt.json"
CANDIDATES = ROOT / "audit/t73_x_m1_stub_band_ribbon_exact_candidates.json"


def load_rectangles(path, kind):
    output = []
    with gzip.open(path, "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            pieces = (
                record["stubs"].items()
                if kind == "stub"
                else ((lane["lane"], lane) for lane in record["lanes"])
            )
            for name, piece in pieces:
                core = [point(value) for value in piece["core_vertices"]]
                push = [point(value) for value in piece["push_vertices"]]
                for index in range(len(core) - 1):
                    output.append(
                        (
                            (core[index], core[index + 1]),
                            (push[index], push[index + 1]),
                            (record["band_index"], name, index),
                        )
                    )
    return output


def verify():
    stubs_receipt = json.loads(STUBS.read_text())
    bands_receipt = json.loads(BANDS.read_text())
    candidates = json.loads(CANDIDATES.read_text())
    stubs = load_rectangles(resolve(stubs_receipt["cache_path"]), "stub")
    bands = load_rectangles(resolve(bands_receipt["cache_path"]), "band")
    displacement = point(stubs_receipt["push_displacement"])
    if displacement != point(bands_receipt["push_displacement"]):
        raise AssertionError("stub/band displacement changed")
    checks = 0
    with gzip.open(
        resolve(candidates["candidate_path"]), "rt", encoding="utf-8"
    ) as source:
        if source.readline().strip() != "stub_band_rectangle_pairs/v1":
            raise AssertionError("stub/band exact candidate schema changed")
        for line in source:
            stub_index, band_index = (int(value) for value in line.split(","))
            stub_core, stub_push, stub_owner = stubs[stub_index]
            band_core, band_push, band_owner = bands[band_index]
            if any(
                subtract(pushed, core) != displacement
                for core, pushed in zip(stub_core + band_core, stub_push + band_push)
            ):
                raise AssertionError("stub/band rectangle is not a common translate")
            checks += 1
            if checks % 100_000 == 0:
                print(
                    f"stub/band rectangles {checks}/{candidates['exact_rectangle_pair_count']}",
                    file=sys.stderr,
                    flush=True,
                )
            if constant_intersection(stub_core, band_core, displacement[0]):
                return {
                    "verdict": "REFUTED_STUB_BAND_RIBBON_CLEARANCE",
                    "stub_rectangle": stub_index,
                    "band_rectangle": band_index,
                    "stub_owner": list(stub_owner),
                    "band_owner": list(band_owner),
                    "checks_before_collision": checks,
                }
    if checks != candidates["exact_rectangle_pair_count"]:
        raise AssertionError("stub/band exact candidate total changed")
    return {
        "verdict": "PASS_STUB_BAND_RIBBON_EXACT_CLEARANCE",
        "exact_rectangle_checks": checks,
        "shared_vertex_triangle_incidences": candidates[
            "shared_vertex_triangle_incidence_count"
        ],
        "adjacent_rectangle_triangle_incidences": candidates[
            "adjacent_rectangle_triangle_incidence_count"
        ],
        "intersections": 0,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
