#!/usr/bin/env python3
"""Exact direction-class hash clearance for all stub core/push segments."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUB_PUSH = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
SOURCE_HOMOTOPY = ROOT / "audit/t73_x_m1_stub_source_normal_homotopy.json"
OUTPUT = ROOT / "audit/t73_x_m1_stub_core_push_clearance.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    return path


def point(values):
    return tuple(Fraction(value) for value in values)


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def direction(segment):
    delta = subtract(segment[1], segment[0])
    pivot = next(value for value in delta if value)
    return tuple(value / pivot for value in delta)


def intersects(first, second):
    a, b = first
    c, d = second
    u, v, w = subtract(b, a), subtract(d, c), subtract(c, a)
    for first_axis, second_axis in ((0, 1), (0, 2), (1, 2)):
        denominator = u[first_axis] * (-v[second_axis]) - u[second_axis] * (-v[first_axis])
        if denominator:
            first_parameter = (
                w[first_axis] * (-v[second_axis]) - w[second_axis] * (-v[first_axis])
            ) / denominator
            second_parameter = (
                u[first_axis] * w[second_axis] - u[second_axis] * w[first_axis]
            ) / denominator
            return (
                0 <= first_parameter <= 1
                and 0 <= second_parameter <= 1
                and all(
                    a[axis] + first_parameter * u[axis]
                    == c[axis] + second_parameter * v[axis]
                    for axis in range(3)
                )
            )
    if cross(u, w) != (0, 0, 0):
        return False
    axis = next(index for index, value in enumerate(u) if value)
    return max(min(a[axis], b[axis]), min(c[axis], d[axis])) <= min(
        max(a[axis], b[axis]), max(c[axis], d[axis])
    )


def build():
    stub_push = json.loads(STUB_PUSH.read_text())
    source_homotopy = json.loads(SOURCE_HOMOTOPY.read_text())
    cores = []
    pushes = []
    with gzip.open(resolve(stub_push["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            for name, stub in record["stubs"].items():
                core_vertices = [point(value) for value in stub["core_vertices"]]
                push_vertices = [point(value) for value in stub["push_vertices"]]
                cores.extend(
                    (record["band_index"], name, index, (a, b))
                    for index, (a, b) in enumerate(zip(core_vertices, core_vertices[1:]))
                )
                pushes.extend(
                    (record["band_index"], name, index, (a, b))
                    for index, (a, b) in enumerate(zip(push_vertices, push_vertices[1:]))
                )
    core_classes = defaultdict(list)
    push_classes = defaultdict(list)
    for record in cores:
        core_classes[direction(record[3])].append(record)
    for record in pushes:
        push_classes[direction(record[3])].append(record)
    if set(core_classes) != set(push_classes) or len(core_classes) != 4:
        raise AssertionError("stub core/push direction classes changed")

    results = []
    total_candidates = total_exact = 0
    for core_direction in sorted(core_classes):
        for push_direction in sorted(push_classes):
            core_group = core_classes[core_direction]
            push_group = push_classes[push_direction]
            normal = cross(core_direction, push_direction)
            buckets = defaultdict(list)
            if any(normal):
                for record in core_group:
                    buckets[dot(normal, record[3][0])].append(record)
                key_for_push = lambda record: dot(normal, record[3][0])
                invariant = "coplanarity scalar (u cross v) dot point"
            else:
                for record in core_group:
                    buckets[cross(record[3][0], core_direction)].append(record)
                key_for_push = lambda record: cross(record[3][0], core_direction)
                invariant = "parallel-line vector point cross direction"
            candidates = exact = 0
            for push_record in push_group:
                for core_record in buckets.get(key_for_push(push_record), ()):
                    candidates += 1
                    exact += 1
                    if intersects(core_record[3], push_record[3]):
                        raise AssertionError(
                            "stub core/push intersection: "
                            f"{core_record[:3]} / {push_record[:3]}"
                        )
            total_candidates += candidates
            total_exact += exact
            results.append({
                "core_direction": [str(value) for value in core_direction],
                "push_direction": [str(value) for value in push_direction],
                "core_segment_count": len(core_group),
                "push_segment_count": len(push_group),
                "hash_invariant": invariant,
                "exact_hash_candidates": candidates,
                "exact_segment_checks": exact,
                "intersections": 0,
            })
    counts = {
        "/".join(str(value) for value in key): len(records)
        for key, records in sorted(core_classes.items())
    }
    result = {
        "schema": "t73_x_m1_stub_core_push_clearance/v1",
        "stub_r3_push_paths_receipt_sha256": stub_push["sha256"],
        "stub_source_normal_homotopy_sha256": source_homotopy["sha256"],
        "core_segment_count": len(cores),
        "push_segment_count": len(pushes),
        "direction_class_count": len(core_classes),
        "direction_class_segment_counts": counts,
        "direction_pair_count": len(results),
        "direction_pair_results": results,
        "exact_hash_candidate_count": total_candidates,
        "exact_segment_check_count": total_exact,
        "core_push_intersection_count": 0,
        "push_push_clearance": "PASS_BY_COMMON_TRANSLATION_OF_EMBEDDED_STUB_CORES",
        "completion_status": "ALL_STUB_CORE_AND_PUSH_PATHS_GLOBALLY_DISJOINT",
        "verdict": "PASS_X_M1_STUB_CORE_PUSH_CLEARANCE",
    }
    result["sha256"] = canonical_sha256(result)
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
        raise AssertionError("stub core/push clearance is stale")
    print(json.dumps({
        "verdict": result["verdict"],
        "directions": result["direction_class_count"],
        "direction_pairs": result["direction_pair_count"],
        "candidates": result["exact_hash_candidate_count"],
        "checks": result["exact_segment_check_count"],
        "intersections": result["core_push_intersection_count"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
