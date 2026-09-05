#!/usr/bin/env python3
"""Construct all six t-band disks in the actual octahedral belt collar S2 x I."""

from __future__ import annotations

import argparse
import hashlib
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


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def midpoint(first, second):
    return tuple((first[index] + second[index]) / 2 for index in range(4))


def add(point, normal):
    return tuple(point[index] + normal[index] for index in range(4))


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
        centerline = [
            as_point(point if len(point) == 4 else [*point, "1/2"])
            for point in band["band_core_on_belt_sphere"]
        ]
        attachment = interval_by_band[index]
        source_pair = [as_point(point) for point in attachment["source_interval"]]
        target_pair = [as_point(point) for point in attachment["target_interval"]]
        if midpoint(*source_pair) != centerline[0] or midpoint(*target_pair) != centerline[-1]:
            raise AssertionError(f"t-band {index} centerline misses its attachment midpoint")
        if any(point[3] != Fraction(1, 2) or sum(abs(value) for value in point[:3]) != radius for point in centerline):
            raise AssertionError(f"t-band {index} centerline leaves the belt sphere")
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
        section_normals = [as_point(normal) for normal in extension["normal_field"]]
        if len(section_normals) != len(cross_sections):
            raise AssertionError(f"t-band {index} framing/collar lengths disagree")
        normals = [normal for normal in section_normals for _ in range(2)]
        push_vertices = [add(point, normal) for point, normal in zip(vertices, normals)]
        surfaces.append({
            "band_index": index,
            "movie_time_order": band["movie_time_order"],
            "component": band["component"],
            "centerline": [encode(point) for point in centerline],
            "vertices": [encode(point) for point in vertices],
            "triangles": triangles,
            "boundary": {
                "source_attachment": [0, 1],
                "negative_u_lane": [2 * position for position in range(len(cross_sections))],
                "target_attachment": [len(vertices) - 2, len(vertices) - 1],
                "positive_u_lane": [2 * position + 1 for position in reversed(range(len(cross_sections)))],
            },
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
