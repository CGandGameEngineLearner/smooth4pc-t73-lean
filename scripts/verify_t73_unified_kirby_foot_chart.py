#!/usr/bin/env python3
"""Verify the final four-handle foot chart and its two surviving foot pairs."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from verify_t73_final_yz_foot_state import verify as verify_final_yz

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_unified_kirby_foot_chart.json"
FEET = ROOT / "geometry/t73_ar_foot_pairing_model.json"
BELTS = ROOT / "geometry/t73_belt_spheres.json"
FINAL_YZ = ROOT / "geometry/t73_final_yz_foot_state.json"
T_DELETION = ROOT / "geometry/t73_t_hcs_handle_pair_deletion.json"
X_DELETION = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"


def determinant3(matrix):
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    feet = json.loads(FEET.read_text(encoding="utf-8"))
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    final_yz = json.loads(FINAL_YZ.read_text(encoding="utf-8"))
    t_deletion = json.loads(T_DELETION.read_text(encoding="utf-8"))
    x_deletion = json.loads(X_DELETION.read_text(encoding="utf-8"))
    if data["actual_binding_status"] != "ALL_FOUR_HANDLES_BOUND_FINAL_YZ_STATE":
        raise AssertionError("unified foot chart is not fully bound")
    expected_hashes = {
        "foot_model_sha256": feet["sha256"],
        "belt_spheres_sha256": belts["sha256"],
        "final_yz_foot_state_sha256": final_yz["sha256"],
        "post_t_hcs_deletion_sha256": t_deletion["sha256"],
        "post_x_m1_deletion_sha256": x_deletion["sha256"],
    }
    if any(data[field] != value for field, value in expected_hashes.items()):
        raise AssertionError("unified foot chart has stale source bindings")
    if verify_final_yz()["verdict"] != "PASS_FINAL_YZ_FOOT_AND_PASSAGE_STATE":
        raise AssertionError("final y/z foot state did not verify")
    handles = {item["name"]: item for item in data["handles"]}
    if set(handles) != {"t", "x", "y", "z"}:
        raise AssertionError("unified foot chart lost a handle")
    if [handles[name]["passage_count"] for name in ("t", "x", "y", "z")] != [7, 1514, 235, 1550]:
        raise AssertionError("unified foot passage counts changed")
    for name, handle in handles.items():
        matrix = [[Fraction(value) for value in row] for row in handle["foot_pair"]["reflection_matrix"]]
        if determinant3(matrix) != -1:
            raise AssertionError(f"{name} foot map is not orientation reversing")
        if name in ("y", "z") and handle["binding_status"] != "BOUND_TO_FINAL_T73_PASSAGE_AND_FOOT_GEOMETRY":
            raise AssertionError(f"{name} final foot binding is incomplete")
    if data["cancelled_handle_pairs"] != [["t", "h_CS"], ["x", "m_1"]]:
        raise AssertionError("unified chart cancellation history changed")
    if data["final_surviving_one_handles"] != ["y", "z"]:
        raise AssertionError("unified chart has the wrong surviving handles")
    return {
        "verdict": "PASS_ALL_FOUR_T73_FOOT_BINDINGS_FINAL_YZ_STATE",
        "four_handle_passage_counts": [7, 1514, 235, 1550],
        "cancelled_pairs": 2,
        "surviving_dotted_handles": ["y", "z"],
        "final_reflection_paired_passages": 1785,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
