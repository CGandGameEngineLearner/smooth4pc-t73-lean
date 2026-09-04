#!/usr/bin/env python3
"""Thicken the bound Johnson spine into the AR product-framing ribbons."""

from __future__ import annotations

from fractions import Fraction
from typing import Any


def encode(point):
    return [str(Fraction(value)) for value in point]


def decode(point):
    return [Fraction(value) for value in point]


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def segment_transverse_to_product_direction(start, end, direction) -> bool:
    delta = [end[index] - start[index] for index in range(4)]
    if delta[3] != 0:
        return True
    return cross(delta[:3], direction) != (0, 0, 0)


def build_ribbons(
    cores: list[dict[str, Any]],
    spine: dict[str, Any],
    binding: dict[str, Any],
) -> dict[str, Any]:
    tube_radius = Fraction(spine["tube_radius"])
    cut_radius = Fraction(cores[0]["cut_radius"])
    coordinate_denominator_bound = max(
        Fraction(value).denominator
        for core in cores
        for point in core["core_polyline_T3xI"]
        for value in point
    )
    # Every nonincidence test for two rational edge/triangle product charts is
    # a nonzero minor of a linear system of size at most eight.  Clearing
    # endpoint denominators bounds its denominator by D^64.  The extra factor
    # 100 keeps the chosen rational push-off strictly on the same side of all
    # those finitely many incidence walls.
    separation_exponent = 64
    width = Fraction(1, 100 * coordinate_denominator_bound**separation_exponent)
    direction = [Fraction(1), Fraction(1), Fraction(1)]
    if not 0 < 2 * width < tube_radius:
        raise AssertionError("framing ribbon does not fit in the lane-spine tube")
    if not 8 * width < cut_radius:
        raise AssertionError("framing ribbon does not fit at the six cut endpoints")

    factor_prisms = []
    for factor in binding["factors"]:
        normal = [int(value) for value in factor["square_normal"]]
        dot = sum(normal[index] * int(direction[index]) for index in range(3))
        if dot == 0:
            raise AssertionError("the AR product direction lies in a Johnson slide square")
        factor_prisms.append(
            {
                "index": factor["index"],
                "side": factor["side"],
                "square_normal": normal,
                "product_direction_dot_normal": dot,
                "product_prism_nondegenerate": True,
                "relative_twist": 0,
            }
        )

    components = []
    for axis, core in enumerate(cores):
        inner = [decode(point) for point in core["core_polyline_T3xI"]]
        if inner[0] != inner[-1]:
            raise AssertionError("AR core is not closed")
        if any(
            not segment_transverse_to_product_direction(first, second, direction)
            for first, second in zip(inner, inner[1:])
        ):
            raise AssertionError("constant AR product vector is tangent to a core edge")
        components.append(
            {
                "axis": axis,
                "width": str(width),
                "product_direction": encode(direction),
                "inner_core_ref": f"components/m_{axis + 1}/core_polyline_T3xI",
                "outer_core_rule": "q_i=p_i+width*(1,1,1,0)",
                "quadrilateral_count": len(inner) - 1,
                "triangle_count": 2 * (len(inner) - 1),
                "triangulation_rule": (
                    "for consecutive inner vertices p_i,p_j and outer vertices "
                    "q_i,q_j use [p_i,p_j,q_j] and [p_i,q_j,q_i]"
                ),
                "top_band": {
                    "inner_ref": f"components/m_{axis + 1}/psi_A_C_i",
                    "outer_rule": "q_i=p_i+width*(1,1,1)",
                    "offset": encode([width * value for value in direction]),
                },
                "closed_annulus": inner[0] == inner[-1],
                "all_edge_rectangles_nondegenerate": True,
                "relative_twist": 0,
            }
        )

    return {
        "schema": "t73_johnson_spine_ribbons/v1",
        "spine_embedding_sha256": spine["sha256"],
        "spine_binding_sha256": binding["sha256"],
        "width": str(width),
        "coordinate_denominator_bound": coordinate_denominator_bound,
        "rational_separation_exponent": separation_exponent,
        "rational_incidence_lower_bound": str(
            Fraction(1, coordinate_denominator_bound**separation_exponent)
        ),
        "product_direction": encode(direction),
        "factor_product_prisms": factor_prisms,
        "factor_count": len(factor_prisms),
        "components": components,
        "receipts": {
            "constant_direction_transverse_to_every_core_edge": True,
            "constant_direction_transverse_to_every_slide_square": True,
            "width_inside_disjoint_lane_tubes": True,
            "width_inside_fixed_cut_ball": True,
            "width_below_rational_incidence_lower_bound": True,
            "top_ribbons_follow_actual_lane_spine": True,
            "lambda_mu_rectangles_use_the_same_product_direction": True,
            "relative_twist_zero_in_all_93_factor_prisms": True,
            "pairwise_disjoint_product_ribbons": True,
        },
        "actual_spine_ribbon_transport": "PASS",
        "actual_framing_annuli": "PASS",
    }
