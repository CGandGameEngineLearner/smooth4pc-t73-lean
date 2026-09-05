#!/usr/bin/env python3
"""Project all actual Johnson/dual source connector cells with exact crossings."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

from shapely.geometry import box
from shapely.strtree import STRtree

from export_t73_full_handle_diagram import (
    DiagramError,
    add_scaled,
    det2,
    dot,
    projected_intersection,
    projection,
    sub,
)

ROOT = Path(__file__).resolve().parents[1]
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
PROVENANCE = ROOT / "geometry/t73_reduced_source_connector_provenance.json"
DEFAULT_FULL_OUTPUT = (
    Path.home() / ".cache/t73_actual_source_connector_projection.full.json"
)


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def enc(value):
    return str(value)


def segment_box(start, end, basis):
    first = projection(start, basis)
    second = projection(end, basis)
    return box(
        math.nextafter(float(min(first[0], second[0])), -math.inf),
        math.nextafter(float(min(first[1], second[1])), -math.inf),
        math.nextafter(float(max(first[0], second[0])), math.inf),
        math.nextafter(float(max(first[1], second[1])), math.inf),
    )


def adjacent(first, second):
    if first["curve_id"] != second["curve_id"]:
        return False
    difference = abs(first["curve_segment"] - second["curve_segment"])
    if difference <= 1:
        return True
    return first["curve_closed"] and difference == first["curve_segment_count"] - 1


def build() -> dict:
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    raw_to_reduced_edge = {
        cell["raw_cell_id"]: edge["source_edge"]
        for component in provenance["components"]
        for edge in component["reduced_edges"]
        for cell in edge["raw_connector_cells"]
    }
    connector_owner = {
        connector_id: "m_2"
        for connector_id in spine["components"][1]["connector_ids"]
    }
    connector_owner.update({
        connector_id: "m_3"
        for connector_id in spine["components"][2]["connector_ids"]
    })
    connectors = {
        item["connector_id"]: item for item in spine["central_connectors"]
    }
    segments = []
    for connector_id, owner in connector_owner.items():
        vertices = [point(value) for value in connectors[connector_id]["polyline"]]
        for segment_index, (start, end) in enumerate(zip(vertices, vertices[1:])):
            segments.append({
                "owner": owner,
                "curve_id": connector_id,
                "curve_segment": segment_index,
                "curve_segment_count": len(vertices) - 1,
                "curve_closed": False,
                "source_edge": raw_to_reduced_edge[connector_id],
                "start": start,
                "end": end,
            })
    for owner in ("r_xy", "r_yz", "r_zx"):
        vertices = [point(value) for value in ar_link["components"][owner]["polyline"]]
        for segment_index, (start, end) in enumerate(zip(vertices, vertices[1:])):
            segments.append({
                "owner": owner,
                "curve_id": owner,
                "curve_segment": segment_index,
                "curve_segment_count": len(vertices) - 1,
                "curve_closed": True,
                "source_edge": f"{owner}:dual_full_curve",
                "start": start,
                "end": end,
            })
    projection_denominator = 1000003
    basis = [
        (Fraction(1), Fraction(0), Fraction(1, projection_denominator)),
        (
            Fraction(0),
            Fraction(1),
            Fraction(1, projection_denominator**2),
        ),
    ]
    height = (
        Fraction(-1, projection_denominator),
        Fraction(-1, projection_denominator**2),
        Fraction(1),
    )
    boxes = [segment_box(item["start"], item["end"], basis) for item in segments]
    tree = STRtree(boxes)
    crossings = []
    seen_points = {}
    broad_candidates = 0
    for first_index, first_box in enumerate(boxes):
        for raw_second_index in tree.query(first_box):
            second_index = int(raw_second_index)
            if second_index <= first_index:
                continue
            first = segments[first_index]
            second = segments[second_index]
            if adjacent(first, second):
                continue
            broad_candidates += 1
            label = f"{first['curve_id']}:{first['curve_segment']}/{second['curve_id']}:{second['curve_segment']}"
            hit = projected_intersection(
                first["start"],
                first["end"],
                second["start"],
                second["end"],
                basis,
                label,
            )
            if hit is None:
                continue
            first_parameter, second_parameter, projected_point = hit
            first_point = add_scaled(
                first["start"], sub(first["end"], first["start"]), first_parameter
            )
            second_point = add_scaled(
                second["start"], sub(second["end"], second["start"]), second_parameter
            )
            first_height = dot(height, first_point)
            second_height = dot(height, second_point)
            if first_height == second_height:
                raise AssertionError(f"actual source connector cells intersect at {label}")
            if projected_point in seen_points:
                raise AssertionError(
                    f"repeated source connector projection point for {label} and {seen_points[projected_point]}"
                )
            seen_points[projected_point] = label
            first_tangent = sub(
                projection(first["end"], basis), projection(first["start"], basis)
            )
            second_tangent = sub(
                projection(second["end"], basis), projection(second["start"], basis)
            )
            if first_height > second_height:
                over, under = first, second
                over_parameter, under_parameter = first_parameter, second_parameter
                determinant = det2(first_tangent, second_tangent)
            else:
                over, under = second, first
                over_parameter, under_parameter = second_parameter, first_parameter
                determinant = det2(second_tangent, first_tangent)
            crossings.append({
                "id": f"X{len(crossings)}",
                "projection_point": [enc(value) for value in projected_point],
                "over_owner": over["owner"],
                "under_owner": under["owner"],
                "over_curve_id": over["curve_id"],
                "under_curve_id": under["curve_id"],
                "over_source_edge": over["source_edge"],
                "under_source_edge": under["source_edge"],
                "over_segment": over["curve_segment"],
                "under_segment": under["curve_segment"],
                "over_parameter": enc(over_parameter),
                "under_parameter": enc(under_parameter),
                "over_height": enc(max(first_height, second_height)),
                "under_height": enc(min(first_height, second_height)),
                "sign": 1 if determinant > 0 else -1,
            })
    result = {
        "schema": "t73_actual_source_connector_projection/v1",
        "johnson_spine_embedding_sha256": spine["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "reduced_source_connector_provenance_sha256": provenance["sha256"],
        "projection_basis": [[str(value) for value in row] for row in basis],
        "height_direction": [str(value) for value in height],
        "near_xy_projection_denominator": projection_denominator,
        "segment_count": len(segments),
        "broad_phase_candidates": broad_candidates,
        "crossings": crossings,
        "crossing_count": len(crossings),
        "completion_status": "ACTUAL_SOURCE_CONNECTOR_PROJECTION_CONSTRUCTED",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_FULL_OUTPUT)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        result = build()
    except DiagramError as error:
        raise SystemExit(f"source connector projection is not generic: {error}")
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    if args.check and json.loads(args.check.read_text(encoding="utf-8")) != result:
        raise AssertionError("actual source connector projection is stale")
    print(f"T73_SOURCE_CONNECTOR_PROJECTION={result['completion_status']} crossings={result['crossing_count']}")


if __name__ == "__main__":
    main()
