#!/usr/bin/env python3
"""Project actual m2/m3 connector cells against their product push-offs."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sqlite3
import sys
from fractions import Fraction
from pathlib import Path

from shapely.geometry import box
from shapely.strtree import STRtree

from export_t73_full_handle_diagram import add_scaled, det2, dot, projected_intersection, projection, sub

ROOT = Path(__file__).resolve().parents[1]
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
PROVENANCE = ROOT / "geometry/t73_reduced_source_connector_provenance.json"
PD_RECEIPT = ROOT / "audit/t73_actual_source_standard_pd_sqlite_receipt.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_actual_source_connector_push_projection_receipt.json"
DEFAULT_DB = Path("/home/lifesize/.cache/t73_actual_source_connector_push_projection.sqlite")

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


def segment_box(start, end, basis):
    first, second = projection(start, basis), projection(end, basis)
    return box(
        math.nextafter(float(min(first[0], second[0])), -math.inf),
        math.nextafter(float(min(first[1], second[1])), -math.inf),
        math.nextafter(float(max(first[0], second[0])), math.inf),
        math.nextafter(float(max(first[1], second[1])), math.inf),
    )


def source_hashes(spine, ar_link, provenance, pd_receipt):
    return {
        "johnson_spine_embedding_sha256": spine["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "reduced_source_connector_provenance_sha256": provenance["sha256"],
        "actual_source_standard_pd_receipt_sha256": pd_receipt["sha256"],
    }


def component_segments(spine, provenance, component):
    component_index = {"m_2": 1, "m_3": 2}[component]
    connectors = {item["connector_id"]: item for item in spine["central_connectors"]}
    edge_by_cell = {
        cell["raw_cell_id"]: edge_index
        for group in provenance["components"] if group["component"] == component
        for edge_index, edge in enumerate(group["reduced_edges"])
        for cell in edge["raw_connector_cells"]
        if cell["kind"] == "actual_johnson_central_connector"
    }
    result = []
    for connector_id in spine["components"][component_index]["connector_ids"]:
        vertices = [point(value) for value in connectors[connector_id]["polyline"]]
        edge = edge_by_cell[connector_id]
        for local_index, (start, end) in enumerate(zip(vertices, vertices[1:])):
            result.append({
                "connector_id": connector_id,
                "local_segment": local_index,
                "pd_segment": 5 * edge + 1 + local_index,
                "start": start,
                "end": end,
            })
    return result


def create_schema(connection):
    connection.executescript(
        """
        CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        CREATE TABLE crossings(
          id INTEGER PRIMARY KEY,
          component TEXT NOT NULL,
          core_connector TEXT NOT NULL,
          core_local_segment INTEGER NOT NULL,
          core_pd_segment INTEGER NOT NULL,
          push_connector TEXT NOT NULL,
          push_local_segment INTEGER NOT NULL,
          push_pd_segment INTEGER NOT NULL,
          projection_point_sha256 TEXT NOT NULL,
          over_role TEXT NOT NULL,sign INTEGER NOT NULL,
          UNIQUE(component,projection_point_sha256)
        );
        CREATE INDEX crossings_component ON crossings(component);
        """
    )


def build(database_path):
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    pd_receipt = json.loads(PD_RECEIPT.read_text(encoding="utf-8"))
    database_path.parent.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        database_path.unlink()
    connection = sqlite3.connect(database_path)
    connection.executescript("PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF; PRAGMA temp_store=FILE; PRAGMA cache_size=-65536;")
    create_schema(connection)
    projection_denominator = 1000003
    basis = [
        (Fraction(1), Fraction(0), Fraction(1, projection_denominator)),
        (Fraction(0), Fraction(1), Fraction(1, projection_denominator**2)),
    ]
    height = (Fraction(-1, projection_denominator), Fraction(-1, projection_denominator**2), Fraction(1))
    total_crossings = total_candidates = next_id = 0
    summaries = {}
    for component in ("m_2", "m_3"):
        segments = component_segments(spine, provenance, component)
        width = Fraction(ar_link["components"][component]["full_framing_annulus"]["width"])
        push_vector = (width, width, width)
        pushed = [
            {**segment,
             "start": tuple(segment["start"][axis] + push_vector[axis] for axis in range(3)),
             "end": tuple(segment["end"][axis] + push_vector[axis] for axis in range(3))}
            for segment in segments
        ]
        boxes = [segment_box(item["start"], item["end"], basis) for item in pushed]
        tree = STRtree(boxes)
        batch = []
        component_candidates = component_crossings = signed_sum = core_over = push_over = 0
        for core_index, core in enumerate(segments):
            if os.environ.get("T73_PROGRESS") and core_index % 250 == 0:
                print(f"{component}: segment {core_index}/{len(segments)} crossings={component_crossings}", file=sys.stderr, flush=True)
            core_box = segment_box(core["start"], core["end"], basis)
            for raw_push_index in tree.query(core_box):
                push_index = int(raw_push_index)
                push = pushed[push_index]
                component_candidates += 1
                hit = projected_intersection(core["start"], core["end"], push["start"], push["end"], basis, f"{component}:{core_index}/{push_index}")
                if hit is None:
                    continue
                core_parameter, push_parameter, projected_point = hit
                core_point = add_scaled(core["start"], sub(core["end"], core["start"]), core_parameter)
                push_point = add_scaled(push["start"], sub(push["end"], push["start"]), push_parameter)
                core_height, push_height = dot(height, core_point), dot(height, push_point)
                if core_height == push_height:
                    raise AssertionError("connector core meets its pushed copy")
                core_tangent = sub(projection(core["end"], basis), projection(core["start"], basis))
                push_tangent = sub(projection(push["end"], basis), projection(push["start"], basis))
                if core_height > push_height:
                    over_role = "core"; determinant = det2(core_tangent, push_tangent); core_over += 1
                else:
                    over_role = "push"; determinant = det2(push_tangent, core_tangent); push_over += 1
                if determinant == 0:
                    raise AssertionError("nontransverse connector core/push crossing")
                sign = 1 if determinant > 0 else -1
                point_sha = canonical_sha([str(projected_point[0]), str(projected_point[1])])
                batch.append((next_id, component, core["connector_id"], core["local_segment"], core["pd_segment"], push["connector_id"], push["local_segment"], push["pd_segment"], point_sha, over_role, sign))
                next_id += 1; component_crossings += 1; signed_sum += sign
                if len(batch) >= 2000:
                    connection.executemany("INSERT INTO crossings VALUES(?,?,?,?,?,?,?,?,?,?,?)", batch)
                    connection.commit(); batch.clear()
        if batch:
            connection.executemany("INSERT INTO crossings VALUES(?,?,?,?,?,?,?,?,?,?,?)", batch)
        summaries[component] = {
            "connector_segments": len(segments),
            "broad_candidates": component_candidates,
            "crossings": component_crossings,
            "signed_sum": signed_sum,
            "core_over_crossings": core_over,
            "push_over_crossings": push_over,
            "push_vector": [str(value) for value in push_vector],
            "parity": "even" if signed_sum % 2 == 0 else "odd",
        }
        total_candidates += component_candidates; total_crossings += component_crossings
        connection.commit()
    metadata = {
        "schema": "t73_actual_source_connector_push_projection/v1",
        "sources": source_hashes(spine, ar_link, provenance, pd_receipt),
        "projection_denominator": projection_denominator,
        "summaries": summaries,
    }
    connection.executemany("INSERT INTO metadata VALUES(?,?)", [(key, json.dumps(value, sort_keys=True)) for key, value in metadata.items()])
    connection.commit(); connection.close()
    receipt = {
        "schema": "t73_actual_source_connector_push_projection_receipt/v1",
        "database_path": str(database_path),
        "database_size": database_path.stat().st_size,
        "database_sha256": file_sha(database_path),
        "builder_sha256": file_sha(Path(__file__)),
        "sources": metadata["sources"],
        "projection_denominator": projection_denominator,
        "component_summaries": summaries,
        "broad_candidate_count": total_candidates,
        "crossing_count": total_crossings,
        "verdict": "PASS_ACTUAL_SOURCE_CONNECTOR_PRODUCT_PUSH_PROJECTION_ONLY",
        "scope_boundary": "connector-cell contribution only; band splice, foot collar and local passage contributions must be joined before integer framings are defined",
        "projection_point_storage": "SHA256 of the two exact rational coordinates; coordinates are independently reconstructible from stored segment pairs and the receipt-bound projection",
        "crossing_parameter_storage": "exact parameters are uniquely reconstructed from each stored core/push segment pair and the receipt-bound rational projection",
    }
    receipt["sha256"] = canonical_sha(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path)
    args = parser.parse_args(); receipt = build(args.output or DEFAULT_DB)
    print(json.dumps({"verdict": receipt["verdict"], "crossings": receipt["crossing_count"], "summaries": receipt["component_summaries"]}, sort_keys=True))


if __name__ == "__main__":
    main()
