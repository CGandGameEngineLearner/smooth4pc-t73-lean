#!/usr/bin/env python3
"""Recover cyclic y/z passage order on all five final framed components."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL_YZ = ROOT / "geometry/t73_final_yz_foot_state.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
X_DELETION = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"
OUTPUT = ROOT / "geometry/t73_final_component_passage_cycles.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def build() -> dict:
    final_yz = json.loads(FINAL_YZ.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    local_movie = json.loads(LOCAL_MOVIE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    x_deletion = json.loads(X_DELETION.read_text(encoding="utf-8"))
    passages = {
        item["passage_id"]: {**item, "handle": handle["name"]}
        for handle in final_yz["handles"]
        for item in handle["passages"]
    }
    replacement_by_source = {
        record["source_id"]: f"x_replacement:{record['band_index']}:m1_z"
        for record in local_movie["bands"]
    }
    spine_arc_by_id = {
        item["arc_id"]: item for item in spine["handle_arcs"]
    }
    cycles = []
    for component_index, component_name in ((1, "m_2"), (2, "m_3")):
        component = spine["components"][component_index]
        passage_ids = [f"{component_name}:C_i"]
        for arc_id in component["handle_arc_ids"]:
            arc = spine_arc_by_id[arc_id]
            if arc["axis"] == 0:
                passage_ids.append(replacement_by_source[arc_id])
            else:
                passage_ids.append(arc_id)
        cycles.append({
            "component": component_name,
            "source_kind": "johnson_component_with_x_replacements",
            "passage_ids": passage_ids,
            "passages": [passages[value] for value in passage_ids],
        })
    dual_orders = {
        "r_xy": [
            "r_xy:y:edge:0",
            "x_replacement:1509:m1_z",
            "r_xy:y:edge:4",
            "x_replacement:1510:m1_z",
        ],
        "r_yz": [
            "r_yz:z:edge:0",
            "r_yz:y:edge:2",
            "r_yz:z:edge:4",
            "r_yz:y:edge:6",
        ],
        "r_zx": [
            "r_zx:z:edge:0",
            "x_replacement:1511:m1_z",
            "r_zx:z:edge:4",
            "x_replacement:1512:m1_z",
        ],
    }
    for component_name, passage_ids in dual_orders.items():
        cycles.append({
            "component": component_name,
            "source_kind": "dual_square_boundary_with_x_replacements",
            "passage_ids": passage_ids,
            "passages": [passages[value] for value in passage_ids],
            "source_polyline_sha256": canonical_sha(
                ar_link["components"][component_name]["polyline"]
            ),
        })
    used = [value for cycle in cycles for value in cycle["passage_ids"]]
    if len(used) != 1785 or len(set(used)) != 1785 or set(used) != set(passages):
        raise AssertionError("final component cycles do not use every passage exactly once")
    result = {
        "schema": "t73_final_component_passage_cycles/v1",
        "final_yz_foot_state_sha256": final_yz["sha256"],
        "johnson_spine_embedding_sha256": spine["sha256"],
        "x_local_movie_sha256": local_movie["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "post_x_m1_deletion_sha256": x_deletion["sha256"],
        "components": cycles,
        "component_order": ["m_2", "m_3", "r_xy", "r_yz", "r_zx"],
        "passage_count": len(used),
        "completion_status": "FIVE_FINAL_COMPONENT_PASSAGE_CYCLES_CONSTRUCTED",
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
        raise AssertionError("final component passage cycles are stale")
    print("T73_FINAL_PASSAGE_CYCLES=FIVE_FINAL_COMPONENT_PASSAGE_CYCLES_CONSTRUCTED")


if __name__ == "__main__":
    main()
