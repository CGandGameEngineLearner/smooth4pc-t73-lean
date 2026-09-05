#!/usr/bin/env python3
"""Independently verify the six t-band disks in the octahedral belt collar."""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

from verify_t73_candidate_t_band0_surface import triangle_nondegenerate, triangles_intersect
from verify_t73_candidate_t_band0_splice import exact_segment_intersection

ROOT = Path(__file__).resolve().parents[1]
SURFACES = ROOT / "geometry/t73_t_band_collar_surfaces.json"
BELTS = ROOT / "geometry/t73_belt_spheres.json"
INTERVALS = ROOT / "geometry/t73_t_band_attachment_intervals.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def edge(first, second):
    return tuple(sorted((first, second)))


def chain_edges(chain):
    return {edge(first, second) for first, second in zip(chain, chain[1:])}


def verify_disk(surface, attachment, radius):
    vertices = [point(value) for value in surface["vertices"]]
    triangles = surface["triangles"]
    if any(not triangle_nondegenerate(vertices, triangle) for triangle in triangles):
        raise AssertionError(f"t-band {surface['band_index']} has a degenerate collar triangle")
    counts = Counter(edge(triangle[i], triangle[(i + 1) % 3]) for triangle in triangles for i in range(3))
    if set(counts.values()) - {1, 2}:
        raise AssertionError("t-band collar surface is not a triangle manifold")
    boundary = surface["boundary"]
    expected_boundary = {
        edge(*boundary["source_attachment"]),
        edge(*boundary["target_attachment"]),
        *chain_edges(boundary["negative_u_lane"]),
        *chain_edges(boundary["positive_u_lane"]),
    }
    actual_boundary = {item for item, count in counts.items() if count == 1}
    if actual_boundary != expected_boundary or len(vertices) - len(counts) + len(triangles) != 1:
        raise AssertionError("t-band collar surface is not the declared disk")
    if [vertices[index] for index in boundary["source_attachment"]] != [point(value) for value in attachment["source_interval"]]:
        raise AssertionError("t-band collar source attachment changed")
    expected_target = [point(value) for value in attachment["target_interval"]]
    if surface["target_input_order_reversed_for_untwisted_ribbon"]:
        expected_target.reverse()
    if [vertices[index] for index in boundary["target_attachment"]] != expected_target:
        raise AssertionError("t-band collar target attachment changed")
    centerline = [point(value) for value in surface["centerline"]]
    if any(center[3] != Fraction(1, 2) or sum(abs(value) for value in center[:3]) != radius for center in centerline):
        raise AssertionError("t-band centerline left the actual octahedral belt sphere")
    negative_lane = [vertices[index] for index in boundary["negative_u_lane"]]
    positive_lane = [vertices[index] for index in boundary["positive_u_lane"]]
    if any(
        exact_segment_intersection(first, second)
        for first in zip(negative_lane, negative_lane[1:])
        for second in zip(positive_lane, positive_lane[1:])
    ):
        raise AssertionError("t-band collar has crossing boundary lanes")
    geometric_triangles = [tuple(vertices[index] for index in triangle) for triangle in triangles]
    local_checks = 0
    for first_index, first_triangle in enumerate(triangles):
        for second_index in range(first_index + 1, len(triangles)):
            second_triangle = triangles[second_index]
            if set(first_triangle) & set(second_triangle):
                continue
            local_checks += 1
            if triangles_intersect(
                geometric_triangles[first_index], geometric_triangles[second_index]
            ):
                raise AssertionError(
                    f"t-band {surface['band_index']} has a nonlocal self-intersection"
                )
    return geometric_triangles, local_checks


def verify() -> dict:
    data = json.loads(SURFACES.read_text(encoding="utf-8"))
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    intervals = json.loads(INTERVALS.read_text(encoding="utf-8"))
    if data["completion_status"] != "COLLAR_SURFACES_CONSTRUCTED_FRAMING_INTERIORS_CANDIDATE":
        raise AssertionError("t-band collar status changed")
    radius = Fraction(belts["t_handle"]["belt_sphere"]["radius"])
    attachments = {item["band_index"]: item for item in intervals["intervals"]}
    triangle_sets = []
    movie_time_levels = []
    local_self_intersection_checks = 0
    for surface in data["surfaces"]:
        triangles, checks = verify_disk(
            surface, attachments[surface["band_index"]], radius
        )
        triangle_sets.append(triangles)
        movie_time_levels.append(surface["movie_time_order"])
        local_self_intersection_checks += checks
    if sorted(movie_time_levels) != list(range(len(triangle_sets))):
        raise AssertionError("t-band collar movie levels are not a total sequential order")

    exact_pair_checks = 0
    spatial_intersections = set()
    for first_index, first_triangles in enumerate(triangle_sets):
        for second_index in range(first_index + 1, len(triangle_sets)):
            for first_triangle in first_triangles:
                for second_triangle in triangle_sets[second_index]:
                    exact_pair_checks += 1
                    if triangles_intersect(first_triangle, second_triangle):
                        spatial_intersections.add((first_index, second_index))
    return {
        "verdict": "PASS_T_BAND_COLLAR_DISKS_SEQUENTIAL_CANDIDATE_FRAMING_ONLY",
        "surfaces": len(triangle_sets),
        "movie_time_levels": sorted(movie_time_levels),
        "local_self_intersection_checks": local_self_intersection_checks,
        "exact_interband_triangle_checks": exact_pair_checks,
        "spatial_intersections_requiring_distinct_movie_times": [
            list(pair) for pair in sorted(spatial_intersections)
        ],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
