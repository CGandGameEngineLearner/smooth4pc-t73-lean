#!/usr/bin/env python3
"""Build elementary tetrahedron sweeps for the Johnson restore overlay."""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "geometry" / "t73_johnson_elementary_sweep.json"


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


def canonical_face(face):
    face = tuple(sorted(tuple(vertex) for vertex in face))
    anchor = min(face)
    shift = tuple((anchor[axis] // 4) * 4 for axis in range(3))
    return tuple(
        sorted(
            tuple(vertex[axis] - shift[axis] for axis in range(3))
            for vertex in face
        )
    )


def periodic_vertex(vertex):
    return tuple(value % 4 for value in vertex)


def build_tetrahedra(analyzer, pl, power):
    matrix = pl.transvection_matrix(0, 1, power)
    owners = pl.johnson_owners()
    tetrahedra = []
    for source_owner, _, source_tetrahedron in analyzer.source_tetrahedra():
        image_tetrahedron = [pl.matvec(matrix, vertex) for vertex in source_tetrahedron]
        lows = [math.floor(min(vertex[axis] for vertex in image_tetrahedron)) for axis in range(3)]
        highs = [math.ceil(max(vertex[axis] for vertex in image_tetrahedron)) for axis in range(3)]
        for cube in itertools.product(*(range(lows[axis], highs[axis]) for axis in range(3))):
            vertices = analyzer.intersection_vertices(pl, image_tetrahedron, cube)
            if not analyzer.rank3(pl, vertices):
                continue
            target_owner = owners[tuple(value % 4 for value in cube)]
            center = tuple(
                sum(vertex[axis] for vertex in vertices) / len(vertices) for axis in range(3)
            )
            for facet in analyzer.polytope_facets(pl, [pl.encode(vertex) for vertex in vertices]):
                for triangle in analyzer.triangulate_face(pl, facet):
                    tetrahedra.append(
                        {
                            "vertices": (triangle[0], triangle[1], triangle[2], center),
                            "source_owner": source_owner,
                            "target_owner": target_owner,
                        }
                    )
    face_occurrences = collections.defaultdict(list)
    for index, tetrahedron in enumerate(tetrahedra):
        for omitted in range(4):
            face = canonical_face(
                tetrahedron["vertices"][vertex]
                for vertex in range(4)
                if vertex != omitted
            )
            face_occurrences[face].append((index, omitted))
    if set(map(len, face_occurrences.values())) != {2}:
        raise AssertionError("restore overlay is not a closed tetrahedral torus")
    adjacency = [[None, None, None, None] for _ in tetrahedra]
    for hits in face_occurrences.values():
        (first, first_face), (second, second_face) = hits
        adjacency[first][first_face] = second
        adjacency[second][second_face] = first
    if any(any(neighbour is None for neighbour in neighbours) for neighbours in adjacency):
        raise AssertionError("an overlay tetrahedron does not have four neighbours")
    return tetrahedra, adjacency, face_occurrences


def barycenter(tetrahedron):
    return tuple(
        sum(tetrahedron["vertices"][index][axis] for index in range(4)) / 4
        for axis in range(3)
    )


def patch_invariants(faces):
    vertices = {periodic_vertex(vertex) for face in faces for vertex in face}
    edge_counts = collections.Counter(
        tuple(sorted((periodic_vertex(face[first]), periodic_vertex(face[second]))))
        for face in faces
        for first, second in ((0, 1), (0, 2), (1, 2))
    )
    face_adjacency = [set() for _ in faces]
    edge_faces = collections.defaultdict(list)
    for face_index, face in enumerate(faces):
        for first, second in ((0, 1), (0, 2), (1, 2)):
            edge = tuple(sorted((periodic_vertex(face[first]), periodic_vertex(face[second]))))
            edge_faces[edge].append(face_index)
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
    for first, second in boundary_edges:
        boundary_adjacency[first].add(second)
        boundary_adjacency[second].add(first)
    if any(len(neighbours) != 2 for neighbours in boundary_adjacency.values()):
        boundary_components = None
    else:
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
    edge_multiplicity_histogram = dict(sorted(collections.Counter(edge_counts.values()).items()))
    surface_manifold = all(count in (1, 2) for count in edge_counts.values())
    topology = (
        "disk"
        if surface_manifold and components == 1 and boundary_components == 1 and euler == 1
        else "annulus"
        if surface_manifold and components == 1 and boundary_components == 2 and euler == 0
        else "two_disks"
        if surface_manifold and components == 2 and boundary_components == 2 and euler == 2
        else "sphere"
        if surface_manifold and components == 1 and boundary_components == 0 and euler == 2
        else "UNCLASSIFIED"
    )
    return {
        "vertices": len(vertices),
        "edges": len(edge_counts),
        "faces": len(faces),
        "euler": euler,
        "surface_components": components,
        "boundary_components": boundary_components,
        "edge_multiplicity_histogram": {
            str(key): value for key, value in edge_multiplicity_histogram.items()
        },
        "surface_manifold": surface_manifold,
        "topology": topology,
        "is_disk": topology == "disk",
    }


def residual_components(remaining, adjacency):
    seen = set()
    components = []
    for start in sorted(remaining):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        component = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbour in adjacency[current]:
                if neighbour in remaining and neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        components.append(sorted(component))
    return components


def grouped_move(analyzer, tetrahedra, adjacency, current, goal, component):
    operations = {goal[index] for index in component}
    if len(operations) != 1:
        raise AssertionError("residual face-component mixes add and remove moves")
    adding = next(iter(operations))
    component_set = set(component)
    boundary_faces = []
    attaching_faces = []
    abstract_tetrahedra = []
    for index in component:
        tetrahedron = tetrahedra[index]
        abstract_tetrahedra.append(
            tuple(periodic_vertex(vertex) for vertex in tetrahedron["vertices"])
        )
        for omitted, neighbour in enumerate(adjacency[index]):
            if neighbour in component_set:
                continue
            face = tuple(
                tetrahedron["vertices"][vertex]
                for vertex in range(4)
                if vertex != omitted
            )
            boundary_faces.append(face)
            if current[neighbour] == adding:
                attaching_faces.append(face)
    boundary = patch_invariants(boundary_faces)
    attaching = patch_invariants(attaching_faces)
    collapse = analyzer.collapse_to_point(abstract_tetrahedra)
    return {
        "operation": "add" if adding else "remove",
        "tetrahedra": component,
        "tetrahedron_count": len(component),
        "support_boundary": boundary,
        "attachment_patch": attaching,
        "support_collapses_to_point": collapse["collapses_to_point"],
        "valid_ball_push": (
            boundary["surface_components"] == 1
            and boundary["boundary_components"] == 0
            and boundary["euler"] == 2
            and collapse["collapses_to_point"]
            and attaching["is_disk"]
        ),
    }


def state_invariants(current, adjacency, face_occurrences):
    boundary_faces = []
    for face, hits in face_occurrences.items():
        (first, _), (second, _) = hits
        if current[first] != current[second]:
            boundary_faces.append(face)
    edge_counts = collections.Counter(
        tuple(sorted((periodic_vertex(face[first]), periodic_vertex(face[second]))))
        for face in boundary_faces
        for first, second in ((0, 1), (0, 2), (1, 2))
    )
    if set(edge_counts.values()) != {2}:
        return None
    vertices = {periodic_vertex(vertex) for face in boundary_faces for vertex in face}
    euler = len(vertices) - len(edge_counts) + len(boundary_faces)
    if euler != -4:
        return None
    face_adjacency = [set() for _ in boundary_faces]
    edge_faces = collections.defaultdict(list)
    for index, face in enumerate(boundary_faces):
        for first, second in ((0, 1), (0, 2), (1, 2)):
            edge = tuple(sorted((periodic_vertex(face[first]), periodic_vertex(face[second]))))
            edge_faces[edge].append(index)
    for hits in edge_faces.values():
        if len(hits) != 2:
            return None
        first, second = hits
        face_adjacency[first].add(second)
        face_adjacency[second].add(first)
    reached = {0}
    stack = [0]
    while stack:
        current_face = stack.pop()
        for neighbour in face_adjacency[current_face]:
            if neighbour not in reached:
                reached.add(neighbour)
                stack.append(neighbour)
    if len(reached) != len(boundary_faces):
        return None
    side_components = []
    for side in (False, True):
        available = {index for index, value in enumerate(current) if value == side}
        components = 0
        while available:
            components += 1
            start = next(iter(available))
            available.remove(start)
            stack = [start]
            while stack:
                index = stack.pop()
                for neighbour in adjacency[index]:
                    if neighbour in available:
                        available.remove(neighbour)
                        stack.append(neighbour)
        side_components.append(components)
    if side_components != [1, 1]:
        return None
    return {
        "boundary_vertices": len(vertices),
        "boundary_edges": len(edge_counts),
        "boundary_faces": len(boundary_faces),
        "boundary_euler": euler,
        "boundary_connected": True,
        "side_face_components": side_components,
    }


def boundary_state(current, face_occurrences):
    faces = set()
    slot_face = {}
    for face, hits in face_occurrences.items():
        (first, first_slot), (second, second_slot) = hits
        slot_face[(first, first_slot)] = face
        slot_face[(second, second_slot)] = face
        if current[first] != current[second]:
            faces.add(face)
    edge_counts = collections.Counter()
    vertex_counts = collections.Counter()
    for face in faces:
        for vertex in face:
            vertex_counts[periodic_vertex(vertex)] += 1
        for first, second in ((0, 1), (0, 2), (1, 2)):
            edge = tuple(sorted((periodic_vertex(face[first]), periodic_vertex(face[second]))))
            edge_counts[edge] += 1
    return faces, edge_counts, vertex_counts, slot_face


def toggle_boundary(index, faces, edge_counts, vertex_counts, slot_face):
    changes = []
    affected_edges = set()
    for slot in range(4):
        face = slot_face[(index, slot)]
        adding = face not in faces
        changes.append((face, adding))
        coefficient = 1 if adding else -1
        if adding:
            faces.add(face)
        else:
            faces.remove(face)
        for vertex in face:
            key = periodic_vertex(vertex)
            vertex_counts[key] += coefficient
            if vertex_counts[key] == 0:
                del vertex_counts[key]
        for first, second in ((0, 1), (0, 2), (1, 2)):
            edge = tuple(sorted((periodic_vertex(face[first]), periodic_vertex(face[second]))))
            edge_counts[edge] += coefficient
            affected_edges.add(edge)
            if edge_counts[edge] == 0:
                del edge_counts[edge]
    valid = (
        all(edge_counts.get(edge) == 2 for edge in affected_edges if edge in edge_counts)
        and len(vertex_counts) - len(edge_counts) + len(faces) == -4
    )
    return valid, changes


def undo_boundary(changes, faces, edge_counts, vertex_counts):
    for face, was_adding in reversed(changes):
        coefficient = -1 if was_adding else 1
        if was_adding:
            faces.remove(face)
        else:
            faces.add(face)
        for vertex in face:
            key = periodic_vertex(vertex)
            vertex_counts[key] += coefficient
            if vertex_counts[key] == 0:
                del vertex_counts[key]
        for first, second in ((0, 1), (0, 2), (1, 2)):
            edge = tuple(sorted((periodic_vertex(face[first]), periodic_vertex(face[second]))))
            edge_counts[edge] += coefficient
            if edge_counts[edge] == 0:
                del edge_counts[edge]


def sweep(analyzer, pl, power, side):
    tetrahedra, adjacency, face_occurrences = build_tetrahedra(analyzer, pl, power)
    current = [tetrahedron["source_owner"] == 0 for tetrahedron in tetrahedra]
    goal = [tetrahedron["target_owner"] == 0 for tetrahedron in tetrahedra]
    remaining = {index for index in range(len(tetrahedra)) if current[index] != goal[index]}
    single_moves = []
    attachment_histogram = collections.Counter()
    rejected_nonmanifold_candidates = 0
    initial_invariants = state_invariants(current, adjacency, face_occurrences)
    if initial_invariants is None:
        raise AssertionError("source handlebody is not a genus-three manifold pair")
    faces, edge_counts, vertex_counts, slot_face = boundary_state(current, face_occurrences)
    while remaining:
        candidates = []
        for index in remaining:
            attachment_faces = sum(
                current[neighbour] if goal[index] else not current[neighbour]
                for neighbour in adjacency[index]
            )
            if 1 <= attachment_faces <= 3:
                newly_blocked = 0
                newly_unblocked = 0
                for neighbour in adjacency[index]:
                    if neighbour not in remaining or neighbour == index:
                        continue
                    before = sum(
                        current[other] if goal[neighbour] else not current[other]
                        for other in adjacency[neighbour]
                    )
                    delta = 1 if goal[index] == goal[neighbour] else -1
                    after = before + delta
                    newly_blocked += before in (1, 2, 3) and after in (0, 4)
                    newly_unblocked += before in (0, 4) and after in (1, 2, 3)
                point = barycenter(tetrahedra[index])
                side_key = (
                    (point[1], point[0], point[2])
                    if side == "prefix-first"
                    else (point[0], point[1], point[2])
                )
                key = (newly_blocked, -newly_unblocked, side_key)
                candidates.append((key, index, attachment_faces))
        if not candidates:
            break
        chosen = None
        for _, index, attachment_faces in sorted(candidates):
            current[index] = goal[index]
            valid, changes = toggle_boundary(
                index, faces, edge_counts, vertex_counts, slot_face
            )
            if valid:
                chosen = (index, attachment_faces)
                break
            undo_boundary(changes, faces, edge_counts, vertex_counts)
            current[index] = not goal[index]
            rejected_nonmanifold_candidates += 1
        if chosen is None:
            break
        index, attachment_faces = chosen
        remaining.remove(index)
        attachment_histogram[str(attachment_faces)] += 1
        single_moves.append(index)
    grouped_moves = []
    for component in residual_components(remaining, adjacency):
        move = grouped_move(analyzer, tetrahedra, adjacency, current, goal, component)
        grouped_moves.append(move)
        if move["valid_ball_push"]:
            for index in component:
                current[index] = goal[index]
                remaining.remove(index)
    add_moves = [move for move in grouped_moves if move["operation"] == "add"]
    remove_moves = [move for move in grouped_moves if move["operation"] == "remove"]
    paired_saddle = {
        "add_group_count": len(add_moves),
        "remove_group_count": len(remove_moves),
        "status": "OPEN",
    }
    if len(grouped_moves) == 2 and len(add_moves) == 1 and len(remove_moves) == 1:
        add_move = add_moves[0]
        remove_move = remove_moves[0]
        topology_match = (
            add_move["support_boundary"]["topology"] == "sphere"
            and add_move["support_collapses_to_point"]
            and add_move["attachment_patch"]["topology"] == "two_disks"
            and remove_move["support_boundary"]["topology"] == "sphere"
            and remove_move["support_collapses_to_point"]
            and remove_move["attachment_patch"]["topology"] == "annulus"
        )
        trial = list(current)
        for move in grouped_moves:
            for index in move["tetrahedra"]:
                trial[index] = goal[index]
        final_invariants = state_invariants(trial, adjacency, face_occurrences)
        reaches_target = trial == goal
        valid = topology_match and final_invariants is not None and reaches_target
        paired_saddle = {
            "add_group_count": 1,
            "remove_group_count": 1,
            "add_tetrahedron_count": add_move["tetrahedron_count"],
            "remove_tetrahedron_count": remove_move["tetrahedron_count"],
            "add_attachment": add_move["attachment_patch"]["topology"],
            "remove_attachment": remove_move["attachment_patch"]["topology"],
            "supports_are_collapsible_balls": (
                add_move["support_collapses_to_point"]
                and remove_move["support_collapses_to_point"]
            ),
            "final_manifold_invariants": final_invariants,
            "reaches_target_after_simultaneous_toggle": reaches_target,
            "status": "PASS" if valid else "OPEN",
        }
        if valid:
            current = trial
            remaining.clear()
    return {
        "power": power,
        "side": side,
        "overlay_tetrahedron_count": len(tetrahedra),
        "initial_mismatch_tetrahedra": sum(
            tetrahedron["source_owner"] != tetrahedron["target_owner"]
            for tetrahedron in tetrahedra
        ),
        "single_move_count": len(single_moves),
        "single_move_tetrahedra": single_moves,
        "single_attachment_face_histogram": dict(sorted(attachment_histogram.items())),
        "rejected_nonmanifold_candidates": rejected_nonmanifold_candidates,
        "initial_manifold_invariants": initial_invariants,
        "final_manifold_invariants": state_invariants(current, adjacency, face_occurrences),
        "grouped_moves": grouped_moves,
        "grouped_move_count": len(grouped_moves),
        "all_grouped_moves_are_ball_pushes": all(
            move["valid_ball_push"] for move in grouped_moves
        ),
        "paired_saddle": paired_saddle,
        "remaining_after_grouped_moves": len(remaining),
        "reaches_target_handlebody": current == goal,
    }


def generate():
    analyzer = load("analyze_t73_johnson_arm_mismatch")
    pl = load("t73_johnson_pl")
    movies = [
        sweep(analyzer, pl, power, side)
        for power in (-1, 1)
        for side in ("prefix-first", "target-first")
    ]
    result = {
        "schema": "t73_johnson_elementary_sweep/v1",
        "canonical_axis_pair": [0, 1],
        "axis_permutation_symmetry": True,
        "movies": movies,
        "all_movies_reach_target": all(movie["reaches_target_handlebody"] for movie in movies),
        "ambient_pl_cell_status": "OPEN",
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
        print(f"T73_JOHNSON_ELEMENTARY_SWEEP={'PASS' if result['all_movies_reach_target'] else 'OPEN'}")
        for movie in result["movies"]:
            print(
                f"POWER_{movie['power']}_{movie['side']}="
                f"{movie['single_move_count']}+{movie['grouped_move_count']};"
                f"REMAINING={movie['remaining_after_grouped_moves']}"
            )
        print(f"AMBIENT_PL_CELLS={result['ambient_pl_cell_status']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
