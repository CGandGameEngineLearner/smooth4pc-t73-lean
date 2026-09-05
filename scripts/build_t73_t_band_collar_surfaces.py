#!/usr/bin/env python3
"""Construct all six t-band disks in the actual octahedral belt collar S2 x I."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from t73_pl_kirby_moves import as_point, encode

ROOT = Path(__file__).resolve().parents[1]
BELTS = ROOT / "geometry/t73_belt_spheres.json"
T_CANCELLATION = ROOT / "geometry/t73_cancel_t_hcs.json"
INTERVALS = ROOT / "geometry/t73_t_band_attachment_intervals.json"
FRAMING = ROOT / "geometry/t73_t_band_framing_extensions.json"
OUTPUT = ROOT / "geometry/t73_t_band_collar_surfaces.json"

# Fractions of the octahedral radius.  These canonical waypoints are introduced
# only when the original scheduled chord hits an earlier current-link state.
ROUTE_WAYPOINTS = {
    2: [(Fraction(0), Fraction(3, 4), Fraction(1, 4))],
    4: [(Fraction(1, 4), Fraction(1, 2), Fraction(1, 4))],
    5: [
        (Fraction(1, 4), Fraction(-3, 4), Fraction(0)),
        (Fraction(3, 4), Fraction(0), Fraction(1, 4)),
    ],
}


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def midpoint(first, second):
    return tuple((first[index] + second[index]) / 2 for index in range(4))


def add(point, normal):
    return tuple(point[index] + normal[index] for index in range(4))


def share_octahedral_face(first, second, radius):
    return any(
        sum(Fraction(signs[axis]) * first[axis] for axis in range(3)) == radius
        and sum(Fraction(signs[axis]) * second[axis] for axis in range(3)) == radius
        for signs in itertools.product((-1, 1), repeat=3)
    )


def build() -> dict[str, Any]:
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    cancellation = json.loads(T_CANCELLATION.read_text(encoding="utf-8"))
    intervals = json.loads(INTERVALS.read_text(encoding="utf-8"))
    framing = json.loads(FRAMING.read_text(encoding="utf-8"))
    radius = Fraction(belts["t_handle"]["belt_sphere"]["radius"])
    interval_by_band = {item["band_index"]: item for item in intervals["intervals"]}
    framing_by_band = {item["band_index"]: item for item in framing["extensions"]}
    surfaces = []
    for band in cancellation["slide_bands"]:
        index = band["index"]
        scheduled_centerline = [
            as_point(point if len(point) == 4 else [*point, "1/2"])
            for point in band["band_core_on_belt_sphere"]
        ]
        route_waypoints = [
            tuple(radius * coordinate for coordinate in waypoint) + (Fraction(1, 2),)
            for waypoint in ROUTE_WAYPOINTS.get(index, [])
        ]
        centerline = (
            [scheduled_centerline[0], *route_waypoints, scheduled_centerline[-1]]
            if index in ROUTE_WAYPOINTS
            else scheduled_centerline
        )
        attachment = interval_by_band[index]
        source_pair = [as_point(point) for point in attachment["source_interval"]]
        target_pair_input = [as_point(point) for point in attachment["target_interval"]]
        source_orientation = source_pair[1][3] - source_pair[0][3]
        target_orientation = target_pair_input[1][3] - target_pair_input[0][3]
        reverse_target = source_orientation * target_orientation < 0
        target_pair = list(reversed(target_pair_input)) if reverse_target else target_pair_input
        if midpoint(*source_pair) != centerline[0] or midpoint(*target_pair) != centerline[-1]:
            raise AssertionError(f"t-band {index} centerline misses its attachment midpoint")
        if any(point[3] != Fraction(1, 2) or sum(abs(value) for value in point[:3]) != radius for point in centerline):
            raise AssertionError(f"t-band {index} centerline leaves the belt sphere")
        if any(
            not share_octahedral_face(first, second, radius)
            for first, second in zip(centerline, centerline[1:])
        ):
            raise AssertionError(f"t-band {index} route cuts through the belt-ball interior")
        source_half_width = (source_pair[1][3] - source_pair[0][3]) / 2
        target_half_width = (target_pair[1][3] - target_pair[0][3]) / 2
        cross_sections = []
        denominator = len(centerline) - 1
        for position, center in enumerate(centerline):
            parameter = Fraction(position, denominator)
            half_width = source_half_width + parameter * (target_half_width - source_half_width)
            cross_sections.append([
                (*center[:3], center[3] - half_width),
                (*center[:3], center[3] + half_width),
            ])
        if cross_sections[0] != source_pair or cross_sections[-1] != target_pair:
            raise AssertionError(f"t-band {index} collar cross-sections lost their attachments")
        vertices = [point for pair in cross_sections for point in pair]
        triangles = []
        for position in range(len(cross_sections) - 1):
            left, right = 2 * position, 2 * position + 1
            next_left, next_right = left + 2, right + 2
            triangles.extend([[left, next_left, next_right], [left, next_right, right]])
        extension = framing_by_band[index]
        source_normal = as_point(extension["source_normal"])
        target_normal = as_point(extension["target_h_CS_normal"])
        section_normals = [
            tuple(
                source_normal[axis]
                + Fraction(position, denominator)
                * (target_normal[axis] - source_normal[axis])
                for axis in range(4)
            )
            for position in range(len(cross_sections))
        ]
        normals = [normal for normal in section_normals for _ in range(2)]
        push_vertices = [add(point, normal) for point, normal in zip(vertices, normals)]
        surfaces.append({
            "band_index": index,
            "movie_time_order": band["movie_time_order"],
            "component": band["component"],
            "centerline": [encode(point) for point in centerline],
            "scheduled_centerline": [encode(point) for point in scheduled_centerline],
            "route_waypoints": [encode(point) for point in route_waypoints],
            "vertices": [encode(point) for point in vertices],
            "triangles": triangles,
            "boundary": {
                "source_attachment": [0, 1],
                "negative_u_lane": [2 * position for position in range(len(cross_sections))],
                "target_attachment": [len(vertices) - 2, len(vertices) - 1],
                "positive_u_lane": [2 * position + 1 for position in reversed(range(len(cross_sections)))],
            },
            "target_input_order_reversed_for_untwisted_ribbon": reverse_target,
            "normal_field": [encode(normal) for normal in normals],
            "push_off_vertices": [encode(point) for point in push_vertices],
            "ambient_chart": "t-belt octahedral S2 x mapping-handle I collar",
            "status": "VERIFIED_COLLAR_DISK_CANDIDATE_FRAMING_INTERIOR",
        })
    result = {
        "schema": "t73_t_band_collar_surfaces/v1",
        "belt_spheres_sha256": belts["sha256"],
        "t_cancellation_sha256": cancellation["sha256"],
        "attachment_intervals_sha256": intervals["sha256"],
        "framing_extensions_sha256": framing["sha256"],
        "surfaces": surfaces,
        "completion_status": "COLLAR_SURFACES_CONSTRUCTED_FRAMING_INTERIORS_CANDIDATE",
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
        raise AssertionError("t-band collar surfaces are stale")
    print(f"T73_T_BAND_COLLAR_SURFACES={result['completion_status']}")


if __name__ == "__main__":
    main()
