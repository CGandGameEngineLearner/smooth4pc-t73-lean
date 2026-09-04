#!/usr/bin/env python3
"""Fail-closed verifier for the C-H1 four-box ambient-isotopy movie.

The accepted movie format is deliberately restrictive: a fixed rational
tetrahedral exterior and a sequence of one-interior-vertex moves.  Each move
is the straight-line motion of one vertex inside its triangulated star.  The
link of the moved vertex must be a connected triangulated 2-sphere and every
incident tetrahedron must keep its nonzero orientation.  Since its determinant
is affine in the moving vertex, this proves nondegeneracy for every time in
the closed move interval, not only at sampled frames.

No current coordinate source exterior/movie exists.  Missing coordinates are
reported as OPEN and the command exits 2 unless ``--allow-open`` is passed.
Stored PASS booleans and endpoint hashes are never accepted as substitutes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict, deque
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MOVIE = ROOT / "geometry" / "t73_c_h1_relative_isotopy.json"
SOURCE = ROOT / "geometry" / "t73_selected_source_exterior.json"
TARGET = ROOT / "geometry" / "t73_selected_canopolis_normal_form.json"
PRIMITIVES = ROOT / "geometry" / "t73_all_owner_product_primitives.json"
LEGACY = ROOT / "geometry" / "t73_product_ribbon_isotopy.json"
REPORT = ROOT / "audit" / "t73_c_h1_relative_isotopy_report.json"

BALL_NAMES = {"Y_minus", "Y_plus", "Z_minus", "Z_plus"}


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def qpoint(raw: list[Any]) -> tuple[Fraction, Fraction, Fraction]:
    if not isinstance(raw, list) or len(raw) != 3:
        raise AssertionError("a rational point is not a three-vector")
    return tuple(Fraction(value) for value in raw)  # type: ignore[return-value]


def determinant(a, b, c, d) -> Fraction:
    rows = [[b[i] - a[i], c[i] - a[i], d[i] - a[i]] for i in range(3)]
    return (
        rows[0][0] * (rows[1][1] * rows[2][2] - rows[1][2] * rows[2][1])
        - rows[0][1] * (rows[1][0] * rows[2][2] - rows[1][2] * rows[2][0])
        + rows[0][2] * (rows[1][0] * rows[2][1] - rows[1][1] * rows[2][0])
    )


def faces(tetrahedron: tuple[str, str, str, str]):
    return [tuple(sorted(face)) for face in combinations(tetrahedron, 3)]


def link_is_sphere(star: list[tuple[str, str, str, str]], vertex: str) -> bool:
    triangles = [tuple(item for item in tetra if item != vertex) for tetra in star]
    if any(len(triangle) != 3 for triangle in triangles):
        return False
    edge_counts = Counter(
        tuple(sorted(edge)) for triangle in triangles for edge in combinations(triangle, 2)
    )
    if not edge_counts or any(count != 2 for count in edge_counts.values()):
        return False
    vertices = {item for triangle in triangles for item in triangle}
    euler = len(vertices) - len(edge_counts) + len(triangles)
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in edge_counts:
        adjacency[edge[0]].add(edge[1])
        adjacency[edge[1]].add(edge[0])
    seen = set()
    queue = deque([next(iter(vertices))])
    while queue:
        current = queue.popleft()
        if current in seen:
            continue
        seen.add(current)
        queue.extend(adjacency[current] - seen)
    return euler == 2 and seen == vertices


def split_matching_obstruction(source: dict[str, Any]) -> dict[str, Any]:
    endpoint_sphere = {
        endpoint["endpoint_id"]: sphere["name"]
        for sphere in source.get("insertion_spheres", [])
        for endpoint in sphere.get("endpoints", [])
    }
    active = []
    for interval in source.get("exterior_intervals", []):
        start_sphere = endpoint_sphere.get(interval.get("from_endpoint_id"))
        end_sphere = endpoint_sphere.get(interval.get("to_endpoint_id"))
        if start_sphere and end_sphere and (
            start_sphere.startswith("Y") or end_sphere.startswith("Y")
        ):
            active.append((interval, start_sphere, end_sphere))
    representable_pairs = {
        frozenset(("Y_minus", "Z_plus")),
        frozenset(("Y_plus", "Z_minus")),
    }
    wrong_side = [
        {
            "interval_id": interval["interval_id"],
            "owner": interval["owner"],
            "copy_sign": interval["copy_sign"],
            "from_source_id": interval["from_source_id"],
            "to_source_id": interval["to_source_id"],
            "from_sphere": start_sphere,
            "to_sphere": end_sphere,
        }
        for interval, start_sphere, end_sphere in active
        if frozenset((start_sphere, end_sphere)) not in representable_pairs
    ]
    transition_counts = Counter(
        tuple(sorted((start_sphere, end_sphere)))
        for _interval, start_sphere, end_sphere in active
    )
    return {
        "active_y_incident_interval_count": len(active),
        "transition_counts": {
            "--".join(key): value for key, value in sorted(transition_counts.items())
        },
        "expected_two_representable_pairs": [
            ["Y_minus", "Z_plus"],
            ["Y_plus", "Z_minus"],
        ],
        "wrong_side_connector_count": len(wrong_side),
        "wrong_side_connectors": wrong_side,
        "literal_two_disjoint_closures_relative_four_balls_possible": len(wrong_side)
        == 0,
        "reason": (
            "wrong-side connectors force both proposed closure factors to use endpoint subsets "
            "on the same Z insertion spheres; arbitrary C_271 tangles do not preserve those subsets"
        ),
    }


def ambient_edges(
    tetrahedra: list[tuple[str, str, str, str]],
) -> set[tuple[str, str]]:
    return {
        tuple(sorted(edge))
        for tetrahedron in tetrahedra
        for edge in combinations(tetrahedron, 2)
    }


def validate_edge_path(
    path: Any,
    positions: dict[str, tuple[Fraction, Fraction, Fraction]],
    edges: set[tuple[str, str]],
    where: str,
) -> list[str]:
    if (
        not isinstance(path, list)
        or len(path) < 2
        or any(not isinstance(vertex, str) or vertex not in positions for vertex in path)
        or len(set(path)) != len(path)
    ):
        raise AssertionError(f"{where} is not an embedded vertex path")
    if any(tuple(sorted(edge)) not in edges for edge in zip(path, path[1:])):
        raise AssertionError(f"{where} uses a non-edge of the ambient triangulation")
    return path


def validate_endpoint_matching(
    records: Any,
    source: dict[str, Any],
    initial: dict[str, tuple[Fraction, Fraction, Fraction]],
    ball_boundaries: dict[str, set[str]],
) -> dict[str, str]:
    expected = {
        (sphere["name"], endpoint["endpoint_id"]): endpoint
        for sphere in source["insertion_spheres"]
        for endpoint in sphere["endpoints"]
    }
    if not isinstance(records, list) or len(records) != len(expected) or len(expected) != 1260:
        raise AssertionError("four-box endpoint matching is incomplete")
    actual_keys = [(item.get("ball"), item.get("endpoint_id")) for item in records]
    if len(set(actual_keys)) != len(actual_keys) or set(actual_keys) != set(expected):
        raise AssertionError("endpoint matching is not the exact saved 1260-point incidence")
    endpoint_vertex: dict[str, str] = {}
    used_vertices = set()
    for item in records:
        key = (item["ball"], item["endpoint_id"])
        vertex = item.get("ambient_vertex")
        if (
            not isinstance(vertex, str)
            or vertex not in initial
            or vertex not in ball_boundaries[item["ball"]]
            or vertex in used_vertices
        ):
            raise AssertionError("an endpoint is not a unique vertex on its named insertion sphere")
        if initial[vertex] != qpoint(expected[key]["point"]):
            raise AssertionError("an endpoint vertex does not have the saved rational coordinate")
        if item.get("orientation") not in (-1, 1):
            raise AssertionError("endpoint matching loses orientation")
        endpoint_vertex[item["endpoint_id"]] = vertex
        used_vertices.add(vertex)
    return endpoint_vertex


def target_binding_records(
    bindings: Any, target: dict[str, Any], strand_ids: set[str]
) -> dict[tuple[str, int], dict[str, Any]]:
    target_records = {
        (side, int(item["index"])): item
        for side, records in (
            ("left", target["left_closure_strands"]),
            ("right", target["right_closure_strands"]),
        )
        for item in records
    }
    if len(target_records) != 630:
        raise AssertionError("saved target strand indices are not unique and complete")
    if not isinstance(bindings, list) or len(bindings) != 630:
        raise AssertionError("target strand binding is incomplete")
    source_keys = [item.get("source_strand_id") for item in bindings]
    target_keys = [
        (item.get("target_side"), item.get("target_index")) for item in bindings
    ]
    if set(source_keys) != strand_ids or len(set(source_keys)) != 630:
        raise AssertionError("target binding is not bijective on source strands")
    if set(target_keys) != set(target_records) or len(set(target_keys)) != 630:
        raise AssertionError("target binding is not bijective on all 630 target strands")
    return target_records


def validate(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("schema") != "t73_c_h1_relative_isotopy/v1":
        raise AssertionError("unexpected C-H1 relative-isotopy schema")
    if not SOURCE.is_file():
        raise AssertionError("coordinate source exterior is absent")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    primitives = json.loads(PRIMITIVES.read_text(encoding="utf-8"))
    for artifact, where in (
        (source, "selected source exterior"),
        (target, "selected canopolis target"),
        (primitives, "all-owner primitives"),
    ):
        recorded = artifact.get("sha256")
        payload = {key: value for key, value in artifact.items() if key != "sha256"}
        if not isinstance(recorded, str) or recorded != canonical_sha(payload):
            raise AssertionError(f"{where} embedded payload SHA256 is stale")
    expected_dependencies = {
        "source_exterior_sha256": source["sha256"],
        "selected_canopolis_target_sha256": target["sha256"],
        "all_owner_primitives_sha256": primitives["sha256"],
    }
    if data.get("dependencies") != expected_dependencies:
        raise AssertionError("movie dependencies are stale or incomplete")
    obstruction = split_matching_obstruction(source)
    if not obstruction["literal_two_disjoint_closures_relative_four_balls_possible"]:
        raise AssertionError(
            "saved split matching has "
            f"{obstruction['wrong_side_connector_count']} wrong-side connectors; "
            "no relative ambient-isotopy movie to the literal split target can pass"
        )

    ambient = data["ambient_exterior"]
    vertices = ambient.get("vertices")
    tetrahedra = ambient.get("tetrahedra")
    if not isinstance(vertices, list) or not isinstance(tetrahedra, list):
        raise AssertionError("ambient coordinates/tetrahedra are absent")
    initial: dict[str, tuple[Fraction, Fraction, Fraction]] = {}
    for item in vertices:
        vertex_id = item.get("id")
        if not isinstance(vertex_id, str) or vertex_id in initial:
            raise AssertionError("ambient vertex IDs are missing or duplicated")
        initial[vertex_id] = qpoint(item.get("point"))
    tets: list[tuple[str, str, str, str]] = []
    for item in tetrahedra:
        vertex_ids = tuple(item.get("vertices", []))
        if len(vertex_ids) != 4 or len(set(vertex_ids)) != 4 or any(v not in initial for v in vertex_ids):
            raise AssertionError("a tetrahedron has invalid vertices")
        if determinant(*(initial[v] for v in vertex_ids)) == 0:
            raise AssertionError("an initial tetrahedron is degenerate")
        tets.append(vertex_ids)  # type: ignore[arg-type]
    if not tets or len(set(tuple(sorted(tetra)) for tetra in tets)) != len(tets):
        raise AssertionError("ambient tetrahedra are empty or duplicated")
    used_vertices = {vertex for tetra in tets for vertex in tetra}
    if used_vertices != set(initial):
        raise AssertionError("ambient triangulation has unused vertices")
    face_counts = Counter(face for tetra in tets for face in faces(tetra))
    if any(count not in (1, 2) for count in face_counts.values()):
        raise AssertionError("ambient complex is not a pseudomanifold with boundary")
    tetra_adjacency = {index: set() for index in range(len(tets))}
    face_owner: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    for index, tetra in enumerate(tets):
        for face in faces(tetra):
            face_owner[face].append(index)
    for owners in face_owner.values():
        if len(owners) == 2:
            tetra_adjacency[owners[0]].add(owners[1])
            tetra_adjacency[owners[1]].add(owners[0])
    reached, queue = set(), deque([0])
    while queue:
        current = queue.popleft()
        if current in reached:
            continue
        reached.add(current)
        queue.extend(tetra_adjacency[current] - reached)
    if len(reached) != len(tets):
        raise AssertionError("ambient tetrahedral exterior is disconnected")
    edges = ambient_edges(tets)

    outer_fixed = set(ambient.get("outer_boundary_vertices", []))
    if not outer_fixed or not outer_fixed <= set(initial):
        raise AssertionError("outer boundary vertex set is absent or invalid")
    balls = ambient.get("insertion_balls", [])
    if len(balls) != 4 or {item.get("name") for item in balls} != BALL_NAMES:
        raise AssertionError("four named insertion balls are not present")
    fixed = set(outer_fixed)
    ball_boundaries: dict[str, set[str]] = {}
    for ball in balls:
        boundary = set(ball.get("boundary_vertices", []))
        if not boundary or not boundary <= set(initial):
            raise AssertionError("an insertion ball has no coordinate boundary subcomplex")
        if fixed & boundary:
            raise AssertionError("named boundary vertex sets overlap")
        ball_boundaries[ball["name"]] = boundary
        fixed |= boundary
    boundary_faces = {face for face, count in face_counts.items() if count == 1}
    if any(not set(face) <= fixed for face in boundary_faces):
        raise AssertionError("ambient boundary has an unnamed vertex")
    for name, vertices_on_component in {
        "outer": outer_fixed,
        **ball_boundaries,
    }.items():
        component_faces = {
            face for face in boundary_faces if set(face) <= vertices_on_component
        }
        component_vertices = {vertex for face in component_faces for vertex in face}
        component_edges = Counter(
            tuple(sorted(edge))
            for face in component_faces
            for edge in combinations(face, 2)
        )
        if (
            component_vertices != vertices_on_component
            or not component_faces
            or set(component_edges.values()) != {2}
            or len(component_vertices) - len(component_edges) + len(component_faces) != 2
        ):
            raise AssertionError(f"named boundary {name} is not a triangulated 2-sphere")
    named_face_union = set().union(
        *[
            {face for face in boundary_faces if set(face) <= component}
            for component in [outer_fixed, *ball_boundaries.values()]
        ]
    )
    if named_face_union != boundary_faces:
        raise AssertionError("named boundary spheres do not exhaust the ambient boundary")

    positions = dict(initial)
    moves = data.get("vertex_moves")
    if not isinstance(moves, list) or not moves:
        raise AssertionError("no rational time-slice/cell-map moves are present")
    previous_time = Fraction(0)
    for index, move in enumerate(moves):
        if int(move.get("index", -1)) != index:
            raise AssertionError("movie move indices are not consecutive")
        interval = move.get("time_interval", [])
        if len(interval) != 2:
            raise AssertionError("a move has no exact time interval")
        start_time, end_time = (Fraction(value) for value in interval)
        if start_time != previous_time or end_time <= start_time:
            raise AssertionError("movie time intervals have a gap or overlap")
        previous_time = end_time
        moved = move.get("moved_vertex")
        if moved not in positions or moved in fixed:
            raise AssertionError("a move changes a missing or boundary-fixed vertex")
        if qpoint(move.get("from")) != positions[moved]:
            raise AssertionError("a vertex move does not start at the current coordinate")
        target_point = qpoint(move.get("to"))
        if target_point == positions[moved]:
            raise AssertionError("a vertex move is the identity")
        star = [tetra for tetra in tets if moved in tetra]
        if sorted(move.get("star_tetrahedra", [])) != sorted([list(tetra) for tetra in star]):
            raise AssertionError("a move does not list its complete tetrahedral star")
        if not link_is_sphere(star, moved):
            raise AssertionError("the moved interior vertex does not have spherical link")
        for tetra in star:
            before = determinant(*(positions[v] for v in tetra))
            trial = dict(positions)
            trial[moved] = target_point
            after = determinant(*(trial[v] for v in tetra))
            if before == 0 or after == 0 or (before > 0) != (after > 0):
                raise AssertionError("a tetrahedron degenerates during a vertex move")
        positions[moved] = target_point
    if previous_time != 1:
        raise AssertionError("movie time intervals do not end at time one")

    strands = data.get("source_strands", [])
    framings = data.get("source_framings", [])
    if len(strands) != 630 or len(framings) != 630:
        raise AssertionError("the 630 source exterior intervals are incomplete")
    source_intervals = {
        item["interval_id"]: item for item in source["exterior_intervals"]
    }
    strand_ids = {item.get("id") for item in strands}
    if strand_ids != set(source_intervals) or len(strand_ids) != 630:
        raise AssertionError("source strand IDs are not the exact saved interval IDs")
    strand_by_id = {item["id"]: item for item in strands}
    used_strand_vertices: set[str] = set()
    for strand in strands:
        path = validate_edge_path(
            strand.get("vertices"), initial, edges, f"source strand {strand['id']}"
        )
        interval = source_intervals[strand["id"]]
        if [qpoint(value) for value in interval["vertices"]] != [
            initial[vertex] for vertex in path
        ]:
            raise AssertionError("a source strand is not the exact saved rational polyline")
        if strand.get("endpoint_ids") != [
            interval["from_endpoint_id"], interval["to_endpoint_id"]
        ]:
            raise AssertionError("a source strand loses its exact endpoint binding")
        if used_strand_vertices & set(path):
            raise AssertionError("two source strands share a vertex")
        used_strand_vertices |= set(path)
        if strand.get("orientation") not in (-1, 1):
            raise AssertionError("a source strand has no orientation")
    framing_by_strand = {item.get("strand_id"): item for item in framings}
    if set(framing_by_strand) != strand_ids:
        raise AssertionError("framing paths do not match source strands")
    used_framing_vertices: set[str] = set()
    for strand_id, framing in framing_by_strand.items():
        path = validate_edge_path(
            framing.get("push_off_vertices"),
            initial,
            edges,
            f"framing push-off {strand_id}",
        )
        interval = source_intervals[strand_id]
        if [qpoint(value) for value in interval["positive_push_off_vertices"]] != [
            initial[vertex] for vertex in path
        ]:
            raise AssertionError("a framing is not the exact saved rational push-off")
        if set(path) & (used_strand_vertices | used_framing_vertices):
            raise AssertionError("a framing push-off shares a vertex with a strand or framing")
        used_framing_vertices |= set(path)
        if framing.get("relative_twist") != 0:
            raise AssertionError("a source framing has nonzero relative twist")

    endpoint_matching = data.get("endpoint_matching", [])
    endpoint_vertex = validate_endpoint_matching(
        endpoint_matching, source, initial, ball_boundaries
    )
    for interval_id, interval in source_intervals.items():
        path = strand_by_id[interval_id]["vertices"]
        if [path[0], path[-1]] != [
            endpoint_vertex[interval["from_endpoint_id"]],
            endpoint_vertex[interval["to_endpoint_id"]],
        ]:
            raise AssertionError("a source edge path is not attached to its saved endpoints")

    bindings = data.get("target_binding", [])
    target_records = target_binding_records(bindings, target, strand_ids)
    for binding in bindings:
        key = (binding.get("target_side"), int(binding.get("target_index", -1)))
        if key not in target_records:
            raise AssertionError("a target binding names no target strand")
        if binding.get("target_endpoint_ids") != target_records[key]["endpoint_ids"]:
            raise AssertionError("a target binding loses exact target endpoint incidence")
        source_strand = next(item for item in strands if item["id"] == binding["source_strand_id"])
        final_points = [[str(value) for value in positions[v]] for v in source_strand["vertices"]]
        if final_points != binding.get("final_polyline"):
            raise AssertionError("a target binding is not the final source image")
        if final_points != target_records[key]["centerline"]:
            raise AssertionError("final source polyline does not equal the target arc")
        final_push_off = [
            [str(value) for value in positions[vertex]]
            for vertex in framing_by_strand[binding["source_strand_id"]][
                "push_off_vertices"
            ]
        ]
        if final_push_off != target_records[key]["positive_push_off"]:
            raise AssertionError("final framing push-off does not equal the target framing")

    degree = data.get("euler_degree", {})
    if any(int(degree.get(name, -1)) != 0 for name in ("births", "saddles", "deaths")):
        raise AssertionError("movie contains topology-changing critical points")
    if int(degree.get("closed_trace_euler_characteristic", 1)) != 0:
        raise AssertionError("closed trace is not a union of annuli")
    if int(degree.get("quantum_shift", 1)) != 0:
        raise AssertionError("ambient isotopy has a nonzero quantum shift")
    if not data.get("boundary_fixed", False) or not data.get("four_insertion_balls_pointwise_fixed", False):
        raise AssertionError("movie is not relative to all required boundary")

    return {
        "status": "PASS_COORDINATE_MOVIE",
        "vertices": len(vertices),
        "tetrahedra": len(tets),
        "moves": len(moves),
        "strands": len(strands),
        "endpoints": len(endpoint_matching),
        "quantum_shift": 0,
    }


def generate_report() -> dict[str, Any]:
    missing = []
    source_summary = None
    target_summary = None
    endpoint_mismatch = None
    split_matching_obstruction = None
    if not SOURCE.is_file():
        missing.append(
            "geometry/t73_selected_source_exterior.json: four-box source incidence"
        )
    else:
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        source_summary = {
            "schema": source.get("schema"),
            "endpoint_counts_per_sphere": source.get("endpoint_counts_per_sphere"),
            "total_boundary_endpoint_count": source.get("total_boundary_endpoint_count"),
            "exterior_interval_count": source.get("exterior_interval_count"),
            "canonical_representative_only": source.get("canonical_representative_only"),
            "actual_ar_relative_isotopy_proved": source.get("actual_ar_relative_isotopy_proved"),
            "has_common_tetrahedral_exterior": "ambient_exterior" in source,
        }
        endpoint_sphere = {
            endpoint["endpoint_id"]: sphere["name"]
            for sphere in source.get("insertion_spheres", [])
            for endpoint in sphere.get("endpoints", [])
        }
        active = []
        for interval in source.get("exterior_intervals", []):
            start_sphere = endpoint_sphere.get(interval.get("from_endpoint_id"))
            end_sphere = endpoint_sphere.get(interval.get("to_endpoint_id"))
            if start_sphere and end_sphere and (
                start_sphere.startswith("Y") or end_sphere.startswith("Y")
            ):
                active.append((interval, start_sphere, end_sphere))
        representable_pairs = {
            frozenset(("Y_minus", "Z_plus")),
            frozenset(("Y_plus", "Z_minus")),
        }
        wrong_side = [
            {
                "interval_id": interval["interval_id"],
                "owner": interval["owner"],
                "copy_sign": interval["copy_sign"],
                "from_source_id": interval["from_source_id"],
                "to_source_id": interval["to_source_id"],
                "from_sphere": start_sphere,
                "to_sphere": end_sphere,
            }
            for interval, start_sphere, end_sphere in active
            if frozenset((start_sphere, end_sphere)) not in representable_pairs
        ]
        transition_counts = Counter(
            tuple(sorted((start_sphere, end_sphere)))
            for _interval, start_sphere, end_sphere in active
        )
        split_matching_obstruction = {
            "active_y_incident_interval_count": len(active),
            "transition_counts": {
                "--".join(key): value for key, value in sorted(transition_counts.items())
            },
            "expected_two_representable_pairs": [
                ["Y_minus", "Z_plus"],
                ["Y_plus", "Z_minus"],
            ],
            "wrong_side_connector_count": len(wrong_side),
            "wrong_side_connectors": wrong_side,
            "literal_two_disjoint_closures_relative_four_balls_possible": len(wrong_side) == 0,
            "reason": (
                "wrong-side connectors force both proposed closure factors to use endpoint subsets "
                "on the same Z insertion spheres; arbitrary C_271 tangles do not preserve those subsets"
            ),
        }
        if "ambient_exterior" not in source:
            missing.append(
                "source exterior common tetrahedral mesh with arcs/ribbons as subcomplexes"
            )
    if TARGET.is_file():
        target = json.loads(TARGET.read_text(encoding="utf-8"))
        target_counts = target.get("endpoint_counts_per_insertion_ball", {})
        target_summary = {
            "schema": target.get("schema"),
            "endpoint_counts_per_insertion_ball": target_counts,
            "total_boundary_endpoint_count": sum(target_counts.values()),
            "strand_count": len(target.get("left_closure_strands", []))
            + len(target.get("right_closure_strands", [])),
            "scope": target.get("scope"),
        }
        if source_summary:
            source_counts = source_summary["endpoint_counts_per_sphere"]
            if (
                sorted(source_counts.values()) != sorted(target_counts.values())
                or source_summary["total_boundary_endpoint_count"]
                != target_summary["total_boundary_endpoint_count"]
            ):
                endpoint_mismatch = {
                    "source_sorted_counts": sorted(source_counts.values()),
                    "target_sorted_counts": sorted(target_counts.values()),
                    "source_total": source_summary["total_boundary_endpoint_count"],
                    "target_total": target_summary["total_boundary_endpoint_count"],
                    "ambient_isotopy_relative_four_balls_possible": False,
                    "reason": "boundary-fixed ambient isotopy preserves endpoint count on every insertion sphere",
                }
    if not MOVIE.is_file():
        missing.append(
            "geometry/t73_c_h1_relative_isotopy.json: rational tetrahedra, every vertex move/time slab, framings, and final target binding"
        )
    legacy_scope = None
    if LEGACY.is_file():
        legacy = json.loads(LEGACY.read_text(encoding="utf-8"))
        legacy_scope = {
            "status_field": legacy.get("status"),
            "exhibited_product_isotopy_field": legacy.get("exhibited_product_isotopy"),
            "rectangle_frames_are_hashes_only": all(
                set(frame) == {"time", "arc_sha256"}
                for movie in legacy.get("rectangle_movies", [])
                for frame in movie.get("frames", [])
            ),
            "accepted_as_coordinate_movie": False,
        }
    report = {
        "schema": "t73_c_h1_relative_isotopy_report/v1",
        "status": (
            "IMPOSSIBLE_LITERAL_SPLIT_BOUNDARY_MATCHING"
            if split_matching_obstruction
            and not split_matching_obstruction[
                "literal_two_disjoint_closures_relative_four_balls_possible"
            ]
            else "IMPOSSIBLE_CURRENT_TARGET_BOUNDARY_TYPE"
            if endpoint_mismatch
            else "OPEN"
            if missing
            else "UNVERIFIED"
        ),
        "missing": missing,
        "source_exterior": source_summary,
        "selected_target": target_summary,
        "boundary_endpoint_mismatch": endpoint_mismatch,
        "split_matching_obstruction": split_matching_obstruction,
        "legacy_product_isotopy": legacy_scope,
        "target_normal_form_present": TARGET.is_file(),
        "target_only_is_not_source_isotopy": True,
    }
    if (
        not missing
        and not endpoint_mismatch
        and (
            not split_matching_obstruction
            or split_matching_obstruction[
                "literal_two_disjoint_closures_relative_four_balls_possible"
            ]
        )
    ):
        try:
            report["verification"] = validate(json.loads(MOVIE.read_text(encoding="utf-8")))
        except (AssertionError, KeyError, ValueError, TypeError) as error:
            report["status"] = "FAIL"
            report["error"] = str(error)
        else:
            report["status"] = "PASS_COORDINATE_MOVIE"
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--allow-open", action="store_true")
    args = parser.parse_args()
    report = generate_report()
    if args.write:
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "PASS_COORDINATE_MOVIE" and not args.allow_open:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
