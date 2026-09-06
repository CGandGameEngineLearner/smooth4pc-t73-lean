#!/usr/bin/env python3
"""Independently verify the exact z-plane transition/middle separation."""

from __future__ import annotations

import json
from pathlib import Path

from build_t73_x_m1_repaired_transition_middle_clearance import OUTPUT, build


def verify():
    saved = json.loads(OUTPUT.read_text())
    replayed = build()
    if saved != replayed:
        raise AssertionError("transition-middle clearance artifact is stale")
    if saved["middle_plane"] != "z=0":
        raise AssertionError("middle plane changed")
    if saved["transition_middle_endpoint_match_count"] != 3026:
        raise AssertionError("transition-middle endpoint count changed")
    if saved["extra_transition_middle_intersections"] != 0:
        raise AssertionError("transition-middle extras are nonzero")
    return {
        "verdict": "PASS_X_M1_REPAIRED_TRANSITION_MIDDLE_CLEARANCE",
        "middle_core_segments": saved["middle_core_segment_count"],
        "transition_middle_endpoint_matches": saved["transition_middle_endpoint_match_count"],
        "extra_intersections": 0,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
