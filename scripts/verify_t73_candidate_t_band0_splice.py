#!/usr/bin/env python3
"""Check exact self-disjointness of the first candidate t-band splice."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPLICE = ROOT / "geometry/t73_candidate_t_band0_splice.json"


def exact_segment_intersection(first, second) -> bool:
    p, p2 = first
    q, q2 = second
    r = tuple(p2[i] - p[i] for i in range(len(p)))
    s = tuple(q2[i] - q[i] for i in range(len(q)))
    rhs = tuple(q[i] - p[i] for i in range(len(p)))
    for a in range(len(p)):
        for b in range(a + 1, len(p)):
            determinant = r[b] * s[a] - r[a] * s[b]
            if determinant == 0:
                continue
            t = (rhs[b] * s[a] - rhs[a] * s[b]) / determinant
            u = (r[a] * rhs[b] - r[b] * rhs[a]) / determinant
            if not (0 <= t <= 1 and 0 <= u <= 1):
                return False
            left = tuple(p[i] + t * r[i] for i in range(len(p)))
            right = tuple(q[i] + u * s[i] for i in range(len(p)))
            return left == right
    axis = next((i for i, value in enumerate(r) if value), None)
    if axis is None:
        return p == q
    parameter = rhs[axis] / r[axis]
    if any(rhs[i] != parameter * r[i] for i in range(len(p))):
        return False
    q_parameter = parameter
    q2_parameter = q_parameter + (s[axis] / r[axis])
    low, high = sorted((q_parameter, q2_parameter))
    return max(Fraction(0), low) <= min(Fraction(1), high)


def verify() -> dict:
    data = json.loads(SPLICE.read_text(encoding="utf-8"))
    if data["completion_status"] != "CANDIDATE_CLOSED_SPLICE_ONLY":
        raise AssertionError("candidate splice status changed")
    points = [tuple(Fraction(value) for value in point) for point in data["closed_core_polyline_T3xI"]]
    if points[0] != points[-1]:
        raise AssertionError("candidate splice is not closed")
    segments = list(zip(points, points[1:]))
    numeric = np.array([[float(value) for value in point] for point in points])
    lower = np.minimum(numeric[:-1], numeric[1:])
    upper = np.maximum(numeric[:-1], numeric[1:])
    checked = 0
    for left in range(len(segments)):
        for right in range(left + 1, len(segments)):
            if right == left + 1 or (left == 0 and right == len(segments) - 1):
                continue
            if np.any(upper[left] < lower[right]) or np.any(upper[right] < lower[left]):
                continue
            checked += 1
            if exact_segment_intersection(segments[left], segments[right]):
                return {
                    "verdict": "OPEN_PERIODIC_T3_LIFT_REQUIRED",
                    "reason": (
                        "the stored AR core uses wrapped T3 coordinates and cannot "
                        "be tested as an affine Q4 polyline"
                    ),
                    "first_affine_collision": [left, right],
                    "segments": len(segments),
                    "exact_candidate_pairs": checked,
                }
    return {
        "verdict": "PASS_CANDIDATE_CLOSED_CORE_EMBEDDEDNESS_ONLY",
        "segments": len(segments),
        "exact_candidate_pairs": checked,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
