#!/usr/bin/env python3
"""Independently verify the complete final y/z passage and foot state."""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_final_yz_foot_state.json"
BASE = ROOT / "geometry/t73_yz_foot_lane_binding.json"
FEET = ROOT / "geometry/t73_ar_foot_pairing_model.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
X_DELETION = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"
PERIOD = Fraction(4)


def point(values):
    return tuple(Fraction(value) for value in values)


def matrix_apply(matrix, value):
    return tuple(
        sum(Fraction(entry) * coordinate for entry, coordinate in zip(row, value))
        for row in matrix
    )


def symmetric(value):
    return value - PERIOD * ((value + PERIOD / 2) // PERIOD)


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    base = json.loads(BASE.read_text(encoding="utf-8"))
    feet = json.loads(FEET.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    foliation = json.loads(FOLIATION.read_text(encoding="utf-8"))
    local_movie = json.loads(LOCAL_MOVIE.read_text(encoding="utf-8"))
    x_deletion = json.loads(X_DELETION.read_text(encoding="utf-8"))
    if data["completion_status"] != "FINAL_YZ_PASSAGES_AND_FOOT_REFLECTIONS_CONSTRUCTED":
        raise AssertionError("final y/z foot-state scope changed")
    expected_hashes = {
        "base_yz_binding_sha256": base["sha256"],
        "ar_foot_model_sha256": feet["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "m1_parallel_foliation_sha256": foliation["sha256"],
        "x_local_movie_sha256": local_movie["sha256"],
        "post_x_m1_deletion_sha256": x_deletion["sha256"],
    }
    if any(data[field] != value for field, value in expected_hashes.items()):
        raise AssertionError("final y/z foot state has stale sources")
    foot_by_index = {item["handle_index"]: item for item in feet["feet"]}
    handles = {item["name"]: item for item in data["handles"]}
    if set(handles) != {"y", "z"} or x_deletion["deletion"]["remaining_one_handles"] != ["y", "z"]:
        raise AssertionError("final y/z handle inventory changed")

    reflection_checks = 0
    all_ids = set()
    for name, handle in handles.items():
        foot = foot_by_index[handle["foot_handle_index"]]
        matrix = foot["reflection_matrix"]
        positive_center = point(foot["positive_center"])
        radius = Fraction(foot["radius"])
        endpoint_pairs = set()
        for passage in handle["passages"]:
            passage_id = passage["passage_id"]
            if passage_id in all_ids:
                raise AssertionError("duplicate final y/z passage id")
            all_ids.add(passage_id)
            positive = point(passage["positive_foot_endpoint"])
            negative = point(passage["negative_foot_endpoint"])
            if matrix_apply(matrix, positive) != negative:
                raise AssertionError("final passage endpoints are not reflection paired")
            if sum((positive[index] - positive_center[index]) ** 2 for index in range(3)) >= radius**2:
                raise AssertionError("final passage endpoint left its foot disk")
            pair = (negative, positive)
            if pair in endpoint_pairs:
                raise AssertionError("two final passages share a foot endpoint pair")
            endpoint_pairs.add(pair)
            reflection_checks += 1
    y_kinds = Counter(item["source_kind"] for item in handles["y"]["passages"])
    z_kinds = Counter(item["source_kind"] for item in handles["z"]["passages"])
    if y_kinds != {"johnson_base_arc": 230, "dual_disk_boundary": 4}:
        raise AssertionError("final y passage decomposition changed")
    if z_kinds != {
        "johnson_base_arc": 32,
        "dual_disk_boundary": 4,
        "x_slide_m1_parallel_z_lane": 1513,
    }:
        raise AssertionError("final z passage decomposition changed")

    replacements = {
        int(item["passage_id"].split(":")[1]): item
        for item in handles["z"]["passages"]
        if item["source_kind"] == "x_slide_m1_parallel_z_lane"
    }
    base_vertices = [point(value) for value in foliation["base_vertices"]]
    normals = [point(value) for value in foliation["unit_normal_field"]]
    middle = base_vertices[19]
    normal = normals[19]
    for record in local_movie["bands"]:
        index = record["band_index"]
        passage = replacements[index]
        level = record["target_parallel_coefficient"]
        expected_belt = (
            symmetric(middle[0] + level * normal[0]),
            symmetric(middle[1] + level * normal[1]),
            Fraction(1),
        )
        if point(passage["belt_point"]) != expected_belt:
            raise AssertionError("replacement z-lane belt point changed")
        if passage["parallel_level"] != level or passage["component"] != record["component"] or passage["orientation"] != record["source_orientation"]:
            raise AssertionError("replacement z-lane owner/orientation changed")
        if Fraction(passage["tangent_z_offset_removed"]) != level * normal[2]:
            raise AssertionError("replacement z-lane tangent adjustment changed")
    if (handles["y"]["passage_count"], handles["z"]["passage_count"]) != (234, 1549):
        raise AssertionError("final y/z passage counts changed")
    return {
        "verdict": "PASS_FINAL_YZ_FOOT_AND_PASSAGE_STATE",
        "y_passages": 234,
        "z_passages": 1549,
        "johnson_base_passages": 262,
        "dual_passages": 8,
        "x_replacement_z_passages": 1513,
        "reflection_pair_checks": reflection_checks,
        "unique_passage_ids": len(all_ids),
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
