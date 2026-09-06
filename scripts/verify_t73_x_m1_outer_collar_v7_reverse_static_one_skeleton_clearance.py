#!/usr/bin/env python3
"""Independently replay reverse mixed one-skeleton matrices."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from verify_t73_x_m1_outer_collar_v7_sequential_static_core_clearance import (
    bounds,
    canonical_sha,
    cross,
    dot,
    intersects,
    subtract,
)
from verify_t73_x_m1_outer_collar_v7_sequential_static_one_skeleton_clearance import (
    MATRICES,
    TYPE_NAMES,
    load,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_static_one_skeleton_clearance.json"
)
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
CORE = ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_static_core_clearance.json"


def replay(records, name, final_key, source_key, allow_opposite):
    sources = [
        (record["interface"], record["neighbor_id"], record[source_key])
        for record in records
    ]
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        ((index, bounds(segment), None) for index, (*_, segment) in enumerate(sources)),
        properties=properties,
    )
    broad = separated = 0
    type_counts = {value: 0 for value in TYPE_NAMES}
    permitted = []
    for record in records:
        for local, final_segment in enumerate(record[final_key]):
            for source_index in tree.intersection(bounds(final_segment)):
                source_interface, source_neighbor, source_segment = sources[
                    source_index
                ]
                if record["interface"] <= source_interface:
                    continue
                broad += 1
                type_counts[TYPE_NAMES[local]] += 1
                if not intersects(final_segment, source_segment):
                    separated += 1
                    continue
                shared = set(final_segment) & set(source_segment)
                if (
                    not allow_opposite
                    or local != 0
                    or record["neighbor_id"] != source_neighbor
                    or len(shared) != 1
                ):
                    raise AssertionError(f"independent reverse {name} collision")
                common = next(iter(shared))
                final_other = next(value for value in final_segment if value != common)
                source_other = next(
                    value for value in source_segment if value != common
                )
                first = subtract(final_other, common)
                second = subtract(source_other, common)
                if cross(first, second) != (0, 0, 0) or dot(first, second) >= 0:
                    raise AssertionError(f"independent reverse {name} germ failed")
                permitted.append(
                    {
                        "final_interface": record["interface"],
                        "source_interface": source_interface,
                        "neighbor_id": record["neighbor_id"],
                        "shared_endpoint": [str(value) for value in common],
                        "relation": "COLLINEAR_OPPOSITE_GERMS",
                    }
                )
    return {
        "matrix": name,
        "broad": broad,
        "separated": separated,
        "permitted": permitted,
        "type_counts": {key: value for key, value in type_counts.items() if value},
    }


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    collars = json.loads(COLLARS.read_text())
    core = json.loads(CORE.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or data["reverse_static_core_clearance_sha256"] != core["sha256"]
        or not core["reverse_mixed_static_core_clearance"]
    ):
        raise AssertionError("reverse one-skeleton bindings changed")
    records = load(collars)
    results = [replay(records, *definition) for definition in MATRICES]
    saved = {value["matrix"]: value for value in data["remaining_directed_matrices"]}
    expected = {
        "push_push": (8, 4, 4),
        "core_push": (4, 4, 0),
        "push_core": (0, 0, 0),
    }
    for result in results:
        name = result["matrix"]
        if (
            (result["broad"], result["separated"], len(result["permitted"]))
            != expected[name]
            or result["type_counts"]
            != saved[name]["candidate_count_by_final_segment_type"]
            or result["permitted"] != saved[name]["permitted_opposite_germ_incidences"]
            or saved[name]["nonpermitted_intersection_count"] != 0
        ):
            raise AssertionError(f"independent reverse {name} replay changed")
    if (
        data["remaining_outward_float_aabb_candidate_count"] != 12
        or data["remaining_exact_segment_check_count"] != 12
        or data["remaining_exact_separated_pair_count"] != 8
        or data["remaining_permitted_opposite_germ_incidence_count"] != 4
        or data["remaining_nonpermitted_intersection_count"] != 0
        or not data["reverse_mixed_static_one_skeleton_clearance"]
    ):
        raise AssertionError("reverse one-skeleton aggregate changed")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_REVERSE_STATIC_ONE_SKELETON_CLEARANCE_INDEPENDENT",
        "directed_matrices_replayed": 3,
        "outward_float_aabb_candidates": 12,
        "exact_segment_checks": 12,
        "exact_separated_pairs": 8,
        "permitted_opposite_germ_incidences": 4,
        "nonpermitted_intersections": 0,
        "reverse_mixed_static_one_skeleton_clearance": True,
        "ribbon_status": "OPEN",
        "reverse_dynamic_status": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
