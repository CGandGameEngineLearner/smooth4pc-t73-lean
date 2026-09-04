#!/usr/bin/env python3
"""Exact polyhedral decomposition of the unit Johnson arm mismatch.

This is an input to the missing ``Restore`` construction, not a certificate
that the restore exists.  Each affine image of a Johnson Freudenthal
tetrahedron is clipped against the period-four unit cubes using rational
half-spaces.  A resulting three-dimensional polytope is a mismatch piece
exactly when the source tetrahedron and target cube have different owners.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "geometry" / "t73_johnson_arm_mismatch.json"


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


def solve3(pl, rows, rhs):
    inverse = pl.invert3([[Fraction(entry) for entry in row] for row in rows])
    return pl.matvec_frac(inverse, [Fraction(entry) for entry in rhs])


def rank3(pl, vertices) -> bool:
    if len(vertices) < 4:
        return False
    base = vertices[0]
    differences = [pl.sub(vertex, base) for vertex in vertices[1:]]
    for first, second, third in itertools.combinations(differences, 3):
        matrix = [[first[row], second[row], third[row]] for row in range(3)]
        if pl.det3(matrix) != 0:
            return True
    return False


def dot(first, second):
    return sum(first[index] * second[index] for index in range(3))


def cross(first, second):
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def polytope_facets(pl, encoded_vertices):
    vertices = [tuple(pl.decode(vertex)) for vertex in encoded_vertices]
    facets = set()
    for first, second, third in itertools.combinations(vertices, 3):
        normal = cross(pl.sub(second, first), pl.sub(third, first))
        if normal == (0, 0, 0):
            continue
        constant = dot(normal, first)
        signs = []
        for vertex in vertices:
            value = dot(normal, vertex) - constant
            signs.append((value > 0) - (value < 0))
        if 1 in signs and -1 in signs:
            continue
        facet = tuple(sorted(vertices[index] for index, sign in enumerate(signs) if sign == 0))
        if len(facet) >= 3:
            facets.add(facet)
    return facets


def canonical_periodic_face_with_shift(face):
    anchor = min(face)
    shift = tuple((anchor[index] // 4) * 4 for index in range(3))
    canonical = tuple(
        sorted(
            tuple(vertex[index] - shift[index] for index in range(3))
            for vertex in face
        )
    )
    return canonical, shift


def canonical_periodic_face(face):
    return canonical_periodic_face_with_shift(face)[0]


def periodic_vertex(vertex):
    return tuple(value % 4 for value in vertex)


def face_edges(pl, face, periodic=True):
    vertices = list(face)
    normal = None
    for first, second, third in itertools.combinations(vertices, 3):
        candidate = cross(pl.sub(second, first), pl.sub(third, first))
        if candidate != (0, 0, 0):
            normal = candidate
            break
    if normal is None:
        raise AssertionError("facet vertices are collinear")
    edges = set()
    for first, second in itertools.combinations(vertices, 2):
        direction = pl.sub(second, first)
        side_normal = cross(normal, direction)
        signs = []
        for vertex in vertices:
            value = dot(side_normal, pl.sub(vertex, first))
            signs.append((value > 0) - (value < 0))
        if 1 in signs and -1 in signs:
            continue
        has_between_vertex = False
        length_squared = dot(direction, direction)
        for vertex in vertices:
            offset = pl.sub(vertex, first)
            if cross(direction, offset) != (0, 0, 0):
                continue
            parameter_numerator = dot(offset, direction)
            if 0 < parameter_numerator < length_squared:
                has_between_vertex = True
                break
        if not has_between_vertex:
            endpoints = (
                (periodic_vertex(first), periodic_vertex(second))
                if periodic
                else (first, second)
            )
            edges.add(tuple(sorted(endpoints)))
    return edges


def triangulate_face(pl, face):
    edges = face_edges(pl, face, periodic=False)
    adjacency = defaultdict(list)
    for first, second in edges:
        adjacency[first].append(second)
        adjacency[second].append(first)
    if any(len(neighbours) != 2 for neighbours in adjacency.values()):
        raise AssertionError("convex facet edge graph is not a cycle")
    start = min(adjacency)
    cycle = [start]
    previous = None
    while True:
        choices = sorted(vertex for vertex in adjacency[cycle[-1]] if vertex != previous)
        following = choices[0]
        if following == start:
            break
        cycle.append(following)
        previous = cycle[-2]
        if len(cycle) > len(face):
            raise AssertionError("facet boundary did not close")
    if len(cycle) != len(face):
        raise AssertionError("facet cycle omits a vertex")
    return [(cycle[0], cycle[index], cycle[index + 1]) for index in range(1, len(cycle) - 1)]


def collapse_to_point(tetrahedra):
    simplices = [set() for _ in range(4)]
    for tetrahedron in tetrahedra:
        for size in range(1, 5):
            for simplex in itertools.combinations(tetrahedron, size):
                simplices[size - 1].add(frozenset(simplex))
    steps = 0
    for dimension in (3, 2, 1):
        while True:
            coface_counts = Counter()
            for simplex in simplices[dimension]:
                for face in itertools.combinations(simplex, dimension):
                    coface_counts[frozenset(face)] += 1
            candidates = []
            for simplex in simplices[dimension]:
                for face in itertools.combinations(simplex, dimension):
                    face = frozenset(face)
                    if coface_counts[face] == 1:
                        candidates.append((tuple(sorted(simplex)), tuple(sorted(face)), simplex, face))
            if not candidates:
                break
            _, _, simplex, face = min(candidates)
            simplices[dimension].remove(simplex)
            simplices[dimension - 1].remove(face)
            steps += 1
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


def triangulate_component(pl, pieces, component, piece_shifts):
    tetrahedra = []
    all_vertices = set()
    facet_occurrences = defaultdict(list)
    for piece_index in component:
        shift = piece_shifts[piece_index]
        vertices = [
            tuple(pl.decode(vertex)[axis] + shift[axis] for axis in range(3))
            for vertex in pieces[piece_index]["vertices"]
        ]
        center = tuple(
            sum(vertex[axis] for vertex in vertices) / len(vertices) for axis in range(3)
        )
        all_vertices.update(vertices)
        all_vertices.add(center)
        facets = polytope_facets(pl, [pl.encode(vertex) for vertex in vertices])
        for facet in facets:
            facet_occurrences[facet].append(center)
            for triangle in triangulate_face(pl, facet):
                tetrahedron = [triangle[0], triangle[1], triangle[2], center]
                determinant = pl.det3(
                    [
                        [tetrahedron[column][row] - tetrahedron[0][row] for column in range(1, 4)]
                        for row in range(3)
                    ]
                )
                if determinant == 0:
                    raise AssertionError("component cone tetrahedron is degenerate")
                if determinant < 0:
                    tetrahedron[1], tetrahedron[2] = tetrahedron[2], tetrahedron[1]
                tetrahedra.append(tuple(tetrahedron))
    face_counts = Counter()
    for tetrahedron in tetrahedra:
        for omitted in range(4):
            face_counts[frozenset(tetrahedron[index] for index in range(4) if index != omitted)] += 1
    if any(count not in (1, 2) for count in face_counts.values()):
        raise AssertionError("component tetrahedralization is not face-to-face")
    collapse = collapse_to_point(tetrahedra)
    lows = [min(vertex[axis] for vertex in all_vertices) for axis in range(3)]
    highs = [max(vertex[axis] for vertex in all_vertices) for axis in range(3)]
    boundary_facets = [
        (facet, centers[0])
        for facet, centers in facet_occurrences.items()
        if len(centers) == 1
    ]
    candidate_centers = [
        tuple((lows[axis] + highs[axis]) / 2 for axis in range(3)),
        tuple(
            sum(vertex[axis] for vertex in all_vertices) / len(all_vertices)
            for axis in range(3)
        ),
    ]
    candidate_centers.extend(center for centers in facet_occurrences.values() for center in centers)
    star_center = None
    for candidate in candidate_centers:
        visible = True
        for facet, interior_point in boundary_facets:
            first, second, third = facet[:3]
            normal = cross(pl.sub(second, first), pl.sub(third, first))
            interior_sign = dot(normal, pl.sub(interior_point, first))
            candidate_sign = dot(normal, pl.sub(candidate, first))
            if interior_sign == 0 or interior_sign * candidate_sign <= 0:
                visible = False
                break
        if visible:
            star_center = candidate
            break
    return {
        "tetrahedron_count": len(tetrahedra),
        "triangle_multiplicities": {
            str(multiplicity): count
            for multiplicity, count in sorted(Counter(face_counts.values()).items())
        },
        "lift_bounding_box": {
            "min": [str(value) for value in lows],
            "max": [str(value) for value in highs],
            "span": [str(highs[axis] - lows[axis]) for axis in range(3)],
        },
        "contained_in_embedded_period_box": all(highs[axis] - lows[axis] < 4 for axis in range(3)),
        "star_shaped": star_center is not None,
        "star_center": (
            [str(value) for value in star_center] if star_center is not None else None
        ),
        "boundary_facet_count": len(boundary_facets),
        **collapse,
    }


def patch_topology(pl, pieces, component, piece_shifts, matrix, owners):
    inverse = pl.invert3([[Fraction(value) for value in row] for row in matrix])
    occurrences = defaultdict(list)
    for piece_index in component:
        shift = piece_shifts[piece_index]
        vertices = [
            pl.add(pl.decode(vertex), shift) for vertex in pieces[piece_index]["vertices"]
        ]
        center = tuple(
            sum(vertex[axis] for vertex in vertices) / len(vertices) for axis in range(3)
        )
        for facet in polytope_facets(pl, [pl.encode(vertex) for vertex in vertices]):
            occurrences[facet].append((piece_index, center))
    patches = defaultdict(list)
    for facet, hits in occurrences.items():
        if len(hits) != 1:
            continue
        piece_index, interior = hits[0]
        facet_center = tuple(
            sum(vertex[axis] for vertex in facet) / len(facet) for axis in range(3)
        )
        outside = tuple(
            facet_center[axis] + Fraction(1, 100) * (facet_center[axis] - interior[axis])
            for axis in range(3)
        )
        piece = pieces[piece_index]
        outside_source = pl.point_owner(pl.matvec_frac(inverse, outside), owners)
        outside_target = pl.point_owner(outside, owners)
        source_changes = outside_source != piece["source_owner"]
        target_changes = outside_target != piece["target_owner"]
        if source_changes == target_changes:
            raise AssertionError("mismatch boundary facet is not on exactly one Heegaard surface")
        patches["source" if source_changes else "target"].append(facet)
    result = {}
    for name in ("source", "target"):
        facets = patches[name]
        edge_counts = Counter(edge for facet in facets for edge in face_edges(pl, facet))
        vertices = {periodic_vertex(vertex) for facet in facets for vertex in facet}
        face_edges_map = [face_edges(pl, facet) for facet in facets]
        edge_faces = defaultdict(list)
        for face_index, edges in enumerate(face_edges_map):
            for edge in edges:
                edge_faces[edge].append(face_index)
        adjacency = [set() for _ in facets]
        for hits in edge_faces.values():
            if len(hits) == 2:
                first, second = hits
                adjacency[first].add(second)
                adjacency[second].add(first)
        seen = set()
        surface_components = 0
        for start in range(len(facets)):
            if start in seen:
                continue
            surface_components += 1
            stack = [start]
            seen.add(start)
            while stack:
                current = stack.pop()
                for neighbour in adjacency[current]:
                    if neighbour not in seen:
                        seen.add(neighbour)
                        stack.append(neighbour)
        boundary_edges = [edge for edge, count in edge_counts.items() if count == 1]
        boundary_adjacency = defaultdict(set)
        for first, second in boundary_edges:
            boundary_adjacency[first].add(second)
            boundary_adjacency[second].add(first)
        if any(len(neighbours) != 2 for neighbours in boundary_adjacency.values()):
            raise AssertionError("patch boundary is not a union of circles")
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
        euler = len(vertices) - len(edge_counts) + len(facets)
        topology = (
            "disk"
            if surface_components == 1 and boundary_components == 1 and euler == 1
            else "annulus"
            if surface_components == 1 and boundary_components == 2 and euler == 0
            else "two_disks"
            if surface_components == 2 and boundary_components == 2 and euler == 2
            else "UNCLASSIFIED"
        )
        if topology == "UNCLASSIFIED":
            raise AssertionError("unexpected Johnson mismatch boundary patch")
        result[name] = {
            "facet_count": len(facets),
            "vertices": len(vertices),
            "edges": len(edge_counts),
            "euler": euler,
            "surface_components": surface_components,
            "boundary_components": boundary_components,
            "boundary_edge_count": len(boundary_edges),
            "topology": topology,
        }
    return result


def component_summary(pl, pieces, matrix, owners):
    occurrences = defaultdict(list)
    facet_shifts = {}
    for index, piece in enumerate(pieces):
        for facet in polytope_facets(pl, piece["vertices"]):
            canonical, shift = canonical_periodic_face_with_shift(facet)
            occurrences[canonical].append(index)
            facet_shifts[(index, canonical)] = shift
    if any(len(hits) not in (1, 2) for hits in occurrences.values()):
        raise AssertionError("mismatch clipping is not a face-to-face complex")
    adjacency = [set() for _ in pieces]
    adjacency_with_shift = [[] for _ in pieces]
    for hits in occurrences.values():
        if len(hits) == 2:
            first, second = hits
            adjacency[first].add(second)
            adjacency[second].add(first)
    for face, hits in occurrences.items():
        if len(hits) == 2:
            first, second = hits
            first_shift = facet_shifts[(first, face)]
            second_shift = facet_shifts[(second, face)]
            delta = tuple(first_shift[axis] - second_shift[axis] for axis in range(3))
            adjacency_with_shift[first].append((second, delta))
            adjacency_with_shift[second].append((first, tuple(-value for value in delta)))
    seen = set()
    components = []
    for start in range(len(pieces)):
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
        components.append(sorted(component))
    records = []
    for component in components:
        component_set = set(component)
        owner_set = {pieces[index]["source_owner"] for index in component}
        if len(owner_set) != 1:
            raise AssertionError("a mismatch component mixes owner directions")
        boundary_faces = [
            face
            for face, hits in occurrences.items()
            if len(hits) == 1 and hits[0] in component_set
        ]
        edge_counts = Counter(
            edge for face in boundary_faces for edge in face_edges(pl, face)
        )
        if set(edge_counts.values()) != {2}:
            raise AssertionError("mismatch boundary is not a closed surface")
        boundary_vertices = {
            periodic_vertex(vertex) for face in boundary_faces for vertex in face
        }
        face_adjacency = [set() for _ in boundary_faces]
        edge_faces = defaultdict(list)
        for face_index, face in enumerate(boundary_faces):
            for edge in face_edges(pl, face):
                edge_faces[edge].append(face_index)
        for hits in edge_faces.values():
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
        connected = len(reached) == len(boundary_faces)
        euler = len(boundary_vertices) - len(edge_counts) + len(boundary_faces)
        piece_shifts = {component[0]: (Fraction(0), Fraction(0), Fraction(0))}
        stack = [component[0]]
        while stack:
            current = stack.pop()
            for neighbour, delta in adjacency_with_shift[current]:
                if neighbour not in component_set:
                    continue
                expected = tuple(
                    piece_shifts[current][axis] + delta[axis] for axis in range(3)
                )
                if neighbour in piece_shifts:
                    if piece_shifts[neighbour] != expected:
                        raise AssertionError("component lift has inconsistent periods")
                else:
                    piece_shifts[neighbour] = expected
                    stack.append(neighbour)
        triangulation = triangulate_component(pl, pieces, component, piece_shifts)
        patches = patch_topology(
            pl, pieces, component, piece_shifts, matrix, owners
        )
        records.append(
            {
                "source_owner": next(iter(owner_set)),
                "piece_count": len(component),
                "piece_indices": component,
                "boundary_vertices": len(boundary_vertices),
                "boundary_edges": len(edge_counts),
                "boundary_faces": len(boundary_faces),
                "boundary_euler": euler,
                "boundary_connected": connected,
                "boundary_edge_multiplicity_two": True,
                "boundary_is_sphere": connected and euler == 2,
                "triangulation": triangulation,
                "boundary_patches": patches,
                "piece_lift_shifts": {
                    str(piece_index): [str(value) for value in piece_shifts[piece_index]]
                    for piece_index in component
                },
                "support_ball_status": (
                    "PASS"
                    if connected
                    and euler == 2
                    and triangulation["contained_in_embedded_period_box"]
                    and triangulation["collapses_to_point"]
                    else "OPEN"
                ),
            }
        )
    records.sort(key=lambda item: (item["source_owner"], -item["piece_count"]))
    for index, record in enumerate(records):
        record["component_id"] = index
    return records


def periodic_polytope_set(pl, pieces, component, prefix, translation=0):
    result = set()
    for piece_index in component["piece_indices"]:
        vertices = []
        for encoded in pieces[piece_index]["vertices"]:
            vertex = pl.decode(encoded)
            vertex[prefix] += translation
            vertices.append(tuple(value % pl.PERIOD for value in vertex))
        result.add(tuple(sorted(vertices)))
    return result


def pair_components(pl, pieces, components, prefix):
    excess = [component for component in components if component["source_owner"] == 0]
    deficiency = [component for component in components if component["source_owner"] == 1]
    pairs = []
    used = set()
    for source_component in excess:
        translated = periodic_polytope_set(
            pl, pieces, source_component, prefix, Fraction(2)
        )
        matches = [
            target_component
            for target_component in deficiency
            if periodic_polytope_set(pl, pieces, target_component, prefix) == translated
        ]
        if len(matches) != 1:
            raise AssertionError("half-period translation does not give a unique ball pair")
        target_component = matches[0]
        if target_component["component_id"] in used:
            raise AssertionError("a deficiency ball is paired twice")
        used.add(target_component["component_id"])
        pairs.append(
            {
                "pair_id": len(pairs),
                "excess_component_id": source_component["component_id"],
                "deficiency_component_id": target_component["component_id"],
                "piece_count": source_component["piece_count"],
                "translation": [
                    "2" if axis == prefix else "0" for axis in range(3)
                ],
                "polyhedral_decompositions_match_exactly": True,
                "transport_support_status": "OPEN",
            }
        )
    if len(pairs) != 3 or len(used) != 3:
        raise AssertionError("mismatch balls do not form three bijective pairs")
    return pairs


def component_intersections(pl, pieces, components, ball_pairs):
    vertex_sets = {}
    for component in components:
        vertex_sets[component["component_id"]] = {
            tuple(value % pl.PERIOD for value in pl.decode(vertex))
            for piece_index in component["piece_indices"]
            for vertex in pieces[piece_index]["vertices"]
        }
    records = []
    graph_edges = set()
    for first, second in itertools.combinations(components, 2):
        common = sorted(
            vertex_sets[first["component_id"]] & vertex_sets[second["component_id"]]
        )
        if not common:
            continue
        dimension = 0
        differences = [pl.sub(vertex, common[0]) for vertex in common[1:]]
        if any(vector != [0, 0, 0] for vector in differences):
            dimension = 1
        if any(cross(a, b) != (0, 0, 0) for a, b in itertools.combinations(differences, 2)):
            dimension = 2
        graph_edges.add(tuple(sorted((first["component_id"], second["component_id"]))))
        records.append(
            {
                "components": [first["component_id"], second["component_id"]],
                "common_vertex_count": len(common),
                "affine_dimension": dimension,
                "common_vertices": [pl.encode(vertex) for vertex in common],
            }
        )
    involution = {}
    for pair in ball_pairs:
        first = pair["excess_component_id"]
        second = pair["deficiency_component_id"]
        involution[first] = second
        involution[second] = first
    transported_edges = {
        tuple(sorted((involution[first], involution[second]))) for first, second in graph_edges
    }
    if transported_edges != graph_edges:
        raise AssertionError("half-period ball pairing does not preserve the intersection graph")
    return {
        "records": records,
        "edge_count": len(graph_edges),
        "edges": [list(edge) for edge in sorted(graph_edges)],
        "closures_pairwise_disjoint": not records,
        "half_period_involution": {str(key): value for key, value in sorted(involution.items())},
        "half_period_involution_preserves_graph": True,
        "independent_shrink_composition_status": (
            "OPEN: component closures meet, so the individual radial charts do not compose "
            "without a common-intersection movie"
        ),
    }


def tetrahedron_halfspaces(pl, vertices):
    base = vertices[0]
    columns = [[vertices[j][i] - base[i] for j in range(1, 4)] for i in range(3)]
    inverse = pl.invert3(columns)
    inequalities = []
    for row in inverse:
        inequalities.append(([-entry for entry in row], -sum(row[i] * base[i] for i in range(3))))
    total = [sum(inverse[row][column] for row in range(3)) for column in range(3)]
    inequalities.append((total, Fraction(1) + sum(total[i] * base[i] for i in range(3))))
    return inequalities


def cube_halfspaces(origin):
    inequalities = []
    for axis in range(3):
        upper = [Fraction(0), Fraction(0), Fraction(0)]
        upper[axis] = 1
        inequalities.append((upper, Fraction(origin[axis] + 1)))
        lower = [Fraction(0), Fraction(0), Fraction(0)]
        lower[axis] = -1
        inequalities.append((lower, Fraction(-origin[axis])))
    return inequalities


def intersection_vertices(pl, tetrahedron, cube_origin):
    inequalities = tetrahedron_halfspaces(pl, tetrahedron) + cube_halfspaces(cube_origin)
    vertices = set()
    for selected in itertools.combinations(inequalities, 3):
        rows = [item[0] for item in selected]
        if pl.det3(rows) == 0:
            continue
        point = solve3(pl, rows, [item[1] for item in selected])
        if all(sum(row[i] * point[i] for i in range(3)) <= bound for row, bound in inequalities):
            vertices.add(tuple(point))
    return sorted(vertices)


def source_tetrahedra():
    pl = load("t73_johnson_pl")
    owners = pl.johnson_owners()
    axes = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    owner_indices = [0, 0]
    result = []
    for origin in itertools.product(range(pl.PERIOD), repeat=3):
        owner = owners[origin]
        for permutation in itertools.permutations(range(3)):
            tetrahedron = [origin]
            current = origin
            for axis in permutation:
                current = tuple(current[i] + axes[axis][i] for i in range(3))
                tetrahedron.append(current)
            index = owner_indices[owner]
            owner_indices[owner] += 1
            result.append((owner, index, tetrahedron))
    if owner_indices != [192, 192]:
        raise AssertionError("unwrapped Johnson lift is not 192+192 tetrahedra")
    return result


def analyze_template(pl, source: int, prefix: int, power: int) -> dict[str, Any]:
    matrix = pl.transvection_matrix(source, prefix, power)
    owners = pl.johnson_owners()
    pieces = []
    source_counts = [0, 0]
    for owner, index, encoded_tetrahedron in source_tetrahedra():
        tetrahedron = [pl.matvec(matrix, vertex) for vertex in encoded_tetrahedron]
        lows = [math.floor(min(vertex[axis] for vertex in tetrahedron)) for axis in range(3)]
        highs = [math.ceil(max(vertex[axis] for vertex in tetrahedron)) for axis in range(3)]
        for cube_origin in itertools.product(
            *(range(lows[axis], highs[axis]) for axis in range(3))
        ):
            vertices = intersection_vertices(pl, tetrahedron, cube_origin)
            if not rank3(pl, vertices):
                continue
            target_owner = owners[tuple(value % pl.PERIOD for value in cube_origin)]
            if target_owner == owner:
                continue
            source_counts[owner] += 1
            pieces.append(
                {
                    "source_owner": owner,
                    "target_owner": target_owner,
                    "source_tetrahedron": index,
                    "target_cube_origin": list(cube_origin),
                    "vertices": [pl.encode(vertex) for vertex in vertices],
                }
            )
    origin_star_hits = [
        piece
        for piece in pieces
        if all(value % pl.PERIOD in (0, 3) for value in piece["target_cube_origin"])
    ]
    if origin_star_hits:
        raise AssertionError("an exact mismatch polytope meets the origin eight-cube star")
    components = component_summary(pl, pieces, matrix, owners)
    ball_pairs = pair_components(pl, pieces, components, prefix)
    intersections = component_intersections(pl, pieces, components, ball_pairs)
    patch_patterns = Counter(
        (
            component["boundary_patches"]["source"]["topology"],
            component["boundary_patches"]["target"]["topology"],
        )
        for component in components
    )
    expected_patterns = Counter(
        {("disk", "disk"): 4, ("annulus", "two_disks"): 1, ("two_disks", "annulus"): 1}
    )
    if patch_patterns != expected_patterns:
        raise AssertionError(f"unexpected Johnson saddle pattern: {patch_patterns}")
    payload = {
        "source_axis": source,
        "prefix_axis": prefix,
        "power": power,
        "matrix": matrix,
        "piece_count": len(pieces),
        "piece_count_by_source_owner": source_counts,
        "origin_star_piece_count": 0,
        "mismatch_disjoint_from_origin_star": True,
        "pieces": pieces,
        "components": components,
        "all_components_are_collapsible_balls": all(
            component["support_ball_status"] == "PASS" for component in components
        ),
        "ball_pairs": ball_pairs,
        "half_period_ball_pairing": "PASS",
        "component_intersections": intersections,
        "boundary_patch_pattern": {
            "disk_to_disk": 4,
            "annulus_to_two_disks": 1,
            "two_disks_to_annulus": 1,
            "johnson_saddle_pattern": "PASS",
        },
        "restore_status": "OPEN",
    }
    payload["sha256"] = canonical_sha(payload)
    return payload


def generate() -> dict[str, Any]:
    pl = load("t73_johnson_pl")
    templates = [
        analyze_template(pl, source, prefix, power)
        for source, prefix in itertools.permutations(range(3), 2)
        for power in (-1, 1)
    ]
    result = {
        "schema": "t73_johnson_arm_mismatch/v1",
        "period": pl.PERIOD,
        "source": (
            "exact rational clipping of the unwrapped period-four affine-image "
            "tetrahedra against target unit cubes"
        ),
        "template_count": len(templates),
        "templates": templates,
        "all_mismatch_pieces_disjoint_from_origin_star": all(
            template["mismatch_disjoint_from_origin_star"] for template in templates
        ),
        "all_mismatch_components_are_collapsible_balls": all(
            template["all_components_are_collapsible_balls"] for template in templates
        ),
        "all_half_period_ball_pairings": all(
            template["half_period_ball_pairing"] == "PASS" for template in templates
        ),
        "johnson_restore_status": "OPEN: mismatch polytopes are decomposed but no fixed-boundary arm homeomorphism has yet been attached",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check or args.write:
        print("T73_JOHNSON_ARM_MISMATCH=DECOMPOSED")
        print(f"TEMPLATES={result['template_count']}")
        print(
            "DISJOINT_FROM_ORIGIN_STAR="
            f"{result['all_mismatch_pieces_disjoint_from_origin_star']}"
        )
        print(
            "COMPONENTS_ARE_BALLS="
            f"{result['all_mismatch_components_are_collapsible_balls']}"
        )
        print(f"HALF_PERIOD_BALL_PAIRS={result['all_half_period_ball_pairings']}")
        print(f"RESTORE_STATUS={result['johnson_restore_status']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
