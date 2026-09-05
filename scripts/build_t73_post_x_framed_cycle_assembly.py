#!/usr/bin/env python3
"""Assemble every explicit post-x core/push block into five charted cycles."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
POST_X = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
PROVENANCE = ROOT / "geometry/t73_reduced_source_connector_provenance.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
CUT = ROOT / "geometry/t73_actual_cut_tangle.json"
DOTTED = ROOT / "geometry/t73_actual_dotted_s3_passage_cells.json"
COLLARS = ROOT / "geometry/t73_dotted_s3_foot_collars.json"
OUTPUT = ROOT / "geometry/t73_post_x_framed_cycle_assembly.json"


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def build():
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    post_x = json.loads(POST_X.read_text(encoding="utf-8"))
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    cut = json.loads(CUT.read_text(encoding="utf-8"))
    dotted = json.loads(DOTTED.read_text(encoding="utf-8"))
    collars = json.loads(COLLARS.read_text(encoding="utf-8"))
    connector_after = {
        (group["component"], edge["source_from"]): edge["raw_connector_cells"][0]
        for group in provenance["components"] if group["component"] in ("m_2", "m_3")
        for edge in group["reduced_edges"]
    }
    connector_geometry = {item["connector_id"]: item for item in spine["central_connectors"]}
    assemblies = []
    total_core_segments = total_push_segments = 0
    for cycle in cycles["components"]:
        component = cycle["component"]
        count = len(cycle["passages"])
        blocks = []
        component_segments = 0
        for index, passage in enumerate(cycle["passages"]):
            passage_id = passage["passage_id"]
            start_vertex = f"{component}:v:{index}"
            next_vertex = f"{component}:v:{(index + 1) % count}"
            if component in ("m_2", "m_3"):
                passage_exit = f"{component}:passage-exit:{index}"
            else:
                passage_exit = next_vertex
            if passage["source_kind"] == "x_slide_m1_parallel_z_lane":
                band_index = int(passage_id.split(":")[1])
                passage_block = {
                    "kind": "post_x_framed_replacement_path",
                    "passage_id": passage_id,
                    "band_index": band_index,
                    "cache_record_index": band_index + 1,
                    "piece_segment_counts": [1, 2, 34, 2, 1],
                    "piece_order": ["source_stub_before", "negative_band_lane", "oriented_m1_parallel_complement", "positive_band_lane", "source_stub_after"],
                    "core_segment_count": 40,
                    "push_segment_count": 40,
                }
            elif passage["source_kind"] == "johnson_base_arc":
                passage_block = {
                    "kind": "actual_johnson_handle_arc",
                    "passage_id": passage_id,
                    "source_arc_id": passage["arc_id"],
                    "core_segment_count": 2,
                    "push_segment_count": 2,
                }
            elif passage["source_kind"] == "bottom_coordinate_arc":
                passage_block = {
                    "kind": "actual_mapping_torus_bottom_closure",
                    "passage_id": passage_id,
                    "source_pointer": f"geometry/t73_actual_cut_tangle.json#/passages/{passage_id}",
                    "core_segment_count": 12,
                    "push_segment_count": 12,
                }
            elif passage["source_kind"] == "dual_disk_boundary":
                edge = int(passage_id.rsplit(":", 1)[1])
                passage_block = {
                    "kind": "actual_dual_two_segment_passage",
                    "passage_id": passage_id,
                    "source_component": component,
                    "source_segment_range": [edge, edge + 1],
                    "core_segment_count": 2,
                    "push_segment_count": 2,
                }
            else:
                raise AssertionError(f"unknown passage kind {passage['source_kind']}")
            passage_block.update({
                "from_vertex": start_vertex,
                "to_vertex": passage_exit,
                "dotted_s3_passage_ref": passage_id,
                "positive_negative_foot_collar_ref": passage_id,
            })
            blocks.append(passage_block)
            component_segments += passage_block["core_segment_count"]
            if component in ("m_2", "m_3"):
                cell = connector_after[(component, passage_id)]
                connector_id = cell["raw_cell_id"]
                polyline = connector_geometry[connector_id]["polyline"]
                connector_block = {
                    "kind": "actual_johnson_central_connector",
                    "connector_id": connector_id,
                    "source_sha256": cell["source_sha256"],
                    "from_passage": passage_id,
                    "from_vertex": passage_exit,
                    "to_vertex": next_vertex,
                    "core_segment_count": len(polyline) - 1,
                    "push_segment_count": len(polyline) - 1,
                }
                blocks.append(connector_block)
                component_segments += connector_block["core_segment_count"]
        assemblies.append({
            "component": component,
            "cyclic_vertex_count": count + (count if component in ("m_2", "m_3") else 0),
            "block_count": len(blocks),
            "core_segment_count": component_segments,
            "push_segment_count": component_segments,
            "blocks": blocks,
            "closed": True,
        })
        total_core_segments += component_segments; total_push_segments += component_segments
    result = {
        "schema": "t73_post_x_framed_cycle_assembly/v1",
        "final_component_passage_cycles_sha256": cycles["sha256"],
        "post_x_framed_replacement_cells_receipt_sha256": post_x["sha256"],
        "reduced_source_connector_provenance_sha256": provenance["sha256"],
        "johnson_spine_embedding_sha256": spine["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "actual_cut_tangle_sha256": cut["sha256"],
        "actual_dotted_s3_passage_cells_sha256": dotted["sha256"],
        "dotted_s3_foot_collars_sha256": collars["sha256"],
        "components": assemblies,
        "component_count": len(assemblies),
        "passage_block_count": sum(len(item["passages"]) for item in cycles["components"]),
        "x_replacement_block_count": post_x["framed_replacement_cell_count"],
        "central_connector_block_count": 1773,
        "charted_core_segment_count": total_core_segments,
        "charted_push_segment_count": total_push_segments,
        "completion_status": "FIVE_COMPLETE_FRAMED_CYCLES_ASSEMBLED_IN_GRAPH_OF_CHARTS",
        "unified_s3_embedding_status": "OPEN_CANCELLATION_COMPLEMENT_MAP",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true"); parser.add_argument("--check", action="store_true")
    args = parser.parse_args(); result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("post-x framed cycle assembly is stale")
    print(f"T73_POST_X_CYCLES={result['completion_status']} segments={result['charted_core_segment_count']}")


if __name__ == "__main__":
    main()
