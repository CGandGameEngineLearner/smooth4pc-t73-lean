#!/usr/bin/env python3
"""Realize the +1,+1,+3 dual-framing corrections as rational PL twists."""

from __future__ import annotations

import argparse
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
FRAMED_RECEIPT = ROOT / "audit/t73_affine_s3_product_framed_realization_receipt.json"
CORRECTION = ROOT / "geometry/t73_kirby_homology_admissible_correction.json"
DOTTED = ROOT / "geometry/t73_actual_dotted_s3_passage_cells.json"
OUTPUT = ROOT / "geometry/t73_dual_zero_framing_twist_ribbons.json"

Q = 1_000_033
PROJECTION_BASIS = (
    (Fraction(1), Fraction(1), Fraction(1, Q)),
    (Fraction(1, Q**2), Fraction(0), Fraction(1)),
)
HEIGHT_COVECTOR = (
    Fraction(1),
    Fraction(1, Q**3) - 1,
    Fraction(-1, Q**2),
)


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def point(values: list[str]) -> tuple[Fraction, Fraction, Fraction]:
    return tuple(Fraction(value) for value in values)  # type: ignore[return-value]


def encode_point(value: tuple[Fraction, Fraction, Fraction]) -> list[str]:
    return [str(coordinate) for coordinate in value]


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


def resolve_cache_path(value: str) -> Path:
    path = Path(value)
    if path.exists() or len(value) < 3 or value[1:3] not in (":\\", ":/"):
        return path
    return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")


def crossing_ledger(core, push) -> list[dict]:
    rows = []
    for core_index, (core_start, core_end) in enumerate(zip(core, core[1:])):
        for push_index, (push_start, push_end) in enumerate(zip(push, push[1:])):
            hit = projected_intersection(
                core_start,
                core_end,
                push_start,
                push_end,
                PROJECTION_BASIS,
                f"dual-twist:{core_index}/{push_index}",
            )
            if hit is None:
                continue
            core_parameter, push_parameter, projected_point = hit
            core_point = add_scaled(core_start, sub(core_end, core_start), core_parameter)
            push_point = add_scaled(push_start, sub(push_end, push_start), push_parameter)
            core_height = dot(HEIGHT_COVECTOR, core_point)
            push_height = dot(HEIGHT_COVECTOR, push_point)
            if core_height == push_height:
                raise AssertionError("corrected push meets its core")
            core_tangent = sub(
                projection(core_end, PROJECTION_BASIS),
                projection(core_start, PROJECTION_BASIS),
            )
            push_tangent = sub(
                projection(push_end, PROJECTION_BASIS),
                projection(push_start, PROJECTION_BASIS),
            )
            over_role = "core" if core_height > push_height else "push"
            determinant = (
                det2(core_tangent, push_tangent)
                if over_role == "core"
                else det2(push_tangent, core_tangent)
            )
            if determinant == 0:
                raise AssertionError("corrected projection has a nontransverse crossing")
            rows.append({
                "core_segment": core_index,
                "push_segment": push_index,
                "projection_point": [str(value) for value in projected_point],
                "over_role": over_role,
                "sign": 1 if determinant > 0 else -1,
            })
    return rows


def make_twist_component(name, turns, source_core, source_push, passage_id):
    start, end = source_core[:2]
    start_push, end_push = source_push[:2]
    tangent = sub(end, start)
    first_normal = sub(start_push, start)
    if sub(end_push, end) != first_normal:
        raise AssertionError(f"{name} selected passage has nonconstant product normal")
    if dot(tangent, first_normal) != 0:
        raise AssertionError(f"{name} selected product normal is not perpendicular")

    second_normal = cross(tangent, first_normal)
    second_normal = scale(
        max(abs(value) for value in first_normal)
        / max(abs(value) for value in second_normal),
        second_normal,
    )
    normal_cycle = (
        first_normal,
        second_normal,
        scale(-1, first_normal),
        scale(-1, second_normal),
    )

    subdivision_count = 4 * turns
    local_core = []
    local_push = []
    normal_field = []
    for index in range(subdivision_count + 1):
        parameter = Fraction(index, subdivision_count)
        base = add(start, scale(parameter, tangent))
        normal = normal_cycle[index % 4]
        local_core.append(base)
        local_push.append(add(base, normal))
        normal_field.append(normal)

    corrected_core = local_core + source_core[2:]
    corrected_push = local_push + source_push[2:]
    triangles = []
    vertex_count = len(local_core)
    for index in range(subdivision_count):
        triangles.extend((
            [index, index + 1, vertex_count + index + 1],
            [index, vertex_count + index + 1, vertex_count + index],
        ))
    ledger = crossing_ledger(corrected_core, corrected_push)
    signed_sum = sum(row["sign"] for row in ledger)
    if signed_sum % 2:
        raise AssertionError(f"{name} has an odd self-linking crossing sum")

    return {
        "component": name,
        "source_passage_id": passage_id,
        "positive_full_twists": turns,
        "source_segment_index": 0,
        "source_endpoint_core": [encode_point(start), encode_point(end)],
        "source_endpoint_push": [encode_point(start_push), encode_point(end_push)],
        "rational_normal_basis": [
            encode_point(first_normal),
            encode_point(second_normal),
        ],
        "local_core_vertices": [encode_point(value) for value in local_core],
        "local_push_vertices": [encode_point(value) for value in local_push],
        "local_normal_field": [encode_point(value) for value in normal_field],
        "local_ribbon_triangles": triangles,
        "corrected_core_vertices": [encode_point(value) for value in corrected_core],
        "corrected_push_vertices": [encode_point(value) for value in corrected_push],
        "crossing_ledger": ledger,
        "crossing_count": len(ledger),
        "signed_crossing_sum": signed_sum,
        "integer_self_linking": signed_sum // 2,
    }


def build() -> dict:
    framed_receipt = json.loads(FRAMED_RECEIPT.read_text())
    correction = json.loads(CORRECTION.read_text())
    dotted = json.loads(DOTTED.read_text())
    model = json.loads(resolve_cache_path(framed_receipt["cache_path"]).read_text())
    cores = {
        component["component"]: [point(value) for value in component["vertices"]]
        for component in model["core_components"]
    }
    pushes = {
        component["component"]: [point(value) for value in component["vertices"]]
        for component in model["push_components"]
    }
    passage_owner = {
        passage["passage_id"]: passage["owner"]
        for chart in dotted["charts"]
        for passage in chart["passages"]
    }
    passage_ids = {
        "r_xy": "r_xy:y:edge:0",
        "r_yz": "r_yz:z:edge:0",
        "r_zx": "r_zx:z:edge:0",
    }

    components = []
    for name, turns in correction["required_framing_corrections"].items():
        passage_id = passage_ids[name]
        if passage_owner.get(passage_id) != name:
            raise AssertionError(f"{name} twist passage provenance changed")
        component = make_twist_component(
            name,
            turns,
            cores[name],
            pushes[name],
            passage_id,
        )
        if component["integer_self_linking"] != 0:
            raise AssertionError(f"{name} correction did not produce zero framing")
        components.append(component)

    result = {
        "schema": "t73_dual_zero_framing_twist_ribbons/v1",
        "affine_product_framed_receipt_sha256": framed_receipt["sha256"],
        "homology_admissible_correction_sha256": correction["sha256"],
        "actual_dotted_passage_cells_sha256": dotted["sha256"],
        "projection_basis": [
            [str(value) for value in row] for row in PROJECTION_BASIS
        ],
        "height_covector": [str(value) for value in HEIGHT_COVECTOR],
        "components": components,
        "component_count": len(components),
        "total_positive_full_twists": sum(
            component["positive_full_twists"] for component in components
        ),
        "total_local_ribbon_triangles": sum(
            len(component["local_ribbon_triangles"]) for component in components
        ),
        "total_exact_self_linking_crossings": sum(
            component["crossing_count"] for component in components
        ),
        "local_twist_ribbon_status": "EXPLICIT_RATIONAL_PL_CELLS",
        "global_clearance_status": "OPEN",
        "relative_source_framing_status": "OPEN",
        "completion_status": "DUAL_ZERO_FRAMING_TWIST_RIBBONS_CONSTRUCTED",
    }
    result["sha256"] = canonical_sha256(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("dual zero-framing twist artifact is stale")
    print(json.dumps({
        "components": result["component_count"],
        "twists": result["total_positive_full_twists"],
        "triangles": result["total_local_ribbon_triangles"],
        "crossings": result["total_exact_self_linking_crossings"],
        "global_clearance": result["global_clearance_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
