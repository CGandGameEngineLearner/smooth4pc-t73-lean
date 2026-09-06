#!/usr/bin/env python3
"""Fail-closed 3D R-tree probe for v3 transition ribbon clearance."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import sys
from fractions import Fraction
from pathlib import Path

from rtree import index as rtree_index
import numpy as np

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from verify_t73_affine_s3_product_ribbon_clearance import triangles_intersect


ROOT = Path(__file__).resolve().parents[1]
TRANSITIONS = ROOT / "audit/t73_x_m1_negative_transition_push_paths_v3_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
BANDS = ROOT / "audit/t73_x_band_global_r3_lane_push_paths_receipt.json"
MIDDLES = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
SCREEN_AXES = (
    (-1_000_033, 1, 1),
    (-1_000_033, 1, 0),
    (-1_000_033, 1, -1),
    (-1_000_032, 1, 1),
    (-1_000_034, 1, 1),
    (1, 1, 1),
    (1, -1, 2),
    (2, 3, -5),
    (1, 2, 3),
    (1, 3, 7),
    (1, 5, 11),
    (1, 7, 17),
    (1, 11, 23),
    (1, -2, 5),
    (1, -3, 7),
    (1, -5, 11),
    (2, -7, 13),
    (3, 5, -17),
    (5, -11, -19),
    (7, 13, 29),
    (11, -17, 31),
)


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def exact_bounds(triangle):
    return tuple(min(vertex[axis] for vertex in triangle) for axis in range(3)), tuple(
        max(vertex[axis] for vertex in triangle) for axis in range(3)
    )


def float_bounds(bounds):
    low, high = bounds
    return tuple(math.nextafter(float(value), -math.inf) for value in low) + tuple(
        math.nextafter(float(value), math.inf) for value in high
    )


def overlap(first, second):
    return all(first[0][axis] <= second[1][axis] and second[0][axis] <= first[1][axis] for axis in range(3))


def screen_bounds(triangle):
    lows, highs = [], []
    for axis in SCREEN_AXES:
        values = [sum(coefficient * coordinate for coefficient, coordinate in zip(axis, vertex)) for vertex in triangle]
        lows.append(math.nextafter(float(min(values)), -math.inf))
        highs.append(math.nextafter(float(max(values)), math.inf))
    return lows, highs


def cache_records(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        return [json.loads(line) for line in source]


def add_triangle(output, system, owner, local_index, vertices, indices):
    output.append((system, owner, local_index, tuple(vertices[index] for index in indices)))


def transition_triangles(receipt):
    output = []
    for record in cache_records(receipt):
        core = [point(value) for value in record["core_vertices"]]
        push = [point(value) for value in record["push_vertices"]]
        vertices = core + push
        owner = (record["band_index"], record["side"])
        for local_index, indices in enumerate(record["ribbon_triangles"]):
            add_triangle(output, "transition", owner, local_index, vertices, indices)
    return output


def stub_triangles(receipt):
    output = []
    for record in cache_records(receipt):
        for name, stub in record["stubs"].items():
            core = [point(value) for value in stub["core_vertices"]]
            push = [point(value) for value in stub["push_vertices"]]
            vertices = core + push
            owner = (record["band_index"], name)
            for local_index, indices in enumerate(stub["ribbon_triangles"]):
                add_triangle(output, "stub", owner, local_index, vertices, indices)
    return output


def band_triangles(receipt):
    output = []
    for record in cache_records(receipt):
        for lane in record["lanes"]:
            core = [point(value) for value in lane["core_vertices"]]
            push = [point(value) for value in lane["push_vertices"]]
            vertices = core + push
            owner = (record["band_index"], lane["lane"])
            for local_index, indices in enumerate(lane["ribbon_triangles"]):
                add_triangle(output, "band", owner, local_index, vertices, indices)
    return output


def middle_triangles(receipt):
    output = []
    translation = (Fraction(20_000), Fraction(2_000), Fraction(0))
    for record in cache_records(receipt):
        core = [tuple(a + b for a, b in zip(point(value), translation)) for value in record["core_vertices_r3"]]
        push = [tuple(a + b for a, b in zip(point(value), translation)) for value in record["push_vertices_r3"]]
        vertices = core + push
        size = len(core)
        for segment in range(size - 1):
            add_triangle(output, "middle", record["band_index"], 2 * segment, vertices, [segment, segment + 1, size + segment + 1])
            add_triangle(output, "middle", record["band_index"], 2 * segment + 1, vertices, [segment, size + segment + 1, size + segment])
    return output


def permitted_incidence(first, second, shared):
    if not shared:
        return False
    if first[0] == second[0] == "transition" and first[1] == second[1]:
        return True
    if {first[0], second[0]} == {"transition", "stub"}:
        transition = first if first[0] == "transition" else second
        stub = second if first[0] == "transition" else first
        band, side = transition[1]
        expected = "target_complement_first" if side == "first" else "target_complement_last"
        return stub[1] == (band, expected)
    if {first[0], second[0]} == {"transition", "middle"}:
        transition = first if first[0] == "transition" else second
        middle = second if first[0] == "transition" else first
        return transition[1][0] == middle[1]
    return False


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def run(comparison_name, candidate_output=None):
    receipts = {
        "transition": json.loads(TRANSITIONS.read_text()),
        "stub": json.loads(STUBS.read_text()),
        "band": json.loads(BANDS.read_text()),
        "middle": json.loads(MIDDLES.read_text()),
    }
    loaders = {
        "transition": transition_triangles,
        "stub": stub_triangles,
        "band": band_triangles,
        "middle": middle_triangles,
    }
    transitions = transition_triangles(receipts["transition"])
    comparisons = loaders[comparison_name](receipts[comparison_name])
    bounds = [exact_bounds(item[3]) for item in comparisons]
    comparison_screens = [screen_bounds(item[3]) for item in comparisons]
    comparison_low = np.asarray([value[0] for value in comparison_screens])
    comparison_high = np.asarray([value[1] for value in comparison_screens])
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        ((item_index, float_bounds(item_bounds), None) for item_index, item_bounds in enumerate(bounds)),
        properties=properties,
    )
    broad = exact_bounds_rejects = screen_rejects = incidence = exact = 0
    raw_output = candidate_output.open("wb") if candidate_output else None
    gzip_output = gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) if raw_output else None
    try:
        if gzip_output:
            gzip_output.write((json.dumps({"comparison": comparison_name, "record": "header"}, sort_keys=True) + "\n").encode())
        for transition_index, transition in enumerate(transitions):
            if os.environ.get("T73_PROGRESS") and transition_index % 1000 == 0:
                print(f"{comparison_name} {transition_index}/{len(transitions)} broad={broad} exact={exact}", file=sys.stderr, flush=True)
            transition_bound = exact_bounds(transition[3])
            candidates = np.fromiter(tree.intersection(float_bounds(transition_bound)), dtype=np.int64)
            if comparison_name == "transition":
                candidates = candidates[candidates < transition_index]
            broad += len(candidates)
            local_low, local_high = screen_bounds(transition[3])
            mask = np.all(comparison_high[candidates] >= local_low, axis=1)
            mask &= np.all(comparison_low[candidates] <= local_high, axis=1)
            screen_rejects += int(np.count_nonzero(~mask))
            for raw_index in candidates[mask]:
                other_index = int(raw_index)
                other = comparisons[other_index]
                if not overlap(transition_bound, bounds[other_index]):
                    exact_bounds_rejects += 1
                    continue
                shared = set(transition[3]) & set(other[3])
                if shared:
                    if not permitted_incidence(transition, other, shared):
                        raise AssertionError(f"unexpected shared ribbon vertex: {transition[:3]} / {other[:3]}")
                    incidence += 1
                    continue
                exact += 1
                if gzip_output:
                    gzip_output.write(f"{transition_index},{other_index}\n".encode())
                    continue
                if triangles_intersect(transition[3], other[3]):
                    return {
                        "verdict": "REFUTED_TRANSITION_RIBBON_GLOBAL_CLEARANCE",
                        "comparison": comparison_name,
                        "transition": [transition[0], transition[1], transition[2]],
                        "other": [other[0], other[1], other[2]],
                        "transition_triangle": [[str(value) for value in vertex] for vertex in transition[3]],
                        "other_triangle": [[str(value) for value in vertex] for vertex in other[3]],
                        "broad_candidates_before_collision": broad,
                        "exact_checks_before_collision": exact,
                    }
    finally:
        if gzip_output:
            gzip_output.close()
        if raw_output:
            raw_output.close()
    result = {
        "verdict": "EXACT_CANDIDATES_EXPORTED" if candidate_output else "PASS_TRANSITION_RIBBON_COMPARISON_PROBE",
        "comparison": comparison_name,
        "transition_triangle_count": len(transitions),
        "comparison_triangle_count": len(comparisons),
        "broad_candidates": broad,
        "exact_integer_functional_interval_rejects": screen_rejects,
        "exact_bounds_rejects": exact_bounds_rejects,
        "permitted_incidences": incidence,
        "exact_triangle_checks": exact,
        "intersections": 0,
    }
    if candidate_output:
        result.update({
            "candidate_path": str(candidate_output),
            "candidate_size": candidate_output.stat().st_size,
            "candidate_sha256": file_sha(candidate_output),
        })
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("comparison", choices=("transition", "stub", "band", "middle"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--candidate-output", type=Path)
    args = parser.parse_args()
    result = run(args.comparison, args.candidate_output)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: result[key] for key in result if key in ("verdict", "comparison", "broad_candidates", "exact_triangle_checks", "transition", "other")}, sort_keys=True))
    if result["verdict"].startswith("REFUTED"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
