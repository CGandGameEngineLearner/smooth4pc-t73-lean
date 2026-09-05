#!/usr/bin/env python3
"""Build the source-cell to railroad 1-skeleton map after the three bigons."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
BIGONS = ROOT / "geometry/t73_final_free_reduction_bigons.json"
RAILROAD = ROOT / "geometry/t73_actual_railroad_core_coordinates.json"
HYBRID = ROOT / "geometry/t73_x_band_hybrid_movie.json"
FOOT_STATE = ROOT / "geometry/t73_final_yz_foot_state.json"
FRAMINGS = ROOT / "geometry/t73_railroad_product_framings.json"
OUTPUT = ROOT / "geometry/t73_hybrid_to_railroad_graph_map.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def build() -> dict:
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    bigons = json.loads(BIGONS.read_text(encoding="utf-8"))
    railroad = json.loads(RAILROAD.read_text(encoding="utf-8"))
    hybrid = json.loads(HYBRID.read_text(encoding="utf-8"))
    foot_state = json.loads(FOOT_STATE.read_text(encoding="utf-8"))
    framings = json.loads(FRAMINGS.read_text(encoding="utf-8"))
    passages = {
        passage["passage_id"]: {**passage, "handle": handle["name"]}
        for handle in foot_state["handles"]
        for passage in handle["passages"]
    }
    hybrid_by_index = {
        transition["band_index"]: transition for transition in hybrid["transitions"]
    }
    railroad_by_name = {item["name"]: item for item in railroad["components"]}
    framing_by_name = {item["name"]: item for item in framings["components"]}
    vertex_maps = []
    edge_maps = []
    component_maps = []
    for component in cycles["component_order"]:
        target = railroad_by_name[component]
        survivor_ids = target["survivor_passage_ids"]
        if not survivor_ids:
            component_maps.append({
                "component": component,
                "source_kind": "zero_word_residual_circle_after_bigons",
                "target_kind": "split_diamond",
                "source_residual_cell": f"{component}:zero_word_residual_core",
                "target_vertex_range": [0, len(target["vertices"]) - 1],
                "target_edge_segment_range": [0, len(target["vertices"]) - 2],
                "framing_push_vector": framing_by_name[component]["push_vector"],
            })
            vertex_maps.append({
                "component": component,
                "source_vertex": f"{component}:zero_word_residual_vertex",
                "target_vertex_index": 0,
                "kind": "residual_split_circle_basepoint",
            })
            edge_maps.append({
                "component": component,
                "source_edge": f"{component}:zero_word_residual_edge",
                "source_from": f"{component}:zero_word_residual_vertex",
                "source_to": f"{component}:zero_word_residual_vertex",
                "target_segment_range": [0, len(target["vertices"]) - 2],
                "kind": "residual_circle_to_split_diamond",
            })
            continue
        event_count = len(survivor_ids)
        component_vertex_start = len(vertex_maps)
        for event_index, passage_id in enumerate(survivor_ids):
            if passage_id.startswith("x_replacement:"):
                band_index = int(passage_id.split(":")[1])
                source_cell = {
                    "kind": "hybrid_x_replacement_z_passage",
                    "hybrid_transition_sha256": canonical_sha(hybrid_by_index[band_index]),
                    "band_index": band_index,
                }
            else:
                source_cell = {
                    "kind": "final_bound_base_or_dual_passage",
                    "passage_sha256": canonical_sha(passages[passage_id]),
                }
            vertex_maps.append({
                "component": component,
                "source_vertex": passage_id,
                "target_vertex_index": event_index,
                "target_vertex": target["vertices"][event_index],
                "source_cell": source_cell,
            })
        for event_index, passage_id in enumerate(survivor_ids):
            next_index = (event_index + 1) % event_count
            if next_index:
                target_range = [event_index, event_index]
            else:
                target_range = [event_count - 1, event_count + 1]
            edge_maps.append({
                "component": component,
                "source_edge": f"{component}:connector_after:{passage_id}",
                "source_from": passage_id,
                "source_to": survivor_ids[next_index],
                "source_cycle_edge_index": event_index,
                "target_segment_range": target_range,
                "kind": "surviving_connector_to_railroad_chain",
            })
        component_maps.append({
            "component": component,
            "source_survivor_count": event_count,
            "source_vertex_map_range": [
                component_vertex_start,
                component_vertex_start + event_count - 1,
            ],
            "target_event_vertex_count": event_count,
            "target_total_vertex_count": len(target["vertices"]),
            "framing_push_vector": framing_by_name[component]["push_vector"],
        })
    if len(vertex_maps) != 1780 or len(edge_maps) != 1780:
        raise AssertionError("hybrid-to-railroad graph map has the wrong cell counts")
    result = {
        "schema": "t73_hybrid_to_railroad_graph_map/v1",
        "final_component_passage_cycles_sha256": cycles["sha256"],
        "free_reduction_bigons_sha256": bigons["sha256"],
        "railroad_core_coordinates_sha256": railroad["sha256"],
        "x_hybrid_movie_sha256": hybrid["sha256"],
        "final_yz_foot_state_sha256": foot_state["sha256"],
        "railroad_product_framings_sha256": framings["sha256"],
        "component_maps": component_maps,
        "vertex_maps": vertex_maps,
        "edge_maps": edge_maps,
        "source_cell_count": len(vertex_maps) + len(edge_maps),
        "target_subdivision_rule": (
            "each surviving event maps to one railroad event vertex; ordinary "
            "connectors map to one segment and each closure maps to its three-segment outer chain"
        ),
        "ambient_extension_status": "OPEN_CELLWISE_TRACKS_AND_DISJOINTNESS_REQUIRED",
        "completion_status": "HYBRID_TO_RAILROAD_FRAMED_GRAPH_ISOMORPHISM_CONSTRUCTED",
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
        raise AssertionError("hybrid-to-railroad graph map is stale")
    print("T73_HYBRID_RAILROAD_GRAPH=HYBRID_TO_RAILROAD_FRAMED_GRAPH_ISOMORPHISM_CONSTRUCTED")


if __name__ == "__main__":
    main()
