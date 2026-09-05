#!/usr/bin/env python3
"""Independently verify the post-x path coverage gap in the current source PD."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_source_pd_post_x_coverage_gap.json"
POST_X = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
PROJECTION = ROOT / "audit/t73_actual_source_connector_projection_receipt.json"
PD = ROOT / "audit/t73_actual_source_standard_pd_sqlite_receipt.json"


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def verify():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    post_x = json.loads(POST_X.read_text(encoding="utf-8"))
    projection = json.loads(PROJECTION.read_text(encoding="utf-8"))
    pd = json.loads(PD.read_text(encoding="utf-8"))
    if data["sha256"] != canonical_sha({key: value for key, value in data.items() if key != "sha256"}):
        raise AssertionError("coverage-gap payload SHA changed")
    if (data["post_x_framed_replacement_cells_receipt_sha256"] != post_x["sha256"]
            or data["source_connector_projection_receipt_sha256"] != projection["sha256"]
            or data["source_standard_pd_receipt_sha256"] != pd["sha256"]):
        raise AssertionError("coverage-gap sources changed")
    segments_per_cell = 2 + 34 + 2
    expected = {component: count * segments_per_cell for component, count in post_x["component_counts"].items()}
    if expected != {"m_2": 10222, "m_3": 47120, "r_xy": 76, "r_zx": 76}:
        raise AssertionError("post-x replacement segment inventory changed")
    if (data["omitted_replacement_core_segments_by_component"] != expected
            or data["omitted_replacement_core_segment_count"] != 57494
            or data["omitted_replacement_push_segment_count"] != 57494):
        raise AssertionError("coverage-gap counts changed")
    forbidden = {"x_band_hybrid_movie_sha256", "post_x_framed_replacement_cells_receipt_sha256"}
    if forbidden & set(projection) or forbidden & set(pd):
        raise AssertionError("source projection/PD now binds post-x cells; coverage audit must be replaced")
    if data["prior_complete_source_native_pd_claim"] != "REFUTED_BY_EXPLICIT_POST_X_PATH_COVERAGE":
        raise AssertionError("coverage-gap verdict changed")
    return {
        "verdict": "PASS_SOURCE_PD_POST_X_COVERAGE_GAP_AUDIT",
        "post_x_cells": 1513,
        "omitted_core_segments": 57494,
        "omitted_push_segments": 57494,
        "current_pd_crossings": pd["crossing_count"],
        "repair_status": "OPEN_PROJECT_FULL_REPLACEMENT_PATHS",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
