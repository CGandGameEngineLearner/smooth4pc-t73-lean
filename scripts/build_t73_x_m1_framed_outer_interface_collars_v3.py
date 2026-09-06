#!/usr/bin/env python3
"""Build source-germ collars with separated functional/height waypoint routes."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

from build_t73_x_m1_framed_outer_interface_collars import (
    add,
    affine_vector_hits_zero,
    canonical,
    canonical_sha,
    cross,
    encode,
    file_sha,
    point,
    subtract,
)

ROOT = Path(__file__).resolve().parents[1]
GAP = ROOT / "audit/t73_x_m1_complete_framed_outer_interface_gap.json"
V2 = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v2_receipt.json"
V2_OBSTRUCTION = ROOT / "audit/t73_x_m1_outer_collar_v2_ribbon_self_clearance.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v3_receipt.json"
DEFAULT_OUTPUT = (
    Path.home() / ".cache/t73_x_m1_framed_outer_interface_collars_v3.jsonl.gz"
)
GERM_FRACTION = Fraction(1, 1_000_000)
SLOPE = 1_000_033
FUNCTIONAL_Z = 2
LIFT_DIRECTION = (Fraction(0), Fraction(-2), Fraction(1))


def scale(factor, value):
    return tuple(factor * coordinate for coordinate in value)


def functional(value):
    return value[1] - SLOPE * value[0] + FUNCTIONAL_Z * value[2]


def lift_to_height(value, height):
    parameter = height - value[2]
    return add(value, scale(parameter, LIFT_DIRECTION))


def route(start, end, interface_index):
    height = Fraction(10_000 + interface_index)
    exterior_x = Fraction(50_000 + 2 * interface_index)
    start_high = lift_to_height(start, height)
    end_high = lift_to_height(end, height)
    start_exterior = (
        exterior_x,
        start_high[1] + SLOPE * (exterior_x - start_high[0]),
        height,
    )
    end_exterior = (
        exterior_x + 1,
        end_high[1] + SLOPE * (exterior_x + 1 - end_high[0]),
        height,
    )
    return [start, start_high, start_exterior, end_exterior, end_high, end]


def ribbon_triangles(vertex_count):
    return [
        triangle
        for index in range(vertex_count - 1)
        for triangle in (
            [index, index + 1, vertex_count + index + 1],
            [index, vertex_count + index + 1, vertex_count + index],
        )
    ]


def build(output_path):
    gap = json.loads(GAP.read_text())
    v2 = json.loads(V2.read_text())
    obstruction = json.loads(V2_OBSTRUCTION.read_text())
    if obstruction["classification"] != "CANDIDATE_REFUTED":
        raise AssertionError("v3 requires the exact v2 ribbon obstruction")
    endpoints = []
    prepared = []
    for interface in gap["interfaces"]:
        inner = point(interface["source_inner_core"])
        source = point(interface["source_core_port"])
        target = point(interface["target_core_port"])
        germ = add(inner, scale(GERM_FRACTION, subtract(source, inner)))
        endpoints.extend((germ, target))
        prepared.append((interface, inner, source, germ, target))
    values = sorted(functional(value) for value in endpoints)
    if len(values) != len(set(values)):
        raise AssertionError("v3 routing functional is not injective on endpoints")
    minimum_functional_separation = min(
        right - left for left, right in pairwise(values)
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_framed_outer_interface_collars/v3",
        "outer_interface_gap_sha256": gap["sha256"],
        "refuted_v2_receipt_sha256": v2["sha256"],
        "v2_ribbon_obstruction_sha256": obstruction["sha256"],
        "source_germ_fraction": str(GERM_FRACTION),
        "routing_functional": [str(-SLOPE), "1", str(FUNCTIONAL_Z)],
        "lift_direction": [str(value) for value in LIFT_DIRECTION],
        "height_rule": "10000+interface_index",
        "exterior_x_rule": "50000+2*interface_index",
        "construction_classification": "CANDIDATE_UNVERIFIED_UNTIL_GLOBAL_CLEARANCE_AND_AMBIENT_SUPPORT",
    }
    records = segments = triangles = exact_checks = 0
    with (
        output_path.open("wb") as raw,
        gzip.GzipFile(
            filename="", fileobj=raw, mode="wb", compresslevel=6, mtime=0
        ) as output,
    ):
        encoded = (canonical(header) + "\n").encode()
        output.write(encoded)
        digest.update(encoded)
        for interface, inner, source, germ, target in prepared:
            source_normal = subtract(point(interface["source_push_port"]), source)
            target_normal = subtract(point(interface["target_push_port"]), target)
            routed = route(germ, target, interface["interface_index"])
            core = [inner, *routed]
            normals = [source_normal] * (len(core) - 1) + [target_normal]
            push = [add(vertex, normal) for vertex, normal in zip(core, normals)]
            if core[1] != germ or core[-1] != target:
                raise AssertionError("v3 route endpoint changed")
            if functional(routed[0]) != functional(routed[1]) or functional(
                routed[-2]
            ) != functional(routed[-1]):
                raise AssertionError("v3 skew lift changes routing functional")
            if (
                routed[1][1] - SLOPE * routed[1][0]
                != routed[2][1] - SLOPE * routed[2][0]
            ):
                raise AssertionError("v3 first exterior ray changes planar functional")
            if (
                routed[3][1] - SLOPE * routed[3][0]
                != routed[4][1] - SLOPE * routed[4][0]
            ):
                raise AssertionError("v3 last exterior ray changes planar functional")
            for index in range(len(core) - 1):
                tangent = subtract(core[index + 1], core[index])
                first_cross = cross(tangent, normals[index])
                second_cross = cross(tangent, normals[index + 1])
                if affine_vector_hits_zero(first_cross, second_cross):
                    raise AssertionError("v3 route normal becomes tangent")
                exact_checks += 1
            record = {
                "record": "framed_outer_interface_collar_v3",
                "interface_index": interface["interface_index"],
                "band_index": interface["band_index"],
                "component": interface["component"],
                "side": interface["side"],
                "neighbor_kind": interface["neighbor_kind"],
                "neighbor_id": interface["neighbor_id"],
                "source_core_segment": [
                    interface["source_inner_core"],
                    interface["source_core_port"],
                ],
                "source_push_segment": [
                    interface["source_inner_push"],
                    interface["source_push_port"],
                ],
                "source_germ_fraction": str(GERM_FRACTION),
                "routing_height": str(10_000 + interface["interface_index"]),
                "routing_exterior_x": str(50_000 + 2 * interface["interface_index"]),
                "final_core_vertices": [encode(value) for value in core],
                "final_normal_field": [encode(value) for value in normals],
                "final_push_vertices": [encode(value) for value in push],
                "final_ribbon_triangles": ribbon_triangles(len(core)),
                "segment_count": len(core) - 1,
                "relative_twist": 0,
                "functional_route_checks": 4,
                "global_core_push_ribbon_clearance_status": "OPEN",
                "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_ISOTOPY_EXTENSION",
                "classification": "CANDIDATE_UNVERIFIED",
            }
            encoded = (canonical(record) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            records += 1
            segments += len(core) - 1
            triangles += len(record["final_ribbon_triangles"])
    receipt = {
        "schema": "t73_x_m1_framed_outer_interface_collars_v3_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha(Path(__file__)),
        "outer_interface_gap_sha256": gap["sha256"],
        "refuted_v2_receipt_sha256": v2["sha256"],
        "v2_ribbon_obstruction_sha256": obstruction["sha256"],
        "source_germ_fraction": str(GERM_FRACTION),
        "routing_functional": [str(-SLOPE), "1", str(FUNCTIONAL_Z)],
        "lift_direction": [str(value) for value in LIFT_DIRECTION],
        "routing_endpoint_count": len(endpoints),
        "minimum_routing_functional_separation": str(minimum_functional_separation),
        "collar_count": records,
        "final_core_segment_count": segments,
        "final_push_segment_count": segments,
        "final_ribbon_triangle_count": triangles,
        "normal_transversality_check_count": exact_checks,
        "relative_twist_sum": 0,
        "classification": "CANDIDATE_UNVERIFIED",
        "global_clearance_status": "OPEN",
        "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_ISOTOPY_EXTENSION",
        "completion_status": "ALL_OUTER_INTERFACE_COLLAR_V3_SEPARATED_WAYPOINT_CANDIDATES_CONSTRUCTED",
        "verdict": "PASS_X_M1_FRAMED_OUTER_INTERFACE_COLLARS_V3_LOCAL_CANDIDATE",
    }
    receipt["sha256"] = canonical_sha(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build(
        args.output
        or Path(os.environ.get("T73_X_M1_OUTER_COLLAR_V3_CACHE", DEFAULT_OUTPUT))
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "collars": result["collar_count"],
                "segments": result["final_core_segment_count"],
                "triangles": result["final_ribbon_triangle_count"],
                "functional_endpoints": result["routing_endpoint_count"],
                "classification": result["classification"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
