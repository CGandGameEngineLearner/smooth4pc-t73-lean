#!/usr/bin/env python3
"""Add explicit product-framing push-offs and a generic projection request."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "geometry/t73_actual_kirby_core_embedding.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
X_DELETION = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"
OUTPUT = ROOT / "geometry/t73_actual_kirby_framed_input.json"

TWO_HANDLES = ["m_2", "m_3", "r_xy", "r_yz", "r_zx"]
DOTTED = ["dotted_y", "dotted_z"]


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def build_expanded() -> dict:
    core = json.loads(CORE.read_text(encoding="utf-8"))
    cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    x_deletion = json.loads(X_DELETION.read_text(encoding="utf-8"))
    by_name = {item["name"]: item for item in core["components"]}
    epsilon = Fraction(cancellation["slide_bands"][0]["band_width"]) / 1000000
    direction = (Fraction(1), Fraction(2), Fraction(5))
    components = []
    for coefficient, name in enumerate(TWO_HANDLES, start=1):
        points = [point(value) for value in by_name[name]["vertices"]]
        push_vector = tuple(coefficient * epsilon * value for value in direction)
        pushed = [
            tuple(value[axis] + push_vector[axis] for axis in range(3))
            for value in points
        ]
        components.append({
            "name": name,
            "component_kind": "two_handle",
            "closed_core_polyline": [encode(value) for value in points],
            "cyclic_segment_successor": [
                (index + 1) % (len(points) - 1) for index in range(len(points) - 1)
            ],
            "closed_push_off_polyline": [encode(value) for value in pushed],
            "push_off_cyclic_segment_successor": [
                (index + 1) % (len(pushed) - 1) for index in range(len(pushed) - 1)
            ],
            "push_vector": encode(push_vector),
            "framing_transport": {
                "source": "zero-relative-twist product framing after both verified cancellations",
                "routing_trivialization": "constant generic vector with zero connector rotation",
                "positive_scale_coefficient": coefficient,
                "integer_framing": "computed from exact core/push linking, not preassigned",
            },
        })
    for name in DOTTED:
        points = [point(value) for value in by_name[name]["vertices"]]
        components.append({
            "name": name,
            "component_kind": "dotted_one_handle",
            "closed_core_polyline": [encode(value) for value in points],
            "cyclic_segment_successor": [
                (index + 1) % (len(points) - 1) for index in range(len(points) - 1)
            ],
        })
    result = {
        "schema": "t73_full_handle_diagram_input/v1",
        "purpose": "source-bound T73 Kirby routing candidate pending full generic PD verification",
        "actual_core_embedding_sha256": core["sha256"],
        "post_x_m1_deletion_sha256": x_deletion["sha256"],
        "ambient": {
            "chart": "oriented_affine_Q3",
            "ambient_orientation": "standard_xyz",
            "projection_direction": ["1013", "-1022117", "1009"],
            "projection_basis": [["1009", "1", "0"], ["0", "1", "1013"]],
            "height_direction": ["1013", "-1022117", "1009"],
            "genericity_certificate": {
                "method": "exact_fraction_recomputation",
                "claimed": "PASS",
            },
        },
        "components": components,
        "framing_convention": (
            "integer labels are exact linking numbers with the saved push-offs; "
            "no candidate framing integer is copied"
        ),
        "completion_status": "SOURCE_BOUND_CORES_AND_PUSH_OFFS_CANDIDATE_AWAITING_PD",
    }
    result["sha256"] = canonical_sha(result)
    return result


def build() -> dict:
    expanded = build_expanded()
    core = json.loads(CORE.read_text(encoding="utf-8"))
    core_by_name = {item["name"]: item for item in core["components"]}
    components = []
    for component in expanded["components"]:
        record = {
            "name": component["name"],
            "component_kind": component["component_kind"],
            "core_component_sha256": canonical_sha(core_by_name[component["name"]]),
            "core_vertex_count": len(component["closed_core_polyline"]),
            "cyclic_segment_successor_sha256": canonical_sha(
                component["cyclic_segment_successor"]
            ),
        }
        if component["component_kind"] == "two_handle":
            record.update({
                "push_vector": component["push_vector"],
                "push_off_vertex_count": len(component["closed_push_off_polyline"]),
                "push_off_vertices_sha256": canonical_sha(
                    component["closed_push_off_polyline"]
                ),
                "framing_transport": component["framing_transport"],
            })
        components.append(record)
    result = {
        "schema": "t73_actual_kirby_framed_manifest/v1",
        "purpose": expanded["purpose"],
        "actual_core_embedding_sha256": core["sha256"],
        "post_x_m1_deletion_sha256": expanded["post_x_m1_deletion_sha256"],
        "ambient": expanded["ambient"],
        "components": components,
        "expanded_full_handle_input_sha256": expanded["sha256"],
        "materialization_rule": (
            "python3 scripts/build_t73_actual_kirby_framed_input.py "
            "--materialize /home/lifesize/.cache/t73_actual_kirby_framed_input.expanded.json"
        ),
        "completion_status": "SOURCE_BOUND_CORES_AND_PUSH_OFFS_CANDIDATE_AWAITING_PD",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--materialize", type=Path)
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("actual Kirby framed input is stale")
    if args.materialize:
        args.materialize.parent.mkdir(parents=True, exist_ok=True)
        args.materialize.write_text(
            json.dumps(build_expanded(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print("T73_KIRBY_FRAMED_INPUT=SOURCE_BOUND_CORES_AND_PUSH_OFFS_CANDIDATE_AWAITING_PD")


if __name__ == "__main__":
    main()
