#!/usr/bin/env python3
"""Full verifier for the global x-m1 stub ribbon clearance certificate."""

from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts/build_t73_x_m1_stub_ribbon_cross_band_clearance.py"
ARTIFACT = ROOT / "audit/t73_x_m1_stub_ribbon_cross_band_clearance.json"


def load_builder():
    spec = importlib.util.spec_from_file_location("stub_ribbon_cross_builder", BUILDER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(path=ARTIFACT):
    saved = json.loads(path.read_text())
    rebuilt = load_builder().build()
    if saved != rebuilt:
        raise AssertionError("cross-band stub ribbon certificate is stale")
    delta = Fraction(saved["ribbon_width_delta"])
    parallel_gap = Fraction(saved["exact_parallel_minimum_lift_gap"])
    nonparallel_gap = Fraction(saved["exact_nonparallel_minimum_lift_gap"])
    if min(parallel_gap, nonparallel_gap) <= delta:
        raise AssertionError("global stub ribbon clearance margin is nonpositive")
    if saved["intersection_count"] != 0 or not saved["global_stub_ribbon_embedding"]:
        raise AssertionError("global stub ribbon result is not closed")
    if saved["verdict"] != "PASS_X_M1_STUB_RIBBON_CROSS_BAND_CLEARANCE":
        raise AssertionError("unexpected global stub ribbon verdict")
    return {
        "verdict": saved["verdict"],
        "segments": saved["segment_count"],
        "ribbons": saved["ribbon_count"],
        "parallel_exact_candidates": saved["exact_parallel_cross_band_candidate_count"],
        "nonparallel_exact_candidates": saved["near_nonparallel_exact_candidate_count"],
        "minimum_clearance_in_ribbon_widths": str(min(parallel_gap, nonparallel_gap) / delta),
        "sha256": saved["sha256"],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
