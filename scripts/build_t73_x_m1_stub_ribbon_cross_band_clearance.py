#!/usr/bin/env python3
"""Certify cross-band clearance of all x-m1 stub framing ribbons.

The common push vector is delta*(1,1,2).  We quotient R^3 by this
direction with (p,r)=(x-y,2x-z).  Two swept rectangles can meet only if
their projected core segments meet.  Shapely's STRtree is used only as a
conservative broad phase; every numerically close lift is checked with
Fraction arithmetic, while a stated roundoff bound certifies the rest.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np
from shapely import box
from shapely.strtree import STRtree


ROOT = Path(__file__).resolve().parents[1]
STUBS = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
CORE_PUSH = ROOT / "audit/t73_x_m1_stub_core_push_clearance.json"
LOCAL = ROOT / "audit/t73_x_m1_stub_ribbon_local_clearance.json"
HOMOTOPY = ROOT / "audit/t73_x_m1_stub_source_normal_homotopy.json"
OUTPUT = ROOT / "audit/t73_x_m1_stub_ribbon_cross_band_clearance.json"

BOX_PAD = 2.0**-30
LIFT_THRESHOLD = 2.0**-10
QUOTIENT_ERROR_BOUND = 2.0**-46
LIFT_ERROR_BOUND = 2.0**-40


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def point(values):
    return tuple(Fraction(value) for value in values)


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def normalized_direction(a, b):
    delta = subtract(b, a)
    if not delta[0]:
        raise AssertionError("stub segment has zero x displacement")
    return tuple(value / delta[0] for value in delta)


def quotient(a):
    return a[0] - a[1], 2 * a[0] - a[2]


def projected_direction(direction):
    return 1 - direction[1], 2 - direction[2]


def cross2(first, second):
    return first[0] * second[1] - first[1] * second[0]


def in_closed_interval(value, endpoint):
    return min(Fraction(0), endpoint) <= value <= max(Fraction(0), endpoint)


def interpolate_lift(segment, q_axis, q_value):
    q0 = quotient(segment["a"])[q_axis]
    q1 = quotient(segment["b"])[q_axis]
    return segment["a"][0] + (q_value - q0) * (
        segment["b"][0] - segment["a"][0]
    ) / (q1 - q0)


def parallel_exact_check(first, second, delta):
    u = projected_direction(first["direction"])
    q_axis = 0 if u[0] else 1
    first_q = [quotient(first[key])[q_axis] for key in ("a", "b")]
    second_q = [quotient(second[key])[q_axis] for key in ("a", "b")]
    lo = max(min(first_q), min(second_q))
    hi = min(max(first_q), max(second_q))
    if lo > hi:
        return False, None
    differences = [
        interpolate_lift(first, q_axis, value)
        - interpolate_lift(second, q_axis, value)
        for value in (lo, hi)
    ]
    minimum = Fraction(0) if differences[0] * differences[1] <= 0 else min(
        abs(differences[0]), abs(differences[1])
    )
    return minimum <= delta, minimum


def nonparallel_exact_check(first, second, delta):
    qa, qb = quotient(first["a"]), quotient(second["a"])
    u = projected_direction(first["direction"])
    v = projected_direction(second["direction"])
    denominator = cross2(u, v)
    offset = (qb[0] - qa[0], qb[1] - qa[1])
    alpha = cross2(offset, v) / denominator
    beta = cross2(offset, u) / denominator
    if not in_closed_interval(alpha, first["b"][0] - first["a"][0]):
        return False, None
    if not in_closed_interval(beta, second["b"][0] - second["a"][0]):
        return False, None
    lift_gap = abs((first["a"][0] + alpha) - (second["a"][0] + beta))
    return lift_gap <= delta, lift_gap


def load_segments(receipt):
    segments = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        header = json.loads(source.readline())
        if header["push_displacement"] != receipt["push_displacement"]:
            raise AssertionError("stub cache/receipt displacement mismatch")
        for line in source:
            record = json.loads(line)
            for name, stub in sorted(record["stubs"].items()):
                vertices = [point(value) for value in stub["core_vertices"]]
                for index, (a, b) in enumerate(zip(vertices, vertices[1:])):
                    segments.append({
                        "band": record["band_index"],
                        "name": name,
                        "index": index,
                        "a": a,
                        "b": b,
                        "direction": normalized_direction(a, b),
                    })
    return segments


def identity(segment):
    return [segment["band"], segment["name"], segment["index"]]


def pair_hash(pairs, segments):
    return canonical_sha256([
        [identity(segments[first]), identity(segments[second])]
        for first, second in sorted(pairs)
    ])


def build():
    stubs = json.loads(STUBS.read_text())
    core_push = json.loads(CORE_PUSH.read_text())
    local = json.loads(LOCAL.read_text())
    homotopy = json.loads(HOMOTOPY.read_text())
    if core_push["stub_r3_push_paths_receipt_sha256"] != stubs["sha256"]:
        raise AssertionError("core/push receipt does not bind stub paths")
    if local["stub_r3_push_paths_receipt_sha256"] != stubs["sha256"]:
        raise AssertionError("local ribbon receipt does not bind stub paths")
    if core_push["stub_source_normal_homotopy_sha256"] != homotopy["sha256"]:
        raise AssertionError("core/push receipt does not bind normal homotopy")

    displacement = tuple(Fraction(value) for value in stubs["push_displacement"])
    delta = displacement[0]
    if displacement != (delta, delta, 2 * delta) or not (0 < delta < Fraction(1, 2**1024)):
        raise AssertionError("unexpected stub ribbon displacement")
    segments = load_segments(stubs)
    if len(segments) != 10582:
        raise AssertionError("stub segment count changed")
    coordinate_bound = max(abs(value) for segment in segments for key in ("a", "b") for value in segment[key])
    if coordinate_bound > 8:
        raise AssertionError("the documented binary64 error bound requires |coordinate| <= 8")

    directions = Counter(segment["direction"] for segment in segments)
    expected_directions = {
        (Fraction(1), Fraction(-1), Fraction(-1)): 2,
        (Fraction(1), Fraction(-1), Fraction(1)): 3778,
        (Fraction(1), Fraction(1), Fraction(-1)): 3024,
        (Fraction(1), Fraction(1), Fraction(1)): 3778,
    }
    if directions != expected_directions:
        raise AssertionError("stub direction classes changed")

    # Exact treatment of parallel projected segments.  Equality of the exact
    # line invariant is necessary, so only tiny buckets reach interval tests.
    line_buckets = defaultdict(list)
    for index, segment in enumerate(segments):
        p, r = quotient(segment["a"])
        dp, dr = projected_direction(segment["direction"])
        key = ("vertical", p) if not dp else ("slope", dr / dp, r - (dr / dp) * p)
        line_buckets[key].append(index)
    parallel_pairs = []
    parallel_minimum = None
    for bucket in line_buckets.values():
        for offset, first in enumerate(bucket):
            for second in bucket[:offset]:
                if segments[first]["band"] == segments[second]["band"]:
                    continue
                intersects, gap = parallel_exact_check(segments[first], segments[second], delta)
                parallel_pairs.append((min(first, second), max(first, second)))
                if gap is not None:
                    parallel_minimum = gap if parallel_minimum is None else min(parallel_minimum, gap)
                if intersects:
                    raise AssertionError(f"cross-band parallel ribbons intersect: {identity(segments[first])} / {identity(segments[second])}")

    # Conservative binary64 broad phase.  With exact coordinates bounded by
    # 8, each quotient coordinate error is <2^-46.  BOX_PAD=2^-30 therefore
    # guarantees that every exact projected intersection is returned.
    projected = np.asarray([
        [float(value) for key in ("a", "b") for value in quotient(segment[key])]
        for segment in segments
    ], dtype=np.float64)
    bounds = np.column_stack((
        np.minimum(projected[:, 0], projected[:, 2]) - BOX_PAD,
        np.minimum(projected[:, 1], projected[:, 3]) - BOX_PAD,
        np.maximum(projected[:, 0], projected[:, 2]) + BOX_PAD,
        np.maximum(projected[:, 1], projected[:, 3]) + BOX_PAD,
    ))
    boxes = box(bounds[:, 0], bounds[:, 1], bounds[:, 2], bounds[:, 3])
    queried = STRtree(boxes).query(boxes)
    first, second = queried[0], queried[1]
    mask = first < second
    first, second = first[mask], second[mask]
    bands = np.asarray([segment["band"] for segment in segments])
    mask = bands[first] != bands[second]
    first, second = first[mask], second[mask]

    direction_codes = np.asarray([
        tuple(int(value) for value in segment["direction"]) for segment in segments
    ])
    quotient_directions = np.column_stack((1 - direction_codes[:, 1], 2 - direction_codes[:, 2]))
    determinants = (
        quotient_directions[first, 0] * quotient_directions[second, 1]
        - quotient_directions[first, 1] * quotient_directions[second, 0]
    )
    mask = determinants != 0
    first, second, determinants = first[mask], second[mask], determinants[mask].astype(np.float64)
    nonparallel_bbox_count = len(first)

    # Infinite-line intersection lift gap.  If the projected finite segments
    # actually meet, this is their only possible quotient point.  The formula
    # uses only bounded additions/multiplications and division by |det|>=2;
    # its absolute binary64 error is conservatively <2^-40.
    pa, ra, pb, rb = projected[first, 0], projected[first, 1], projected[second, 0], projected[second, 1]
    up, ur = quotient_directions[first, 0], quotient_directions[first, 1]
    vp, vr = quotient_directions[second, 0], quotient_directions[second, 1]
    wp, wr = pb - pa, rb - ra
    alpha = (wp * vr - wr * vp) / determinants
    beta = (wp * ur - wr * up) / determinants
    x0 = np.asarray([float(segment["a"][0]) for segment in segments])
    intersection_p = pa + alpha * up
    intersection_r = ra + alpha * ur
    finite_mask = (
        (intersection_p >= bounds[first, 0])
        & (intersection_p <= bounds[first, 2])
        & (intersection_r >= bounds[first, 1])
        & (intersection_r <= bounds[first, 3])
        & (intersection_p >= bounds[second, 0])
        & (intersection_p <= bounds[second, 2])
        & (intersection_r >= bounds[second, 1])
        & (intersection_r <= bounds[second, 3])
    )
    approximate_gap = np.abs((x0[first] + alpha) - (x0[second] + beta))
    near_mask = finite_mask & (approximate_gap <= LIFT_THRESHOLD)
    near_pairs = list(zip(first[near_mask].tolist(), second[near_mask].tolist()))

    exact_projected_intersections = 0
    exact_minimum = None
    exact_minimum_pair = None
    for first_index, second_index in near_pairs:
        intersects, gap = nonparallel_exact_check(
            segments[first_index], segments[second_index], delta
        )
        if gap is None:
            continue
        exact_projected_intersections += 1
        if exact_minimum is None or gap < exact_minimum:
            exact_minimum = gap
            exact_minimum_pair = [identity(segments[first_index]), identity(segments[second_index])]
        if intersects:
            raise AssertionError(
                f"cross-band nonparallel ribbons intersect: {identity(segments[first_index])} / {identity(segments[second_index])}"
            )
    if LIFT_THRESHOLD - LIFT_ERROR_BOUND <= float(delta):
        raise AssertionError("far-candidate error margin does not dominate ribbon width")

    result = {
        "schema": "t73_x_m1_stub_ribbon_cross_band_clearance/v1",
        "stub_r3_push_paths_receipt_sha256": stubs["sha256"],
        "stub_core_push_clearance_sha256": core_push["sha256"],
        "stub_ribbon_local_clearance_sha256": local["sha256"],
        "stub_source_normal_homotopy_sha256": homotopy["sha256"],
        "segment_count": len(segments),
        "ribbon_count": stubs["ribbon_triangle_count"] // 2,
        "direction_class_counts": {
            "/".join(str(value) for value in key): value for key, value in sorted(directions.items())
        },
        "quotient_map": ["p=x-y", "r=2*x-z"],
        "common_push_direction": [1, 1, 2],
        "coordinate_absolute_bound": str(coordinate_bound),
        "binary64_quotient_error_bound": "2^-46",
        "binary64_lift_error_bound": "2^-40",
        "broad_phase_box_padding": "2^-30",
        "near_lift_threshold": "2^-10",
        "exact_parallel_line_bucket_count": len(line_buckets),
        "exact_parallel_cross_band_candidate_count": len(parallel_pairs),
        "exact_parallel_candidate_sha256": pair_hash(parallel_pairs, segments),
        "exact_parallel_minimum_lift_gap": str(parallel_minimum),
        "expanded_bbox_nonparallel_cross_band_candidate_count": nonparallel_bbox_count,
        "expanded_finite_segment_nonparallel_candidate_count": int(np.count_nonzero(finite_mask)),
        "near_nonparallel_exact_candidate_count": len(near_pairs),
        "near_nonparallel_exact_candidate_sha256": pair_hash(near_pairs, segments),
        "near_nonparallel_projected_intersection_count": exact_projected_intersections,
        "exact_nonparallel_minimum_lift_gap": str(exact_minimum),
        "exact_nonparallel_minimum_pair": exact_minimum_pair,
        "ribbon_width_delta": str(delta),
        "intersection_count": 0,
        "cross_band_stub_ribbon_clearance": True,
        "global_stub_ribbon_embedding": True,
        "completion_status": "ALL_X_M1_STUB_FRAMING_RIBBONS_GLOBALLY_DISJOINT",
        "verdict": "PASS_X_M1_STUB_RIBBON_CROSS_BAND_CLEARANCE",
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
        raise AssertionError("stub cross-band ribbon clearance is stale")
    print(json.dumps({
        "verdict": result["verdict"],
        "parallel_exact": result["exact_parallel_cross_band_candidate_count"],
        "nonparallel_bbox": result["expanded_bbox_nonparallel_cross_band_candidate_count"],
        "nonparallel_exact": result["near_nonparallel_exact_candidate_count"],
        "minimum_gap": result["exact_nonparallel_minimum_lift_gap"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
