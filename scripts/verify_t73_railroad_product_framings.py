#!/usr/bin/env python3
"""Independently verify all five railroad target product framings."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from export_t73_full_handle_diagram import curve_crossings, pairwise_linking_matrix

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_railroad_product_framings.json"
CORE = ROOT / "geometry/t73_actual_railroad_core_coordinates.json"
X_DELETION = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    core = json.loads(CORE.read_text(encoding="utf-8"))
    x_deletion = json.loads(X_DELETION.read_text(encoding="utf-8"))
    if data["completion_status"] != "RAILROAD_TARGET_ZERO_PRODUCT_FRAMINGS_VERIFIED":
        raise AssertionError("railroad framing scope changed")
    if data["railroad_core_coordinates_sha256"] != core["sha256"] or data["post_x_m1_deletion_sha256"] != x_deletion["sha256"]:
        raise AssertionError("railroad framings have stale sources")
    records = {item["name"]: item for item in data["components"]}
    curves = []
    for component_index, component in enumerate(core["components"]):
        name = component["name"]
        points = [point(value) for value in component["vertices"]]
        epsilon = Fraction(component_index + 1, 10**9)
        expected_vector = (
            (epsilon, 2 * epsilon, 3 * epsilon)
            if name == "r_zx"
            else (-epsilon, -epsilon, -epsilon)
        )
        if point(records[name]["push_vector"]) != expected_vector:
            raise AssertionError("railroad push vector changed")
        pushed = [
            tuple(value[axis] + expected_vector[axis] for axis in range(3))
            for value in points
        ]
        if [point(value) for value in records[name]["push_vertices"]] != pushed:
            raise AssertionError("railroad push vertices changed")
        curves.extend([
            {"name": name, "points": points},
            {"name": f"{name}__push_off", "points": pushed},
        ])
    basis = [(Fraction(1), Fraction(0), Fraction(0)), (Fraction(0), Fraction(1), Fraction(0))]
    height = (Fraction(0), Fraction(0), Fraction(1))
    crossings = curve_crossings(
        curves, basis, height, include_self=True, require_unique_projection_points=True
    )
    if crossings != data["framed_crossings"] or len(crossings) != 5144:
        raise AssertionError("railroad framed crossing list changed")
    names = [curve["name"] for curve in curves]
    linking = pairwise_linking_matrix(names, crossings)
    if linking != data["framed_pairwise_linking_matrix"]:
        raise AssertionError("railroad framed linking matrix changed")
    framings = {
        name: linking[names.index(name)][names.index(f"{name}__push_off")]
        for name in records
    }
    if framings != {name: 0 for name in records} or data["integer_surgery_framings"] != framings:
        raise AssertionError("railroad integer product framings changed")
    if data["source_transport_status"] != "OPEN_HYBRID_TO_RAILROAD_FRAMED_ISOTOPY":
        raise AssertionError("railroad target framing overstates source transport")
    return {
        "verdict": "PASS_RAILROAD_TARGET_FIVE_ZERO_PRODUCT_FRAMINGS",
        "framed_components": 5,
        "framed_curves": len(curves),
        "framed_crossings": len(crossings),
        "integer_surgery_framings": framings,
        "source_framed_isotopy": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
