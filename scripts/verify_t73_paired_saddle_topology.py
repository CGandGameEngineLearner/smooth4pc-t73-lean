#!/usr/bin/env python3
"""Verify the PL-topological hypotheses for the four paired saddle supports.

This does not construct the legacy claimed affine-cell map.  It verifies a
smaller paper-level route: every support is a PL 3-ball, both dividing patches
are properly embedded PL disks, and the recorded boundary triangle moves give
an isotopy between their boundary curves.  Standard PL disk uniqueness and
isotopy extension then supply an ambient map after adding a thin collar.
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import itertools
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SWEEP = ROOT / "geometry" / "t73_johnson_elementary_sweep.json"
SUPPORT = ROOT / "geometry" / "t73_johnson_paired_saddle_support.json"
OUTER = ROOT / "geometry" / "t73_johnson_outer_curve_collar.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pvertex(vertex):
    return tuple(Fraction(value) % 4 for value in vertex)


def edges(face):
    return {frozenset(edge) for edge in itertools.combinations(face, 2)}


def connected_graph(adjacency):
    if not adjacency:
        return False
    start = next(iter(adjacency))
    seen, stack = {start}, [start]
    while stack:
        current = stack.pop()
        for neighbour in adjacency[current]:
            if neighbour not in seen:
                seen.add(neighbour)
                stack.append(neighbour)
    return len(seen) == len(adjacency)


def surface_invariants(triangles):
    triangles = [frozenset(face) for face in triangles]
    if not triangles or any(len(face) != 3 for face in triangles):
        raise AssertionError("surface has a missing or degenerate triangle")
    vertices = set().union(*triangles)
    edge_counts = collections.Counter(edge for face in triangles for edge in edges(face))
    if any(count not in (1, 2) for count in edge_counts.values()):
        raise AssertionError("surface edge multiplicity is not one or two")
    triangle_adjacency = {index: set() for index in range(len(triangles))}
    edge_hosts = collections.defaultdict(list)
    for index, face in enumerate(triangles):
        for edge in edges(face):
            edge_hosts[edge].append(index)
    for hosts in edge_hosts.values():
        if len(hosts) == 2:
            first, second = hosts
            triangle_adjacency[first].add(second)
            triangle_adjacency[second].add(first)
    if not connected_graph(triangle_adjacency):
        raise AssertionError("surface is disconnected")

    # Check every vertex link, not just Euler characteristic.
    for vertex in vertices:
        link_edges = [tuple(face - {vertex}) for face in triangles if vertex in face]
        adjacency = collections.defaultdict(set)
        for first, second in link_edges:
            adjacency[first].add(second)
            adjacency[second].add(first)
        degrees = [len(neighbours) for neighbours in adjacency.values()]
        path = degrees.count(1) == 2 and all(degree in (1, 2) for degree in degrees)
        cycle = degrees and all(degree == 2 for degree in degrees)
        if not connected_graph(adjacency) or not (path or cycle):
            raise AssertionError("surface has a nonmanifold vertex link")

    boundary_edges = {edge for edge, count in edge_counts.items() if count == 1}
    boundary_adjacency = collections.defaultdict(set)
    for first, second in boundary_edges:
        boundary_adjacency[first].add(second)
        boundary_adjacency[second].add(first)
    boundary_components = 0
    unseen = set(boundary_adjacency)
    if any(len(neighbours) != 2 for neighbours in boundary_adjacency.values()):
        raise AssertionError("surface boundary is not a union of circles")
    while unseen:
        boundary_components += 1
        start = next(iter(unseen))
        reached, stack = {start}, [start]
        while stack:
            current = stack.pop()
            for neighbour in boundary_adjacency[current]:
                if neighbour not in reached:
                    reached.add(neighbour)
                    stack.append(neighbour)
        unseen -= reached
    return {
        "vertices": len(vertices),
        "edges": len(edge_counts),
        "triangles": len(triangles),
        "euler": len(vertices) - len(edge_counts) + len(triangles),
        "boundary_components": boundary_components,
        "boundary_edges": boundary_edges,
        "boundary_vertices": set().union(*boundary_edges) if boundary_edges else set(),
    }


def is_simple_cycle(curve):
    adjacency = collections.defaultdict(set)
    for first, second in curve:
        adjacency[first].add(second)
        adjacency[second].add(first)
    return bool(adjacency) and all(len(value) == 2 for value in adjacency.values()) and connected_graph(adjacency)


def serialized_edge(raw):
    return frozenset(pvertex(vertex) for vertex in raw)


def movie_complex(analyzer, pl, sweep_tools, movie, record):
    tetrahedra, _, face_occurrences = sweep_tools.build_tetrahedra(
        analyzer, pl, movie["power"]
    )
    support_ids = set(record["support_tetrahedra"])
    support_tets = [
        frozenset(pvertex(vertex) for vertex in tetrahedra[index]["vertices"])
        for index in support_ids
    ]
    if any(len(tet) != 4 for tet in support_tets):
        raise AssertionError("support has a degenerate quotient tetrahedron")
    face_counts = collections.Counter(
        frozenset(face)
        for tet in support_tets
        for face in itertools.combinations(tet, 3)
    )
    if set(face_counts.values()) - {1, 2}:
        raise AssertionError("support has a nonmanifold face multiplicity")
    boundary = {face for face, count in face_counts.items() if count == 1}
    boundary_result = surface_invariants(boundary)
    if boundary_result["euler"] != 2 or boundary_result["boundary_components"] != 0:
        raise AssertionError("support boundary is not a combinatorial 2-sphere")

    support_vertices = set().union(*support_tets)
    boundary_vertices = set().union(*boundary)
    vertex_link_kinds = collections.Counter()
    for vertex in support_vertices:
        link = [tet - {vertex} for tet in support_tets if vertex in tet]
        result = surface_invariants(link)
        if vertex in boundary_vertices:
            if result["euler"] != 1 or result["boundary_components"] != 1:
                raise AssertionError("boundary vertex does not have a disk link")
            vertex_link_kinds["disk"] += 1
        else:
            if result["euler"] != 2 or result["boundary_components"] != 0:
                raise AssertionError("interior vertex does not have a sphere link")
            vertex_link_kinds["sphere"] += 1

    collapse = analyzer.collapse_to_point([tuple(tet) for tet in support_tets])
    if not collapse["collapses_to_point"]:
        raise AssertionError("support does not replay as collapsible")

    current = [tet["source_owner"] == 0 for tet in tetrahedra]
    target = [tet["target_owner"] == 0 for tet in tetrahedra]
    for index in movie["single_move_tetrahedra"]:
        current[index] = target[index]
    source_patch, target_patch = [], []
    for face, hits in face_occurrences.items():
        (first, _), (second, _) = hits
        if first not in support_ids or second not in support_ids:
            continue
        wrapped = frozenset(pvertex(vertex) for vertex in face)
        if current[first] != current[second]:
            source_patch.append(wrapped)
        if target[first] != target[second]:
            target_patch.append(wrapped)

    boundary_edge_set = set().union(*(edges(face) for face in boundary))
    patch_results = []
    for name, patch in (("source", source_patch), ("target", target_patch)):
        result = surface_invariants(patch)
        if result["euler"] != 1 or result["boundary_components"] != 1:
            raise AssertionError(f"{name} patch is not a combinatorial disk")
        if not result["boundary_edges"] <= boundary_edge_set:
            raise AssertionError(f"{name} disk boundary is not on the support sphere")
        patch_vertices = set().union(*patch)
        if patch_vertices & boundary_vertices != result["boundary_vertices"]:
            raise AssertionError(f"{name} disk has an improper boundary intersection")
        if set(patch) & boundary:
            raise AssertionError(f"{name} disk contains a support-boundary triangle")
        patch_results.append(result)

    return {
        "support_tetrahedra": len(support_tets),
        "support_boundary": boundary_result,
        "vertex_link_kinds": dict(vertex_link_kinds),
        "source_patch": patch_results[0],
        "target_patch": patch_results[1],
    }, boundary, patch_results[0]["boundary_edges"], patch_results[1]["boundary_edges"]


def verify_boundary_isotopy(record, boundary, source_curve, target_curve):
    curve = set(source_curve)
    if not is_simple_cycle(curve):
        raise AssertionError("source patch boundary is not a simple curve")
    for position, placement in enumerate(record["placements"]):
        face = frozenset(pvertex(vertex) for vertex in placement["actual_face"])
        if face not in boundary:
            raise AssertionError("outer curve move is not on the support sphere")
        before = {serialized_edge(edge) for edge in placement["before_local_edges"]}
        after = {serialized_edge(edge) for edge in placement["after_local_edges"]}
        if before != curve & edges(face):
            raise AssertionError(f"boundary move {position} has the wrong incoming local curve")
        if {len(before), len(after)} != {1, 2}:
            raise AssertionError(f"boundary move {position} is not a triangle isotopy")
        curve = (curve - before) | after
        if not is_simple_cycle(curve):
            raise AssertionError(f"boundary move {position} creates a nonsimple curve")
    if curve != set(target_curve):
        raise AssertionError("boundary triangle isotopy does not end at the target disk")
    return len(record["placements"])


def verify():
    analyzer = load("analyze_t73_johnson_arm_mismatch")
    pl = load("t73_johnson_pl")
    sweep_tools = load("build_t73_johnson_elementary_sweep")
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
    support = json.loads(SUPPORT.read_text(encoding="utf-8"))
    outer = json.loads(OUTER.read_text(encoding="utf-8"))
    if not (len(sweep["movies"]) == len(support["movies"]) == len(outer["movies"]) == 4):
        raise AssertionError("canonical movie lists do not have four aligned entries")
    checks = []
    for movie, support_record, outer_record in zip(
        sweep["movies"], support["movies"], outer["movies"]
    ):
        key = (movie["power"], movie["side"])
        if key != (support_record["power"], support_record["side"]) or key != (
            outer_record["power"], outer_record["side"]
        ):
            raise AssertionError("canonical movie keys are not aligned")
        topology, boundary, source_curve, target_curve = movie_complex(
            analyzer, pl, sweep_tools, movie, support_record
        )
        move_count = verify_boundary_isotopy(
            outer_record, boundary, source_curve, target_curve
        )
        checks.append(
            {
                "power": key[0],
                "side": key[1],
                "support_tetrahedra": topology["support_tetrahedra"],
                "boundary_euler": topology["support_boundary"]["euler"],
                "vertex_link_kinds": topology["vertex_link_kinds"],
                "source_disk_euler": topology["source_patch"]["euler"],
                "target_disk_euler": topology["target_patch"]["euler"],
                "boundary_triangle_isotopy_moves": move_count,
            }
        )
    return {
        "schema": "t73_paired_saddle_topology/v1",
        "verdict": "PASS_PL_TOPOLOGICAL_HYPOTHESES",
        "movies": checks,
        "paper_consequence": (
            "PL Schoenflies makes each collapsible 3-manifold with sphere "
            "boundary a 3-ball; proper-disk uniqueness and PL isotopy extension, "
            "tapered across a thin external collar, give an ambient "
            "homeomorphism fixed on the collar outer boundary"
        ),
        "scope": (
            "local paired-saddle existence only; no canonical coordinate "
            "evaluator and no binding to the later spine or detector geometry"
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.check:
        print(f"PAIRED_SADDLE_TOPOLOGY={result['verdict']}")
        for movie in result["movies"]:
            print(
                f"MOVIE_{movie['power']}_{movie['side']}="
                f"TETS:{movie['support_tetrahedra']},"
                f"LINKS:{movie['vertex_link_kinds']},"
                f"CURVE_MOVES:{movie['boundary_triangle_isotopy_moves']}"
            )
        print("LOCAL_AMBIENT_EXISTENCE=PAPER_THEOREM")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
