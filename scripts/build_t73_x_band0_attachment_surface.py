#!/usr/bin/env python3
"""Build x-band 0 with actual post-t-cancellation source/target attachments."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from build_t73_t_hcs_cancellation_readiness import final_states

ROOT = Path(__file__).resolve().parents[1]
POST_CANCEL = ROOT / "geometry/t73_t_hcs_handle_pair_deletion.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
OUTPUT = ROOT / "geometry/t73_x_band0_attachment_surface.json"
PERIOD = Fraction(4)


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def translate(value, deck):
    return tuple(value[axis] + PERIOD * deck[axis] for axis in range(3)) + (value[3],)


def find_current_arc(points, local_arc):
    matches = []
    for index in range(len(points) - len(local_arc) + 1):
        candidate = points[index : index + len(local_arc)]
        differences = [
            (candidate[0][axis] - local_arc[0][axis]) / PERIOD
            for axis in range(3)
        ]
        if any(value.denominator != 1 for value in differences):
            continue
        deck = tuple(int(value) for value in differences)
        if candidate == [translate(value, deck) for value in local_arc]:
            matches.append((index, deck))
    if len(matches) != 1:
        raise AssertionError(f"x-band 0 source arc has {len(matches)} post-cancel occurrences")
    return matches[0]


def build() -> dict:
    post_cancel = json.loads(POST_CANCEL.read_text(encoding="utf-8"))
    x_cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    band = x_cancellation["slide_bands"][0]
    source_arc_record = next(
        item for item in spine["handle_arcs"] if item["arc_id"] == band["source_id"]
    )
    local_arc = [point([*value, "1"]) for value in source_arc_record["lift_polyline"]]
    current_points, current_normals, _ = final_states()["m_2"]
    current_index, deck = find_current_arc(current_points, local_arc)

    width = Fraction(band["band_width"])
    source_center = local_arc[1]
    source_interval = [
        (source_center[0] - width, *source_center[1:]),
        (source_center[0] + width, *source_center[1:]),
    ]
    target_y, target_z, target_normal = point(band["parallel_m1_target"])
    target_interval = [
        (Fraction(2) - width, target_y, target_z, target_normal),
        (Fraction(2) + width, target_y, target_z, target_normal),
    ]
    centerline = [
        (Fraction(2), *point(value)) for value in band["band_core_on_positive_belt_face"]
    ]
    if centerline[0] != source_center or centerline[-1][1:] != point(band["parallel_m1_target"]):
        raise AssertionError("x-band 0 centerline lost an attachment center")

    cross_sections = []
    for center in centerline:
        cross_sections.append([
            (center[0] - width, *center[1:]),
            (center[0] + width, *center[1:]),
        ])
    vertices = [value for pair in cross_sections for value in pair]
    triangles = []
    for index in range(len(cross_sections) - 1):
        left = 2 * index
        triangles.extend([[left, left + 2, left + 3], [left, left + 3, left + 1]])
    actual_source_normal = current_normals[current_index + 1]
    source_normal_mod_x_tangent = (
        Fraction(0),
        actual_source_normal[1],
        actual_source_normal[2],
        actual_source_normal[3],
    )
    target_parallel_normal = (Fraction(0), width, Fraction(0), Fraction(0))
    denominator = len(cross_sections) - 1
    section_normals = [
        tuple(
            source_normal_mod_x_tangent[axis]
            + Fraction(index, denominator)
            * (target_parallel_normal[axis] - source_normal_mod_x_tangent[axis])
            for axis in range(4)
        )
        for index in range(len(cross_sections))
    ]
    normal_field = [normal for normal in section_normals for _ in range(2)]
    pushed = [
        tuple(value[axis] + normal[axis] for axis in range(4))
        for value, normal in zip(vertices, normal_field)
    ]
    result = {
        "schema": "t73_x_band0_attachment_surface/v1",
        "post_t_hcs_deletion_sha256": post_cancel["sha256"],
        "x_cancellation_sha256": x_cancellation["sha256"],
        "johnson_spine_embedding_sha256": spine["sha256"],
        "band_index": 0,
        "component": "m_2",
        "source_id": band["source_id"],
        "source_arc_local": [encode(value) for value in local_arc],
        "source_arc_current_state_vertex_range": [current_index, current_index + 2],
        "source_arc_current_state_deck": list(deck),
        "source_interval_local": [encode(value) for value in source_interval],
        "source_interval_current_state": [
            encode(translate(value, deck)) for value in source_interval
        ],
        "target_parallel_m1_interval_local": [encode(value) for value in target_interval],
        "target_parallel_coefficient": int(target_y / width),
        "centerline": [encode(value) for value in centerline],
        "vertices": [encode(value) for value in vertices],
        "triangles": triangles,
        "boundary": {
            "source_attachment": [0, 1],
            "negative_x_lane": [2 * index for index in range(len(cross_sections))],
            "target_attachment": [len(vertices) - 2, len(vertices) - 1],
            "positive_x_lane": [
                2 * index + 1 for index in reversed(range(len(cross_sections)))
            ],
        },
        "actual_source_normal_current_state": encode(actual_source_normal),
        "source_normal_mod_x_tangent": encode(source_normal_mod_x_tangent),
        "target_parallel_normal": encode(target_parallel_normal),
        "normal_field": [encode(value) for value in normal_field],
        "normal_extension_rule": "linear nonzero homotopy (0,w,(1-t)w,0)",
        "push_off_vertices": [encode(value) for value in pushed],
        "completion_status": "X_BAND0_ACTUAL_ATTACHMENTS_BOUNDARY_FRAMING_DERIVED",
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
        raise AssertionError("x-band 0 attachment surface is stale")
    print(f"T73_X_BAND0={result['completion_status']}")


if __name__ == "__main__":
    main()
