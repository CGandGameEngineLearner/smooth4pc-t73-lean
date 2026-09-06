#!/usr/bin/env python3
"""Verify the saved exact direction-class stub core/push clearance."""

from __future__ import annotations

import json

from build_t73_x_m1_stub_core_push_clearance import OUTPUT, build


def verify():
    saved = json.loads(OUTPUT.read_text())
    replayed = build()
    if saved != replayed:
        raise AssertionError("stub core/push clearance artifact is stale")
    if saved["direction_class_count"] != 4 or saved["direction_pair_count"] != 16:
        raise AssertionError("stub direction-pair coverage changed")
    if saved["exact_hash_candidate_count"] != 1582:
        raise AssertionError("stub exact hash candidate count changed")
    if saved["core_push_intersection_count"] != 0:
        raise AssertionError("stub core/push intersections are nonzero")
    if any(record["intersections"] != 0 for record in saved["direction_pair_results"]):
        raise AssertionError("a stub direction pair contains an intersection")
    return {
        "verdict": "PASS_X_M1_STUB_CORE_PUSH_CLEARANCE",
        "core_segments": saved["core_segment_count"],
        "push_segments": saved["push_segment_count"],
        "direction_pairs": saved["direction_pair_count"],
        "exact_segment_checks": saved["exact_segment_check_count"],
        "intersections": 0,
        "stub_ribbon_clearance": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
