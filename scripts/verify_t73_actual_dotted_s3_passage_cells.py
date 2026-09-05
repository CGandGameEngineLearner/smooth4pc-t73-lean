#!/usr/bin/env python3
"""Independently verify all framed local Hopf passage cells in dotted S3."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_actual_dotted_s3_passage_cells.json"
SLOTS = ROOT / "geometry/t73_foot_to_dotted_slot_map.json"
TRACKS = ROOT / "geometry/t73_dotted_disk_ambient_extensions.json"
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
PD_RECEIPT = ROOT / "audit/t73_actual_source_standard_pd_sqlite_receipt.json"
COMPONENT_ORDER = ["m_2", "m_3", "r_xy", "r_yz", "r_zx", "dotted_y", "dotted_z"]


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def cross(left, right):
    return (left[1] * right[2] - left[2] * right[1],
            left[2] * right[0] - left[0] * right[2],
            left[0] * right[1] - left[1] * right[0])


def verify():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    slots = json.loads(SLOTS.read_text(encoding="utf-8"))
    tracks = json.loads(TRACKS.read_text(encoding="utf-8"))
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    pd_receipt = json.loads(PD_RECEIPT.read_text(encoding="utf-8"))
    if data["sha256"] != canonical_sha({key: value for key, value in data.items() if key != "sha256"}):
        raise AssertionError("dotted-S3 passage payload SHA changed")
    bindings = {
        "foot_to_dotted_slot_map_sha256": slots["sha256"],
        "dotted_disk_ambient_extensions_sha256": tracks["sha256"],
        "final_component_passage_cycles_sha256": cycles["sha256"],
        "actual_source_standard_pd_receipt_sha256": pd_receipt["sha256"],
    }
    if any(data[key] != value for key, value in bindings.items()):
        raise AssertionError("dotted-S3 passage source binding changed")
    cycle_index = {passage["passage_id"]: (component["component"], index)
                   for component in cycles["components"]
                   for index, passage in enumerate(component["passages"])}
    slot_handles = {item["handle"]: item for item in slots["handles"]}
    passage_count = crossing_count = triangle_count = reflection_endpoints = 0
    local_linking = defaultdict(lambda: defaultdict(int))
    chart_ranges = []
    for chart in data["charts"]:
        name = chart["handle"]
        handle = slot_handles[name]
        entries = handle["entries"]
        center = Fraction(-4 if name == "y" else 4)
        delta = Fraction(1, 4 * (len(entries) + 1))
        expected_dotted = [
            (center - 1, Fraction(-1), Fraction(0)),
            (center + 1, Fraction(-1), Fraction(0)),
            (center + 1, Fraction(1), Fraction(0)),
            (center - 1, Fraction(1), Fraction(0)),
            (center - 1, Fraction(-1), Fraction(0)),
        ]
        if [point(value) for value in chart["dotted_vertices"]] != expected_dotted or Fraction(chart["passage_push_delta"]) != delta:
            raise AssertionError("canonical dotted rectangle changed")
        if len(chart["passages"]) != len(entries) or chart["passage_count"] != len(entries):
            raise AssertionError("dotted chart passage count changed")
        chart_ranges.append((center - 2, center + 2))
        previous_push_y = None
        for entry, passage in zip(entries, chart["passages"]):
            passage_id = entry["passage_id"]
            owner, position = cycle_index[passage_id]
            orientation = entry["orientation"]
            slot = point(entry["target_disk_slot"])
            lane_y = slot[1]
            height = Fraction(1, 2) + Fraction(entry["rank"] + 1, 10 * (len(entries) + 1))
            left, right = (center - 2, lane_y, -height), (center + 2, lane_y, height)
            left_push, right_push = (left[0], left[1] + delta, left[2]), (right[0], right[1] + delta, right[2])
            expected_core = [left, right] if orientation == 1 else [right, left]
            expected_push = [left_push, right_push] if orientation == 1 else [right_push, left_push]
            if (passage["passage_id"] != passage_id or passage["owner"] != owner
                    or passage["component_cycle_position"] != position
                    or passage["orientation"] != orientation or passage["slot_rank"] != entry["rank"]
                    or point(passage["normalized_foot_slot"]) != slot):
                raise AssertionError("dotted passage provenance changed")
            if [point(value) for value in passage["core_vertices"]] != expected_core or [point(value) for value in passage["push_vertices"]] != expected_push:
                raise AssertionError("dotted passage core/push coordinates changed")
            normal = point(passage["product_normal"])
            if normal != (0, delta, 0) or passage["local_self_linking_contribution"] != 0:
                raise AssertionError("dotted passage product normal changed")
            mapping = passage["foot_to_chart_endpoint_map"]
            if point(mapping["positive"]) != left or point(mapping["negative"]) != right:
                raise AssertionError("foot-to-chart endpoint map changed")
            if (mapping["oriented_start"], mapping["oriented_end"]) != (("positive", "negative") if orientation == 1 else ("negative", "positive")):
                raise AssertionError("oriented foot order changed")
            reflection_endpoints += 2
            vertices = [point(value) for value in passage["ribbon_vertices"]]
            if vertices != expected_core + expected_push or passage["ribbon_triangles"] != [[0, 1, 3], [0, 3, 2]]:
                raise AssertionError("passage ribbon cells changed")
            for ids in passage["ribbon_triangles"]:
                first, second, third = [vertices[index] for index in ids]
                if cross(tuple(second[i] - first[i] for i in range(3)), tuple(third[i] - first[i] for i in range(3))) == (0, 0, 0):
                    raise AssertionError("degenerate dotted passage ribbon")
                triangle_count += 1
            # At x=center-1 the core is below z=0 and at x=center+1 it is
            # above z=0. Reversing core orientation reverses both signs.
            expected_crossings = [
                ((center - 1, lane_y), 3, "under"),
                ((center + 1, lane_y), 1, "over"),
            ]
            for record, (projection_point, dotted_segment, role) in zip(passage["dotted_crossings"], expected_crossings):
                if (point(record["projection_point"]) != projection_point
                        or record["dotted_segment"] != dotted_segment
                        or record["core_role"] != role or record["sign"] != orientation):
                    raise AssertionError("local Hopf crossing changed")
                crossing_count += 1
            # Ribbon y intervals are ordered and disjoint, including pushes.
            if previous_push_y is not None and lane_y <= previous_push_y:
                raise AssertionError("neighboring passage ribbons overlap")
            previous_push_y = lane_y + delta
            if not (-1 < lane_y < lane_y + delta < 1):
                raise AssertionError("passage ribbon left dotted rectangle interior")
            local_linking[owner][f"dotted_{name}"] += orientation
            passage_count += 1
    if not (chart_ranges[0][1] < chart_ranges[1][0]):
        raise AssertionError("y/z dotted charts are not disjoint")
    linking = {owner: {dotted: local_linking[owner].get(dotted, 0) for dotted in ("dotted_y", "dotted_z")}
               for owner in COMPONENT_ORDER[:5]}
    if linking != data["local_dotted_linking"]:
        raise AssertionError("local dotted linking summary changed")
    matrix = pd_receipt["pairwise_linking_matrix"]
    for owner_index, owner in enumerate(COMPONENT_ORDER[:5]):
        if linking[owner]["dotted_y"] != matrix[owner_index][5] or linking[owner]["dotted_z"] != matrix[owner_index][6]:
            raise AssertionError("local geometry disagrees with source-native PD linking")
    if (passage_count, crossing_count, triangle_count, reflection_endpoints) != (1785, 3570, 3570, 3570):
        raise AssertionError("dotted passage verification counts changed")
    if (data["passage_count"], data["dotted_crossing_count"], data["ribbon_triangle_count"]) != (passage_count, crossing_count, triangle_count):
        raise AssertionError("dotted passage aggregate counts changed")
    return {
        "verdict": "PASS_ACTUAL_DISJOINT_FRAMED_DOTTED_S3_PASSAGE_CELLS",
        "passages": passage_count,
        "dotted_crossings": crossing_count,
        "ribbon_triangles": triangle_count,
        "foot_chart_endpoints": reflection_endpoints,
        "local_dotted_linking": linking,
        "scope_boundary": data["scope_boundary"],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
