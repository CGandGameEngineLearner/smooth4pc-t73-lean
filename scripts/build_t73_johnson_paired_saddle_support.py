#!/usr/bin/env python3
"""Build the ball support for the final paired Johnson saddle."""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import itertools
import json
import math
import functools
import heapq
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SWEEP = ROOT / "geometry" / "t73_johnson_elementary_sweep.json"
DISK_CELLS = ROOT / "geometry" / "t73_johnson_disk_move_cells.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_paired_saddle_support.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def boundary_edges(sweep_tools, faces):
    counts = collections.Counter(
        tuple(
            sorted(
                (
                    sweep_tools.periodic_vertex(face[first]),
                    sweep_tools.periodic_vertex(face[second]),
                )
            )
        )
        for face in faces
        for first, second in ((0, 1), (0, 2), (1, 2))
    )
    return {edge for edge, count in counts.items() if count == 1}


def shortest_path(adjacency, starts, targets):
    queue = collections.deque(sorted(starts))
    parent = {index: None for index in starts}
    end = None
    while queue and end is None:
        current = queue.popleft()
        for neighbour in sorted(adjacency[current]):
            if neighbour in parent:
                continue
            parent[neighbour] = current
            if neighbour in targets:
                end = neighbour
                break
            queue.append(neighbour)
    if end is None:
        raise AssertionError("paired saddle balls have no dual-face path")
    path = []
    current = end
    while current is not None and current not in starts:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path


def induced_ball_path(analyzer, sweep_tools, tetrahedra, adjacency, face_occurrences, starts, targets):
    outside = set(range(len(tetrahedra))) - starts - targets
    entries = [
        index
        for index in outside
        if sum(neighbour in starts for neighbour in adjacency[index]) == 1
        and not any(neighbour in targets for neighbour in adjacency[index])
    ]
    exits = {
        index
        for index in outside
        if sum(neighbour in targets for neighbour in adjacency[index]) == 1
        and not any(neighbour in starts for neighbour in adjacency[index])
    }
    internal = {
        index
        for index in outside
        if not any(
            neighbour in starts or neighbour in targets for neighbour in adjacency[index]
        )
    }
    allowed = internal | set(entries) | exits
    for entry in sorted(entries):
        queue = collections.deque([entry])
        parent = {entry: None}
        while queue:
            current = queue.popleft()
            if current in exits:
                path = []
                vertex = current
                while vertex is not None:
                    path.append(vertex)
                    vertex = parent[vertex]
                path.reverse()
                support = starts | targets | set(path)
                boundary = [
                    face
                    for face, hits in face_occurrences.items()
                    if sum(index in support for index, _ in hits) == 1
                ]
                collapse = analyzer.collapse_to_point(
                    [
                        tuple(
                            sweep_tools.periodic_vertex(vertex)
                            for vertex in tetrahedra[index]["vertices"]
                        )
                        for index in support
                    ]
                )
                if (
                    sweep_tools.patch_invariants(boundary)["topology"] == "sphere"
                    and collapse["collapses_to_point"]
                ):
                    return path
            for neighbour in sorted(adjacency[current]):
                if neighbour in allowed and neighbour not in parent:
                    parent[neighbour] = current
                    queue.append(neighbour)
    raise AssertionError("no induced ball path joins the paired saddle cores")


def curve_complement_regions(sweep_tools, support_boundary, cut_edges):
    edge_faces = collections.defaultdict(list)
    for face_index, face in enumerate(support_boundary):
        for first, second in ((0, 1), (0, 2), (1, 2)):
            edge = tuple(
                sorted(
                    (
                        sweep_tools.periodic_vertex(face[first]),
                        sweep_tools.periodic_vertex(face[second]),
                    )
                )
            )
            edge_faces[edge].append(face_index)
    adjacency = [set() for _ in support_boundary]
    for edge, hits in edge_faces.items():
        if edge in cut_edges:
            continue
        if len(hits) != 2:
            raise AssertionError("support boundary is not a triangulated surface")
        first, second = hits
        adjacency[first].add(second)
        adjacency[second].add(first)
    seen = set()
    regions = []
    for start in range(len(support_boundary)):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        component = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbour in adjacency[current]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        regions.append(
            sweep_tools.patch_invariants(
                [support_boundary[index] for index in component]
            )
        )
    return regions


def subdivide_tetrahedron(tetrahedron):
    return [
        tuple(frozenset(permutation[:size]) for size in range(1, 5))
        for permutation in itertools.permutations(tetrahedron)
    ]


def fast_collapse_to_point(tetrahedra):
    simplices = [set() for _ in range(4)]
    for tetrahedron in tetrahedra:
        for size in range(1, 5):
            simplices[size - 1].update(
                frozenset(simplex) for simplex in itertools.combinations(tetrahedron, size)
            )
    steps = 0
    for dimension in (3, 2, 1):
        cofaces = collections.defaultdict(set)
        for simplex in simplices[dimension]:
            for face in itertools.combinations(simplex, dimension):
                cofaces[frozenset(face)].add(simplex)
        queue = collections.deque(
            face for face in simplices[dimension - 1] if len(cofaces[face]) == 1
        )
        while queue:
            face = queue.popleft()
            if face not in simplices[dimension - 1]:
                continue
            hosts = cofaces[face] & simplices[dimension]
            if len(hosts) != 1:
                continue
            simplex = next(iter(hosts))
            simplices[dimension].remove(simplex)
            simplices[dimension - 1].remove(face)
            steps += 1
            for facet in itertools.combinations(simplex, dimension):
                facet = frozenset(facet)
                cofaces[facet].discard(simplex)
                if facet in simplices[dimension - 1] and len(cofaces[facet]) == 1:
                    queue.append(facet)
    return {
        "collapse_steps": steps,
        "remaining_vertices": len(simplices[0]),
        "remaining_edges": len(simplices[1]),
        "remaining_faces": len(simplices[2]),
        "remaining_tetrahedra": len(simplices[3]),
        "collapses_to_point": (
            len(simplices[0]) == 1
            and not simplices[1]
            and not simplices[2]
            and not simplices[3]
        ),
    }


def fast_relative_collapse(tetrahedra, protected_faces):
    simplices = [set() for _ in range(4)]
    for tetrahedron in tetrahedra:
        for size in range(1, 5):
            simplices[size - 1].update(
                frozenset(simplex) for simplex in itertools.combinations(tetrahedron, size)
            )
    protected = [set() for _ in range(4)]
    for face in protected_faces:
        for size in range(1, 4):
            protected[size - 1].update(
                frozenset(simplex) for simplex in itertools.combinations(face, size)
            )
    histogram = collections.Counter()
    step_digest_rows = []
    for dimension in (3, 2, 1):
        cofaces = collections.defaultdict(set)
        for simplex in simplices[dimension]:
            for face in itertools.combinations(simplex, dimension):
                cofaces[frozenset(face)].add(simplex)
        queue = []
        for face in simplices[dimension - 1] - protected[dimension - 1]:
            hosts = cofaces[face] & simplices[dimension]
            if len(hosts) == 1:
                simplex = next(iter(hosts))
                if simplex not in protected[dimension]:
                    heapq.heappush(
                        queue,
                        (tuple(sorted(simplex)), tuple(sorted(face))),
                    )
        while queue:
            simplex_key, face_key = heapq.heappop(queue)
            simplex = frozenset(simplex_key)
            face = frozenset(face_key)
            if (
                simplex not in simplices[dimension]
                or face not in simplices[dimension - 1]
                or face in protected[dimension - 1]
            ):
                continue
            hosts = cofaces[face] & simplices[dimension]
            if hosts != {simplex}:
                continue
            simplices[dimension].remove(simplex)
            simplices[dimension - 1].remove(face)
            histogram[dimension] += 1
            step_digest_rows.append((dimension, simplex_key, face_key))
            for facet in itertools.combinations(simplex, dimension):
                facet = frozenset(facet)
                cofaces[facet].discard(simplex)
                hosts = cofaces[facet] & simplices[dimension]
                if (
                    facet in simplices[dimension - 1]
                    and facet not in protected[dimension - 1]
                    and len(hosts) == 1
                ):
                    host = next(iter(hosts))
                    if host not in protected[dimension]:
                        heapq.heappush(
                            queue,
                            (tuple(sorted(host)), tuple(sorted(facet))),
                        )
    equality = [simplices[dimension] == protected[dimension] for dimension in range(4)]
    if equality != [True, True, True, True]:
        raise AssertionError("derived path star does not collapse exactly to its cap disk")
    return {
        "step_count": len(step_digest_rows),
        "dimension_histogram": {
            str(key): value for key, value in sorted(histogram.items())
        },
        "remaining_simplex_counts": [len(simplices[dimension]) for dimension in range(4)],
        "protected_simplex_counts": [len(protected[dimension]) for dimension in range(4)],
        "remaining_equals_cap_by_dimension": equality,
        "step_sequence_sha256": canonical_sha(step_digest_rows),
        "relative_collapse_status": "PASS",
    }


def abstract_ball_invariants(tetrahedra):
    face_counts = collections.Counter(
        frozenset(tetrahedron[index] for index in range(4) if index != omitted)
        for tetrahedron in tetrahedra
        for omitted in range(4)
    )
    boundary = [face for face, count in face_counts.items() if count == 1]
    edge_counts = collections.Counter(
        frozenset(edge) for face in boundary for edge in itertools.combinations(face, 2)
    )
    vertices = {vertex for face in boundary for vertex in face}
    face_adjacency = [set() for _ in boundary]
    edge_faces = collections.defaultdict(list)
    for face_index, face in enumerate(boundary):
        for edge in itertools.combinations(face, 2):
            edge_faces[frozenset(edge)].append(face_index)
    for hits in edge_faces.values():
        if len(hits) == 2:
            first, second = hits
            face_adjacency[first].add(second)
            face_adjacency[second].add(first)
    reached = {0}
    stack = [0]
    while stack:
        current = stack.pop()
        for neighbour in face_adjacency[current]:
            if neighbour not in reached:
                reached.add(neighbour)
                stack.append(neighbour)
    return {
        "tetrahedra": len(tetrahedra),
        "boundary_vertices": len(vertices),
        "boundary_edges": len(edge_counts),
        "boundary_faces": len(boundary),
        "boundary_euler": len(vertices) - len(edge_counts) + len(boundary),
        "boundary_edge_multiplicities": {
            str(key): value
            for key, value in sorted(collections.Counter(edge_counts.values()).items())
        },
        "boundary_connected": len(reached) == len(boundary),
        "boundary_is_sphere": (
            len(reached) == len(boundary)
            and set(edge_counts.values()) == {2}
            and len(vertices) - len(edge_counts) + len(boundary) == 2
        ),
    }


def abstract_surface_invariants(faces):
    edge_counts = collections.Counter(
        frozenset(edge) for face in faces for edge in itertools.combinations(face, 2)
    )
    vertices = {vertex for face in faces for vertex in face}
    face_adjacency = [set() for _ in faces]
    edge_faces = collections.defaultdict(list)
    for face_index, face in enumerate(faces):
        for edge in itertools.combinations(face, 2):
            edge_faces[frozenset(edge)].append(face_index)
    for hits in edge_faces.values():
        if len(hits) == 2:
            first, second = hits
            face_adjacency[first].add(second)
            face_adjacency[second].add(first)
    seen = set()
    components = 0
    for start in range(len(faces)):
        if start in seen:
            continue
        components += 1
        stack = [start]
        seen.add(start)
        while stack:
            current = stack.pop()
            for neighbour in face_adjacency[current]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
    boundary_edges = [edge for edge, count in edge_counts.items() if count == 1]
    boundary_adjacency = collections.defaultdict(set)
    for edge in boundary_edges:
        first, second = tuple(edge)
        boundary_adjacency[first].add(second)
        boundary_adjacency[second].add(first)
    boundary_seen = set()
    boundary_components = 0
    for start in boundary_adjacency:
        if start in boundary_seen:
            continue
        boundary_components += 1
        stack = [start]
        boundary_seen.add(start)
        while stack:
            current = stack.pop()
            for neighbour in boundary_adjacency[current]:
                if neighbour not in boundary_seen:
                    boundary_seen.add(neighbour)
                    stack.append(neighbour)
    euler = len(vertices) - len(edge_counts) + len(faces)
    manifold = all(count in (1, 2) for count in edge_counts.values())
    return {
        "vertices": len(vertices),
        "edges": len(edge_counts),
        "faces": len(faces),
        "euler": euler,
        "surface_components": components,
        "boundary_components": boundary_components,
        "edge_multiplicities": {
            str(key): value
            for key, value in sorted(collections.Counter(edge_counts.values()).items())
        },
        "surface_manifold": manifold,
        "topology": (
            "disk"
            if manifold and components == 1 and boundary_components == 1 and euler == 1
            else "OPEN"
        ),
    }


def regular_path_neighbourhood(sweep_tools, tetrahedra, adjacency, path, add_ball, remove_ball):
    core_path = [index for index in path if index not in add_ball and index not in remove_ball]
    if not core_path:
        raise AssertionError("paired saddle has no agreement path")
    original = [
        tuple(sweep_tools.periodic_vertex(vertex) for vertex in tetrahedra[index]["vertices"])
        for index in core_path
    ]
    full_barycentres = [frozenset(tetrahedron) for tetrahedron in original]
    shared_faces = [
        frozenset(set(original[index]) & set(original[index + 1]))
        for index in range(len(original) - 1)
    ]
    if any(len(face) != 3 for face in shared_faces):
        raise AssertionError("dual path does not cross triangular faces")
    add_neighbour = next(
        neighbour for neighbour in adjacency[core_path[0]] if neighbour in add_ball
    )
    remove_neighbour = next(
        neighbour for neighbour in adjacency[core_path[-1]] if neighbour in remove_ball
    )
    cap_faces = [
        frozenset(
            set(original[0])
            & {
                sweep_tools.periodic_vertex(vertex)
                for vertex in tetrahedra[add_neighbour]["vertices"]
            }
        ),
        frozenset(
            set(original[-1])
            & {
                sweep_tools.periodic_vertex(vertex)
                for vertex in tetrahedra[remove_neighbour]["vertices"]
            }
        ),
    ]
    if any(len(face) != 3 for face in cap_faces):
        raise AssertionError("path cap is not a triangular face")
    core_vertices = set(full_barycentres) | set(shared_faces) | set(cap_faces)
    core_edges = {
        frozenset((cap_faces[0], full_barycentres[0])),
        frozenset((full_barycentres[-1], cap_faces[1])),
    }
    core_edges.update(
        frozenset((full_barycentres[index], shared_faces[index]))
        for index in range(len(shared_faces))
    )
    core_edges.update(
        frozenset((shared_faces[index], full_barycentres[index + 1]))
        for index in range(len(shared_faces))
    )
    subdivided_core = {frozenset((vertex,)) for vertex in core_vertices} | core_edges
    first_subdivision = [
        simplex
        for tetrahedron in original
        for simplex in subdivide_tetrahedron(tetrahedron)
    ]
    second_subdivision = [
        simplex
        for tetrahedron in first_subdivision
        for simplex in subdivide_tetrahedron(tetrahedron)
    ]
    star = [
        tetrahedron
        for tetrahedron in second_subdivision
        if any(vertex in subdivided_core for vertex in tetrahedron)
    ]
    vertices = sorted({vertex for tetrahedron in star for vertex in tetrahedron}, key=repr)
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    indexed = [
        tuple(vertex_index[vertex] for vertex in tetrahedron) for tetrahedron in star
    ]
    face_counts = collections.Counter(
        frozenset(tetrahedron[index] for index in range(4) if index != omitted)
        for tetrahedron in star
        for omitted in range(4)
    )
    boundary_faces = [face for face, count in face_counts.items() if count == 1]

    def original_carrier(second_vertex):
        return frozenset(
            original_vertex
            for first_vertex in second_vertex
            for original_vertex in first_vertex
        )

    cap_records = []
    for cap_face in cap_faces:
        cap_triangles_nested = [
            face
            for face in boundary_faces
            if all(original_carrier(vertex) <= cap_face for vertex in face)
        ]
        cap_triangles = [
            tuple(vertex_index[vertex] for vertex in face)
            for face in cap_triangles_nested
        ]
        cap_invariants = abstract_surface_invariants(cap_triangles)
        if cap_invariants["topology"] != "disk" or len(cap_triangles) != 12:
            raise AssertionError("derived path cap is not a twelve-triangle disk")
        cap_records.append(
            {
                "triangle_count": len(cap_triangles),
                "triangles": [list(face) for face in cap_triangles],
                "surface": cap_invariants,
                "relative_collapse": fast_relative_collapse(indexed, cap_triangles),
            }
        )
    invariants = abstract_ball_invariants(indexed)
    collapse = fast_collapse_to_point(indexed)
    if not invariants["boundary_is_sphere"] or not collapse["collapses_to_point"]:
        raise AssertionError("second-derived path star is not a collapsible ball")
    return {
        "subdivision": "closed star of the subdivided dual path in sd^2",
        "path_tetrahedra": len(core_path),
        "core_vertices": len(core_vertices),
        "core_edges": len(core_edges),
        "first_subdivision_tetrahedra": len(first_subdivision),
        "second_subdivision_tetrahedra": len(second_subdivision),
        "star_tetrahedra": len(star),
        "cap_faces": [
            [[str(value) for value in vertex] for vertex in sorted(face)]
            for face in cap_faces
        ],
        "caps": cap_records,
        "both_caps_are_twelve_triangle_disks": all(
            cap["triangle_count"] == 12 and cap["surface"]["topology"] == "disk"
            for cap in cap_records
        ),
        "both_cap_relative_collapses": (
            "PASS"
            if all(
                cap["relative_collapse"]["relative_collapse_status"] == "PASS"
                for cap in cap_records
            )
            else "OPEN"
        ),
        **invariants,
        **collapse,
        "regular_neighbourhood_status": "PASS",
    }


def bbox_clearance(tetrahedra, support):
    best = None
    for index in support:
        vertices = tetrahedra[index]["vertices"]
        lows = [min(vertex[axis] for vertex in vertices) for axis in range(3)]
        highs = [max(vertex[axis] for vertex in vertices) for axis in range(3)]
        for lattice in itertools.product(
            *(
                range(
                    math.floor(float(lows[axis]) / 4) - 1,
                    math.ceil(float(highs[axis]) / 4) + 2,
                )
                for axis in range(3)
            )
        ):
            point = [Fraction(4 * value) for value in lattice]
            gaps = [
                lows[axis] - point[axis]
                if point[axis] < lows[axis]
                else point[axis] - highs[axis]
                if point[axis] > highs[axis]
                else Fraction(0)
                for axis in range(3)
            ]
            distance = max(gaps)
            best = distance if best is None else min(best, distance)
    if best is None:
        raise AssertionError("paired saddle support is empty")
    return best


def planar_genus(invariants):
    numerator = (
        2 * invariants["surface_components"]
        - invariants["boundary_components"]
        - invariants["euler"]
    )
    if numerator < 0 or numerator % 2:
        raise AssertionError("paired saddle patch has invalid orientable genus")
    return numerator // 2


def component_boundary_partition(sweep_tools, faces):
    face_edges = []
    edge_faces = collections.defaultdict(list)
    for index, face in enumerate(faces):
        edges = {
            tuple(
                sorted(
                    (
                        sweep_tools.periodic_vertex(face[first]),
                        sweep_tools.periodic_vertex(face[second]),
                    )
                )
            )
            for first, second in ((0, 1), (0, 2), (1, 2))
        }
        face_edges.append(edges)
        for edge in edges:
            edge_faces[edge].append(index)
    adjacency = [set() for _ in faces]
    for hits in edge_faces.values():
        if len(hits) == 2:
            first, second = hits
            adjacency[first].add(second)
            adjacency[second].add(first)
    seen = set()
    partitions = []
    for start in range(len(faces)):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        component = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbour in adjacency[current]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        counts = collections.Counter(
            edge for face_index in component for edge in face_edges[face_index]
        )
        partitions.append(
            tuple(
                sorted(
                    tuple(tuple(str(value) for value in vertex) for vertex in edge)
                    for edge, count in counts.items()
                    if count == 1
                )
            )
        )
    return sorted(partitions)


def boundary_loop_groups(sweep_tools, faces):
    face_edges = []
    edge_faces = collections.defaultdict(list)
    for index, face in enumerate(faces):
        edges = {
            tuple(
                sorted(
                    (
                        sweep_tools.periodic_vertex(face[first]),
                        sweep_tools.periodic_vertex(face[second]),
                    )
                )
            )
            for first, second in ((0, 1), (0, 2), (1, 2))
        }
        face_edges.append(edges)
        for edge in edges:
            edge_faces[edge].append(index)
    face_adjacency = [set() for _ in faces]
    for hits in edge_faces.values():
        if len(hits) == 2:
            first, second = hits
            face_adjacency[first].add(second)
            face_adjacency[second].add(first)
    seen_faces = set()
    groups = []
    for start in range(len(faces)):
        if start in seen_faces:
            continue
        stack = [start]
        seen_faces.add(start)
        component = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbour in face_adjacency[current]:
                if neighbour not in seen_faces:
                    seen_faces.add(neighbour)
                    stack.append(neighbour)
        counts = collections.Counter(
            edge for face_index in component for edge in face_edges[face_index]
        )
        boundary = {edge for edge, count in counts.items() if count == 1}
        vertex_edges = collections.defaultdict(set)
        for edge in boundary:
            vertex_edges[edge[0]].add(edge)
            vertex_edges[edge[1]].add(edge)
        unseen_edges = set(boundary)
        loops = []
        while unseen_edges:
            edge = min(unseen_edges)
            unseen_edges.remove(edge)
            loop = {edge}
            vertices = list(edge)
            while vertices:
                vertex = vertices.pop()
                for neighbour_edge in vertex_edges[vertex]:
                    if neighbour_edge in unseen_edges:
                        unseen_edges.remove(neighbour_edge)
                        loop.add(neighbour_edge)
                        vertices.extend(neighbour_edge)
            loops.append(
                tuple(
                    sorted(
                        tuple(tuple(str(value) for value in vertex) for vertex in item)
                        for item in loop
                    )
                )
            )
        groups.append(sorted(loops))
    return sorted(groups)


def minimal_loop_permutation(source_groups, target_groups):
    loops = sorted({loop for group in source_groups for loop in group})
    if loops != sorted({loop for group in target_groups for loop in group}):
        raise AssertionError("source and target do not have the same boundary loops")
    loop_index = {loop: index for index, loop in enumerate(loops)}
    source = sorted(tuple(sorted(loop_index[loop] for loop in group)) for group in source_groups)
    target = sorted(tuple(sorted(loop_index[loop] for loop in group)) for group in target_groups)
    candidates = []
    for permutation in itertools.permutations(range(len(loops))):
        image = sorted(
            tuple(sorted(permutation[index] for index in group)) for group in source
        )
        if image == target:
            moved = sum(index != image_index for index, image_index in enumerate(permutation))
            candidates.append((moved, permutation))
    if not candidates:
        raise AssertionError("no boundary-loop permutation matches component partitions")
    _, permutation = min(candidates)
    seen = set()
    cycles = []
    for start in range(len(permutation)):
        if start in seen or permutation[start] == start:
            seen.add(start)
            continue
        cycle = []
        current = start
        while current not in seen:
            seen.add(current)
            cycle.append(current)
            current = permutation[current]
        cycles.append(cycle)
    return {
        "loop_count": len(loops),
        "source_groups": [list(group) for group in source],
        "target_groups": [list(group) for group in target],
        "permutation": list(permutation),
        "nontrivial_cycles": cycles,
        "all_cycles_are_transpositions": all(len(cycle) == 2 for cycle in cycles),
        "loop_edge_counts": [len(loop) for loop in loops],
    }


def loop_tree(sweep_tools, support_boundary, source_patch, loop_permutation):
    source_groups = boundary_loop_groups(sweep_tools, source_patch)
    loops = sorted({loop for group in source_groups for loop in group})
    loop_index = {edge: index for index, loop in enumerate(loops) for edge in loop}
    edge_faces = collections.defaultdict(list)
    serialized_face_edges = []
    for face_index, face in enumerate(support_boundary):
        edges = []
        for first, second in ((0, 1), (0, 2), (1, 2)):
            edge = tuple(
                tuple(str(value) for value in vertex)
                for vertex in sorted(
                    (
                        sweep_tools.periodic_vertex(face[first]),
                        sweep_tools.periodic_vertex(face[second]),
                    )
                )
            )
            edges.append(edge)
            edge_faces[edge].append(face_index)
        serialized_face_edges.append(edges)
    adjacency = [set() for _ in support_boundary]
    for edge, hits in edge_faces.items():
        if edge in loop_index:
            continue
        if len(hits) != 2:
            raise AssertionError(
                f"support sphere edge does not have two faces: {edge} -> {hits}"
            )
        first, second = hits
        adjacency[first].add(second)
        adjacency[second].add(first)
    face_region = {}
    regions = []
    for start in range(len(support_boundary)):
        if start in face_region:
            continue
        region_id = len(regions)
        stack = [start]
        face_region[start] = region_id
        region = []
        while stack:
            current = stack.pop()
            region.append(current)
            for neighbour in adjacency[current]:
                if neighbour not in face_region:
                    face_region[neighbour] = region_id
                    stack.append(neighbour)
        regions.append(sorted(region))
    incidence = []
    for loop in loops:
        adjacent_regions = set()
        for edge in loop:
            for face_index in edge_faces[edge]:
                adjacent_regions.add(face_region[face_index])
        if len(adjacent_regions) != 2:
            raise AssertionError("boundary loop does not separate two sphere regions")
        incidence.append(tuple(sorted(adjacent_regions)))
    if len(regions) != len(loops) + 1:
        raise AssertionError("loop complement graph is not a tree")
    permutation = tuple(loop_permutation["permutation"])
    region_permutation = None
    for candidate in itertools.permutations(range(len(regions))):
        if all(
            tuple(sorted((candidate[first], candidate[second])))
            == incidence[permutation[index]]
            for index, (first, second) in enumerate(incidence)
        ):
            region_permutation = candidate
            break
    if region_permutation is None:
        raise AssertionError("boundary loop permutation does not preserve nesting")
    return {
        "loop_count": len(loops),
        "region_count": len(regions),
        "region_face_counts": [len(region) for region in regions],
        "loop_region_incidence": [list(edge) for edge in incidence],
        "region_permutation": list(region_permutation),
        "is_tree": True,
        "loop_permutation_extends_to_tree_automorphism": True,
    }


def build_movie(analyzer, pl, sweep_tools, movie):
    tetrahedra, adjacency, face_occurrences = sweep_tools.build_tetrahedra(
        analyzer, pl, movie["power"]
    )
    current = [tetrahedron["source_owner"] == 0 for tetrahedron in tetrahedra]
    goal = [tetrahedron["target_owner"] == 0 for tetrahedron in tetrahedra]
    for index in movie["single_move_tetrahedra"]:
        current[index] = goal[index]
    add_ball = set(
        next(
            move["tetrahedra"] for move in movie["grouped_moves"] if move["operation"] == "add"
        )
    )
    remove_ball = set(
        next(
            move["tetrahedra"]
            for move in movie["grouped_moves"]
            if move["operation"] == "remove"
        )
    )
    path = (
        shortest_path(adjacency, add_ball, remove_ball)
        if movie["power"] < 0
        else induced_ball_path(
            analyzer,
            sweep_tools,
            tetrahedra,
            adjacency,
            face_occurrences,
            add_ball,
            remove_ball,
        )
    )
    core = add_ball | remove_ball | set(path)
    support = core
    support_boundary = []
    source_patch = []
    target_patch = []
    boundary_agrees = True
    for face, hits in face_occurrences.items():
        (first, _), (second, _) = hits
        first_inside = first in support
        second_inside = second in support
        if first_inside != second_inside:
            support_boundary.append(face)
            inside = first if first_inside else second
            outside = second if first_inside else first
            boundary_agrees &= current[inside] == goal[inside]
            boundary_agrees &= current[outside] == goal[outside]
        elif first_inside:
            if current[first] != current[second]:
                source_patch.append(face)
            if goal[first] != goal[second]:
                target_patch.append(face)
    boundary_invariants = sweep_tools.patch_invariants(support_boundary)
    source_invariants = sweep_tools.patch_invariants(source_patch)
    target_invariants = sweep_tools.patch_invariants(target_patch)
    source_invariants["total_genus"] = planar_genus(source_invariants)
    target_invariants["total_genus"] = planar_genus(target_invariants)
    source_curve = boundary_edges(sweep_tools, source_patch)
    target_curve = boundary_edges(sweep_tools, target_patch)
    source_vertices = {vertex for edge in source_curve for vertex in edge}
    target_vertices = {vertex for edge in target_curve for vertex in edge}
    complement_regions = curve_complement_regions(
        sweep_tools, support_boundary, source_curve | target_curve
    )
    regular_neighbourhood = regular_path_neighbourhood(
        sweep_tools, tetrahedra, adjacency, path, add_ball, remove_ball
    )
    collapse = analyzer.collapse_to_point(
        [
            tuple(sweep_tools.periodic_vertex(vertex) for vertex in tetrahedra[index]["vertices"])
            for index in support
        ]
    )
    clearance = bbox_clearance(tetrahedra, support)
    if clearance <= pl.PROTECTED_RADIUS:
        raise AssertionError("paired saddle support meets the protected ball")
    transition_pattern = (
        len(source_curve & target_curve) == 1
        and len(source_vertices & target_vertices) == 2
        and len(complement_regions) == 3
        and all(region["topology"] == "disk" for region in complement_regions)
        if movie["power"] < 0
        else not (source_curve & target_curve)
        and not (source_vertices & target_vertices)
        and sorted(region["topology"] for region in complement_regions)
        == ["annulus", "disk", "disk"]
    )
    passed = (
        boundary_invariants["topology"] == "sphere"
        and collapse["collapses_to_point"]
        and source_invariants["topology"] == "disk"
        and target_invariants["topology"] == "disk"
        and transition_pattern
    )
    return {
        "power": movie["power"],
        "side": movie["side"],
        "add_ball_tetrahedra": len(add_ball),
        "remove_ball_tetrahedra": len(remove_ball),
        "dual_path": path,
        "dual_path_length": len(path),
        "core_tetrahedron_count": len(core),
        "path_kind": "shortest" if movie["power"] < 0 else "induced_ball",
        "support_tetrahedron_count": len(support),
        "support_tetrahedra": sorted(support),
        "support_boundary": boundary_invariants,
        "support_collapses_to_point": collapse["collapses_to_point"],
        "source_patch": source_invariants,
        "target_patch": target_invariants,
        "source_boundary_edge_count": len(source_curve),
        "target_boundary_edge_count": len(target_curve),
        "shared_boundary_edge_count": len(source_curve & target_curve),
        "shared_boundary_vertex_count": len(source_vertices & target_vertices),
        "boundary_curves_equal": source_curve == target_curve,
        "curve_complement_regions": complement_regions,
        "disk_transition_pattern": "PASS" if transition_pattern else "OPEN",
        "regular_path_neighbourhood": regular_neighbourhood,
        "outer_boundary_membership_agrees": boundary_agrees,
        "outer_boundary_requires_halfturn": not boundary_agrees,
        "protected_ball_bbox_clearance": str(clearance),
        "paired_saddle_ball_support": "PASS" if passed else "OPEN",
        "paired_saddle_support": "PASS" if passed else "OPEN",
        "boundary_halfturn_cells": "OPEN",
        "ambient_pl_cells": "OPEN",
    }


def generate():
    analyzer = load("analyze_t73_johnson_arm_mismatch")
    pl = load("t73_johnson_pl")
    sweep_tools = load("build_t73_johnson_elementary_sweep")
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
    disk_cells = json.loads(DISK_CELLS.read_text(encoding="utf-8"))
    if disk_cells["sweep_sha256"] != sweep["sha256"]:
        raise AssertionError("disk cells are not bound to the elementary sweep")
    movies = [
        build_movie(analyzer, pl, sweep_tools, movie) for movie in sweep["movies"]
    ]
    result = {
        "schema": "t73_johnson_paired_saddle_support/v1",
        "sweep_sha256": sweep["sha256"],
        "disk_cells_sha256": disk_cells["sha256"],
        "movies": movies,
        "all_supports_are_balls": all(
            movie["support_collapses_to_point"]
            and movie["support_boundary"]["topology"] == "sphere"
            for movie in movies
        ),
        "all_disk_transition_patterns_pass": all(
            movie["disk_transition_pattern"] == "PASS" for movie in movies
        ),
        "all_outer_boundaries_require_halfturns": all(
            movie["outer_boundary_requires_halfturn"] for movie in movies
        ),
        "all_regular_path_neighbourhoods_pass": all(
            movie["regular_path_neighbourhood"]["regular_neighbourhood_status"]
            == "PASS"
            for movie in movies
        ),
        "all_regular_path_caps_collapse_relatively": all(
            movie["regular_path_neighbourhood"]["both_cap_relative_collapses"]
            == "PASS"
            for movie in movies
        ),
        "paired_saddle_support": (
            "PASS"
            if all(movie["paired_saddle_support"] == "PASS" for movie in movies)
            else "OPEN"
        ),
        "paired_saddle_ambient_cells": "OPEN",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check or args.write:
        print(f"T73_JOHNSON_PAIRED_SADDLE_SUPPORT={result['paired_saddle_support']}")
        for movie in result["movies"]:
            print(
                f"POWER_{movie['power']}_{movie['side']}="
                f"{movie['support_tetrahedron_count']};"
                f"PATCHES={movie['source_patch']['surface_components']}/"
                f"{movie['source_patch']['boundary_components']}"
            )
        print(f"AMBIENT_PL_CELLS={result['paired_saddle_ambient_cells']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
