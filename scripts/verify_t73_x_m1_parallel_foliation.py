#!/usr/bin/env python3
"""Verify the quotient annulus containing all 1513 framed m1 parallels."""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from pathlib import Path

from build_t73_t_hcs_cancellation_readiness import final_states
from verify_t73_candidate_t_band0_quotient_splice import (
    translate_segment,
)
from verify_t73_candidate_t_band0_splice import exact_segment_intersection
from verify_t73_candidate_t_band0_surface import (
    segment_meets_triangle,
    triangles_intersect,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
PERIOD = Fraction(4)


def point(values):
    return tuple(Fraction(value) for value in values)


def floor(value):
    return value.numerator // value.denominator


def ceil(value):
    return -floor(-value)


def triangle_translations(first, second):
    ranges = []
    for axis in range(3):
        first_low = min(value[axis] for value in first)
        first_high = max(value[axis] for value in first)
        second_low = min(value[axis] for value in second)
        second_high = max(value[axis] for value in second)
        low = ceil((first_low - second_high) / PERIOD)
        high = floor((first_high - second_low) / PERIOD)
        if low > high:
            return []
        ranges.append(range(low, high + 1))
    if max(value[3] for value in first) < min(value[3] for value in second) or max(
        value[3] for value in second
    ) < min(value[3] for value in first):
        return []
    return itertools.product(*ranges)


def translate_triangle(triangle, deck):
    return tuple(
        tuple(value[axis] + PERIOD * deck[axis] for axis in range(3)) + (value[3],)
        for value in triangle
    )


def triangle_segment_translations(triangle, segment):
    ranges = []
    for axis in range(3):
        triangle_low = min(value[axis] for value in triangle)
        triangle_high = max(value[axis] for value in triangle)
        segment_low, segment_high = sorted(
            (segment[0][axis], segment[1][axis])
        )
        low = ceil((triangle_low - segment_high) / PERIOD)
        high = floor((triangle_high - segment_low) / PERIOD)
        if low > high:
            return []
        ranges.append(range(low, high + 1))
    if max(value[3] for value in triangle) < min(
        segment[0][3], segment[1][3]
    ) or max(segment[0][3], segment[1][3]) < min(
        value[3] for value in triangle
    ):
        return []
    return itertools.product(*ranges)


def quotient_coordinate(value):
    return value - PERIOD * ((value + PERIOD / 2) // PERIOD)


def spatial_triangle_meets_segment(triangle, segment):
    embedded_triangle = tuple((*value, Fraction(0)) for value in triangle)
    embedded_segment = tuple((*value, Fraction(0)) for value in segment)
    origin, first, second = embedded_triangle
    left = tuple(first[index] - origin[index] for index in range(4))
    right = tuple(second[index] - origin[index] for index in range(4))
    nondegenerate = any(
        left[j] * right[i] != left[i] * right[j]
        for i in range(4)
        for j in range(i + 1, 4)
    )
    if nondegenerate:
        return segment_meets_triangle(embedded_segment, embedded_triangle)
    edges = [
        (triangle[index], triangle[(index + 1) % 3]) for index in range(3)
    ]
    return any(exact_segment_intersection(segment, edge) for edge in edges)


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    if data["completion_status"] != "ALL_1513_M1_PARALLELS_IN_ONE_QUOTIENT_ANNULUS":
        raise AssertionError("m1 parallel foliation scope changed")
    base = [point(value) for value in data["base_vertices"]]
    normals = [point(value) for value in data["unit_normal_field"]]
    outer = [point(value) for value in data["outer_vertices"]]
    if base != final_states()["m_1"][0]:
        raise AssertionError("parallel foliation has the wrong m1 base")
    maximum = data["maximum_parallel_coefficient"]
    if any(
        tuple(value[axis] + maximum * normal[axis] for axis in range(4)) != pushed
        for value, normal, pushed in zip(base, normals, outer)
    ):
        raise AssertionError("outer foliation boundary is not the maximum level")
    levels = data["parallel_levels"]
    if levels != list(range(20, 30261, 20)) or len(set(levels)) != 1513:
        raise AssertionError("m1 parallel levels changed")
    if any(not any(normal) for normal in normals):
        raise AssertionError("m1 foliation normal field meets zero")
    vertices = [*base, *outer]
    triangle_ids = data["triangles"]
    triangles = [tuple(vertices[index] for index in ids) for ids in triangle_ids]
    seam_triangles = set(data["mapping_torus_seam_triangle_indices"])
    self_checks = 0
    for first_index, first in enumerate(triangles):
        if first_index in seam_triangles:
            continue
        for second_index in range(first_index + 1, len(triangles)):
            if second_index in seam_triangles:
                continue
            second = triangles[second_index]
            for deck in triangle_translations(first, second):
                deck = tuple(deck)
                if deck == (0, 0, 0) and set(triangle_ids[first_index]) & set(
                    triangle_ids[second_index]
                ):
                    continue
                if (
                    first_index // 2 == 0
                    and second_index // 2 == len(base) - 2
                    and deck == (1, 0, -1)
                ):
                    continue
                self_checks += 1
                if triangles_intersect(first, translate_triangle(second, deck)):
                    raise AssertionError(
                        "m1 quotient framing annulus self-intersects at "
                        f"{first_index}/{second_index}/{deck}"
                    )

    states = final_states()
    curve_checks = 0
    for triangle_index, triangle in enumerate(triangles):
        if triangle_index in seam_triangles:
            continue
        for component in ("m_2", "m_3"):
            other_points, _, other_seams = states[component]
            for segment_index, segment in enumerate(zip(other_points, other_points[1:])):
                if segment_index in other_seams:
                    continue
                for deck in triangle_segment_translations(triangle, segment):
                    curve_checks += 1
                    if segment_meets_triangle(translate_segment(segment, tuple(deck)), triangle):
                        raise AssertionError(f"m1 framing annulus meets {component}")
    dual_checks = 0
    for triangle_index, triangle in enumerate(triangles):
        if triangle_index in seam_triangles:
            continue
        spatial_triangle = tuple(
            tuple(quotient_coordinate(coordinate) for coordinate in value[:3])
            for value in triangle
        )
        for component in ("r_xy", "r_yz", "r_zx"):
            dual = [point(value) for value in ar_link["components"][component]["polyline"]]
            for segment in zip(dual, dual[1:]):
                dual_checks += 1
                if spatial_triangle_meets_segment(spatial_triangle, segment):
                    raise AssertionError(f"m1 framing annulus spatially meets {component}")
    return {
        "verdict": "PASS_ALL_1513_M1_PARALLELS_IN_EMBEDDED_QUOTIENT_ANNULUS",
        "parallel_levels": len(levels),
        "maximum_coefficient": maximum,
        "triangles": len(triangles),
        "seam_triangles_as_gluing_cells": len(seam_triangles),
        "exact_annulus_self_checks": self_checks,
        "exact_m2_m3_checks": curve_checks,
        "exact_dual_projection_checks": dual_checks,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
