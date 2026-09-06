#!/usr/bin/env python3
"""Independently replay the three rational PL dual-framing twists."""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from export_t73_full_handle_diagram import (
    add_scaled,
    det2,
    dot,
    projected_intersection,
    projection,
    sub,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_dual_zero_framing_twist_ribbons.json"
FRAMED_RECEIPT = ROOT / "audit/t73_affine_s3_product_framed_realization_receipt.json"
CORRECTION = ROOT / "geometry/t73_kirby_homology_admissible_correction.json"
DOTTED = ROOT / "geometry/t73_actual_dotted_s3_passage_cells.json"


def canonical_sha256(value: dict) -> str:
    unsigned = {key: item for key, item in value.items() if key != "sha256"}
    encoded = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def scale(factor, value):
    return tuple(factor * coordinate for coordinate in value)


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def replay_crossings(core, push, basis, height):
    rows = []
    for core_index, (core_start, core_end) in enumerate(zip(core, core[1:])):
        for push_index, (push_start, push_end) in enumerate(zip(push, push[1:])):
            hit = projected_intersection(
                core_start,
                core_end,
                push_start,
                push_end,
                basis,
                f"verify-dual-twist:{core_index}/{push_index}",
            )
            if hit is None:
                continue
            core_parameter, push_parameter, projected_point = hit
            core_point = add_scaled(core_start, sub(core_end, core_start), core_parameter)
            push_point = add_scaled(push_start, sub(push_end, push_start), push_parameter)
            core_height = dot(height, core_point)
            push_height = dot(height, push_point)
            if core_height == push_height:
                raise AssertionError("corrected framing meets its core")
            core_tangent = sub(projection(core_end, basis), projection(core_start, basis))
            push_tangent = sub(projection(push_end, basis), projection(push_start, basis))
            over_role = "core" if core_height > push_height else "push"
            determinant = (
                det2(core_tangent, push_tangent)
                if over_role == "core"
                else det2(push_tangent, core_tangent)
            )
            if determinant == 0:
                raise AssertionError("nontransverse corrected crossing")
            rows.append({
                "core_segment": core_index,
                "push_segment": push_index,
                "projection_point": [str(value) for value in projected_point],
                "over_role": over_role,
                "sign": 1 if determinant > 0 else -1,
            })
    return rows


def verify() -> dict:
    data = json.loads(DATA.read_text())
    framed = json.loads(FRAMED_RECEIPT.read_text())
    correction = json.loads(CORRECTION.read_text())
    dotted = json.loads(DOTTED.read_text())
    if data["sha256"] != canonical_sha256(data):
        raise AssertionError("dual twist payload SHA mismatch")
    bindings = {
        "affine_product_framed_receipt_sha256": framed["sha256"],
        "homology_admissible_correction_sha256": correction["sha256"],
        "actual_dotted_passage_cells_sha256": dotted["sha256"],
    }
    if any(data[key] != value for key, value in bindings.items()):
        raise AssertionError("dual twist source binding changed")

    basis = tuple(tuple(Fraction(value) for value in row) for row in data["projection_basis"])
    height = tuple(Fraction(value) for value in data["height_covector"])
    dotted_passages = {
        passage["passage_id"]: (chart, passage)
        for chart in dotted["charts"]
        for passage in chart["passages"]
    }
    required_turns = correction["required_framing_corrections"]
    if {component["component"] for component in data["components"]} != set(required_turns):
        raise AssertionError("dual component inventory changed")

    triangle_checks = normal_checks = crossing_checks = 0
    for component in data["components"]:
        name = component["component"]
        turns = required_turns[name]
        if component["positive_full_twists"] != turns:
            raise AssertionError(f"{name} twist count changed")
        chart, passage = dotted_passages[component["source_passage_id"]]
        source_core = [point(value) for value in passage["core_vertices"]]
        source_push = [point(value) for value in passage["push_vertices"]]
        if component["source_endpoint_core"] != passage["core_vertices"]:
            raise AssertionError(f"{name} source core endpoints changed")
        if component["source_endpoint_push"] != passage["push_vertices"]:
            raise AssertionError(f"{name} source push endpoints changed")

        local_core = [point(value) for value in component["local_core_vertices"]]
        local_push = [point(value) for value in component["local_push_vertices"]]
        normals = [point(value) for value in component["local_normal_field"]]
        first_normal, second_normal = [
            point(value) for value in component["rational_normal_basis"]
        ]
        tangent = sub(source_core[1], source_core[0])
        subdivision_count = 4 * turns
        if len(local_core) != subdivision_count + 1 or len(local_push) != len(local_core):
            raise AssertionError(f"{name} local subdivision count changed")
        if dot(tangent, first_normal) or dot(tangent, second_normal):
            raise AssertionError(f"{name} normal basis is not transverse")
        if cross(first_normal, second_normal) == (0, 0, 0):
            raise AssertionError(f"{name} normal basis is dependent")
        expected_cycle = (
            first_normal,
            second_normal,
            scale(-1, first_normal),
            scale(-1, second_normal),
        )
        for index, (core_vertex, push_vertex, normal) in enumerate(
            zip(local_core, local_push, normals)
        ):
            parameter = Fraction(index, subdivision_count)
            expected_core = add(source_core[0], scale(parameter, tangent))
            if core_vertex != expected_core or normal != expected_cycle[index % 4]:
                raise AssertionError(f"{name} rational square twist changed")
            if push_vertex != add(core_vertex, normal) or normal == (0, 0, 0):
                raise AssertionError(f"{name} push is not the declared normal graph")
            normal_checks += 1

        # Projection onto the passage tangent is strictly ordered by the core
        # parameter while every normal has zero tangent component.  Therefore
        # the ruled rectangle is globally injective within this local patch.
        axial = [dot(tangent, vertex) for vertex in local_core]
        if any(right <= left for left, right in zip(axial, axial[1:])):
            raise AssertionError(f"{name} twist patch is not axially monotone")

        ribbon_vertices = local_core + local_push
        expected_triangles = []
        offset = len(local_core)
        for index in range(subdivision_count):
            expected_triangles.extend((
                [index, index + 1, offset + index + 1],
                [index, offset + index + 1, offset + index],
            ))
        if component["local_ribbon_triangles"] != expected_triangles:
            raise AssertionError(f"{name} ribbon triangulation changed")
        for indices in expected_triangles:
            first, second, third = [ribbon_vertices[index] for index in indices]
            if cross(sub(second, first), sub(third, first)) == (0, 0, 0):
                raise AssertionError(f"{name} ribbon triangle degenerated")
            triangle_checks += 1

        # The full square twist remains inside the free y-slot around its
        # passage.  Neighboring passage ribbons are four delta apart, whereas
        # this patch uses only plus/minus one delta.
        lane_y = source_core[0][1]
        delta = Fraction(chart["passage_push_delta"])
        patch_y = [vertex[1] for vertex in ribbon_vertices]
        if min(patch_y) < lane_y - delta or max(patch_y) > lane_y + delta:
            raise AssertionError(f"{name} twist escaped its reserved y-slot")
        if not (-1 < min(patch_y) <= max(patch_y) < 1):
            raise AssertionError(f"{name} twist meets a horizontal dotted edge")
        other_intervals = []
        for other in chart["passages"]:
            if other["passage_id"] == component["source_passage_id"]:
                continue
            other_lane = point(other["core_vertices"][0])[1]
            other_intervals.append((other_lane, other_lane + delta))
        patch_interval = (min(patch_y), max(patch_y))
        if any(
            not (patch_interval[1] < interval[0] or interval[1] < patch_interval[0])
            for interval in other_intervals
        ):
            raise AssertionError(f"{name} twist overlaps another passage ribbon slot")

        full_core = [point(value) for value in component["corrected_core_vertices"]]
        full_push = [point(value) for value in component["corrected_push_vertices"]]
        if full_core[:len(local_core)] != local_core or full_push[:len(local_push)] != local_push:
            raise AssertionError(f"{name} corrected cycle does not contain its twist")
        if full_core[0] != full_core[-1] or full_push[0] != full_push[-1]:
            raise AssertionError(f"{name} corrected core/push is not closed")
        replayed = replay_crossings(full_core, full_push, basis, height)
        if replayed != component["crossing_ledger"]:
            raise AssertionError(f"{name} exact crossing ledger changed")
        signed_sum = sum(row["sign"] for row in replayed)
        if signed_sum != 0 or component["integer_self_linking"] != 0:
            raise AssertionError(f"{name} corrected framing is not zero")
        crossing_checks += len(replayed)

    totals = (
        len(data["components"]),
        sum(component["positive_full_twists"] for component in data["components"]),
        triangle_checks,
        crossing_checks,
    )
    if totals != (3, 5, 40, 144):
        raise AssertionError(f"dual twist totals changed: {totals}")
    if data["global_clearance_status"] != "OPEN":
        raise AssertionError("global clearance was claimed without a full replay")

    return {
        "verdict": "PASS_DUAL_ZERO_FRAMING_LOCAL_PL_TWIST_RIBBONS",
        "components": 3,
        "positive_full_twists": 5,
        "ribbon_triangles": triangle_checks,
        "exact_self_linking_crossings": crossing_checks,
        "integer_self_linkings": {name: 0 for name in required_turns},
        "neighbor_passage_ribbon_clearance": "PASS",
        "global_clearance": "OPEN",
        "relative_source_framing": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
