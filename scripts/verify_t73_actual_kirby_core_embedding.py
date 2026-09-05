#!/usr/bin/env python3
"""Verify the rational seven-component Kirby core embedding structurally."""

from __future__ import annotations

import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

from verify_t73_candidate_t_band0_splice import exact_segment_intersection
from verify_t73_final_component_passage_cycles import verify as verify_cycles

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_actual_kirby_core_embedding.json"
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
FINAL_YZ = ROOT / "geometry/t73_final_yz_foot_state.json"
FOOT_CHART = ROOT / "geometry/t73_unified_kirby_foot_chart.json"
X_DELETION = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"

HANDLE_CENTERS = {"y": Fraction(-4), "z": Fraction(4)}
HALF_THICKNESS = Fraction(1, 2)


def point(values):
    return tuple(Fraction(value) for value in values)


def passage_segment(passage):
    lane = point(passage["belt_point"])
    center = HANDLE_CENTERS[passage["handle"]]
    left = (center - HALF_THICKNESS, lane[0] / 4, lane[1] / 4)
    right = (center + HALF_THICKNESS, lane[0] / 4, lane[1] / 4)
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


def connector(exit_point, exit_handle, entry_point, entry_handle, index, port_y_unit):
    exit_x, exit_port = outward_port(
        exit_point, exit_handle, 2 * index + 1, port_y_unit
    )
    entry_x, entry_port = outward_port(
        entry_point, entry_handle, 2 * index + 2, port_y_unit
    )
    exit_far_x = Fraction(20 + 2 * (2 * index + 1))
    entry_far_x = Fraction(20 + 2 * (2 * index + 2))
    exit_port_z = Fraction(2) + Fraction(2 * index + 1, 10000)
    entry_port_z = Fraction(2) + Fraction(2 * index + 2, 10000)
    height = Fraction(-10 - index)
    route = Fraction(10000 + index)
    return [
        exit_point,
        exit_x,
        exit_port,
        (exit_port[0], exit_port[1], exit_port_z),
        (exit_far_x, exit_port[1], exit_port_z),
        (exit_far_x, exit_port[1], height),
        (exit_far_x, route, height),
        (entry_far_x, route, height),
        (entry_far_x, entry_port[1], height),
        (entry_far_x, entry_port[1], entry_port_z),
        (entry_port[0], entry_port[1], entry_port_z),
        entry_port,
        entry_x,
        entry_point,
    ]


def between(value, first, second):
    return min(first, second) <= value <= max(first, second)


def verify() -> dict:
    if verify_cycles()["verdict"] != "PASS_FIVE_FINAL_COMPONENT_PASSAGE_CYCLES":
        raise AssertionError("final passage cycles did not verify")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    cycles = json.loads(CYCLES.read_text(encoding="utf-8"))
    final_yz = json.loads(FINAL_YZ.read_text(encoding="utf-8"))
    foot_chart = json.loads(FOOT_CHART.read_text(encoding="utf-8"))
    x_deletion = json.loads(X_DELETION.read_text(encoding="utf-8"))
    x_cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    if data["completion_status"] != "SOURCE_BOUND_KIRBY_CORE_CANDIDATE_STRUCTURAL_CHECK_ONLY":
        raise AssertionError("Kirby core embedding scope changed")
    expected_hashes = {
        "final_component_passage_cycles_sha256": cycles["sha256"],
        "final_yz_foot_state_sha256": final_yz["sha256"],
        "unified_foot_chart_sha256": foot_chart["sha256"],
        "post_x_m1_deletion_sha256": x_deletion["sha256"],
        "x_cancellation_sha256": x_cancellation["sha256"],
    }
    if any(data[field] != value for field, value in expected_hashes.items()):
        raise AssertionError("Kirby core embedding has stale sources")
    components = {item["name"]: item for item in data["components"]}
    if list(data["component_order"]) != [
        "dotted_y", "dotted_z", "m_2", "m_3", "r_xy", "r_yz", "r_zx"
    ]:
        raise AssertionError("Kirby component order changed")
    lane_points = {"y": set(), "z": set()}
    port_y_unit = Fraction(data["port_y_unit"])
    expected_port_y_unit = Fraction(x_cancellation["slide_bands"][0]["band_width"]) / 100000
    if port_y_unit != expected_port_y_unit:
        raise AssertionError("connector port-y unit changed")
    port_x = set()
    port_y = set()
    route_coordinates = set()
    far_x_coordinates = set()
    x_stubs_by_z = defaultdict(list)
    y_stubs_by_z = defaultdict(list)
    connector_count = 0
    total_segments = 0
    cycles_by_name = {item["component"]: item for item in cycles["components"]}
    for name in ("m_2", "m_3", "r_xy", "r_yz", "r_zx"):
        cycle = cycles_by_name[name]
        passages = cycle["passages"]
        passage_segments = [passage_segment(value) for value in passages]
        vertices = [passage_segments[0][0], passage_segments[0][1]]
        for index, passage in enumerate(passages):
            lane = (passage_segments[index][0][1], passage_segments[index][0][2])
            if lane in lane_points[passage["handle"]]:
                raise AssertionError("two passages share a dotted-disk lane")
            lane_points[passage["handle"]].add(lane)
            next_index = (index + 1) % len(passages)
            path = connector(
                passage_segments[index][1],
                passage["handle"],
                passage_segments[next_index][0],
                passages[next_index]["handle"],
                connector_count,
                port_y_unit,
            )
            vertices.extend(path[1:])
            for port in (path[3], path[10]):
                if port[0] in port_x or port[1] in port_y:
                    raise AssertionError("connector foot ports are not coordinate-unique")
                port_x.add(port[0])
                port_y.add(port[1])
            far_values = (path[4][0], path[9][0])
            if any(value in far_x_coordinates for value in far_values):
                raise AssertionError("far-x ports are not unique")
            far_x_coordinates.update(far_values)
            route = Fraction(10000 + connector_count)
            if route in route_coordinates or route in port_x or route in port_y or route in far_x_coordinates:
                raise AssertionError("route corridor collides with a foot port coordinate")
            route_coordinates.add(route)
            x_stubs_by_z[path[0][2]].extend([
                (connector_count, (path[0], path[1])),
                (connector_count, (path[12], path[13])),
            ])
            y_stubs_by_z[path[1][2]].extend([
                (connector_count, (path[1], path[2])),
                (connector_count, (path[11], path[12])),
            ])
            connector_count += 1
            if next_index:
                vertices.append(passage_segments[next_index][1])
        stored = [point(value) for value in components[name]["vertices"]]
        if stored != vertices or stored[0] != stored[-1]:
            raise AssertionError(f"{name}: stored routed cycle changed or is open")
        if any(first == second for first, second in zip(stored, stored[1:])):
            raise AssertionError(f"{name}: routed cycle has a zero segment")
        if len(components[name]["segment_roles"]) != len(stored) - 1:
            raise AssertionError(f"{name}: segment-role coverage changed")
        total_segments += len(stored) - 1
    if connector_count != 1785:
        raise AssertionError("Kirby core connector count changed")

    near_foot_cross_checks = 0
    for height in set(x_stubs_by_z) & set(y_stubs_by_z):
        for x_connector, x_stub in x_stubs_by_z[height]:
            for y_connector, y_stub in y_stubs_by_z[height]:
                near_foot_cross_checks += 1
                if exact_segment_intersection(x_stub, y_stub):
                    shared = set(x_stub) & set(y_stub)
                    if not shared:
                        raise AssertionError(
                            "two near-foot connector stubs intersect: "
                            f"x connector {x_connector}, y connector {y_connector}"
                        )
    for handle, center in HANDLE_CENTERS.items():
        dotted = [point(value) for value in components[f"dotted_{handle}"]["vertices"]]
        if dotted != [
            (center, Fraction(-1), Fraction(-1)),
            (center, Fraction(1), Fraction(-1)),
            (center, Fraction(1), Fraction(1)),
            (center, Fraction(-1), Fraction(1)),
            (center, Fraction(-1), Fraction(-1)),
        ]:
            raise AssertionError("dotted circle polygon changed")
        if any(max(abs(value) for value in lane) >= 1 for lane in lane_points[handle]):
            raise AssertionError("a passage lane meets its dotted-circle boundary")
    if port_x & route_coordinates or port_y & route_coordinates:
        raise AssertionError("vertical port can meet a horizontal route corridor")
    # Distinct connector heights separate all horizontal route pieces. Unique
    # port x/y coordinates then exclude every non-adjacent vertical/horizontal
    # incidence; the only shared points are within each connector itself.
    return {
        "verdict": "PASS_SOURCE_BOUND_KIRBY_CORE_STRUCTURAL_CONSTRUCTION_ONLY",
        "components": len(components),
        "framed_components": 5,
        "dotted_components": 2,
        "passage_segments": data["passage_count"],
        "external_connectors": connector_count,
        "routed_segments": total_segments,
        "unique_port_x": len(port_x),
        "unique_port_y": len(port_y),
        "near_foot_exact_cross_checks": near_foot_cross_checks,
        "framing_status": "OPEN",
        "full_pairwise_embedding_status": "OPEN_PENDING_GENERIC_PD_EXPORT",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
