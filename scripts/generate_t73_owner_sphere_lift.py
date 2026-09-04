#!/usr/bin/env python3
"""Lift the T73 spherical H2 columns to the five two-handle owners."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any


OWNER_ORDER = ["m_2", "m_3", "r_xy", "r_yz", "r_zx"]
ROOT = Path(__file__).resolve().parents[1]
SPINE = ROOT / "geometry" / "t73_johnson_spine_embedding.json"
CANCEL_X = ROOT / "geometry" / "t73_cancel_x_m1.json"
CUT = ROOT / "geometry" / "t73_actual_cut_tangle.json"


def load_kirby() -> ModuleType:
    path = Path(__file__).resolve().parent / "generate_t73_compact_kirby_ledger.py"
    spec = importlib.util.spec_from_file_location("compact_kirby", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import compact Kirby generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def determinant2(matrix: list[list[int]]) -> int:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def multiply(matrix: list[list[int]], vector: list[int]) -> list[int]:
    return [sum(value * entry for value, entry in zip(row, vector)) for row in matrix]


def generate_ledger() -> dict[str, Any]:
    cut = json.loads(CUT.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    cancel_x = json.loads(CANCEL_X.read_text(encoding="utf-8"))
    sphere_ledger_path = Path(__file__).resolve().parent / "generate_t73_sphere_slide_ledger.py"
    spec = importlib.util.spec_from_file_location("sphere_ledger", sphere_ledger_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import sphere slide ledger")
    sphere_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sphere_module)
    sphere_data = sphere_module.generate_ledger()
    sphere_columns = sphere_data["sphere_coordinate_matrix"]
    m2_events = cut["post_x_event_lists"]["m_2"]
    m2 = {
        axis: sum(event["orientation"] for event in m2_events if event["label"] == axis)
        for axis in ("y", "z")
    }
    m3_arcs = [arc for arc in spine["handle_arcs"] if int(arc["component"]) == 2]
    m3 = {
        "y": sum(int(arc["sign"]) for arc in m3_arcs if int(arc["axis"]) == 1),
        "z": sum(int(arc["sign"]) for arc in m3_arcs if int(arc["axis"]) in (0, 2)) - 1,
    }
    boundary = [
        [m2["y"], m3["y"], 0, 0, 0],
        [m2["z"], m3["z"], 0, 0, 0],
    ]
    active_minor = [row[:2] for row in boundary]
    if active_minor != [[40, 189], [269, 1271]]:
        raise AssertionError("compact boundary minor differs")
    if determinant2(active_minor) != -1:
        raise AssertionError("m2/m3 boundary minor is not unimodular")

    owner_lifts = [
        [0, 0, sphere_columns[0][column], sphere_columns[1][column], sphere_columns[2][column]]
        for column in range(3)
    ]
    for lift in owner_lifts:
        if multiply(boundary, lift) != [0, 0]:
            raise AssertionError("sphere owner lift is not a two-cycle")

    # Since the first two columns form a unimodular 2x2 matrix, every kernel
    # vector has zero m2 and m3 entries.  The remaining three owner coordinates
    # are therefore the unique integral lift of the displayed H2 coordinates.
    ledger = {
        "schema": "t73_five_owner_sphere_lift/v1",
        "owner_order": OWNER_ORDER,
        "one_handle_order": ["y", "z"],
        "cellular_boundary_d2": boundary,
        "m2_m3_minor_determinant": -1,
        "kernel_basis": [
            [0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1],
        ],
        "sphere_columns_in_kernel_basis": sphere_columns,
        "sphere_slide_ledger_sha256": sphere_data["ledger_sha256"],
        "actual_cut_tangle_sha256": cut["sha256"],
        "actual_spine_embedding_sha256": spine["sha256"],
        "actual_x_cancellation_sha256": cancel_x["sha256"],
        "owner_lifts": owner_lifts,
        "conclusion": (
            "the three five-owner lifts are unique integral two-cycles and "
            "involve only r_xy,r_yz,r_zx"
        ),
    }
    ledger["ledger_sha256"] = canonical_sha(ledger)
    return ledger


def main() -> None:
    print(json.dumps(generate_ledger(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
