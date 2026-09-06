#!/usr/bin/env python3
"""Record the fixed retained-germ framing boundary missed by normal field 3017."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_t73_x_m1_outer_collar_v7_retained_ribbon_candidate_matrix as retained_module

ROOT = Path(__file__).resolve().parents[1]
NORMAL = ROOT / "geometry/t73_x_m1_outer_collar_v7_normal_field_3017.json"
CORE = ROOT / "geometry/t73_x_m1_outer_collar_v7_explicit_core_detour_3017.json"
RETAINED_CLEARANCE = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_retained_ribbon_clearance.json"
)
OUTPUT = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_retained_germ_boundary_obstruction_3017.json"
)


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def load_retained():
    gap = json.loads(retained_module.GAP.read_text())
    cycles = json.loads(retained_module.CYCLES.read_text())
    spine = json.loads(retained_module.SPINE.read_text())
    ar_link = json.loads(retained_module.AR_LINK.read_text())
    passages = json.loads(retained_module.PASSAGES.read_text())
    return retained_module.load_retained(gap, cycles, spine, ar_link, passages)[0]


def build():
    normal = json.loads(NORMAL.read_text())
    core = json.loads(CORE.read_text())
    clearance = json.loads(RETAINED_CLEARANCE.read_text())
    if (
        normal["explicit_core_detour_sha256"] != core["sha256"]
        or not clearance["global_retained_cross_clearance"]
        or normal["interface_index"] != 3017
    ):
        raise AssertionError("retained-germ boundary inputs are stale or failed")
    collars_receipt = json.loads(retained_module.COLLARS.read_text())
    collars = retained_module.load_collars(collars_receipt)
    germ = next(
        rectangle
        for rectangle in collars
        if rectangle["interface"] == 3017 and rectangle["type"] == 0
    )
    retained = load_retained()
    matches = [
        (index, rectangle)
        for index, rectangle in enumerate(retained)
        if rectangle["owner_id"] == germ["neighbor_id"]
        and len(set(rectangle["quad"]) & set(germ["quad"])) == 2
    ]
    if len(matches) != 1:
        raise AssertionError("interface-3017 retained framing adjacency changed")
    retained_index, rectangle = matches[0]
    retained_outer_edge = tuple(set(rectangle["quad"]) & set(germ["quad"]))
    fixed_edge = germ["target_edge"]
    core_states = [[point(vertex) for vertex in state] for state in core["states"]]
    push_states = [
        [point(vertex) for vertex in state] for state in normal["push_states"]
    ]
    state_edges = [
        (core_state[0], push_state[0])
        for core_state, push_state in zip(core_states, push_states)
    ]
    matching = [
        index for index, edge in enumerate(state_edges) if set(edge) == set(fixed_edge)
    ]
    mismatching = [index for index in range(len(state_edges)) if index not in matching]
    if matching != [0, 1, 2, 3, 4, 5, 17, 18, 19, 20, 21] or mismatching != list(
        range(6, 17)
    ):
        raise AssertionError(
            "normal-field retained-boundary mismatch pattern changed: "
            f"matching={matching} mismatching={mismatching}"
        )
    result = {
        "schema": "t73_x_m1_outer_collar_v7_retained_germ_boundary_obstruction/v1",
        "normal_field_sha256": normal["sha256"],
        "explicit_core_detour_sha256": core["sha256"],
        "retained_ribbon_clearance_sha256": clearance["sha256"],
        "interface_index": 3017,
        "retained_rectangle_index": retained_index,
        "retained_kind": rectangle["kind"],
        "retained_owner_id": rectangle["owner_id"],
        "retained_outer_shared_edge": [
            [str(coordinate) for coordinate in vertex] for vertex in retained_outer_edge
        ],
        "collar_germ_bridge_rectangle": [
            [str(coordinate) for coordinate in vertex] for vertex in germ["quad"]
        ],
        "fixed_framing_edge": [
            [str(coordinate) for coordinate in vertex] for vertex in fixed_edge
        ],
        "state_count": len(state_edges),
        "matching_state_indices": matching,
        "mismatching_state_indices": mismatching,
        "matching_state_count": len(matching),
        "mismatching_state_count": len(mismatching),
        "fixed_core_germ_vertex_all_states": len(
            {core_state[0] for core_state in core_states}
        )
        == 1,
        "fixed_push_germ_vertex_all_states": len(
            {push_state[0] for push_state in push_states}
        )
        == 1,
        "literal_retained_framing_boundary_status": "REFUTED",
        "normal_field_internal_status": "RETAINED",
        "required_repair": "FIX_PUSH_VERTEX_0_TO_SOURCE_NORMAL_AND_REPAIR_RELATIVE_FRAMING_TWIST",
        "verdict": "REFUTED_X_M1_OUTER_COLLAR_V7_RETAINED_GERM_BOUNDARY_3017",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("retained-germ boundary obstruction 3017 is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "retained": result["retained_rectangle_index"],
                "matching": result["matching_state_count"],
                "mismatching": result["mismatching_state_count"],
                "core_fixed": result["fixed_core_germ_vertex_all_states"],
                "push_fixed": result["fixed_push_germ_vertex_all_states"],
                "repair": result["required_repair"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
