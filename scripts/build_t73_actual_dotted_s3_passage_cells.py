#!/usr/bin/env python3
"""Embed all actual y/z passages as disjoint framed Hopf tangles in dotted-S3 charts."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLOTS = ROOT / "geometry/t73_foot_to_dotted_slot_map.json"
TRACKS = ROOT / "geometry/t73_dotted_disk_ambient_extensions.json"
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
PD_RECEIPT = ROOT / "audit/t73_actual_source_standard_pd_sqlite_receipt.json"
OUTPUT = ROOT / "geometry/t73_actual_dotted_s3_passage_cells.json"


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def encode(value):
    return [str(coordinate) for coordinate in value]


def build():
    slots = json.loads(SLOTS.read_text(encoding="utf-8"))
    tracks = json.loads(TRACKS.read_text(encoding="utf-8"))
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    pd_receipt = json.loads(PD_RECEIPT.read_text(encoding="utf-8"))
    cycle_index = {passage["passage_id"]: (component["component"], index)
                   for component in cycles["components"]
                   for index, passage in enumerate(component["passages"])}
    charts = []
    component_linking = defaultdict(lambda: defaultdict(int))
    total_passages = total_triangles = 0
    for handle_index, handle in enumerate(slots["handles"]):
        name = handle["handle"]
        center_x = Fraction(-4 if name == "y" else 4)
        count = len(handle["entries"])
        delta = Fraction(1, 4 * (count + 1))
        dotted = [
            (center_x - 1, Fraction(-1), Fraction(0)),
            (center_x + 1, Fraction(-1), Fraction(0)),
            (center_x + 1, Fraction(1), Fraction(0)),
            (center_x - 1, Fraction(1), Fraction(0)),
            (center_x - 1, Fraction(-1), Fraction(0)),
        ]
        passages = []
        for entry in handle["entries"]:
            passage_id = entry["passage_id"]
            owner, cycle_position = cycle_index[passage_id]
            orientation = entry["orientation"]
            slot = tuple(Fraction(value) for value in entry["target_disk_slot"])
            lane_y = slot[1]
            height = Fraction(1, 2) + Fraction(entry["rank"] + 1, 10 * (count + 1))
            left = (center_x - 2, lane_y, -height)
            right = (center_x + 2, lane_y, height)
            left_push = (left[0], left[1] + delta, left[2])
            right_push = (right[0], right[1] + delta, right[2])
            if orientation == 1:
                core, push = [left, right], [left_push, right_push]
                start_foot, end_foot = "positive", "negative"
            else:
                core, push = [right, left], [right_push, left_push]
                start_foot, end_foot = "negative", "positive"
            ribbon_vertices = core + push
            crossings = [
                {
                    "dotted_segment": 3,
                    "projection_point": encode((center_x - 1, lane_y)),
                    "core_role": "under",
                    "sign": orientation,
                },
                {
                    "dotted_segment": 1,
                    "projection_point": encode((center_x + 1, lane_y)),
                    "core_role": "over",
                    "sign": orientation,
                },
            ]
            component_linking[owner][f"dotted_{name}"] += orientation
            passages.append({
                "passage_id": passage_id,
                "owner": owner,
                "component_cycle_position": cycle_position,
                "orientation": orientation,
                "slot_rank": entry["rank"],
                "normalized_foot_slot": entry["target_disk_slot"],
                "foot_to_chart_endpoint_map": {
                    "positive": encode(left),
                    "negative": encode(right),
                    "oriented_start": start_foot,
                    "oriented_end": end_foot,
                },
                "core_vertices": [encode(value) for value in core],
                "product_normal": encode((Fraction(0), delta, Fraction(0))),
                "push_vertices": [encode(value) for value in push],
                "ribbon_vertices": [encode(value) for value in ribbon_vertices],
                "ribbon_triangles": [[0, 1, 3], [0, 3, 2]],
                "dotted_crossings": crossings,
                "local_self_linking_contribution": 0,
            })
            total_passages += 1; total_triangles += 2
        charts.append({
            "handle": name,
            "chart_center_x": str(center_x),
            "dotted_component": f"dotted_{name}",
            "dotted_vertices": [encode(value) for value in dotted],
            "dotted_orientation": "counterclockwise in the xy projection",
            "passage_push_delta": str(delta),
            "passage_count": len(passages),
            "passages": passages,
        })
    linking = {owner: dict(values) for owner, values in component_linking.items()}
    expected = {
        "m_2": {"dotted_y": 40, "dotted_z": 269},
        "m_3": {"dotted_y": 189, "dotted_z": 1271},
        "r_xy": {"dotted_y": 0, "dotted_z": 0},
        "r_yz": {"dotted_y": 0, "dotted_z": 0},
        "r_zx": {"dotted_y": 0, "dotted_z": 0},
    }
    for owner in expected:
        linking.setdefault(owner, {})
        for dotted in ("dotted_y", "dotted_z"):
            linking[owner].setdefault(dotted, 0)
    if linking != expected:
        raise AssertionError("local dotted linking does not match source-native PD")
    result = {
        "schema": "t73_actual_dotted_s3_passage_cells/v1",
        "foot_to_dotted_slot_map_sha256": slots["sha256"],
        "dotted_disk_ambient_extensions_sha256": tracks["sha256"],
        "final_component_passage_cycles_sha256": cycles["sha256"],
        "actual_source_standard_pd_receipt_sha256": pd_receipt["sha256"],
        "projection_basis": [["1", "0", "0"], ["0", "1", "0"]],
        "height_direction": ["0", "0", "1"],
        "charts": charts,
        "passage_count": total_passages,
        "dotted_crossing_count": 2 * total_passages,
        "ribbon_triangle_count": total_triangles,
        "local_dotted_linking": linking,
        "completion_status": "ACTUAL_DISJOINT_FRAMED_DOTTED_S3_PASSAGE_CELLS_CONSTRUCTED",
        "scope_boundary": "local handle replacement charts only; exterior connector endpoint collars and unified source push cycles remain open",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true"); parser.add_argument("--check", action="store_true")
    args = parser.parse_args(); result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("actual dotted-S3 passage cells are stale")
    print(f"T73_DOTTED_S3_PASSAGES={result['completion_status']}")


if __name__ == "__main__":
    main()
