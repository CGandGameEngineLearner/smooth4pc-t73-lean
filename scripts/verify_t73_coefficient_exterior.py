#!/usr/bin/env python3
"""Fail-closed verifier for the complete four-box coefficient exterior."""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "audit" / "t73_coefficient_exterior_schema.json"
CURRENT = ROOT / "geometry" / "t73_selected_canopolis_normal_form.json"
SOURCE = ROOT / "geometry" / "t73_selected_source_exterior.json"
TARGET = ROOT / "geometry" / "t73_selected_canopolis_normal_form.json"


class ExteriorError(ValueError):
    pass


def fail(message: str) -> None:
    raise ExteriorError(message)


def load_gate():
    path = ROOT / "scripts" / "verify_t73_gs1_gp3.py"
    spec = importlib.util.spec_from_file_location("t73_simplex_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def checked_payload_sha(data: dict[str, Any], where: str) -> str:
    """Return an embedded payload digest only after recomputing it."""
    recorded = data.get("sha256")
    if not isinstance(recorded, str):
        fail(f"{where} has no embedded payload SHA256")
    payload = {key: value for key, value in data.items() if key != "sha256"}
    if recorded != sha(payload):
        fail(f"{where} embedded payload SHA256 is stale")
    return recorded


def current_dependencies() -> tuple[dict[str, str], dict[str, Any], dict[str, Any]]:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    dependencies = {
        "source_exterior_sha256": checked_payload_sha(source, "selected source exterior"),
        "selected_canopolis_target_sha256": checked_payload_sha(
            target, "selected canopolis target"
        ),
    }
    return dependencies, source, target


def qpoint(raw: Any, where: str) -> tuple[Fraction, Fraction, Fraction]:
    if not isinstance(raw, list) or len(raw) != 3:
        fail(f"{where} is not a rational three-coordinate")
    try:
        return tuple(Fraction(value) for value in raw)  # type: ignore[return-value]
    except (ValueError, TypeError, ZeroDivisionError) as error:
        raise ExteriorError(f"{where} is not rational: {error}") from error


def reduced_polyline(
    points: list[tuple[Fraction, Fraction, Fraction]],
) -> list[tuple[Fraction, Fraction, Fraction]]:
    """Delete only collinear, order-preserving subdivision vertices."""
    result: list[tuple[Fraction, Fraction, Fraction]] = []
    for value in points:
        result.append(value)
        while len(result) >= 3:
            first, middle, last = result[-3:]
            left = tuple(middle[i] - first[i] for i in range(3))
            right = tuple(last[i] - middle[i] for i in range(3))
            cross = (
                left[1] * right[2] - left[2] * right[1],
                left[2] * right[0] - left[0] * right[2],
                left[0] * right[1] - left[1] * right[0],
            )
            if cross != (0, 0, 0) or sum(left[i] * right[i] for i in range(3)) < 0:
                break
            result.pop(-2)
    return result


def edge_path_points(frame: dict[str, Any], path: list[int], where: str):
    vertices = frame["raw"]["complex"]["vertices"]
    return reduced_polyline(
        [qpoint(vertices[vertex], f"{where} vertex {vertex}") for vertex in path]
    )


def triangle_components(triangles: set[tuple[int, ...]]) -> list[set[tuple[int, ...]]]:
    remaining = set(triangles)
    components = []
    while remaining:
        seed = remaining.pop()
        component = {seed}
        stack = [seed]
        while stack:
            triangle = stack.pop()
            neighbours = {
                other
                for other in remaining
                if len(set(triangle) & set(other)) == 2
            }
            component |= neighbours
            remaining -= neighbours
            stack.extend(neighbours)
        components.append(component)
    return components


def validate_manifold_with_boundary(raw: dict[str, Any], where: str) -> dict[str, Any]:
    gate = load_gate()
    gate.require_fields(raw, ["vertices", "tetrahedra"], where)
    vertices = raw["vertices"]
    if not isinstance(vertices, list) or len(vertices) < 4:
        fail(f"{where}.vertices is not an explicit vertex list")
    if not isinstance(raw["tetrahedra"], list) or not raw["tetrahedra"]:
        fail(f"{where}.tetrahedra is not a nonempty list")
    tetrahedra = [
        tuple(sorted(gate.simplex(tet, 4, len(vertices), f"{where}.tetrahedra[{i}]")))
        for i, tet in enumerate(raw["tetrahedra"])
    ]
    if len(set(tetrahedra)) != len(tetrahedra):
        fail(f"{where} contains duplicate tetrahedra")
    counts = Counter(face for tet in tetrahedra for face in gate.faces(tet))
    if set(counts.values()) - {1, 2}:
        fail(f"{where} has nonmanifold face incidence")
    boundary = {face for face, count in counts.items() if count == 1}
    if not boundary:
        fail(f"{where} has empty boundary")
    if not gate.connected_simplices(tetrahedra):
        fail(f"{where} has disconnected tetrahedron adjacency")
    used = {vertex for tet in tetrahedra for vertex in tet}
    if used != set(range(len(vertices))):
        fail(f"{where} has unused vertices")
    # Each vertex link must be S2 (interior) or D2 (boundary).
    boundary_vertices = {vertex for face in boundary for vertex in face}
    vertex_stars: dict[int, list[tuple[int, ...]]] = {
        vertex: [] for vertex in range(len(vertices))
    }
    for tetrahedron in tetrahedra:
        for vertex in tetrahedron:
            vertex_stars[vertex].append(tetrahedron)
    for vertex in range(len(vertices)):
        link_triangles = [
            tuple(item for item in tet if item != vertex)
            for tet in vertex_stars[vertex]
        ]
        link_edges = Counter(
            edge for triangle in link_triangles for edge in gate.faces(triangle)
        )
        link_vertices = {item for tri in link_triangles for item in tri}
        chi = len(link_vertices) - len(link_edges) + len(link_triangles)
        expected = 1 if vertex in boundary_vertices else 2
        if (
            set(link_edges.values()) - {1, 2}
            or chi != expected
            or not gate.connected_simplices(link_triangles)
        ):
            fail(f"{where} vertex {vertex} has the wrong link")
        if vertex in boundary_vertices:
            link_boundary_edges = [edge for edge, count in link_edges.items() if count == 1]
            degrees = Counter(item for edge in link_boundary_edges for item in edge)
            if not degrees or set(degrees.values()) != {2}:
                fail(f"{where} boundary vertex {vertex} link is not a disk")
    components = triangle_components(boundary)
    for component in components:
        edges = Counter(edge for tri in component for edge in gate.faces(tri))
        verts = {vertex for tri in component for vertex in tri}
        if (
            set(edges.values()) != {2}
            or len(verts) - len(edges) + len(component) != 2
            or not gate.connected_simplices(list(component))
        ):
            fail(f"{where} has a boundary component that is not a triangulated S2")
    return {
        "vertices": vertices,
        "tetrahedra": tetrahedra,
        "boundary": boundary,
        "boundary_components": components,
        "sha256": sha({"vertices": vertices, "tetrahedra": raw["tetrahedra"]}),
    }


def validate_surface_disk(
    triangles: list[tuple[int, ...]], gate, where: str
) -> tuple[set[tuple[int, int]], set[int]]:
    edges = Counter(edge for tri in triangles for edge in gate.faces(tri))
    vertices = {vertex for tri in triangles for vertex in tri}
    if (
        set(edges.values()) - {1, 2}
        or len(vertices) - len(edges) + len(triangles) != 1
        or not gate.connected_simplices(triangles)
    ):
        fail(f"{where} is not a connected triangulated disk")
    boundary_edges = {edge for edge, count in edges.items() if count == 1}
    degrees = Counter(vertex for edge in boundary_edges for vertex in edge)
    if not degrees or set(degrees.values()) != {2}:
        fail(f"{where} boundary is not one circle")
    return boundary_edges, vertices


def validate_frame(raw: dict[str, Any], expected_components: int = 5) -> dict[str, Any]:
    gate = load_gate()
    gate.require_fields(raw, ["complex", "boundary_components", "arcs", "ribbons"], "frame")
    complex_data = validate_manifold_with_boundary(raw["complex"], "frame.complex")
    if len(complex_data["boundary_components"]) != expected_components:
        fail(f"frame.complex does not have {expected_components} spherical boundary components")
    names = raw["boundary_components"]
    expected_names = ["outer", "y_left", "y_right", "z_left", "z_right"] if expected_components == 5 else list(names)
    if not isinstance(names, dict) or set(names) != set(expected_names):
        fail("frame.boundary_components has the wrong names")
    named_components: dict[str, set[tuple[int, ...]]] = {}
    available = list(complex_data["boundary_components"])
    for name, listed in names.items():
        if not isinstance(listed, list):
            fail(f"boundary component {name} is not a triangle list")
        component = {
            tuple(sorted(gate.simplex(tri, 3, len(complex_data["vertices"]), f"boundary {name}")))
            for tri in listed
        }
        matches = [candidate for candidate in available if candidate == component]
        if len(matches) != 1:
            fail(f"boundary component {name} is not an exact connected component")
        available.remove(matches[0])
        named_components[name] = component
    if available:
        fail("frame.boundary_components does not exhaust the boundary")

    all_edges = {
        tuple(sorted((tet[i], tet[j])))
        for tet in complex_data["tetrahedra"]
        for i in range(4) for j in range(i + 1, 4)
    }
    boundary_vertex_sets = {
        name: {vertex for tri in component for vertex in tri}
        for name, component in named_components.items()
    }
    arcs = {}
    occupied_interior: set[int] = set()
    for index, arc in enumerate(raw["arcs"]):
        gate.require_fields(arc, ["name", "edge_path", "start_boundary", "end_boundary"], f"arc[{index}]")
        if not isinstance(arc["name"], str) or not arc["name"] or arc["name"] in arcs:
            fail("arc names must be nonempty and unique")
        path = arc["edge_path"]
        if (
            not isinstance(path, list) or len(path) < 2
            or any(not isinstance(vertex, int) or vertex < 0 or vertex >= len(complex_data["vertices"]) for vertex in path)
            or len(set(path)) != len(path)
            or any(tuple(sorted(edge)) not in all_edges for edge in zip(path, path[1:]))
        ):
            fail(f"arc {arc['name']} is not an embedded edge path")
        if arc["start_boundary"] not in boundary_vertex_sets or path[0] not in boundary_vertex_sets[arc["start_boundary"]]:
            fail(f"arc {arc['name']} has the wrong start boundary")
        if arc["end_boundary"] not in boundary_vertex_sets or path[-1] not in boundary_vertex_sets[arc["end_boundary"]]:
            fail(f"arc {arc['name']} has the wrong end boundary")
        interior = set(path[1:-1])
        if interior & occupied_interior:
            fail("arc interiors are not pairwise vertex-disjoint")
        occupied_interior |= interior
        arcs[arc["name"]] = path

    face_set = {
        face for tet in complex_data["tetrahedra"] for face in gate.faces(tet)
    }
    ribbons = {}
    occupied_ribbon_vertices: set[int] = set()
    for index, ribbon in enumerate(raw["ribbons"]):
        gate.require_fields(ribbon, ["name", "core_arc", "push_off_path", "triangles"], f"ribbon[{index}]")
        if ribbon["core_arc"] not in arcs:
            fail(f"ribbon {ribbon['name']} has no typed core arc")
        push = ribbon["push_off_path"]
        if (
            not isinstance(push, list) or len(push) < 2
            or any(not isinstance(vertex, int) or vertex < 0 or vertex >= len(complex_data["vertices"]) for vertex in push)
            or len(set(push)) != len(push)
            or any(tuple(sorted(edge)) not in all_edges for edge in zip(push, push[1:]))
        ):
            fail(f"ribbon {ribbon['name']} push-off is not an edge path")
        if set(push) & set(arcs[ribbon["core_arc"]]):
            fail(f"ribbon {ribbon['name']} core and push-off are not disjoint")
        triangles = [
            tuple(sorted(gate.simplex(tri, 3, len(complex_data["vertices"]), f"ribbon[{index}]")))
            for tri in ribbon["triangles"]
        ]
        if any(triangle not in face_set for triangle in triangles):
            fail(f"ribbon {ribbon['name']} is not a triangle subcomplex")
        disk_boundary, vertices = validate_surface_disk(triangles, gate, f"ribbon {ribbon['name']}")
        core = arcs[ribbon["core_arc"]]
        connectors = []
        for key, endpoints in (
            ("start_connector_path", (core[0], push[0])),
            ("end_connector_path", (core[-1], push[-1])),
        ):
            connector = ribbon.get(key, list(endpoints))
            if (
                not isinstance(connector, list)
                or len(connector) < 2
                or connector[0] != endpoints[0]
                or connector[-1] != endpoints[1]
                or len(set(connector)) != len(connector)
                or any(
                    not isinstance(vertex, int)
                    or vertex < 0
                    or vertex >= len(complex_data["vertices"])
                    for vertex in connector
                )
                or any(
                    tuple(sorted(edge)) not in all_edges
                    for edge in zip(connector, connector[1:])
                )
            ):
                fail(f"ribbon {ribbon['name']} has an invalid {key}")
            connectors.append(connector)
        expected_boundary = {
            tuple(sorted(edge)) for edge in zip(core, core[1:])
        } | {
            tuple(sorted(edge)) for edge in zip(push, push[1:])
        } | {
            tuple(sorted(edge))
            for connector in connectors
            for edge in zip(connector, connector[1:])
        }
        if disk_boundary != expected_boundary:
            fail(f"ribbon {ribbon['name']} boundary is not core plus framed push-off")
        if vertices & occupied_ribbon_vertices:
            fail("framed ribbons are not pairwise vertex-disjoint")
        other_arc_vertices = set().union(
            *[
                set(path) for name, path in arcs.items()
                if name != ribbon["core_arc"]
            ]
        )
        if vertices & other_arc_vertices:
            fail(f"ribbon {ribbon['name']} meets another coefficient arc")
        occupied_ribbon_vertices |= vertices
        ribbons[ribbon["name"]] = {"triangles": triangles, "vertices": vertices}
    if expected_components == 5:
        owner_names = {"m_2", "r_xy"}
        for arc in raw["arcs"]:
            gate.require_fields(
                arc,
                ["owner", "closure_side", "endpoint_index", "source_id"],
                f"complete arc {arc.get('name')}",
            )
            if (
                arc["owner"] not in owner_names
                or arc["closure_side"] not in {"left", "right"}
                or not isinstance(arc["endpoint_index"], int)
                or not isinstance(arc["source_id"], str)
                or not arc["source_id"]
            ):
                fail("complete arc has invalid S-movie provenance typing")
        for side in ("left", "right"):
            indices = sorted(
                arc["endpoint_index"] for arc in raw["arcs"]
                if arc["closure_side"] == side
            )
            if indices != list(range(315)):
                fail(f"{side} closure endpoint indices are not exactly 0..314")
        endpoint_counts = Counter()
        for arc in raw["arcs"]:
            endpoint_counts[arc["start_boundary"]] += 1
            endpoint_counts[arc["end_boundary"]] += 1
        if endpoint_counts != {
            "y_left": 88,
            "y_right": 88,
            "z_left": 542,
            "z_right": 542,
        }:
            fail("insertion-boundary endpoint counts are not Y88,Y88,Z542,Z542")
        if len(arcs) != 630 or len(ribbons) != 630 or {
            ribbon["core_arc"] for ribbon in raw["ribbons"]
        } != set(arcs):
            fail("complete exterior must contain 630 typed arcs and 630 framed ribbons")
    return {
        "complex": complex_data,
        "boundary_components": named_components,
        "boundary_vertex_sets": boundary_vertex_sets,
        "arcs": arcs,
        "ribbons": ribbons,
        "raw": raw,
    }


def verify_ambient_isomorphism(before: dict[str, Any], after: dict[str, Any], move: dict[str, Any]) -> None:
    gate = load_gate()
    gate.require_fields(move, ["vertex_map"], "ambient move")
    mapping = move["vertex_map"]
    if (
        not isinstance(mapping, list)
        or len(mapping) != len(before["complex"]["vertices"])
        or len(set(mapping)) != len(mapping)
        or any(not isinstance(vertex, int) or vertex < 0 or vertex >= len(after["complex"]["vertices"]) for vertex in mapping)
    ):
        fail("ambient vertex_map is not a bijection")
    image_tets = {
        tuple(sorted(mapping[vertex] for vertex in tet))
        for tet in before["complex"]["tetrahedra"]
    }
    if image_tets != set(after["complex"]["tetrahedra"]):
        fail("ambient map is not a simplicial isomorphism")
    insertion_names = [
        name for name in ("y_left", "y_right", "z_left", "z_right")
        if name in before["boundary_vertex_sets"]
    ]
    fixed = set().union(
        *[before["boundary_vertex_sets"][name] for name in insertion_names]
    )
    if any(mapping[vertex] != vertex for vertex in fixed):
        fail("ambient map moves an insertion-boundary vertex")
    for name, component in before["boundary_components"].items():
        image = {
            tuple(sorted(mapping[vertex] for vertex in triangle))
            for triangle in component
        }
        if name not in after["boundary_components"] or image != after[
            "boundary_components"
        ][name]:
            fail(f"ambient map does not preserve named boundary component {name}")
    for name, path in before["arcs"].items():
        if name not in after["arcs"] or [mapping[vertex] for vertex in path] != after["arcs"][name]:
            fail(f"ambient map does not carry arc {name}")
    for name, ribbon in before["ribbons"].items():
        image = {
            tuple(sorted(mapping[vertex] for vertex in tri))
            for tri in ribbon["triangles"]
        }
        if name not in after["ribbons"] or image != set(after["ribbons"][name]["triangles"]):
            fail(f"ambient map does not carry ribbon {name}")

    before_arcs = {item["name"]: item for item in before["raw"]["arcs"]}
    after_arcs = {item["name"]: item for item in after["raw"]["arcs"]}
    if set(before_arcs) != set(after_arcs):
        fail("ambient map changes the typed arc inventory")
    for name, record in before_arcs.items():
        transported = dict(record)
        transported["edge_path"] = [mapping[vertex] for vertex in record["edge_path"]]
        if transported != after_arcs[name]:
            fail(f"ambient map changes the typing or path of arc {name}")

    before_ribbons = {item["name"]: item for item in before["raw"]["ribbons"]}
    after_ribbons = {item["name"]: item for item in after["raw"]["ribbons"]}
    if set(before_ribbons) != set(after_ribbons):
        fail("ambient map changes the framed-ribbon inventory")
    for name, record in before_ribbons.items():
        transported = dict(record)
        transported["push_off_path"] = [
            mapping[vertex] for vertex in record["push_off_path"]
        ]
        for key in ("start_connector_path", "end_connector_path"):
            if key in record:
                transported[key] = [mapping[vertex] for vertex in record[key]]
        transported["triangles"] = [
            sorted(mapping[vertex] for vertex in triangle)
            for triangle in record["triangles"]
        ]
        candidate = dict(after_ribbons[name])
        candidate["triangles"] = [sorted(triangle) for triangle in candidate["triangles"]]
        if transported != candidate:
            fail(f"ambient map changes the typing or framing of ribbon {name}")


def verify_bistellar(before: dict[str, Any], after: dict[str, Any], move: dict[str, Any]) -> None:
    gate = load_gate()
    gate.require_fields(move, ["removed_tetrahedra", "added_tetrahedra"], "bistellar move")
    removed = {
        tuple(sorted(gate.simplex(tet, 4, len(before["complex"]["vertices"]), "removed tetrahedron")))
        for tet in move["removed_tetrahedra"]
    }
    added = {
        tuple(sorted(gate.simplex(tet, 4, len(after["complex"]["vertices"]), "added tetrahedron")))
        for tet in move["added_tetrahedra"]
    }
    if (len(removed), len(added)) not in {(2, 3), (3, 2)}:
        fail("v1 replays only vertex-preserving 2-3 or 3-2 bistellar replacements")
    if removed - set(before["complex"]["tetrahedra"]) or added - set(after["complex"]["tetrahedra"]):
        fail("bistellar clusters are not subcomplexes of their frames")
    old_boundary = {
        face for face, count in Counter(face for tet in removed for face in gate.faces(tet)).items() if count == 1
    }
    new_boundary = {
        face for face, count in Counter(face for tet in added for face in gate.faces(tet)).items() if count == 1
    }
    if old_boundary != new_boundary:
        fail("bistellar clusters do not have the same local boundary")
    expected = (set(before["complex"]["tetrahedra"]) - removed) | added
    if expected != set(after["complex"]["tetrahedra"]):
        fail("after frame is not the stated bistellar replacement")
    protected = set().union(
        *[set(path) for path in before["arcs"].values()],
        *[ribbon["vertices"] for ribbon in before["ribbons"].values()],
    )
    if {vertex for tet in removed for vertex in tet} & protected:
        fail("bistellar support meets an arc or ribbon")
    if before["arcs"] != after["arcs"] or {
        name: set(value["triangles"]) for name, value in before["ribbons"].items()
    } != {
        name: set(value["triangles"]) for name, value in after["ribbons"].items()
    }:
        fail("protected arc/ribbon data changed in a disjoint bistellar move")
    insertion_names = {
        "y_left", "y_right", "z_left", "z_right"
    } & set(before["boundary_vertex_sets"])
    insertion_vertices = set().union(
        *[before["boundary_vertex_sets"][name] for name in insertion_names]
    )
    if {vertex for tet in removed for vertex in tet} & insertion_vertices:
        fail("bistellar support meets a fixed insertion boundary")
    if before["raw"]["boundary_components"] != after["raw"]["boundary_components"]:
        fail("bistellar move changes a named boundary triangulation")
    if before["raw"]["arcs"] != after["raw"]["arcs"] or before["raw"][
        "ribbons"
    ] != after["raw"]["ribbons"]:
        fail("bistellar move changes typed arc or ribbon metadata")


def verify_source_target_bindings(
    payload: dict[str, Any],
    initial: dict[str, Any],
    final: dict[str, Any],
    source: dict[str, Any],
    target: dict[str, Any],
) -> None:
    """Bind all ambient arcs bijectively to the saved source and target."""
    source_bindings = payload.get("initial_source_binding")
    target_bindings = payload.get("final_target_binding")
    if not isinstance(source_bindings, list) or len(source_bindings) != 630:
        fail("initial_source_binding is not a complete 630-row binding")
    if not isinstance(target_bindings, list) or len(target_bindings) != 630:
        fail("final_target_binding is not a complete 630-row binding")
    source_binding_interval_ids = [
        item.get("source_interval_id") if isinstance(item, dict) else None
        for item in source_bindings
    ]
    source_binding_arc_names = [
        item.get("arc_name") if isinstance(item, dict) else None
        for item in source_bindings
    ]
    if (
        len(set(source_binding_interval_ids)) != 630
        or len(set(source_binding_arc_names)) != 630
    ):
        fail("initial source binding is not bijective")
    target_binding_keys = [
        (item.get("target_side"), item.get("target_index"))
        if isinstance(item, dict)
        else (None, None)
        for item in target_bindings
    ]
    target_binding_arc_names = [
        item.get("arc_name") if isinstance(item, dict) else None
        for item in target_bindings
    ]
    if len(set(target_binding_keys)) != 630 or len(set(target_binding_arc_names)) != 630:
        fail("final target binding is not bijective")

    initial_arcs = {item["name"]: item for item in initial["raw"]["arcs"]}
    final_arcs = {item["name"]: item for item in final["raw"]["arcs"]}
    initial_ribbons = {
        item["core_arc"]: item for item in initial["raw"]["ribbons"]
    }
    final_ribbons = {item["core_arc"]: item for item in final["raw"]["ribbons"]}
    source_intervals = {
        item["interval_id"]: item for item in source["exterior_intervals"]
    }
    source_endpoint_ball = {
        endpoint["endpoint_id"]: sphere["name"]
        for sphere in source["insertion_spheres"]
        for endpoint in sphere["endpoints"]
    }
    if len(source_intervals) != 630 or len(source_endpoint_ball) != 1260:
        fail("saved source exterior does not have complete interval incidence")
    source_ball_name = {
        "Y_minus": "y_left",
        "Y_plus": "y_right",
        "Z_minus": "z_left",
        "Z_plus": "z_right",
    }

    seen_source, seen_initial_arcs = set(), set()
    for index, binding in enumerate(source_bindings):
        if not isinstance(binding, dict):
            fail(f"initial source binding {index} is not an object")
        interval_id = binding.get("source_interval_id")
        arc_name = binding.get("arc_name")
        if interval_id not in source_intervals or arc_name not in initial_arcs:
            fail("an initial source binding names no saved interval or ambient arc")
        if interval_id in seen_source or arc_name in seen_initial_arcs:
            fail("initial source binding is not bijective")
        interval = source_intervals[interval_id]
        expected_endpoints = [
            interval["from_endpoint_id"], interval["to_endpoint_id"]
        ]
        if binding.get("endpoint_ids") != expected_endpoints:
            fail(f"source interval {interval_id} endpoint IDs changed")
        arc = initial_arcs[arc_name]
        expected_boundaries = [
            source_ball_name[source_endpoint_ball[endpoint_id]]
            for endpoint_id in expected_endpoints
        ]
        if [arc["start_boundary"], arc["end_boundary"]] != expected_boundaries:
            fail(f"source interval {interval_id} has the wrong boundary pairing")
        if binding.get("endpoint_vertices") != [
            arc["edge_path"][0], arc["edge_path"][-1]
        ]:
            fail(f"source interval {interval_id} is not bound to its path endpoints")
        expected_centerline = [
            qpoint(value, f"saved source interval {interval_id}")
            for value in interval["vertices"]
        ]
        if edge_path_points(initial, arc["edge_path"], f"source arc {arc_name}") != expected_centerline:
            fail(f"source interval {interval_id} is not bound to its complete saved PL centerline")
        expected_push_off = [
            qpoint(value, f"saved source push-off {interval_id}")
            for value in interval["positive_push_off_vertices"]
        ]
        if edge_path_points(
            initial,
            initial_ribbons[arc_name]["push_off_path"],
            f"source push-off {arc_name}",
        ) != expected_push_off:
            fail(f"source interval {interval_id} is not bound to its complete saved PL push-off")
        seen_source.add(interval_id)
        seen_initial_arcs.add(arc_name)
    if seen_source != set(source_intervals) or seen_initial_arcs != set(initial_arcs):
        fail("initial source binding does not exhaust source intervals and ambient arcs")

    target_records = {
        (side, int(item["index"])): item
        for side, records in (
            ("left", target["left_closure_strands"]),
            ("right", target["right_closure_strands"]),
        )
        for item in records
    }
    target_endpoint_ball = {
        endpoint["endpoint_id"]: ball["name"]
        for ball in target["insertion_balls"]
        for endpoint in ball["endpoints"]
    }
    if len(target_records) != 630 or len(target_endpoint_ball) != 1260:
        fail("saved target does not have complete strand incidence")
    # These are the only identifications compatible with the two displayed
    # opposite-side representable factors.
    target_ball_name = {
        "Y_source": "y_left",
        "Y_target": "y_right",
        "Z_source": "z_left",
        "Z_target": "z_right",
    }
    seen_target, seen_final_arcs = set(), set()
    for index, binding in enumerate(target_bindings):
        if not isinstance(binding, dict):
            fail(f"final target binding {index} is not an object")
        key = (binding.get("target_side"), binding.get("target_index"))
        arc_name = binding.get("arc_name")
        if key not in target_records or arc_name not in final_arcs:
            fail("a final target binding names no target strand or ambient arc")
        if key in seen_target or arc_name in seen_final_arcs:
            fail("final target binding is not bijective")
        record = target_records[key]
        if binding.get("endpoint_ids") != record["endpoint_ids"]:
            fail(f"target strand {key} endpoint IDs changed")
        arc = final_arcs[arc_name]
        expected_boundaries = [
            target_ball_name[target_endpoint_ball[endpoint_id]]
            for endpoint_id in record["endpoint_ids"]
        ]
        if [arc["start_boundary"], arc["end_boundary"]] != expected_boundaries:
            fail(f"target strand {key} has the wrong boundary pairing")
        if binding.get("endpoint_vertices") != [
            arc["edge_path"][0], arc["edge_path"][-1]
        ]:
            fail(f"target strand {key} is not bound to its path endpoints")
        expected_centerline = [
            qpoint(value, f"saved target strand {key}")
            for value in record["centerline"]
        ]
        if edge_path_points(final, arc["edge_path"], f"target arc {arc_name}") != expected_centerline:
            fail(f"target strand {key} is not bound to its complete saved PL centerline")
        expected_push_off = [
            qpoint(value, f"saved target push-off {key}")
            for value in record["positive_push_off"]
        ]
        if edge_path_points(
            final,
            final_ribbons[arc_name]["push_off_path"],
            f"target push-off {arc_name}",
        ) != expected_push_off:
            fail(f"target strand {key} is not bound to its complete saved PL push-off")
        seen_target.add(key)
        seen_final_arcs.add(arc_name)
    if seen_target != set(target_records) or seen_final_arcs != set(final_arcs):
        fail("final target binding does not exhaust target strands and ambient arcs")


def verify_payload(payload: dict[str, Any]) -> dict[str, Any]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    if payload.get("schema") != schema["schema"]:
        fail("input is not a t73_coefficient_exterior_isotopy/v1 witness")
    for key in schema["required"]:
        if key not in payload:
            fail(f"witness missing {key}")
    expected_dependencies, source, target = current_dependencies()
    if payload.get("dependencies") != expected_dependencies:
        fail("coefficient-exterior witness dependencies are stale or incomplete")
    if not isinstance(payload.get("moves"), list) or not payload["moves"]:
        fail("coefficient-exterior witness requires a nonempty ambient movie")
    current = validate_frame(payload["initial"])
    initial = current
    for index, raw_move in enumerate(payload["moves"]):
        if not isinstance(raw_move, dict) or "kind" not in raw_move or "after" not in raw_move:
            fail(f"move {index} is incomplete")
        after = validate_frame(raw_move["after"])
        if raw_move["kind"] == "ambient_simplicial_isomorphism":
            verify_ambient_isomorphism(current, after, raw_move)
        elif raw_move["kind"] == "interior_bistellar_replacement":
            verify_bistellar(current, after, raw_move)
        else:
            fail(f"move {index} has unsupported kind")
        current = after
    final = validate_frame(payload["final"])
    if sha(current["raw"]) != sha(final["raw"]):
        fail("final frame does not equal the last replayed frame")
    verify_source_target_bindings(payload, initial, final, source, target)
    return {"verdict": "PASS", "moves": len(payload["moves"]), "sha256": sha(payload)}


def inspect_current() -> dict[str, Any]:
    payload = json.loads(CURRENT.read_text(encoding="utf-8"))
    try:
        verify_payload(payload)
    except ExteriorError as error:
        return {
            "verdict": "OPEN",
            "reason": str(error),
            "current": str(CURRENT.relative_to(ROOT)),
        }
    raise AssertionError("current normal-form metadata unexpectedly passed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("witness", nargs="?", type=Path)
    args = parser.parse_args()
    if args.witness is None:
        print(json.dumps(inspect_current(), indent=2, sort_keys=True))
        return
    try:
        result = verify_payload(json.loads(args.witness.read_text(encoding="utf-8")))
    except ExteriorError as error:
        result = {"verdict": "OPEN", "reason": str(error)}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
