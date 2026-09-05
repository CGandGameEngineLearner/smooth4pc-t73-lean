#!/usr/bin/env python3
"""Build the complete post-cancellation y/z belt passages and foot endpoints."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "geometry/t73_yz_foot_lane_binding.json"
FEET = ROOT / "geometry/t73_ar_foot_pairing_model.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
HYBRID = ROOT / "geometry/t73_x_band_hybrid_movie.json"
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
X_DELETION = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"
OUTPUT = ROOT / "geometry/t73_final_yz_foot_state.json"
PERIOD = Fraction(4)


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def add(left, right):
    return tuple(left[index] + right[index] for index in range(3))


def scale(value, vector):
    return tuple(value * coordinate for coordinate in vector)


def symmetric(value):
    return value - PERIOD * ((value + PERIOD / 2) // PERIOD)


def foot_endpoints(foot, tangent_basis, lane):
    positive_center = point(foot["positive_center"])
    negative_center = point(foot["negative_center"])
    lane_scale = Fraction(foot["radius"]) / 10
    offset = add(
        scale(lane_scale * lane[0], tangent_basis[0]),
        scale(lane_scale * lane[1], tangent_basis[1]),
    )
    return add(negative_center, offset), add(positive_center, offset)


def dual_axis_passages(ar_link, axis, handle_name, foot, tangent_basis):
    transverse_axes = [value for value in range(3) if value != axis]
    passages = []
    for component in ("r_xy", "r_yz", "r_zx"):
        polyline = [point(value) for value in ar_link["components"][component]["polyline"]]
        for index in range(len(polyline) - 2):
            triple = polyline[index : index + 3]
            axis_values = [value[axis] for value in triple]
            if axis_values not in ([Fraction(1), Fraction(2), Fraction(3)], [Fraction(3), Fraction(2), Fraction(1)]):
                continue
            if any(
                triple[position][transverse] != triple[0][transverse]
                for position in range(1, 3)
                for transverse in transverse_axes
            ):
                continue
            orientation = 1 if axis_values[0] == 1 else -1
            lane = tuple(symmetric(triple[1][value]) for value in transverse_axes)
            negative, positive = foot_endpoints(foot, tangent_basis, lane)
            passages.append({
                "passage_id": f"{component}:{handle_name}:edge:{index}",
                "source_kind": "dual_disk_boundary",
                "component": component,
                "orientation": orientation,
                "belt_point": encode((*lane, Fraction(1))),
                "negative_foot_endpoint": encode(negative),
                "positive_foot_endpoint": encode(positive),
            })
    return passages


def build() -> dict:
    base = json.loads(BASE.read_text(encoding="utf-8"))
    feet = json.loads(FEET.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    foliation = json.loads(FOLIATION.read_text(encoding="utf-8"))
    hybrid = json.loads(HYBRID.read_text(encoding="utf-8"))
    local_movie = json.loads(LOCAL_MOVIE.read_text(encoding="utf-8"))
    x_deletion = json.loads(X_DELETION.read_text(encoding="utf-8"))
    foot_by_index = {item["handle_index"]: item for item in feet["feet"]}
    base_by_name = {item["name"]: item for item in base["handles"]}
    y_basis = tuple(point(value) for value in base_by_name["y"]["tangent_basis"])
    z_basis = tuple(point(value) for value in base_by_name["z"]["tangent_basis"])

    y_passages = [
        {**item, "passage_id": item["arc_id"], "source_kind": "johnson_base_arc"}
        for item in base_by_name["y"]["passages"]
    ]
    z_passages = [
        {**item, "passage_id": item["arc_id"], "source_kind": "johnson_base_arc"}
        for item in base_by_name["z"]["passages"]
        if item["arc_id"] != "c0:letter:0"
    ]
    y_passages.extend(
        dual_axis_passages(ar_link, 1, "y", foot_by_index[2], y_basis)
    )
    z_passages.extend(
        dual_axis_passages(ar_link, 2, "z", foot_by_index[3], z_basis)
    )

    m1_base = [point(value) for value in foliation["base_vertices"]]
    m1_normals = [point(value) for value in foliation["unit_normal_field"]]
    z_arc_range = [18, 20]
    if [value[2] for value in m1_base[18:21]] != [5, 6, 7]:
        raise AssertionError("m1 z-lane range changed in its universal lift")
    z_middle = m1_base[19]
    z_normal = m1_normals[19]
    for record in local_movie["bands"]:
        level = record["target_parallel_coefficient"]
        lane = (
            symmetric(z_middle[0] + level * z_normal[0]),
            symmetric(z_middle[1] + level * z_normal[1]),
        )
        negative, positive = foot_endpoints(foot_by_index[3], z_basis, lane)
        z_passages.append({
            "passage_id": f"x_replacement:{record['band_index']}:m1_z",
            "source_kind": "x_slide_m1_parallel_z_lane",
            "component": record["component"],
            "orientation": record["source_orientation"],
            "parallel_level": level,
            "base_m1_z_global_vertex_range": z_arc_range,
            "tangent_z_offset_removed": str(level * z_normal[2]),
            "belt_point": encode((*lane, Fraction(1))),
            "negative_foot_endpoint": encode(negative),
            "positive_foot_endpoint": encode(positive),
        })
    y_passages.sort(key=lambda item: item["passage_id"])
    z_passages.sort(key=lambda item: item["passage_id"])
    if (len(y_passages), len(z_passages)) != (234, 1549):
        raise AssertionError("final y/z passage inventory changed")
    result = {
        "schema": "t73_final_yz_foot_state/v1",
        "base_yz_binding_sha256": base["sha256"],
        "ar_foot_model_sha256": feet["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "m1_parallel_foliation_sha256": foliation["sha256"],
        "x_hybrid_movie_sha256": hybrid["sha256"],
        "x_local_movie_sha256": local_movie["sha256"],
        "post_x_m1_deletion_sha256": x_deletion["sha256"],
        "handles": [
            {
                "name": "y",
                "foot_handle_index": 2,
                "belt_sphere": base_by_name["y"]["belt_sphere"],
                "tangent_basis": base_by_name["y"]["tangent_basis"],
                "passages": y_passages,
                "passage_count": len(y_passages),
            },
            {
                "name": "z",
                "foot_handle_index": 3,
                "belt_sphere": base_by_name["z"]["belt_sphere"],
                "tangent_basis": base_by_name["z"]["tangent_basis"],
                "passages": z_passages,
                "passage_count": len(z_passages),
            },
        ],
        "completion_status": "FINAL_YZ_PASSAGES_AND_FOOT_REFLECTIONS_CONSTRUCTED",
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
        raise AssertionError("final y/z foot state is stale")
    print("T73_FINAL_YZ_FEET=FINAL_YZ_PASSAGES_AND_FOOT_REFLECTIONS_CONSTRUCTED")


if __name__ == "__main__":
    main()
