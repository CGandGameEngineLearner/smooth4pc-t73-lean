#!/usr/bin/env python3
"""Independent fail-closed verifier for the saved TetGen source frame."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "geometry" / "t73_selected_source_exterior.json"
FRAME = ROOT / "geometry" / "t73_selected_source_tetrahedral_frame.json"


class FrameError(ValueError):
    pass


def sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def load_module(filename: str, module_name: str):
    path = ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise FrameError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def qpoint(raw: Any, where: str) -> tuple[Fraction, Fraction, Fraction]:
    if not isinstance(raw, list) or len(raw) != 3:
        raise FrameError(f"{where} is not a three-coordinate")
    try:
        return tuple(Fraction(value) for value in raw)  # type: ignore[return-value]
    except (ValueError, TypeError, ZeroDivisionError) as error:
        raise FrameError(f"{where} is not rational: {error}") from error


def determinant6(points: list[tuple[Fraction, Fraction, Fraction]]) -> Fraction:
    base = points[0]
    columns = [
        tuple(points[index][axis] - base[axis] for axis in range(3))
        for index in (1, 2, 3)
    ]
    return (
        columns[0][0]
        * (columns[1][1] * columns[2][2] - columns[1][2] * columns[2][1])
        - columns[1][0]
        * (columns[0][1] * columns[2][2] - columns[0][2] * columns[2][1])
        + columns[2][0]
        * (columns[0][1] * columns[1][2] - columns[0][2] * columns[1][1])
    )


def triangle_geometry(vertices, triangle, where):
    if not isinstance(triangle, list) or len(triangle) != 3:
        raise FrameError(f"{where} is not a triangle")
    try:
        return frozenset(vertices[int(index)] for index in triangle)
    except (IndexError, TypeError, ValueError) as error:
        raise FrameError(f"{where} has an invalid vertex index") from error


def orient2(a, b, c, axes):
    first, second = axes
    return (b[first] - a[first]) * (c[second] - a[second]) - (
        b[second] - a[second]
    ) * (c[first] - a[first])


def triangle_axes(triangle):
    for axes in ((0, 1), (0, 2), (1, 2)):
        if orient2(*triangle, axes) != 0:
            return axes
    raise FrameError("saved source ribbon has a degenerate triangle")


def point_in_triangle(point, triangle, axes):
    orientation = orient2(*triangle, axes)
    signs = [
        orient2(triangle[index], triangle[(index + 1) % 3], point, axes)
        for index in range(3)
    ]
    return all(value >= 0 for value in signs) if orientation > 0 else all(
        value <= 0 for value in signs
    )


def verify_triangle_subdivision(vertices, actual_indices, originals, where):
    """Check exact planar containment and projected-area exhaustion."""
    axes = [triangle_axes(triangle) for triangle in originals]
    expected_areas = [abs(orient2(*triangle, axis)) for triangle, axis in zip(originals, axes)]
    actual_areas = [Fraction(0) for _ in originals]
    for raw in actual_indices:
        if not isinstance(raw, list) or len(raw) != 3:
            raise FrameError(f"{where} contains a nontriangle")
        try:
            triangle = [vertices[int(index)] for index in raw]
        except (IndexError, TypeError, ValueError) as error:
            raise FrameError(f"{where} contains an invalid vertex") from error
        carriers = [
            index
            for index, (original, axis) in enumerate(zip(originals, axes))
            if all(point_in_triangle(point, original, axis) for point in triangle)
            and orient2(*triangle, axis) != 0
        ]
        if len(carriers) != 1:
            raise FrameError(f"{where} subtriangle has no unique saved carrier")
        carrier = carriers[0]
        actual_areas[carrier] += abs(orient2(*triangle, axes[carrier]))
    if actual_areas != expected_areas:
        raise FrameError(f"{where} subtriangles do not exhaust the saved ribbon")


def verify(payload: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    if payload.get("schema") != "t73_selected_source_tetrahedral_frame/v1":
        raise FrameError("wrong tetrahedral source-frame schema")
    recorded_sha = payload.get("sha256")
    if not isinstance(recorded_sha, str) or recorded_sha != sha(
        {key: value for key, value in payload.items() if key != "sha256"}
    ):
        raise FrameError("missing or stale tetrahedral source-frame SHA256")
    if payload.get("source_exterior_sha256") != source.get("sha256"):
        raise FrameError("tetrahedral frame is stale with respect to the source exterior")
    scope = payload.get("scope")
    if scope == "complete":
        expected_routes = 630
    elif isinstance(scope, str) and scope.startswith("prefix:"):
        try:
            expected_routes = int(scope.split(":", 1)[1])
        except ValueError as error:
            raise FrameError("invalid prefix scope") from error
        if not 1 <= expected_routes < 630:
            raise FrameError("prefix scope must contain between 1 and 629 routes")
    else:
        raise FrameError("tetrahedral frame has no valid complete/prefix scope")
    if payload.get("actual_ar_relative_isotopy_proved") is not False:
        raise FrameError("source meshing must not claim the still-open AR relative isotopy")
    frame_raw = payload.get("frame")
    if not isinstance(frame_raw, dict):
        raise FrameError("tetrahedral frame payload is missing")

    exterior = load_module("verify_t73_coefficient_exterior.py", "source_frame_exterior_gate")
    try:
        if expected_routes == 630:
            frame = exterior.validate_frame(frame_raw, expected_components=5)
        else:
            complex_data = exterior.validate_manifold_with_boundary(
                frame_raw["complex"], "prefix frame.complex"
            )
            expected_names = {"outer", "y_left", "y_right", "z_left", "z_right"}
            if set(frame_raw.get("boundary_components", {})) != expected_names:
                raise FrameError("prefix frame does not name all five boundary spheres")
            available = list(complex_data["boundary_components"])
            named = {}
            for name, raw_triangles in frame_raw["boundary_components"].items():
                component = {tuple(sorted(triangle)) for triangle in raw_triangles}
                matches = [candidate for candidate in available if candidate == component]
                if len(matches) != 1:
                    raise FrameError(f"prefix boundary {name} is not an exact S2 component")
                available.remove(matches[0])
                named[name] = component
            if available:
                raise FrameError("prefix named boundaries do not exhaust the boundary")
            frame = {
                "raw": frame_raw,
                "complex": complex_data,
                "boundary_components": named,
            }
    except ValueError as error:
        raise FrameError(str(error)) from error

    vertices = [
        qpoint(point, f"frame vertex {index}")
        for index, point in enumerate(frame_raw["complex"]["vertices"])
    ]
    determinants = [
        determinant6([vertices[vertex] for vertex in tetrahedron])
        # The shared combinatorial gate sorts simplex vertices.  Orientation
        # must instead be checked against TetGen's saved ordering.
        for tetrahedron in frame_raw["complex"]["tetrahedra"]
    ]
    signs = {1 if value > 0 else -1 if value < 0 else 0 for value in determinants}
    if signs not in ({1}, {-1}):
        raise FrameError("tetrahedra are degenerate or inconsistently oriented over Q")
    volume = sum(abs(value) for value in determinants) / 6
    if volume != Fraction(63968):
        raise FrameError(f"exact tetrahedral volume is {volume}, not 63968")

    intervals = {item["interval_id"]: item for item in source["exterior_intervals"]}
    arcs = {item["name"]: item for item in frame_raw["arcs"]}
    ribbons = {item["core_arc"]: item for item in frame_raw["ribbons"]}
    bindings = payload.get("initial_source_binding")
    if (
        len(intervals) != 630
        or len(arcs) != expected_routes
        or len(ribbons) != expected_routes
        or not isinstance(bindings, list)
        or len(bindings) != expected_routes
    ):
        raise FrameError("source-frame route/arc/ribbon/binding inventory is incomplete")
    expected_interval_ids = {
        interval["interval_id"]
        for interval in source["exterior_intervals"][:expected_routes]
    }

    seen_intervals: set[str] = set()
    seen_arcs: set[str] = set()
    for index, binding in enumerate(bindings):
        if not isinstance(binding, dict):
            raise FrameError(f"source binding {index} is not an object")
        interval_id, arc_name = binding.get("source_interval_id"), binding.get("arc_name")
        if interval_id not in intervals or arc_name not in arcs or arc_name not in ribbons:
            raise FrameError(f"source binding {index} names unknown data")
        if interval_id in seen_intervals or arc_name in seen_arcs:
            raise FrameError("source bindings are not bijective")
        interval, arc, ribbon = intervals[interval_id], arcs[arc_name], ribbons[arc_name]
        expected_endpoint_ids = [interval["from_endpoint_id"], interval["to_endpoint_id"]]
        if binding.get("endpoint_ids") != expected_endpoint_ids:
            raise FrameError(f"source binding {interval_id} changed endpoint IDs")
        if binding.get("endpoint_vertices") != [arc["edge_path"][0], arc["edge_path"][-1]]:
            raise FrameError(f"source binding {interval_id} changed endpoint vertices")
        expected_core = [qpoint(point, f"source core {interval_id}") for point in interval["vertices"]]
        actual_core = exterior.edge_path_points(frame, arc["edge_path"], f"frame core {arc_name}")
        if actual_core != expected_core:
            raise FrameError(f"frame core {arc_name} is not the saved rational polyline")
        expected_push = [
            qpoint(point, f"source push-off {interval_id}")
            for point in interval["positive_push_off_vertices"]
        ]
        actual_push = exterior.edge_path_points(
            frame, ribbon["push_off_path"], f"frame push-off {arc_name}"
        )
        if actual_push != expected_push:
            raise FrameError(f"frame push-off {arc_name} is not the saved rational polyline")
        expected_triangles = [
            [qpoint(point, f"source ribbon {interval_id}") for point in triangle]
            for triangle in interval["ruled_ribbon_triangles"]
        ]
        verify_triangle_subdivision(
            vertices,
            ribbon["triangles"],
            expected_triangles,
            f"frame ribbon {arc_name}",
        )
        gate = exterior.load_gate()
        triangles = [tuple(sorted(int(vertex) for vertex in triangle)) for triangle in ribbon["triangles"]]
        disk_boundary, _ = exterior.validate_surface_disk(
            triangles, gate, f"frame ribbon {arc_name}"
        )
        connector_paths = [
            ribbon.get("start_connector_path", [arc["edge_path"][0], ribbon["push_off_path"][0]]),
            ribbon.get("end_connector_path", [arc["edge_path"][-1], ribbon["push_off_path"][-1]]),
        ]
        expected_boundary = {
            tuple(sorted(edge))
            for path in [arc["edge_path"], ribbon["push_off_path"], *connector_paths]
            for edge in zip(path, path[1:])
        }
        if disk_boundary != expected_boundary:
            raise FrameError(f"frame ribbon {arc_name} has the wrong subdivided boundary")
        seen_intervals.add(interval_id)
        seen_arcs.add(arc_name)
    if seen_intervals != expected_interval_ids or seen_arcs != set(arcs):
        raise FrameError("source bindings do not exhaust the saved data")

    declared = payload.get("verification")
    if not isinstance(declared, dict) or declared.get("verdict") != "PASS":
        raise FrameError("constructor did not save its PASS summary")
    recomputed = {
        "verdict": "PASS" if expected_routes == 630 else "PASS_PREFIX_ONLY",
        "source_exterior_sha256": source["sha256"],
        "vertices": len(vertices),
        "tetrahedra": len(frame_raw["complex"]["tetrahedra"]),
        "boundary_components": len(frame["boundary_components"]),
        "arcs": len(arcs),
        "ribbons": len(ribbons),
        "exact_exterior_volume": str(volume),
        "sha256": recorded_sha,
    }
    for key in (
        "vertices",
        "tetrahedra",
        "boundary_components",
        "arcs",
        "ribbons",
        "exact_exterior_volume",
    ):
        if declared.get(key) != recomputed[key]:
            raise FrameError(f"saved verification field {key} is stale")
    return recomputed


def inspect(path: Path = FRAME) -> dict[str, Any]:
    if not path.exists():
        return {"verdict": "OPEN", "reason": f"missing {path.relative_to(ROOT)}"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        return verify(payload, source)
    except (FrameError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        return {"verdict": "OPEN", "reason": str(error)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("frame", nargs="?", type=Path, default=FRAME)
    args = parser.parse_args()
    print(json.dumps(inspect(args.frame), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
