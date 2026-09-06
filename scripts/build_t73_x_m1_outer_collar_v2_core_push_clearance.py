#!/usr/bin/env python3
"""Exact global core/push segment clearance for source-germ collars v2."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_core_push_clearance import (
    exact_bounds,
    float_bounds,
    overlap,
    point,
    resolve,
    segment_intersects,
)

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v2_receipt.json"
LOCAL_VERIFY = (
    ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v2_verification.json"
)
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_v2_core_push_clearance.json"


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def load(receipt):
    paths = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            value = json.loads(line)
            paths.append(
                {
                    "interface": value["interface_index"],
                    "neighbor_id": value["neighbor_id"],
                    "core": [point(vertex) for vertex in value["final_core_vertices"]],
                    "push": [point(vertex) for vertex in value["final_push_vertices"]],
                }
            )
    segments = {"core": [], "push": []}
    for path in paths:
        for kind in ("core", "push"):
            for local, (first, second) in enumerate(zip(path[kind], path[kind][1:])):
                segments[kind].append(
                    {
                        "interface": path["interface"],
                        "neighbor_id": path["neighbor_id"],
                        "local": local,
                        "vertices": (first, second),
                    }
                )
    return paths, segments


def permitted_incidence(first, second, same_kind):
    shared = set(first["vertices"]) & set(second["vertices"])
    if not shared or not same_kind:
        return False
    if first["interface"] == second["interface"]:
        return abs(first["local"] - second["local"]) == 1
    return (
        first["neighbor_id"] == second["neighbor_id"]
        and first["vertices"][0] == second["vertices"][0]
    )


def compare(first_segments, second_segments, same_kind):
    bounds = [exact_bounds(segment["vertices"]) for segment in second_segments]
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        ((index, float_bounds(value), None) for index, value in enumerate(bounds)),
        properties=properties,
    )
    broad = bounds_rejects = incidences = exact = 0
    for first_index, first in enumerate(first_segments):
        first_bounds = exact_bounds(first["vertices"])
        candidates = tree.intersection(float_bounds(first_bounds))
        for second_index in candidates:
            if same_kind and second_index >= first_index:
                continue
            broad += 1
            if not overlap(first_bounds, bounds[second_index]):
                bounds_rejects += 1
                continue
            second = second_segments[second_index]
            if permitted_incidence(first, second, same_kind):
                incidences += 1
                continue
            exact += 1
            if segment_intersects(first["vertices"], second["vertices"]):
                return {
                    "status": "REFUTED",
                    "first": [first["interface"], first["local"]],
                    "second": [second["interface"], second["local"]],
                    "exact_checks_before_collision": exact,
                }
    return {
        "status": "PASS",
        "broad_candidates": broad,
        "exact_bounds_rejects": bounds_rejects,
        "permitted_incidences": incidences,
        "exact_segment_checks": exact,
        "intersections": 0,
    }


def build():
    collars = json.loads(COLLARS.read_text())
    local = json.loads(LOCAL_VERIFY.read_text())
    if local["construction_receipt_sha256"] != collars["sha256"]:
        raise AssertionError("v2 collar local verification is stale")
    paths, segments = load(collars)
    results = {
        "core/core": compare(segments["core"], segments["core"], True),
        "push/push": compare(segments["push"], segments["push"], True),
        "core/push": compare(segments["core"], segments["push"], False),
    }
    failing = [pair for pair, result in results.items() if result["status"] != "PASS"]
    result = {
        "schema": "t73_x_m1_outer_collar_v2_core_push_clearance/v1",
        "outer_collars_v2_receipt_sha256": collars["sha256"],
        "outer_collars_v2_local_verification_sha256": local["sha256"],
        "collar_count": len(paths),
        "core_segment_count": len(segments["core"]),
        "push_segment_count": len(segments["push"]),
        "pair_results": results,
        "failing_pairs": failing,
        "global_core_push_clearance": not failing,
        "classification": "ACTUAL_CORE_PUSH_PATHS"
        if not failing
        else "CANDIDATE_REFUTED",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V2_CORE_PUSH_CLEARANCE"
        if not failing
        else "REFUTED_X_M1_OUTER_COLLAR_V2_CORE_PUSH_CLEARANCE",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("v2 outer collar core/push clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "failing_pairs": result["failing_pairs"],
                "pair_results": result["pair_results"],
            },
            sort_keys=True,
        )
    )
    if result["failing_pairs"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
