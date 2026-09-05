#!/usr/bin/env python3
"""Verify that all reduced graph edges retain actual source connector provenance."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_reduced_source_connector_provenance.json"
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
BIGONS = ROOT / "geometry/t73_final_free_reduction_bigons.json"
GRAPH = ROOT / "geometry/t73_hybrid_to_railroad_graph_map.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    bigons = json.loads(BIGONS.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    if data["completion_status"] != "ALL_REDUCED_EDGES_BOUND_TO_ACTUAL_SOURCE_CONNECTOR_CELLS":
        raise AssertionError("source connector provenance scope changed")
    expected_hashes = {
        "final_component_passage_cycles_sha256": cycles["sha256"],
        "free_reduction_bigons_sha256": bigons["sha256"],
        "hybrid_to_railroad_graph_map_sha256": graph["sha256"],
        "johnson_spine_embedding_sha256": spine["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
    }
    if any(data[field] != value for field, value in expected_hashes.items()):
        raise AssertionError("source connector provenance has stale sources")
    central = {item["connector_id"]: item for item in spine["central_connectors"]}
    graph_edges = {item["source_edge"]: item for item in graph["edge_maps"]}
    raw_ids = []
    composite_lengths = {}
    for component in data["components"]:
        name = component["component"]
        lengths = []
        for edge in component["reduced_edges"]:
            if edge["source_edge"] not in graph_edges:
                raise AssertionError("reduced connector cites an unknown graph edge")
            graph_edge = graph_edges[edge["source_edge"]]
            if edge["source_from"] != graph_edge["source_from"] or edge["source_to"] != graph_edge["source_to"] or edge["target_segment_range"] != graph_edge["target_segment_range"]:
                raise AssertionError("reduced connector incidence/target changed")
            cells = edge["raw_connector_cells"]
            lengths.append(len(cells))
            for cell in cells:
                raw_id = cell["raw_cell_id"]
                raw_ids.append(raw_id)
                if cell["kind"] == "actual_johnson_central_connector":
                    if raw_id not in central or cell["source_sha256"] != canonical_sha(central[raw_id]):
                        raise AssertionError("Johnson connector source hash changed")
                elif cell["kind"] == "actual_dual_square_boundary_connector":
                    dual_component = raw_id.split(":", 1)[0]
                    if dual_component != name:
                        raise AssertionError("dual connector owner changed")
                else:
                    raise AssertionError("unknown raw connector provenance kind")
        if component["raw_connector_cell_count"] != sum(lengths) or component[
            "reduced_edge_count"
        ] != len(lengths):
            raise AssertionError("component connector provenance counts changed")
        composite_lengths[name] = Counter(lengths)
    if len(raw_ids) != 1785 or len(set(raw_ids)) != 1785:
        raise AssertionError("raw connector cells are duplicated or missing")
    expected_central_ids = set(spine["components"][1]["connector_ids"]) | set(
        spine["components"][2]["connector_ids"]
    )
    used_central_ids = {value for value in raw_ids if value in central}
    if used_central_ids != expected_central_ids or len(used_central_ids) != 1773:
        raise AssertionError("Johnson central connector coverage changed")
    if composite_lengths["m_3"] != {1: 1459, 3: 1} or composite_lengths["r_zx"] != {4: 1}:
        raise AssertionError("bigon-composed connector lengths changed")
    return {
        "verdict": "PASS_ALL_REDUCED_EDGES_ACTUAL_CONNECTOR_PROVENANCE",
        "reduced_edges": data["reduced_edge_count"],
        "raw_connector_cells": len(raw_ids),
        "johnson_central_connectors": len(used_central_ids),
        "dual_boundary_connectors": len(raw_ids) - len(used_central_ids),
        "m3_three_cell_composites": composite_lengths["m_3"][3],
        "rzx_four_cell_composites": composite_lengths["r_zx"][4],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
