#!/usr/bin/env python3
"""Independently verify the five final cyclic y/z passage orders."""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_final_component_passage_cycles.json"
FINAL_YZ = ROOT / "geometry/t73_final_yz_foot_state.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
X_DELETION = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def dual_cycle(component, polyline, replacement_by_source):
    entries = []
    points = [point(value) for value in polyline]
    for index in range(len(points) - 2):
        triple = points[index : index + 3]
        varying_axes = [
            axis
            for axis in range(3)
            if [value[axis] for value in triple]
            in (
                [Fraction(1), Fraction(2), Fraction(3)],
                [Fraction(3), Fraction(2), Fraction(1)],
            )
        ]
        if len(varying_axes) != 1:
            continue
        axis = varying_axes[0]
        center_index = index + 1
        if axis == 0:
            source_id = f"{component}:vertex:{center_index}"
            entries.append(replacement_by_source[source_id])
        elif axis == 1:
            entries.append(f"{component}:y:edge:{index}")
        else:
            entries.append(f"{component}:z:edge:{index}")
    return entries


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    final_yz = json.loads(FINAL_YZ.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    local_movie = json.loads(LOCAL_MOVIE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    x_deletion = json.loads(X_DELETION.read_text(encoding="utf-8"))
    if data["completion_status"] != "FIVE_FINAL_COMPONENT_PASSAGE_CYCLES_CONSTRUCTED":
        raise AssertionError("final passage-cycle scope changed")
    expected_hashes = {
        "final_yz_foot_state_sha256": final_yz["sha256"],
        "johnson_spine_embedding_sha256": spine["sha256"],
        "x_local_movie_sha256": local_movie["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "post_x_m1_deletion_sha256": x_deletion["sha256"],
    }
    if any(data[field] != value for field, value in expected_hashes.items()):
        raise AssertionError("final passage cycles have stale sources")
    cycles = {item["component"]: item for item in data["components"]}
    if list(data["component_order"]) != ["m_2", "m_3", "r_xy", "r_yz", "r_zx"]:
        raise AssertionError("final component order changed")
    passages = {
        item["passage_id"]: {**item, "handle": handle["name"]}
        for handle in final_yz["handles"]
        for item in handle["passages"]
    }
    replacement_by_source = {
        record["source_id"]: f"x_replacement:{record['band_index']}:m1_z"
        for record in local_movie["bands"]
    }
    arcs = {item["arc_id"]: item for item in spine["handle_arcs"]}
    expected = {}
    for component_index, name in ((1, "m_2"), (2, "m_3")):
        expected[name] = [f"{name}:C_i"] + [
            replacement_by_source[arc_id]
            if arcs[arc_id]["axis"] == 0
            else arc_id
            for arc_id in spine["components"][component_index]["handle_arc_ids"]
        ]
    expected["r_xy"] = [
        replacement_by_source["r_xy:vertex:3"],
        "r_xy:y:edge:0",
        replacement_by_source["r_xy:vertex:7"],
        "r_xy:y:edge:4",
    ]
    expected["r_yz"] = [
        "r_yz:y:edge:2",
        "r_yz:z:edge:0",
        "r_yz:y:edge:6",
        "r_yz:z:edge:4",
    ]
    expected["r_zx"] = dual_cycle(
        "r_zx", ar_link["components"]["r_zx"]["polyline"], replacement_by_source
    )
    for name, passage_ids in expected.items():
        if cycles[name]["passage_ids"] != passage_ids:
            raise AssertionError(f"{name}: cyclic passage order changed")
        if [item["passage_id"] for item in cycles[name]["passages"]] != passage_ids:
            raise AssertionError(f"{name}: embedded passage records changed")
        for passage_id in passage_ids:
            if passages[passage_id]["component"] != name:
                raise AssertionError(f"{passage_id}: owner changed")
    used = [value for passage_ids in expected.values() for value in passage_ids]
    if len(used) != len(set(used)) or set(used) != set(passages):
        raise AssertionError("final cycles do not partition the passage set")
    handle_counts = Counter(passages[value]["handle"] for value in used)
    if handle_counts != {"y": 235, "z": 1550}:
        raise AssertionError("final cycle handle counts changed")
    component_counts = {name: len(values) for name, values in expected.items()}
    if component_counts != {"m_2": 311, "m_3": 1462, "r_xy": 4, "r_yz": 4, "r_zx": 4}:
        raise AssertionError("final component passage counts changed")
    return {
        "verdict": "PASS_FIVE_FINAL_COMPONENT_PASSAGE_CYCLES",
        "component_passage_counts": component_counts,
        "handle_passage_counts": dict(handle_counts),
        "used_passages": len(used),
        "unique_passages": len(set(used)),
        "cycles": 5,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
