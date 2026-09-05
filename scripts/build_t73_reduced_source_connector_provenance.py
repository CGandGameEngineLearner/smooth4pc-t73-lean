#!/usr/bin/env python3
"""Bind every reduced source connector edge to actual Johnson/dual cells."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
BIGONS = ROOT / "geometry/t73_final_free_reduction_bigons.json"
GRAPH_MAP = ROOT / "geometry/t73_hybrid_to_railroad_graph_map.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
OUTPUT = ROOT / "geometry/t73_reduced_source_connector_provenance.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def initial_cycle(component, passage_ids, raw_connectors):
    if len(passage_ids) != len(raw_connectors):
        raise AssertionError(f"{component}: passage/connector cycle lengths differ")
    return [
        {"passage_id": passage_id, "outgoing_raw_cells": [raw_connectors[index]]}
        for index, passage_id in enumerate(passage_ids)
    ]


def collapse_adjacent_pair(nodes, first_id, second_id):
    first_index = next(
        index for index, node in enumerate(nodes) if node["passage_id"] == first_id
    )
    second_index = (first_index + 1) % len(nodes)
    if nodes[second_index]["passage_id"] != second_id:
        raise AssertionError("bigon pair is not adjacent in connector provenance cycle")
    if len(nodes) == 2:
        residual = [
            *nodes[0]["outgoing_raw_cells"],
            *nodes[1]["outgoing_raw_cells"],
        ]
        return [], residual
    previous_index = (first_index - 1) % len(nodes)
    merged = [
        *nodes[previous_index]["outgoing_raw_cells"],
        *nodes[first_index]["outgoing_raw_cells"],
        *nodes[second_index]["outgoing_raw_cells"],
    ]
    survivors = [
        node
        for index, node in enumerate(nodes)
        if index not in {first_index, second_index}
    ]
    previous_id = nodes[previous_index]["passage_id"]
    next(node for node in survivors if node["passage_id"] == previous_id)[
        "outgoing_raw_cells"
    ] = merged
    return survivors, None


def build() -> dict:
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    bigons = json.loads(BIGONS.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH_MAP.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    cycle_by_name = {item["component"]: item for item in cycles["components"]}
    graph_edges = {}
    for edge in graph["edge_maps"]:
        graph_edges.setdefault(edge["component"], []).append(edge)
    connector_by_id = {item["connector_id"]: item for item in spine["central_connectors"]}
    component_records = []
    all_raw_ids = []
    for component in cycles["component_order"]:
        passage_ids = cycle_by_name[component]["passage_ids"]
        if component in ("m_2", "m_3"):
            component_index = 1 if component == "m_2" else 2
            connector_ids = spine["components"][component_index]["connector_ids"]
            raw_connectors = [
                {
                    "raw_cell_id": connector_id,
                    "kind": "actual_johnson_central_connector",
                    "source_sha256": canonical_sha(connector_by_id[connector_id]),
                }
                for connector_id in connector_ids
            ]
        else:
            polyline = ar_link["components"][component]["polyline"]
            raw_connectors = [
                {
                    "raw_cell_id": f"{component}:dual_boundary_connector:{index}",
                    "kind": "actual_dual_square_boundary_connector",
                    "source_sha256": canonical_sha({
                        "component_polyline": polyline,
                        "from_passage": passage_ids[index],
                        "to_passage": passage_ids[(index + 1) % len(passage_ids)],
                    }),
                }
                for index in range(len(passage_ids))
            ]
        nodes = initial_cycle(component, passage_ids, raw_connectors)
        residual = None
        for move in bigons["moves"]:
            if move["component"] != component:
                continue
            nodes, current_residual = collapse_adjacent_pair(
                nodes, move["first_passage_id"], move["second_passage_id"]
            )
            if current_residual is not None:
                residual = current_residual
        reduced_edges = []
        if nodes:
            edge_by_source = {
                edge["source_from"]: edge for edge in graph_edges[component]
            }
            for node in nodes:
                source_edge = edge_by_source[node["passage_id"]]
                reduced_edges.append({
                    "source_edge": source_edge["source_edge"],
                    "source_from": source_edge["source_from"],
                    "source_to": source_edge["source_to"],
                    "raw_connector_cells": node["outgoing_raw_cells"],
                    "target_segment_range": source_edge["target_segment_range"],
                })
                all_raw_ids.extend(
                    cell["raw_cell_id"] for cell in node["outgoing_raw_cells"]
                )
        else:
            if residual is None:
                raise AssertionError("zero-word component lost its residual connector cells")
            source_edge = graph_edges[component][0]
            reduced_edges.append({
                "source_edge": source_edge["source_edge"],
                "source_from": source_edge["source_from"],
                "source_to": source_edge["source_to"],
                "raw_connector_cells": residual,
                "target_segment_range": source_edge["target_segment_range"],
            })
            all_raw_ids.extend(cell["raw_cell_id"] for cell in residual)
        component_records.append({
            "component": component,
            "raw_passage_count": len(passage_ids),
            "reduced_edge_count": len(reduced_edges),
            "reduced_edges": reduced_edges,
            "raw_connector_cell_count": sum(
                len(edge["raw_connector_cells"]) for edge in reduced_edges
            ),
        })
    if len(all_raw_ids) != 1785 or len(set(all_raw_ids)) != 1785:
        raise AssertionError("raw source connector cells are not used exactly once")
    result = {
        "schema": "t73_reduced_source_connector_provenance/v1",
        "final_component_passage_cycles_sha256": cycles["sha256"],
        "free_reduction_bigons_sha256": bigons["sha256"],
        "hybrid_to_railroad_graph_map_sha256": graph["sha256"],
        "johnson_spine_embedding_sha256": spine["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "components": component_records,
        "reduced_edge_count": sum(item["reduced_edge_count"] for item in component_records),
        "raw_connector_cell_count": len(all_raw_ids),
        "completion_status": "ALL_REDUCED_EDGES_BOUND_TO_ACTUAL_SOURCE_CONNECTOR_CELLS",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("reduced source connector provenance is stale")
    print("T73_REDUCED_CONNECTORS=ALL_REDUCED_EDGES_BOUND_TO_ACTUAL_SOURCE_CONNECTOR_CELLS")


if __name__ == "__main__":
    main()
