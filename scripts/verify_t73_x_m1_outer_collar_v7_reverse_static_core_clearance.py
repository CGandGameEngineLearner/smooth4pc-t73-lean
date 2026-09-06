#!/usr/bin/env python3
"""Independently verify reverse-ordered final/source core clearance."""

from __future__ import annotations

import gzip
import json
import sys
from itertools import pairwise
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
    point,
    resolve,
    subtract,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_static_core_clearance.json"
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
REVERSE = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_isotopy_trace_receipt.json"
)
REVERSE_VERIFY = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_isotopy_trace_verification.json"
)


def verify_full():
    data = json.loads(DATA.read_text())
    payload = {key: value for key, value in data.items() if key != "sha256"}
    collars = json.loads(COLLARS.read_text())
    reverse = json.loads(REVERSE.read_text())
    verification = json.loads(REVERSE_VERIFY.read_text())
    if (
        data["sha256"] != canonical_sha(payload)
        or data["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or data["reverse_trace_receipt_sha256"] != reverse["sha256"]
        or data["reverse_trace_verification_sha256"] != verification["sha256"]
    ):
        raise AssertionError("reverse mixed-core bindings changed")
    sources = []
    finals = []
    with gzip.open(resolve(collars["cache_path"]), "rt", encoding="utf-8") as stream:
        stream.readline()
        for line in stream:
            record = json.loads(line)
            interface = record["interface_index"]
            source = tuple(point(value) for value in record["source_core_segment"])
            sources.append((interface, record["neighbor_id"], source))
            vertices = [point(value) for value in record["final_core_vertices"]]
            finals.extend(
                (interface, record["neighbor_id"], local, segment)
                for local, segment in enumerate(pairwise(vertices))
            )
    properties = rtree_index.Property()
    properties.dimension = 3
    tree = rtree_index.Index(
        ((index, bounds(segment), None) for index, (*_, segment) in enumerate(sources)),
        properties=properties,
    )
    broad = separated = 0
    permitted = []
    for final_interface, final_neighbor, local, final_segment in finals:
        for source_index in tree.intersection(bounds(final_segment)):
            source_interface, source_neighbor, source_segment = sources[source_index]
            if final_interface <= source_interface:
                continue
            broad += 1
            if not intersects(final_segment, source_segment):
                separated += 1
                continue
            shared = set(final_segment) & set(source_segment)
            if local != 0 or final_neighbor != source_neighbor or len(shared) != 1:
                raise AssertionError(
                    "independent reverse core intersection is forbidden"
                )
            common = next(iter(shared))
            final_other = next(value for value in final_segment if value != common)
            source_other = next(value for value in source_segment if value != common)
            first = subtract(final_other, common)
            second = subtract(source_other, common)
            if cross(first, second) != (0, 0, 0) or dot(first, second) >= 0:
                raise AssertionError("independent reverse germ is not opposite")
            permitted.append(
                {
                    "final_interface": final_interface,
                    "source_interface": source_interface,
                    "neighbor_id": final_neighbor,
                    "shared_endpoint": [str(value) for value in common],
                    "relation": "COLLINEAR_OPPOSITE_GERMS",
                }
            )
    if (
        (broad, separated, len(permitted)) != (8, 4, 4)
        or permitted != data["permitted_opposite_germ_incidences"]
        or data["nonpermitted_intersection_count"] != 0
        or not data["reverse_mixed_static_core_clearance"]
    ):
        raise AssertionError("independent reverse core replay changed")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_REVERSE_STATIC_CORE_CLEARANCE_INDEPENDENT",
        "outward_float_aabb_candidates": broad,
        "exact_segment_checks": broad,
        "exact_separated_pairs": separated,
        "permitted_opposite_germ_incidences": len(permitted),
        "nonpermitted_intersections": 0,
        "reverse_mixed_static_core_clearance": True,
        "push_and_ribbon_status": "OPEN",
        "reverse_dynamic_status": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
