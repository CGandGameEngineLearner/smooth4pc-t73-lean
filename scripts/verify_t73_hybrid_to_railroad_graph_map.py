#!/usr/bin/env python3
"""Verify the framed 1-skeleton isomorphism before ambient track construction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from verify_t73_final_free_reduction_bigons import verify as verify_bigons
from verify_t73_actual_railroad_core_coordinates import verify as verify_railroad
from verify_t73_railroad_product_framings import verify as verify_framings

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_hybrid_to_railroad_graph_map.json"
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
BIGONS = ROOT / "geometry/t73_final_free_reduction_bigons.json"
RAILROAD = ROOT / "geometry/t73_actual_railroad_core_coordinates.json"
HYBRID = ROOT / "geometry/t73_x_band_hybrid_movie.json"
FOOT_STATE = ROOT / "geometry/t73_final_yz_foot_state.json"
FRAMINGS = ROOT / "geometry/t73_railroad_product_framings.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def verify() -> dict:
    prerequisites = {
        "bigons": verify_bigons()["verdict"],
        "railroad": verify_railroad()["verdict"],
        "framings": verify_framings()["verdict"],
    }
    data = json.loads(DATA.read_text(encoding="utf-8"))
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    bigons = json.loads(BIGONS.read_text(encoding="utf-8"))
    railroad = json.loads(RAILROAD.read_text(encoding="utf-8"))
    hybrid = json.loads(HYBRID.read_text(encoding="utf-8"))
    foot_state = json.loads(FOOT_STATE.read_text(encoding="utf-8"))
    framings = json.loads(FRAMINGS.read_text(encoding="utf-8"))
    if data["completion_status"] != "HYBRID_TO_RAILROAD_FRAMED_GRAPH_ISOMORPHISM_CONSTRUCTED":
        raise AssertionError("hybrid-to-railroad graph-map scope changed")
    expected_hashes = {
        "final_component_passage_cycles_sha256": cycles["sha256"],
        "free_reduction_bigons_sha256": bigons["sha256"],
        "railroad_core_coordinates_sha256": railroad["sha256"],
        "x_hybrid_movie_sha256": hybrid["sha256"],
        "final_yz_foot_state_sha256": foot_state["sha256"],
        "railroad_product_framings_sha256": framings["sha256"],
    }
    if any(data[field] != value for field, value in expected_hashes.items()):
        raise AssertionError("hybrid-to-railroad graph map has stale sources")
    passages = {
        passage["passage_id"]: {**passage, "handle": handle["name"]}
        for handle in foot_state["handles"]
        for passage in handle["passages"]
    }
    hybrid_by_index = {
        transition["band_index"]: transition for transition in hybrid["transitions"]
    }
    target_by_name = {item["name"]: item for item in railroad["components"]}
    framing_by_name = {item["name"]: item for item in framings["components"]}
    vertex_maps = data["vertex_maps"]
    edge_maps = data["edge_maps"]
    vertex_by_source = {
        (item["component"], item["source_vertex"]): item for item in vertex_maps
    }
    if len(vertex_by_source) != len(vertex_maps):
        raise AssertionError("source graph vertex map is not injective")
    edge_count = vertex_count = replacement_checks = 0
    for component_map in data["component_maps"]:
        component = component_map["component"]
        target = target_by_name[component]
        survivors = target["survivor_passage_ids"]
        component_vertices = [item for item in vertex_maps if item["component"] == component]
        component_edges = [item for item in edge_maps if item["component"] == component]
        if not survivors:
            if len(component_vertices) != 1 or len(component_edges) != 1:
                raise AssertionError("zero-word residual component is not a one-vertex circle")
            covered_segments = set(
                range(
                    component_edges[0]["target_segment_range"][0],
                    component_edges[0]["target_segment_range"][1] + 1,
                )
            )
        else:
            if len(component_vertices) != len(survivors) or len(component_edges) != len(survivors):
                raise AssertionError("surviving component graph has wrong V/E counts")
            covered_segments = set()
            for index, passage_id in enumerate(survivors):
                vertex = vertex_by_source[component, passage_id]
                if vertex["target_vertex_index"] != index or vertex["target_vertex"] != target["vertices"][index]:
                    raise AssertionError("railroad event vertex map changed")
                source_cell = vertex["source_cell"]
                if passage_id.startswith("x_replacement:"):
                    band_index = int(passage_id.split(":")[1])
                    if source_cell["hybrid_transition_sha256"] != canonical_sha(hybrid_by_index[band_index]):
                        raise AssertionError("replacement vertex lost its hybrid cell binding")
                    replacement_checks += 1
                elif source_cell["passage_sha256"] != canonical_sha(passages[passage_id]):
                    raise AssertionError("base/dual vertex lost its foot-passage binding")
                edge = next(item for item in component_edges if item["source_from"] == passage_id)
                if edge["source_to"] != survivors[(index + 1) % len(survivors)]:
                    raise AssertionError("source connector cyclic incidence changed")
                start, end = edge["target_segment_range"]
                segment_set = set(range(start, end + 1))
                if covered_segments & segment_set:
                    raise AssertionError("two source edges map over the same target segment")
                covered_segments.update(segment_set)
        if covered_segments != set(range(len(target["vertices"]) - 1)):
            raise AssertionError("target railroad segments are not covered exactly once")
        if component_map["framing_push_vector"] != framing_by_name[component]["push_vector"]:
            raise AssertionError("graph-map target framing vector changed")
        vertex_count += len(component_vertices)
        edge_count += len(component_edges)
    if vertex_count != 1780 or edge_count != 1780 or replacement_checks != 1510:
        raise AssertionError("hybrid-to-railroad graph-map totals changed")
    if data["ambient_extension_status"] != "OPEN_CELLWISE_TRACKS_AND_DISJOINTNESS_REQUIRED":
        raise AssertionError("graph map overstates ambient isotopy completion")
    return {
        "verdict": "PASS_HYBRID_TO_RAILROAD_FRAMED_GRAPH_ISOMORPHISM_ONLY",
        "vertices": vertex_count,
        "edges": edge_count,
        "components": len(data["component_maps"]),
        "hybrid_replacement_vertex_bindings": replacement_checks,
        "target_segment_partition": "PASS",
        "prerequisite_verdicts": prerequisites,
        "ambient_isotopy_status": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
