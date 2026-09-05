#!/usr/bin/env python3
"""Quantify post-x framed paths omitted by the current source PD projection."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POST_X = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
PROJECTION = ROOT / "audit/t73_actual_source_connector_projection_receipt.json"
PD = ROOT / "audit/t73_actual_source_standard_pd_sqlite_receipt.json"
OUTPUT = ROOT / "audit/t73_source_pd_post_x_coverage_gap.json"


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def build():
    post_x = json.loads(POST_X.read_text(encoding="utf-8"))
    projection = json.loads(PROJECTION.read_text(encoding="utf-8"))
    pd = json.loads(PD.read_text(encoding="utf-8"))
    segments_per_cell = (3 - 1) + (35 - 1) + (3 - 1)
    missing = {component: count * segments_per_cell for component, count in post_x["component_counts"].items()}
    result = {
        "schema": "t73_source_pd_post_x_coverage_gap/v1",
        "post_x_framed_replacement_cells_receipt_sha256": post_x["sha256"],
        "source_connector_projection_receipt_sha256": projection["sha256"],
        "source_standard_pd_receipt_sha256": pd["sha256"],
        "projected_connector_segments": projection["segment_count"],
        "projected_local_hopf_events": pd["dotted_crossings"],
        "post_x_replacement_cell_count": post_x["framed_replacement_cell_count"],
        "replacement_core_segments_per_cell": segments_per_cell,
        "omitted_replacement_core_segments_by_component": missing,
        "omitted_replacement_core_segment_count": sum(missing.values()),
        "omitted_replacement_push_segment_count": sum(missing.values()),
        "source_projection_binds_post_x_cells": False,
        "source_pd_binds_post_x_cells": False,
        "prior_complete_source_native_pd_claim": "REFUTED_BY_EXPLICIT_POST_X_PATH_COVERAGE",
        "current_pd_scope": "JOHNSON_CENTRAL_CONNECTORS_PLUS_ABSTRACT_LOCAL_HOPF_EVENTS_ONLY",
        "completion_status": "SOURCE_PD_POST_X_REPLACEMENT_COVERAGE_GAP_CONFIRMED",
        "required_repair": "project the 57494 replacement core segments and their pushes in one dotted-S3 chart, including splice crossings, then rebuild PD and framings",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true"); parser.add_argument("--check", action="store_true")
    args = parser.parse_args(); result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("source-PD post-x coverage audit is stale")
    print(json.dumps({"status": result["completion_status"], "omitted_core_segments": result["omitted_replacement_core_segment_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()
