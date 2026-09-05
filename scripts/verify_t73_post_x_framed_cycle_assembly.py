#!/usr/bin/env python3
"""Independently verify five complete framed cycles in the graph of charts."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_post_x_framed_cycle_assembly.json"
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
POST_X = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
PROVENANCE = ROOT / "geometry/t73_reduced_source_connector_provenance.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
CUT = ROOT / "geometry/t73_actual_cut_tangle.json"
DOTTED = ROOT / "geometry/t73_actual_dotted_s3_passage_cells.json"
COLLARS = ROOT / "geometry/t73_dotted_s3_foot_collars.json"


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def verify():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    post_x = json.loads(POST_X.read_text(encoding="utf-8"))
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    cut = json.loads(CUT.read_text(encoding="utf-8"))
    dotted = json.loads(DOTTED.read_text(encoding="utf-8"))
    collars = json.loads(COLLARS.read_text(encoding="utf-8"))
    if data["sha256"] != canonical_sha({key: value for key, value in data.items() if key != "sha256"}):
        raise AssertionError("framed-cycle assembly payload SHA changed")
    sources = {
        "final_component_passage_cycles_sha256": cycles["sha256"],
        "post_x_framed_replacement_cells_receipt_sha256": post_x["sha256"],
        "reduced_source_connector_provenance_sha256": provenance["sha256"],
        "johnson_spine_embedding_sha256": spine["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "actual_cut_tangle_sha256": cut["sha256"],
        "actual_dotted_s3_passage_cells_sha256": dotted["sha256"],
        "dotted_s3_foot_collars_sha256": collars["sha256"],
    }
    if any(data[key] != value for key, value in sources.items()):
        raise AssertionError("framed-cycle assembly sources changed")
    cycles_by_name = {item["component"]: item for item in cycles["components"]}
    connector_ids = {
        group["component"]: {cell["raw_cell_id"] for edge in group["reduced_edges"] for cell in edge["raw_connector_cells"]}
        for group in provenance["components"] if group["component"] in ("m_2", "m_3")
    }
    expected_segments = {"m_2": 12087, "m_3": 55891, "r_xy": 84, "r_yz": 8, "r_zx": 84}
    kinds = Counter(); all_bands = set(); used_connectors = {"m_2": set(), "m_3": set()}
    total_segments = total_blocks = degree_checks = 0
    for assembly in data["components"]:
        component = assembly["component"]
        cycle = cycles_by_name[component]
        blocks = assembly["blocks"]
        incoming, outgoing = Counter(), Counter()
        passage_blocks = [item for item in blocks if item["kind"] != "actual_johnson_central_connector"]
        if [item["passage_id"] for item in passage_blocks] != cycle["passage_ids"]:
            raise AssertionError("passage block cyclic order changed")
        segment_count = 0
        for block in blocks:
            kinds[block["kind"]] += 1
            outgoing[block["from_vertex"]] += 1; incoming[block["to_vertex"]] += 1
            if block["core_segment_count"] != block["push_segment_count"]:
                raise AssertionError("core/push block subdivisions disagree")
            segment_count += block["core_segment_count"]
            if block["kind"] == "post_x_framed_replacement_path":
                if block["piece_segment_counts"] != [1, 2, 34, 2, 1] or block["core_segment_count"] != 40:
                    raise AssertionError("x replacement path subdivision changed")
                if block["cache_record_index"] != block["band_index"] + 1:
                    raise AssertionError("x replacement cache index changed")
                all_bands.add(block["band_index"])
            elif block["kind"] == "actual_johnson_handle_arc" and block["core_segment_count"] != 2:
                raise AssertionError("Johnson handle arc subdivision changed")
            elif block["kind"] == "actual_bottom_cut_arc" and block["core_segment_count"] != 1:
                raise AssertionError("bottom cut arc subdivision changed")
            elif block["kind"] == "actual_dual_two_segment_passage" and block["core_segment_count"] != 2:
                raise AssertionError("dual passage subdivision changed")
            elif block["kind"] == "actual_johnson_central_connector":
                if block["core_segment_count"] != 4 or block["connector_id"] not in connector_ids[component]:
                    raise AssertionError("central connector provenance changed")
                used_connectors[component].add(block["connector_id"])
        vertices = set(incoming) | set(outgoing)
        if any(incoming[vertex] != 1 or outgoing[vertex] != 1 for vertex in vertices):
            raise AssertionError("charted component is not a disjoint degree-two cycle")
        degree_checks += len(vertices)
        if (not assembly["closed"] or len(vertices) != assembly["cyclic_vertex_count"]
                or segment_count != expected_segments[component]
                or assembly["core_segment_count"] != segment_count
                or assembly["push_segment_count"] != segment_count):
            raise AssertionError("charted component aggregate changed")
        total_segments += segment_count; total_blocks += len(blocks)
    expected_kinds = {
        "post_x_framed_replacement_path": 1513,
        "actual_johnson_handle_arc": 262,
        "actual_bottom_cut_arc": 2,
        "actual_dual_two_segment_passage": 8,
        "actual_johnson_central_connector": 1773,
    }
    if dict(kinds) != expected_kinds or all_bands != set(range(1513)):
        raise AssertionError("framed-cycle block inventory changed")
    if any(used_connectors[name] != connector_ids[name] for name in used_connectors):
        raise AssertionError("central connectors are not exhaustive")
    if total_segments != 68154 or data["charted_core_segment_count"] != 68154 or data["charted_push_segment_count"] != 68154:
        raise AssertionError("framed-cycle total segment count changed")
    if data["completion_status"] != "FIVE_COMPLETE_FRAMED_CYCLES_ASSEMBLED_IN_GRAPH_OF_CHARTS" or data["unified_s3_embedding_status"] != "OPEN_CANCELLATION_COMPLEMENT_MAP":
        raise AssertionError("framed-cycle scope changed")
    return {
        "verdict": "PASS_FIVE_COMPLETE_FRAMED_CYCLES_IN_GRAPH_OF_CHARTS",
        "components": 5,
        "blocks": total_blocks,
        "core_segments": total_segments,
        "push_segments": total_segments,
        "degree_two_vertices_checked": degree_checks,
        "block_kinds": dict(kinds),
        "unified_s3_embedding_status": data["unified_s3_embedding_status"],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
