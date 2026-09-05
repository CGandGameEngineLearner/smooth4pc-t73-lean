#!/usr/bin/env python3
"""Verify the actual connector/product-push SQLite projection and receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from fractions import Fraction
from pathlib import Path

from export_t73_full_handle_diagram import add_scaled, det2, dot, projected_intersection, projection, sub

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "audit/t73_actual_source_connector_push_projection_receipt.json"
BUILDER = ROOT / "scripts/build_t73_actual_source_connector_push_projection.py"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
PROVENANCE = ROOT / "geometry/t73_reduced_source_connector_provenance.json"
PD_RECEIPT = ROOT / "audit/t73_actual_source_standard_pd_sqlite_receipt.json"

sys.set_int_max_str_digits(0)


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def cache_path(value):
    path = Path(value)
    if path.is_file() or len(value) < 3 or value[1:3] not in (":\\", ":/"):
        return path
    # Permit a Windows-generated receipt to be verified from WSL.
    return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")


def source_segments(spine, provenance, component):
    index = {"m_2": 1, "m_3": 2}[component]
    connectors = {item["connector_id"]: item for item in spine["central_connectors"]}
    edge_by_id = {
        cell["raw_cell_id"]: edge_index
        for group in provenance["components"] if group["component"] == component
        for edge_index, edge in enumerate(group["reduced_edges"])
        for cell in edge["raw_connector_cells"] if cell["kind"] == "actual_johnson_central_connector"
    }
    result = {}
    for connector_id in spine["components"][index]["connector_ids"]:
        vertices = [point(value) for value in connectors[connector_id]["polyline"]]
        for local, (start, end) in enumerate(zip(vertices, vertices[1:])):
            result[(connector_id, local)] = (start, end, 5 * edge_by_id[connector_id] + 1 + local)
    return result


def current_sources():
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    pd_receipt = json.loads(PD_RECEIPT.read_text(encoding="utf-8"))
    hashes = {
        "johnson_spine_embedding_sha256": spine["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "reduced_source_connector_provenance_sha256": provenance["sha256"],
        "actual_source_standard_pd_receipt_sha256": pd_receipt["sha256"],
    }
    return spine, ar_link, provenance, hashes


def check_receipt():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    _, _, _, hashes = current_sources()
    summaries = receipt["component_summaries"]
    checks = {
        "payload": receipt["sha256"] == canonical_sha({key: value for key, value in receipt.items() if key != "sha256"}),
        "builder": receipt["builder_sha256"] == file_sha(BUILDER),
        "sources": receipt["sources"] == hashes,
        "counts": receipt["crossing_count"] == 2528401
        and receipt["broad_candidate_count"] == 6936192
        and summaries["m_2"]["crossings"] == 101683
        and summaries["m_3"]["crossings"] == 2426718,
        "signed_sums": summaries["m_2"]["signed_sum"] == -345
        and summaries["m_2"]["parity"] == "odd"
        and summaries["m_3"]["signed_sum"] == -1206
        and summaries["m_3"]["parity"] == "even",
        "scope": receipt["verdict"] == "PASS_ACTUAL_SOURCE_CONNECTOR_PRODUCT_PUSH_PROJECTION_ONLY",
    }
    if not all(checks.values()):
        raise AssertionError(f"connector-push receipt failed: {checks}")
    return receipt, checks


def verify_full(check_database_sha=False):
    receipt, fast_checks = check_receipt()
    database = cache_path(receipt["database_path"])
    if not database.is_file() or database.stat().st_size != receipt["database_size"]:
        raise AssertionError("connector-push database missing or size changed")
    if check_database_sha and file_sha(database) != receipt["database_sha256"]:
        raise AssertionError("connector-push database SHA changed")
    spine, ar_link, provenance, _ = current_sources()
    segments = {component: source_segments(spine, provenance, component) for component in ("m_2", "m_3")}
    widths = {component: Fraction(ar_link["components"][component]["full_framing_annulus"]["width"]) for component in ("m_2", "m_3")}
    denominator = receipt["projection_denominator"]
    basis = [(Fraction(1), Fraction(0), Fraction(1, denominator)),
             (Fraction(0), Fraction(1), Fraction(1, denominator**2))]
    height = (Fraction(-1, denominator), Fraction(-1, denominator**2), Fraction(1))
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise AssertionError("connector-push SQLite integrity check failed")
    if connection.execute("SELECT COUNT(*),MIN(id),MAX(id) FROM crossings").fetchone() != (2528401, 0, 2528400):
        raise AssertionError("connector-push row ids/count changed")
    counts = {"m_2": 0, "m_3": 0}; sums = {"m_2": 0, "m_3": 0}; core_over = {"m_2": 0, "m_3": 0}
    query = "SELECT id,component,core_connector,core_local_segment,core_pd_segment,push_connector,push_local_segment,push_pd_segment,projection_point_sha256,over_role,sign FROM crossings ORDER BY id"
    for row in connection.execute(query):
        row_id, component, core_id, core_local, core_pd, push_id, push_local, push_pd, stored_point_sha, stored_over, stored_sign = row
        core_start, core_end, expected_core_pd = segments[component][(core_id, core_local)]
        push_base_start, push_base_end, expected_push_pd = segments[component][(push_id, push_local)]
        width = widths[component]; vector = (width, width, width)
        push_start = tuple(push_base_start[axis] + vector[axis] for axis in range(3))
        push_end = tuple(push_base_end[axis] + vector[axis] for axis in range(3))
        if core_pd != expected_core_pd or push_pd != expected_push_pd:
            raise AssertionError(f"PD segment provenance changed at row {row_id}")
        hit = projected_intersection(core_start, core_end, push_start, push_end, basis, f"verify:{row_id}")
        if hit is None:
            raise AssertionError(f"stored non-crossing segment pair at row {row_id}")
        core_parameter, push_parameter, projected_point = hit
        if canonical_sha([str(projected_point[0]), str(projected_point[1])]) != stored_point_sha:
            raise AssertionError(f"projection point changed at row {row_id}")
        core_point = add_scaled(core_start, sub(core_end, core_start), core_parameter)
        push_point = add_scaled(push_start, sub(push_end, push_start), push_parameter)
        core_height, push_height = dot(height, core_point), dot(height, push_point)
        if core_height == push_height:
            raise AssertionError(f"core meets push at row {row_id}")
        core_tangent = sub(projection(core_end, basis), projection(core_start, basis))
        push_tangent = sub(projection(push_end, basis), projection(push_start, basis))
        expected_over = "core" if core_height > push_height else "push"
        determinant = det2(core_tangent, push_tangent) if expected_over == "core" else det2(push_tangent, core_tangent)
        expected_sign = 1 if determinant > 0 else -1
        if determinant == 0 or stored_over != expected_over or stored_sign != expected_sign:
            raise AssertionError(f"crossing role/sign changed at row {row_id}")
        counts[component] += 1; sums[component] += stored_sign
        if stored_over == "core": core_over[component] += 1
        if os.environ.get("T73_PROGRESS") and row_id and row_id % 250000 == 0:
            print(f"verified {row_id}/2528401", file=sys.stderr, flush=True)
    connection.close()
    expected = receipt["component_summaries"]
    for component in counts:
        if (counts[component] != expected[component]["crossings"]
                or sums[component] != expected[component]["signed_sum"]
                or core_over[component] != expected[component]["core_over_crossings"]):
            raise AssertionError("connector-push full summaries changed")
    return {
        "verdict": "PASS_ACTUAL_SOURCE_CONNECTOR_PRODUCT_PUSH_PROJECTION_FULL",
        "fast_checks": fast_checks,
        "crossings": sum(counts.values()),
        "component_crossings": counts,
        "signed_sums": sums,
        "database_sha_checked": check_database_sha,
        "framing_status": "OPEN_SPLICE_CONTRIBUTIONS_REQUIRED",
    }


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--full", action="store_true"); parser.add_argument("--check-database-sha", action="store_true")
    args = parser.parse_args()
    if args.full:
        result = verify_full(args.check_database_sha)
    else:
        receipt, checks = check_receipt(); result = {"verdict": "PASS_ACTUAL_SOURCE_CONNECTOR_PUSH_RECEIPT", "checks": checks, "crossings": receipt["crossing_count"]}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
