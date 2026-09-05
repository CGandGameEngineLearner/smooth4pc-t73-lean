#!/usr/bin/env python3
"""Verify the cached 1.76M-crossing source-native PD and its compact receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "audit/t73_actual_source_standard_pd_sqlite_receipt.json"
PROJECTION_RECEIPT = ROOT / "audit/t73_actual_source_connector_projection_receipt.json"
PROVENANCE = ROOT / "geometry/t73_reduced_source_connector_provenance.json"
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
SLOTS = ROOT / "geometry/t73_foot_to_dotted_slot_map.json"
BUILDER = ROOT / "scripts/build_t73_actual_source_standard_pd_sqlite.py"
COVERAGE_GAP = ROOT / "audit/t73_source_pd_post_x_coverage_gap.json"
COMPONENT_ORDER = ["m_2", "m_3", "r_xy", "r_yz", "r_zx", "dotted_y", "dotted_z"]


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def check_receipt():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    projection = json.loads(PROJECTION_RECEIPT.read_text(encoding="utf-8"))
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    slots = json.loads(SLOTS.read_text(encoding="utf-8"))
    coverage = json.loads(COVERAGE_GAP.read_text(encoding="utf-8"))
    checks = {
        "projection": receipt["source_projection_receipt_sha256"] == projection["sha256"],
        "provenance": receipt["connector_provenance_sha256"] == provenance["sha256"],
        "cycles": receipt["component_cycles_sha256"] == cycles["sha256"],
        "slots": receipt["dotted_slot_map_sha256"] == slots["sha256"],
        "builder": receipt["builder_sha256"] == file_sha(BUILDER),
        "counts": receipt["source_crossings"] == 1758060
        and receipt["dotted_crossings"] == 3570
        and receipt["crossing_count"] == 1761630
        and receipt["arc_label_count"] == 3523260,
        "verdict": receipt["verdict"] == "PASS_ACTUAL_SOURCE_STANDARD_PD_CORE_ONLY",
        "post_x_coverage": coverage["source_standard_pd_receipt_sha256"] == receipt["sha256"]
        and coverage["omitted_replacement_core_segment_count"] == 57494
        and coverage["prior_complete_source_native_pd_claim"] == "REFUTED_BY_EXPLICIT_POST_X_PATH_COVERAGE",
    }
    if not all(checks.values()):
        raise AssertionError(f"actual source PD receipt failed: {checks}")
    return receipt, checks


def database_linking(connection):
    matrix = [[0 for _ in COMPONENT_ORDER] for _ in COMPONENT_ORDER]
    for first_index, first in enumerate(COMPONENT_ORDER):
        for second_index in range(first_index + 1, len(COMPONENT_ORDER)):
            second = COMPONENT_ORDER[second_index]
            signed_sum = connection.execute(
                "SELECT COALESCE(SUM(sign),0) FROM crossings WHERE "
                "(over_owner=? AND under_owner=?) OR (over_owner=? AND under_owner=?)",
                (first, second, second, first),
            ).fetchone()[0]
            if signed_sum % 2:
                raise AssertionError("cached source PD has an odd mixed crossing sum")
            matrix[first_index][second_index] = signed_sum // 2
            matrix[second_index][first_index] = signed_sum // 2
    return matrix


def verify_full(check_database_sha=False):
    receipt, fast_checks = check_receipt()
    database = Path(receipt["database_path"])
    if not database.is_file():
        raise FileNotFoundError(database)
    if check_database_sha and file_sha(database) != receipt["database_sha256"]:
        raise AssertionError("cached source PD database SHA changed")
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise AssertionError("cached source PD SQLite integrity check failed")
    counts = {
        table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in ("crossings", "occurrences", "pd_rows", "component_summary")
    }
    if counts != {
        "crossings": 1761630,
        "occurrences": 3523260,
        "pd_rows": 1761630,
        "component_summary": 7,
    }:
        raise AssertionError("cached source PD table counts changed")
    kind_counts = dict(
        connection.execute(
            "SELECT kind,COUNT(*) FROM crossings GROUP BY kind ORDER BY kind"
        )
    )
    if kind_counts != {
        "actual_foot_dotted_hopf": 3570,
        "actual_source_connector": 1758060,
    }:
        raise AssertionError("cached source PD crossing provenance changed")
    bad_labels = connection.execute(
        """
        SELECT label,COUNT(*) FROM (
          SELECT a AS label FROM pd_rows UNION ALL
          SELECT b FROM pd_rows UNION ALL
          SELECT c FROM pd_rows UNION ALL
          SELECT d FROM pd_rows
        ) GROUP BY label HAVING COUNT(*)<>2 LIMIT 1
        """
    ).fetchone()
    if bad_labels is not None:
        raise AssertionError(f"cached PD arc incidence failed at {bad_labels}")
    summaries = list(
        connection.execute(
            "SELECT component,event_count FROM component_summary ORDER BY first_arc"
        )
    )
    if [component for component, _ in summaries] != COMPONENT_ORDER or sum(
        count for _, count in summaries
    ) != 3523260:
        raise AssertionError("cached source PD component cycles changed")
    linking = database_linking(connection)
    connection.close()
    if linking != receipt["pairwise_linking_matrix"]:
        raise AssertionError("cached source PD linking matrix changed")
    return {
        "verdict": "PASS_ACTUAL_SOURCE_STANDARD_PD_SQLITE_FULL",
        "fast_checks": fast_checks,
        "table_counts": counts,
        "crossing_kind_counts": kind_counts,
        "arc_incidence": "EVERY_LABEL_TWICE",
        "component_event_counts": dict(summaries),
        "pairwise_linking_matrix": linking,
        "database_sha_checked": check_database_sha,
        "framing_status": receipt["framing_status"],
        "coverage_status": "PARTIAL_CONNECTOR_PLUS_LOCAL_HOPF_SKELETON",
        "omitted_post_x_core_segments": 57494,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--check-database-sha", action="store_true")
    args = parser.parse_args()
    if args.full:
        result = verify_full(args.check_database_sha)
    else:
        receipt, checks = check_receipt()
        result = {
            "verdict": "PASS_ACTUAL_SOURCE_STANDARD_PD_RECEIPT",
            "checks": checks,
            "crossings": receipt["crossing_count"],
            "framing_status": receipt["framing_status"],
            "coverage_status": "PARTIAL_CONNECTOR_PLUS_LOCAL_HOPF_SKELETON",
            "omitted_post_x_core_segments": 57494,
        }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
