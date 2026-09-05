#!/usr/bin/env python3
"""Build four reflection-paired marked-strip collars into dotted-S3 charts."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOOT_MODEL = ROOT / "geometry/t73_ar_foot_pairing_model.json"
FINAL_FEET = ROOT / "geometry/t73_final_yz_foot_state.json"
AMBIENT = ROOT / "geometry/t73_dotted_disk_ambient_extensions.json"
DOTTED = ROOT / "geometry/t73_actual_dotted_s3_passage_cells.json"
OUTPUT = ROOT / "geometry/t73_dotted_s3_foot_collars.json"


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def add(left, right):
    return tuple(left[index] + right[index] for index in range(3))


def scale(factor, value):
    return tuple(factor * coordinate for coordinate in value)


def disk_point(center, basis, lane_scale, uv):
    return add(center, add(scale(lane_scale * uv[0], basis[0]), scale(lane_scale * uv[1], basis[1])))


def target_point(handle, foot, uv):
    center = Fraction(-4 if handle == "y" else 4)
    if foot == "positive":
        return (center - 2, uv[1], -Fraction(1, 2) + uv[0] / 10)
    return (center + 2, uv[1], Fraction(1, 2) + uv[0] / 10)


def prism_tetrahedra():
    result = []
    for triangle in ((0, 1, 2), (0, 2, 3)):
        a, b, c = sorted(triangle)
        result.extend(((a, b, c, c + 4), (a, b, b + 4, c + 4), (a, a + 4, b + 4, c + 4)))
    return [list(value) for value in result]


def build():
    foot_model = json.loads(FOOT_MODEL.read_text(encoding="utf-8"))
    final_feet = json.loads(FINAL_FEET.read_text(encoding="utf-8"))
    ambient = json.loads(AMBIENT.read_text(encoding="utf-8"))
    dotted = json.loads(DOTTED.read_text(encoding="utf-8"))
    feet_by_index = {item["handle_index"]: item for item in foot_model["feet"]}
    dotted_by_handle = {item["handle"]: item for item in dotted["charts"]}
    collars = []
    endpoint_records = []
    for handle_data in final_feet["handles"]:
        handle = handle_data["name"]
        foot = feet_by_index[handle_data["foot_handle_index"]]
        basis = tuple(point(value) for value in handle_data["tangent_basis"])
        lane_scale = Fraction(foot["radius"]) / 10
        entries = handle_data["passages"]
        count = len(entries)
        delta = Fraction(1, 4 * (count + 1))
        u_half = delta
        v_low, v_high = Fraction(1, 2 * (count + 1)), Fraction(2 * count + 1, 2 * (count + 1))
        normalized_vertices = [(-u_half, v_low), (u_half, v_low), (u_half, v_high), (-u_half, v_high)]
        chart_passages = {item["passage_id"]: item for item in dotted_by_handle[handle]["passages"]}
        for physical_foot in ("positive", "negative"):
            center = point(foot[f"{physical_foot}_center"])
            collars.append({
                "handle": handle,
                "physical_foot": physical_foot,
                "normalized_strip_vertices": [encode(value) for value in normalized_vertices],
                "source_disk_vertices": [encode(disk_point(center, basis, lane_scale, value)) for value in normalized_vertices],
                "target_chart_vertices": [encode(target_point(handle, physical_foot, value)) for value in normalized_vertices],
                "slice_triangles": [[0, 1, 2], [0, 2, 3]],
                "mapping_cylinder_tetrahedra": prism_tetrahedra(),
                "source_embedding_rule": "foot_center + radius/10*(u*tangent_basis_0+v*tangent_basis_1)",
                "target_embedding_rule": "fixed chart x; y=v; z=foot_sign/2+u/10",
            })
        for entry in entries:
            passage = chart_passages[entry["passage_id"]]
            uv = point(passage["normalized_foot_slot"])
            push_uv = (uv[0], uv[1] + delta)
            record = {
                "passage_id": entry["passage_id"],
                "handle": handle,
                "owner": entry["component"],
                "orientation": entry["orientation"],
                "normalized_slot": encode(uv),
                "normalized_push_slot": encode(push_uv),
                "feet": {},
            }
            for physical_foot in ("positive", "negative"):
                center = point(foot[f"{physical_foot}_center"])
                record["feet"][physical_foot] = {
                    "source_endpoint": encode(disk_point(center, basis, lane_scale, uv)),
                    "source_push_endpoint": encode(disk_point(center, basis, lane_scale, push_uv)),
                    "target_endpoint": encode(target_point(handle, physical_foot, uv)),
                    "target_push_endpoint": encode(target_point(handle, physical_foot, push_uv)),
                }
            endpoint_records.append(record)
    result = {
        "schema": "t73_dotted_s3_foot_collars/v1",
        "ar_foot_pairing_model_sha256": foot_model["sha256"],
        "final_yz_foot_state_sha256": final_feet["sha256"],
        "dotted_disk_ambient_extensions_sha256": ambient["sha256"],
        "actual_dotted_s3_passage_cells_sha256": dotted["sha256"],
        "collars": collars,
        "endpoint_records": endpoint_records,
        "collar_count": len(collars),
        "mapping_cylinder_tetrahedron_count": len(collars) * 6,
        "passage_count": len(endpoint_records),
        "endpoint_pair_count": 2 * len(endpoint_records),
        "completion_status": "REFLECTION_PAIRED_FRAMED_MARKED_STRIP_COLLARS_TO_DOTTED_S3_CONSTRUCTED",
        "scope_boundary": "maps all marked foot endpoints and product pushes; extension across the central connector complement remains open",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true"); parser.add_argument("--check", action="store_true")
    args = parser.parse_args(); result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("dotted-S3 foot collars are stale")
    print(f"T73_DOTTED_S3_FOOT_COLLARS={result['completion_status']}")


if __name__ == "__main__":
    main()
