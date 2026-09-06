#!/usr/bin/env python3
"""Exact global core/push segment clearance for straight outer collars."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
from pathlib import Path

from gmpy2 import mpq
from rtree import index as rtree_index

ROOT = Path(__file__).resolve().parents[1]
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_receipt.json"
LOCAL_VERIFY = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_verification.json"
OUTPUT = ROOT / "audit/t73_x_m1_outer_collar_core_push_clearance.json"


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
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
    return tuple(mpq(coordinate) for coordinate in value)


def subtract(first, second):
    return tuple(a - b for a, b in zip(first, second))


def cross(first, second):
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def segment_intersects(first, second):
    a, b = first
    c, d = second
    u, v, w = subtract(b, a), subtract(d, c), subtract(c, a)
    for first_axis, second_axis in ((0, 1), (0, 2), (1, 2)):
        denominator = u[first_axis] * (-v[second_axis]) - u[second_axis] * (
            -v[first_axis]
        )
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
    if cross(u, w) != (mpq(0), mpq(0), mpq(0)):
        return False
    axis = next(index for index, value in enumerate(u) if value)
    return max(min(a[axis], b[axis]), min(c[axis], d[axis])) <= min(
        max(a[axis], b[axis]), max(c[axis], d[axis])
    )


def exact_bounds(segment):
    return tuple(min(segment[0][axis], segment[1][axis]) for axis in range(3)), tuple(
        max(segment[0][axis], segment[1][axis]) for axis in range(3)
    )


def float_bounds(bounds):
    return tuple(
        math.nextafter(float(value), -math.inf) for value in bounds[0]
    ) + tuple(math.nextafter(float(value), math.inf) for value in bounds[1])


def overlap(first, second):
    return all(
        first[0][axis] <= second[1][axis] and second[0][axis] <= first[1][axis]
        for axis in range(3)
    )


def load(receipt):
    records = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            value = json.loads(line)
            records.append(
                {
                    "interface": value["interface_index"],
                    "neighbor_id": value["neighbor_id"],
                    "core": tuple(
                        point(vertex) for vertex in value["final_core_vertices"]
                    ),
                    "push": tuple(
                        point(vertex) for vertex in value["final_push_vertices"]
                    ),
                }
            )
    return records


def allowed_incidence(first, second, kind):
    first_segment, second_segment = first[kind], second[kind]
    shared = set(first_segment) & set(second_segment)
    return (
        bool(shared)
        and first["neighbor_id"] == second["neighbor_id"]
        and first_segment[0] == second_segment[0]
    )


def compare(first_records, first_kind, second_records, second_kind, symmetric):
    second_segments = [record[second_kind] for record in second_records]
    second_bounds = [exact_bounds(segment) for segment in second_segments]
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        (
            (index, float_bounds(bounds), None)
            for index, bounds in enumerate(second_bounds)
        ),
        properties=properties,
    )
    broad = bounds_rejects = incidences = exact = 0
    for first_index, first_record in enumerate(first_records):
        segment = first_record[first_kind]
        segment_bounds = exact_bounds(segment)
        for second_index in tree.intersection(float_bounds(segment_bounds)):
            if symmetric and second_index >= first_index:
                continue
            broad += 1
            if not overlap(segment_bounds, second_bounds[second_index]):
                bounds_rejects += 1
                continue
            second_record = second_records[second_index]
            if first_kind == second_kind and allowed_incidence(
                first_record, second_record, first_kind
            ):
                incidences += 1
                continue
            exact += 1
            if segment_intersects(segment, second_record[second_kind]):
                return {
                    "status": "REFUTED",
                    "first_interface": first_record["interface"],
                    "second_interface": second_record["interface"],
                    "broad_candidates_before_collision": broad,
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
        raise AssertionError("outer collar local verification is stale")
    records = load(collars)
    results = {
        "core/core": compare(records, "core", records, "core", True),
        "push/push": compare(records, "push", records, "push", True),
        "core/push": compare(records, "core", records, "push", False),
    }
    failing = [pair for pair, result in results.items() if result["status"] != "PASS"]
    result = {
        "schema": "t73_x_m1_outer_collar_core_push_clearance/v1",
        "outer_collars_receipt_sha256": collars["sha256"],
        "outer_collars_local_verification_sha256": local["sha256"],
        "collar_count": len(records),
        "pair_results": results,
        "failing_pairs": failing,
        "global_core_push_clearance": not failing,
        "classification": "ACTUAL_CORE_PUSH_PATHS"
        if not failing
        else "CANDIDATE_REFUTED",
        "verdict": "PASS_X_M1_OUTER_COLLAR_CORE_PUSH_CLEARANCE"
        if not failing
        else "REFUTED_X_M1_OUTER_COLLAR_CORE_PUSH_CLEARANCE",
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
        raise AssertionError("outer collar core/push clearance is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "failing_pairs": result["failing_pairs"],
                "results": result["pair_results"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
