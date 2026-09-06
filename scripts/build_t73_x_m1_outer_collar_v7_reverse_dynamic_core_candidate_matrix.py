#!/usr/bin/env python3
"""Build the complete conservative matrix for reverse dynamic core clearance."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import sys
from collections import Counter
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

from rtree import index as rtree_index

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_outer_collar_v7_sequential_isotopy_trace import resolve

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
COLLARS = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
REVERSE = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_isotopy_trace_receipt.json"
)
REVERSE_VERIFY = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_isotopy_trace_verification.json"
)
VOLUME = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_framed_isotopy_volume_receipt.json"
)
VOLUME_VERIFY = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_reverse_sequential_framed_isotopy_volume_verification.json"
)
STATIC_CORE = ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_static_core_clearance.json"
OUTPUT = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_reverse_dynamic_core_candidate_matrix.json"
)
FUNCTIONALS = (
    (1, 0, 0, 0),
    (0, 1, 0, 0),
    (0, 0, 1, 0),
    (0, 0, 0, 1),
    (-1000033, 1, 2, 0),
    (-1000033, 1, 0, 0),
    (-1000033, 1, 2, 1000000),
    (-1000033, 1, 2, -1000000),
    (0, 0, 1, 10000),
    (0, 0, 1, -10000),
    (1, 0, 0, 50000),
    (1, 0, 0, -50000),
)
ACTIVE_TYPES = (
    "source_to_start_skew",
    "source_to_first_exterior",
    "source_to_height_bridge",
    "source_to_last_exterior",
    "source_to_end_skew",
)
FINAL_TYPES = (
    "retained_source_germ",
    "start_skew_lift",
    "first_exterior_ray",
    "staggered_height_bridge",
    "staggered_last_exterior_ray",
    "end_skew_lift",
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


def functional_box(vertices):
    values = [
        [
            sum(
                coefficient * coordinate for coefficient, coordinate in zip(row, vertex)
            )
            for vertex in vertices
        ]
        for row in FUNCTIONALS
    ]
    low = [min(row) for row in values]
    high = [max(row) for row in values]
    return tuple(math.nextafter(float(value), -math.inf) for value in low) + tuple(
        math.nextafter(float(value), math.inf) for value in high
    )


def vertical_triangles(segment):
    vertices = (
        (*segment[0], Fraction(0)),
        (*segment[1], Fraction(0)),
        (*segment[0], Fraction(1)),
        (*segment[1], Fraction(1)),
    )
    return (
        (vertices[0], vertices[1], vertices[3]),
        (vertices[0], vertices[3], vertices[2]),
    )


def load_active(receipt):
    triangles = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            vertices = [
                point(value) for value in record["phase_one_core_spacetime_vertices"]
            ]
            triangles.extend(
                (
                    record["interface_index"],
                    local // 2,
                    local,
                    tuple(vertices[index] for index in cell),
                )
                for local, cell in enumerate(record["phase_one_core_trace_triangles"])
            )
    return triangles


def load_static(receipt):
    sources = []
    finals = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            interface = record["interface_index"]
            source_segment = tuple(
                point(value) for value in record["source_core_segment"]
            )
            sources.extend(
                (interface, half, triangle)
                for half, triangle in enumerate(vertical_triangles(source_segment))
            )
            final_vertices = [point(value) for value in record["final_core_vertices"]]
            for semantic_type, segment in enumerate(pairwise(final_vertices)):
                finals.extend(
                    (interface, semantic_type, half, triangle)
                    for half, triangle in enumerate(vertical_triangles(segment))
                )
    return sources, finals


def build():
    local = json.loads(LOCAL.read_text())
    collars = json.loads(COLLARS.read_text())
    reverse = json.loads(REVERSE.read_text())
    reverse_verification = json.loads(REVERSE_VERIFY.read_text())
    volume = json.loads(VOLUME.read_text())
    volume_verification = json.loads(VOLUME_VERIFY.read_text())
    static_core = json.loads(STATIC_CORE.read_text())
    if (
        reverse["local_trace_receipt_sha256"] != local["sha256"]
        or reverse_verification["construction_receipt_sha256"] != reverse["sha256"]
        or volume["reverse_trace_receipt_sha256"] != reverse["sha256"]
        or volume_verification["construction_receipt_sha256"] != volume["sha256"]
        or static_core["outer_collars_v7_receipt_sha256"] != collars["sha256"]
        or not static_core["reverse_mixed_static_core_clearance"]
    ):
        raise AssertionError("reverse dynamic-core matrix inputs are stale or failed")
    active = load_active(local)
    sources, finals = load_static(collars)
    if (len(active), len(sources), len(finals)) != (30260, 6052, 36312):
        raise AssertionError("reverse dynamic-core triangle inventory changed")

    properties = rtree_index.Property()
    properties.dimension = len(FUNCTIONALS)
    source_tree = rtree_index.Index(
        (
            (index, functional_box(value[2]), None)
            for index, value in enumerate(sources)
        ),
        properties=properties,
    )
    final_tree = rtree_index.Index(
        ((index, functional_box(value[3]), None) for index, value in enumerate(finals)),
        properties=properties,
    )
    matrix = Counter()
    source_count = final_count = 0
    for interface, active_type, _local, triangle in active:
        query = functional_box(triangle)
        for source_index in source_tree.intersection(query):
            source_interface, _half, _triangle = sources[source_index]
            if source_interface < interface:
                source_count += 1
                matrix[f"active:{ACTIVE_TYPES[active_type]}/source:source_core"] += 1
        for final_index in final_tree.intersection(query):
            final_interface, final_type, _half, _triangle = finals[final_index]
            if final_interface > interface:
                final_count += 1
                matrix[
                    f"active:{ACTIVE_TYPES[active_type]}/final:{FINAL_TYPES[final_type]}"
                ] += 1
    total = source_count + final_count
    if (source_count, final_count, total, len(matrix)) != (
        18403145,
        26507429,
        44910574,
        14,
    ):
        raise AssertionError("reverse dynamic-core candidate totals changed")
    result = {
        "schema": "t73_x_m1_outer_collar_v7_reverse_dynamic_core_candidate_matrix/v1",
        "local_trace_receipt_sha256": local["sha256"],
        "outer_collars_v7_receipt_sha256": collars["sha256"],
        "reverse_trace_receipt_sha256": reverse["sha256"],
        "reverse_trace_verification_sha256": reverse_verification["sha256"],
        "reverse_framed_volume_receipt_sha256": volume["sha256"],
        "reverse_framed_volume_verification_sha256": volume_verification["sha256"],
        "reverse_static_core_clearance_sha256": static_core["sha256"],
        "schedule_order": "REVERSE_INTERFACE_INDEX",
        "linear_functionals": [list(value) for value in FUNCTIONALS],
        "outward_rounding": "one binary64 nextafter step in both directions",
        "active_phase_one_core_triangle_count": len(active),
        "source_vertical_core_triangle_count": len(sources),
        "final_vertical_core_triangle_count": len(finals),
        "source_candidate_count": source_count,
        "final_candidate_count": final_count,
        "total_candidate_count": total,
        "nonempty_semantic_type_pair_count": len(matrix),
        "semantic_candidate_matrix": dict(sorted(matrix.items())),
        "inventory_complete": True,
        "exact_clearance_status": "OPEN_APPLY_SEMANTIC_EXACT_R4_TRIANGLE_REDUCTIONS",
        "classification": "CANDIDATE_MATRIX_ONLY",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_REVERSE_DYNAMIC_CORE_CANDIDATE_MATRIX_ONLY",
    }
    result["sha256"] = canonical_sha(result)
    return result


def check_saved(result):
    payload = {key: value for key, value in result.items() if key != "sha256"}
    if result.get("sha256") != canonical_sha(payload):
        raise AssertionError("reverse dynamic-core matrix self hash changed")
    expected = {
        "source_candidate_count": 18403145,
        "final_candidate_count": 26507429,
        "total_candidate_count": 44910574,
        "nonempty_semantic_type_pair_count": 14,
        "inventory_complete": True,
        "exact_clearance_status": "OPEN_APPLY_SEMANTIC_EXACT_R4_TRIANGLE_REDUCTIONS",
        "classification": "CANDIDATE_MATRIX_ONLY",
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_REVERSE_DYNAMIC_CORE_CANDIDATE_MATRIX_ONLY",
    }
    if any(result.get(key) != value for key, value in expected.items()):
        raise AssertionError("reverse dynamic-core saved matrix changed")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--rebuild-check", action="store_true")
    args = parser.parse_args()
    result = (
        build() if args.write or args.rebuild_check else json.loads(OUTPUT.read_text())
    )
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.rebuild_check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("reverse dynamic-core candidate matrix is stale")
    check_saved(result)
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "active": result["active_phase_one_core_triangle_count"],
                "source": result["source_candidate_count"],
                "final": result["final_candidate_count"],
                "total": result["total_candidate_count"],
                "types": result["nonempty_semantic_type_pair_count"],
                "clearance": result["exact_clearance_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
