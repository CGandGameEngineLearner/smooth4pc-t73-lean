#!/usr/bin/env python3
"""Assemble all actual current-link passage arcs in the positive x-belt chart."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POST_CANCEL = ROOT / "geometry/t73_t_hcs_handle_pair_deletion.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
BELTS = ROOT / "geometry/t73_belt_spheres.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
OUTPUT = ROOT / "geometry/t73_x_positive_belt_state0.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def with_positive_normal(polyline):
    return [[*point, "1"] for point in polyline]


def build() -> dict:
    post_cancel = json.loads(POST_CANCEL.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    passages = belts["x_handle"]["passages"]
    passage_by_source = {item["source_id"]: item for item in passages}
    arcs = []
    for handle_arc in spine["handle_arcs"]:
        if handle_arc["axis"] != 0:
            continue
        source_id = handle_arc["arc_id"]
        passage = passage_by_source[source_id]
        polyline = with_positive_normal(handle_arc["lift_polyline"])
        if polyline[1][1:] != passage["belt_face_point"]:
            raise AssertionError(f"{source_id}: Johnson arc misses its x-belt point")
        if handle_arc["sign"] != passage["orientation"]:
            raise AssertionError(f"{source_id}: Johnson and belt orientations differ")
        arcs.append({
            "source_id": source_id,
            "component": passage["component"],
            "source_kind": passage["source_kind"],
            "orientation": passage["orientation"],
            "polyline": polyline,
        })
    for passage in passages:
        if passage["source_kind"] != "dual_cell_boundary":
            continue
        y_coordinate, z_coordinate, normal = passage["belt_face_point"]
        arcs.append({
            "source_id": passage["source_id"],
            "component": passage["component"],
            "source_kind": passage["source_kind"],
            "orientation": passage["orientation"],
            "polyline": [
                ["1", y_coordinate, z_coordinate, normal],
                ["2", y_coordinate, z_coordinate, normal],
                ["3", y_coordinate, z_coordinate, normal],
            ],
        })
    m1_passage = passage_by_source["m_1:C_i"]
    arcs.append({
        "source_id": "m_1:C_i",
        "component": "m_1",
        "source_kind": m1_passage["source_kind"],
        "orientation": m1_passage["orientation"],
        "polyline": with_positive_normal(cancellation["attaching_polyline"]),
    })
    arcs.sort(key=lambda item: item["source_id"])
    if len(arcs) != 1514 or len({item["source_id"] for item in arcs}) != 1514:
        raise AssertionError("positive x-belt state does not contain 1514 unique passages")
    result = {
        "schema": "t73_x_positive_belt_state/v1",
        "post_t_hcs_deletion_sha256": post_cancel["sha256"],
        "johnson_spine_embedding_sha256": spine["sha256"],
        "belt_spheres_sha256": belts["sha256"],
        "x_cancellation_sha256": cancellation["sha256"],
        "chart_coordinates": ["x", "y", "z", "nu"],
        "chart_scope": "positive x-belt passage collar nu=1",
        "arcs": arcs,
        "counts": {
            "cancelling_m1": 1,
            "johnson_x_passages": 1509,
            "dual_x_passages": 4,
            "total": 1514,
        },
        "completion_status": "ACTUAL_POSITIVE_X_BELT_PASSAGE_STATE0",
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
        raise AssertionError("positive x-belt state0 is stale")
    print("T73_X_BELT_STATE0=ACTUAL_POSITIVE_X_BELT_PASSAGE_STATE0")


if __name__ == "__main__":
    main()
