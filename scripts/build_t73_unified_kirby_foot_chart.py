#!/usr/bin/env python3
"""Assemble AR Figure 2 feet with the T73 t/x belt-chart anchors."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FEET = ROOT / "geometry/t73_ar_foot_pairing_model.json"
BELTS = ROOT / "geometry/t73_belt_spheres.json"
FIXED = ROOT / "geometry/t73_ar_figure5_fixed_points.json"
FINAL_YZ = ROOT / "geometry/t73_final_yz_foot_state.json"
X_DELETION = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"
T_DELETION = ROOT / "geometry/t73_t_hcs_handle_pair_deletion.json"
OUTPUT = ROOT / "geometry/t73_unified_kirby_foot_chart.json"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def build() -> dict[str, Any]:
    feet = json.loads(FEET.read_text(encoding="utf-8"))
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    fixed = json.loads(FIXED.read_text(encoding="utf-8"))
    final_yz = json.loads(FINAL_YZ.read_text(encoding="utf-8"))
    x_deletion = json.loads(X_DELETION.read_text(encoding="utf-8"))
    t_deletion = json.loads(T_DELETION.read_text(encoding="utf-8"))
    final_by_name = {item["name"]: item for item in final_yz["handles"]}
    models = {item["handle_index"]: item for item in feet["feet"]}
    if set(models) != {0, 1, 2, 3}:
        raise AssertionError("AR foot model does not have four handles")
    handles = []
    for index, name in enumerate(("t", "x", "y", "z")):
        item = {"name": name, "foot_pair": models[index]}
        if name == "t":
            item.update({
                "binding_status": "BOUND_TO_T73_BELT_GEOMETRY",
                "belt_reference": "geometry/t73_belt_spheres.json#/t_handle",
                "attaching_component": belts["t_handle"]["attaching_component"],
                "passage_count": len(belts["t_handle"]["passages"]),
            })
        elif name == "x":
            item.update({
                "binding_status": "BOUND_TO_T73_BELT_GEOMETRY",
                "belt_reference": "geometry/t73_belt_spheres.json#/x_handle",
                "attaching_component": belts["x_handle"]["attaching_component"],
                "passage_count": len(belts["x_handle"]["passages"]),
            })
        else:
            item.update({
                "binding_status": "BOUND_TO_FINAL_T73_PASSAGE_AND_FOOT_GEOMETRY",
                "belt_reference": f"geometry/t73_final_yz_foot_state.json#/handles/{name}",
                "passage_count": final_by_name[name]["passage_count"],
                "passage_state_sha256": canonical_sha(final_by_name[name]),
            })
        handles.append(item)
    result = {
        "schema": "t73_unified_kirby_foot_chart/v2",
        "foot_model_sha256": feet["sha256"],
        "belt_spheres_sha256": belts["sha256"],
        "figure5_fixed_points_sha256": fixed["sha256"],
        "final_yz_foot_state_sha256": final_yz["sha256"],
        "post_x_m1_deletion_sha256": x_deletion["sha256"],
        "post_t_hcs_deletion_sha256": t_deletion["sha256"],
        "handles": handles,
        "cancelled_handle_pairs": [["t", "h_CS"], ["x", "m_1"]],
        "final_surviving_one_handles": x_deletion["deletion"]["remaining_one_handles"],
        "actual_binding_status": "ALL_FOUR_HANDLES_BOUND_FINAL_YZ_STATE",
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
        raise AssertionError("unified Kirby foot chart is stale")
    print(f"T73_UNIFIED_KIRBY_FOOT_CHART={result['actual_binding_status']}")


if __name__ == "__main__":
    main()
