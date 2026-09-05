#!/usr/bin/env python3
"""Construct exact zero-linking push-offs for the five railroad core curves."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from export_t73_full_handle_diagram import curve_crossings, pairwise_linking_matrix

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "geometry/t73_actual_railroad_core_coordinates.json"
X_DELETION = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"
OUTPUT = ROOT / "geometry/t73_railroad_product_framings.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def build() -> dict:
    core = json.loads(CORE.read_text(encoding="utf-8"))
    x_deletion = json.loads(X_DELETION.read_text(encoding="utf-8"))
    curves = []
    components = []
    for component_index, component in enumerate(core["components"]):
        name = component["name"]
        points = [point(value) for value in component["vertices"]]
        epsilon = Fraction(component_index + 1, 10**9)
        if name == "r_zx":
            push_vector = (epsilon, 2 * epsilon, 3 * epsilon)
        else:
            push_vector = (-epsilon, -epsilon, -epsilon)
        pushed = [
            tuple(value[axis] + push_vector[axis] for axis in range(3))
            for value in points
        ]
        curves.extend([
            {"name": name, "points": points},
            {"name": f"{name}__push_off", "points": pushed},
        ])
        components.append({
            "name": name,
            "push_vector": encode(push_vector),
            "push_vertices": [encode(value) for value in pushed],
            "transport_rule": (
                "constant generic vector on the zero-twist railroad product collar; "
                "r_zx uses the positive asymmetric vector to avoid a collinear diamond projection"
            ),
        })
    basis = [(Fraction(1), Fraction(0), Fraction(0)), (Fraction(0), Fraction(1), Fraction(0))]
    height = (Fraction(0), Fraction(0), Fraction(1))
    crossings = curve_crossings(
        curves, basis, height, include_self=True, require_unique_projection_points=True
    )
    names = [curve["name"] for curve in curves]
    linking = pairwise_linking_matrix(names, crossings)
    integer_framings = {}
    receipts = {}
    for component in components:
        name = component["name"]
        push_name = f"{name}__push_off"
        first = names.index(name)
        second = names.index(push_name)
        framing = linking[first][second]
        integer_framings[name] = framing
        receipts[name] = {
            "core_owner": name,
            "push_owner": push_name,
            "mixed_signed_sum": 2 * framing,
            "integer_linking": framing,
        }
    if integer_framings != {name: 0 for name in ("m_2", "m_3", "r_xy", "r_yz", "r_zx")}:
        raise AssertionError("railroad product push-offs do not all have zero linking")
    result = {
        "schema": "t73_railroad_product_framings/v1",
        "railroad_core_coordinates_sha256": core["sha256"],
        "post_x_m1_deletion_sha256": x_deletion["sha256"],
        "components": components,
        "framed_curve_order": names,
        "framed_crossings": crossings,
        "framed_crossing_count": len(crossings),
        "framed_pairwise_linking_matrix": linking,
        "integer_surgery_framings": integer_framings,
        "framing_linking_receipts": receipts,
        "genericity": {
            "all_cores_and_push_offs_disjoint": "PASS",
            "no_vertex_crossings": "PASS",
            "no_repeated_projection_points": "PASS",
            "no_equal_height_crossings": "PASS",
        },
        "source_transport_status": "OPEN_HYBRID_TO_RAILROAD_FRAMED_ISOTOPY",
        "completion_status": "RAILROAD_TARGET_ZERO_PRODUCT_FRAMINGS_VERIFIED",
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
        raise AssertionError("railroad product framings are stale")
    print(f"T73_RAILROAD_FRAMINGS={result['completion_status']} crossings={result['framed_crossing_count']}")


if __name__ == "__main__":
    main()
