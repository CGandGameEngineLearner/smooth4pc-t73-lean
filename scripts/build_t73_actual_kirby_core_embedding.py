#!/usr/bin/env python3
"""Embed the two dotted circles and five final passage cycles in rational R3."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
FINAL_YZ = ROOT / "geometry/t73_final_yz_foot_state.json"
FOOT_CHART = ROOT / "geometry/t73_unified_kirby_foot_chart.json"
X_DELETION = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
OUTPUT = ROOT / "geometry/t73_actual_kirby_core_embedding.json"

HANDLE_CENTERS = {"y": Fraction(-4), "z": Fraction(4)}
DISK_HALF_THICKNESS = Fraction(1, 2)


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def passage_segment(passage):
    lane = point(passage["belt_point"])
    center = HANDLE_CENTERS[passage["handle"]]
    left = (center - DISK_HALF_THICKNESS, lane[0] / 4, lane[1] / 4)
    right = (center + DISK_HALF_THICKNESS, lane[0] / 4, lane[1] / 4)
    return (left, right) if passage["orientation"] == 1 else (right, left)


def outward_port(endpoint, handle, port_id, port_y_unit):
    center = HANDLE_CENTERS[handle]
    direction = -1 if endpoint[0] < center else 1
    x_coordinate = endpoint[0] + direction * Fraction(1, 100000 + port_id)
    y_coordinate = endpoint[1] + port_id * port_y_unit
    return (x_coordinate, endpoint[1], endpoint[2]), (
        x_coordinate,
        y_coordinate,
        endpoint[2],
    )


def connector(
    exit_point,
    exit_handle,
    entry_point,
    entry_handle,
    connector_index,
    port_y_unit,
):
    exit_x_port, exit_port = outward_port(
        exit_point, exit_handle, 2 * connector_index + 1, port_y_unit
    )
    entry_x_port, entry_port = outward_port(
        entry_point, entry_handle, 2 * connector_index + 2, port_y_unit
    )
    exit_far_x = Fraction(20 + 2 * (2 * connector_index + 1))
    entry_far_x = Fraction(20 + 2 * (2 * connector_index + 2))
    exit_port_z = Fraction(2) + Fraction(2 * connector_index + 1, 10000)
    entry_port_z = Fraction(2) + Fraction(2 * connector_index + 2, 10000)
    height = Fraction(-10 - connector_index)
    route_y = Fraction(10000 + connector_index)
    return [
        exit_point,
        exit_x_port,
        exit_port,
        (exit_port[0], exit_port[1], exit_port_z),
        (exit_far_x, exit_port[1], exit_port_z),
        (exit_far_x, exit_port[1], height),
        (exit_far_x, route_y, height),
        (entry_far_x, route_y, height),
        (entry_far_x, entry_port[1], height),
        (entry_far_x, entry_port[1], entry_port_z),
        (entry_port[0], entry_port[1], entry_port_z),
        entry_port,
        entry_x_port,
        entry_point,
    ]


def dotted_circle(center):
    return [
        (center, Fraction(-1), Fraction(-1)),
        (center, Fraction(1), Fraction(-1)),
        (center, Fraction(1), Fraction(1)),
        (center, Fraction(-1), Fraction(1)),
        (center, Fraction(-1), Fraction(-1)),
    ]


def build() -> dict:
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    final_yz = json.loads(FINAL_YZ.read_text(encoding="utf-8"))
    foot_chart = json.loads(FOOT_CHART.read_text(encoding="utf-8"))
    x_deletion = json.loads(X_DELETION.read_text(encoding="utf-8"))
    x_cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    port_y_unit = Fraction(x_cancellation["slide_bands"][0]["band_width"]) / 100000
    components = [
        {
            "name": "dotted_y",
            "kind": "dotted_one_handle",
            "vertices": [encode(value) for value in dotted_circle(HANDLE_CENTERS["y"])],
            "spanning_disk": {"plane": "x=-4", "square_half_width": "1"},
        },
        {
            "name": "dotted_z",
            "kind": "dotted_one_handle",
            "vertices": [encode(value) for value in dotted_circle(HANDLE_CENTERS["z"])],
            "spanning_disk": {"plane": "x=4", "square_half_width": "1"},
        },
    ]
    connector_index = 0
    passage_count = 0
    for cycle in cycles["components"]:
        passages = cycle["passages"]
        passage_segments = [passage_segment(passage) for passage in passages]
        vertices = [passage_segments[0][0], passage_segments[0][1]]
        segment_roles = [{"kind": "handle_passage", "passage_id": passages[0]["passage_id"]}]
        connector_records = []
        for index, passage in enumerate(passages):
            next_index = (index + 1) % len(passages)
            path = connector(
                passage_segments[index][1],
                passage["handle"],
                passage_segments[next_index][0],
                passages[next_index]["handle"],
                connector_index,
                port_y_unit,
            )
            first_segment = len(vertices) - 1
            vertices.extend(path[1:])
            for _ in range(len(path) - 1):
                segment_roles.append(
                    {"kind": "external_connector", "connector_index": connector_index}
                )
            connector_records.append({
                "connector_index": connector_index,
                "from_passage": passage["passage_id"],
                "to_passage": passages[next_index]["passage_id"],
                "segment_range": [first_segment, first_segment + len(path) - 2],
                "height": str(-10 - connector_index),
                "vertices_sha256": canonical_sha([encode(value) for value in path]),
            })
            connector_index += 1
            if next_index:
                vertices.append(passage_segments[next_index][1])
                segment_roles.append(
                    {
                        "kind": "handle_passage",
                        "passage_id": passages[next_index]["passage_id"],
                    }
                )
        if vertices[-1] != vertices[0]:
            raise AssertionError(f"{cycle['component']}: routed core did not close")
        components.append({
            "name": cycle["component"],
            "kind": "framed_two_handle_core",
            "vertices": [encode(value) for value in vertices],
            "segment_roles": segment_roles,
            "passage_ids": cycle["passage_ids"],
            "connectors": connector_records,
            "closed": True,
        })
        passage_count += len(passages)
    if connector_index != 1785 or passage_count != 1785:
        raise AssertionError("Kirby core embedding lost a passage connector")
    result = {
        "schema": "t73_actual_kirby_core_embedding/v1",
        "final_component_passage_cycles_sha256": cycles["sha256"],
        "final_yz_foot_state_sha256": final_yz["sha256"],
        "unified_foot_chart_sha256": foot_chart["sha256"],
        "post_x_m1_deletion_sha256": x_deletion["sha256"],
        "x_cancellation_sha256": x_cancellation["sha256"],
        "ambient": "rational R3 surgery presentation",
        "component_order": [
            "dotted_y",
            "dotted_z",
            "m_2",
            "m_3",
            "r_xy",
            "r_yz",
            "r_zx",
        ],
        "components": components,
        "passage_count": passage_count,
        "connector_count": connector_index,
        "port_y_unit": str(port_y_unit),
        "routing_rule": (
            "unique outward foot ports; connector j lies at z=-10-j with "
            "adjacent increasing far-x ports and a unique far-y corridor"
        ),
        "completion_status": "SOURCE_BOUND_KIRBY_CORE_CANDIDATE_STRUCTURAL_CHECK_ONLY",
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
        raise AssertionError("actual Kirby core embedding is stale")
    print("T73_KIRBY_CORE=SOURCE_BOUND_KIRBY_CORE_CANDIDATE_STRUCTURAL_CHECK_ONLY")


if __name__ == "__main__":
    main()
