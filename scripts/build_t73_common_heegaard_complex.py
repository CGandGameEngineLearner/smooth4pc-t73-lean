#!/usr/bin/env python3
"""Build the T73 Heegaard pair from cubical barycentric dual 3-blocks.

The ambient cellulation is the 2 x 2 x 2 cubulation of T^3 (period 4, cubes
of side 2).  Each handlebody is the union of dual 3-blocks of the four
vertices of one coordinate spine.  On this lattice those dual blocks are
the l_infinity cubes of radius 1 about the spine vertices; after Freudenthal
subdivision they become 192 tetrahedra.  Tetrahedra are never assigned by
comparing a tetrahedron barycenter to the two spines.

H ↘ K is an explicit elementary-collapse sequence onto the spine graph.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
GEOM = ROOT / "geometry"
PERIOD = 4
AXES = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
Vertex = tuple[int, int, int]
Simplex = frozenset[Vertex]

JOHNSON_BASES = ((0, 0, 0), (2, 2, 2))
AR_BASES = ((-1, -1, -1), (1, 1, 1))


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def add(a: Vertex, b: Vertex) -> Vertex:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def wrap_delta(value: float | int, period: int = PERIOD) -> float:
    residue = float(value) % period
    if residue > period / 2:
        residue -= period
    return residue


def qv_johnson(vertex: Iterable[int]) -> Vertex:
    return tuple(int(x) % PERIOD for x in vertex)  # type: ignore[return-value]


def qv_ar(vertex: Iterable[int]) -> Vertex:
    return tuple((int(x) + 2) % PERIOD for x in vertex)  # type: ignore[return-value]


def scaled_s(vertex: Iterable[int]) -> Vertex:
    """Integer model of S(u)=2u-(1/2,1/2,1/2) on the period-4 Johnson mesh."""
    return tuple(int(x) - 1 for x in vertex)  # type: ignore[return-value]


def coarse_spine_vertices(base: Vertex) -> tuple[Vertex, ...]:
    origin = tuple(base)
    arms = [origin]
    for axis in range(3):
        vertex = list(origin)
        vertex[axis] = origin[axis] + 2
        arms.append(tuple(vertex))
    return tuple(arms)  # type: ignore[arg-type]


def spine_graph(base: Vertex, qv_fn) -> tuple[set[Vertex], set[Simplex]]:
    vertices: set[Vertex] = set()
    edges: set[Simplex] = set()
    for axis in range(3):
        sequence: list[Vertex] = []
        for offset in range(PERIOD + 1):
            vertex = list(base)
            vertex[axis] = base[axis] + offset
            sequence.append(qv_fn(vertex))
        for start, end in zip(sequence, sequence[1:]):
            vertices.add(start)
            vertices.add(end)
            edges.add(frozenset((start, end)))
    return vertices, edges


def graph_rank(vertices: set[Vertex], edges: set[Simplex]) -> int:
    if not vertices:
        return 0
    adj: dict[Vertex, set[Vertex]] = {vertex: set() for vertex in vertices}
    for edge in edges:
        a, b = tuple(edge)
        adj[a].add(b)
        adj[b].add(a)
    seen: set[Vertex] = set()
    components = 0
    for start in vertices:
        if start in seen:
            continue
        components += 1
        stack = [start]
        seen.add(start)
        while stack:
            vertex = stack.pop()
            for neighbour in adj[vertex]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
    return len(edges) - len(vertices) + components


def inf_dist_to_set(point: tuple[float, float, float], family: Iterable[Vertex]) -> float:
    best: float | None = None
    for vertex in family:
        dist = max(abs(wrap_delta(point[i] - vertex[i])) for i in range(3))
        if best is None or dist < best:
            best = dist
    if best is None:
        raise AssertionError("empty dual-block family")
    return best


def cube_owner(origin: Vertex, family_a: tuple[Vertex, ...], family_b: tuple[Vertex, ...]) -> int:
    center = (origin[0] + 0.5, origin[1] + 0.5, origin[2] + 0.5)
    dist_a = inf_dist_to_set(center, family_a)
    dist_b = inf_dist_to_set(center, family_b)
    if dist_a == dist_b:
        raise AssertionError(f"unit cube {origin} is not in a unique dual 3-block")
    return 0 if dist_a < dist_b else 1


def nearest_coarse(origin: Vertex, family: tuple[Vertex, ...]) -> Vertex:
    center = (origin[0] + 0.5, origin[1] + 0.5, origin[2] + 0.5)
    return min(family, key=lambda vertex: inf_dist_to_set(center, (vertex,)))


def freudenthal_cube(origin: Vertex) -> list[list[Vertex]]:
    tetrahedra: list[list[Vertex]] = []
    for permutation in itertools.permutations(range(3)):
        v0 = origin
        v1 = add(v0, AXES[permutation[0]])
        v2 = add(v1, AXES[permutation[1]])
        v3 = add(v2, AXES[permutation[2]])
        tetrahedra.append([v0, v1, v2, v3])
    return tetrahedra


def facets(simplex: Simplex) -> list[Simplex]:
    vertices = list(simplex)
    return [frozenset(vertices[j] for j in range(len(vertices)) if j != i) for i in range(len(vertices))]


def simplex_key(simplex: Simplex) -> tuple[tuple[int, int, int], ...]:
    return tuple(sorted(simplex))


def build_downward(tets: Iterable[Iterable[Vertex]]) -> list[set[Simplex]]:
    simplices: list[set[Simplex]] = [set() for _ in range(4)]
    for tet in tets:
        tau = frozenset(tet)
        simplices[3].add(tau)
        verts = list(tau)
        for combo in itertools.combinations(verts, 3):
            simplices[2].add(frozenset(combo))
        for combo in itertools.combinations(verts, 2):
            simplices[1].add(frozenset(combo))
        for vertex in verts:
            simplices[0].add(frozenset((vertex,)))
    return simplices


def collapse_relative(
    tets: list[list[Vertex]],
    protected_vertices: set[Vertex],
    protected_edges: set[Simplex],
) -> list[dict[str, Any]]:
    """Elementary collapses onto the protected 1-complex, highest dimension first."""

    simplices = build_downward(tets)
    cofaces: list[dict[Simplex, set[Simplex]]] = [defaultdict(set) for _ in range(3)]
    for dim in range(1, 4):
        for tau in simplices[dim]:
            for face in facets(tau):
                cofaces[dim - 1][face].add(tau)
    protected: list[set[Simplex]] = [
        {frozenset((vertex,)) for vertex in protected_vertices},
        set(protected_edges),
        set(),
        set(),
    ]
    steps: list[dict[str, Any]] = []
    for dim in (3, 2, 1):
        progressed = True
        while progressed:
            progressed = False
            candidates: list[tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...], Simplex, Simplex]] = []
            for tau in simplices[dim]:
                if tau in protected[dim]:
                    continue
                for sigma in facets(tau):
                    if sigma in protected[dim - 1]:
                        continue
                    hosts = cofaces[dim - 1][sigma] & simplices[dim]
                    if len(hosts) == 1 and tau in hosts:
                        candidates.append((simplex_key(tau), simplex_key(sigma), tau, sigma))
            if not candidates:
                continue
            candidates.sort()
            _, _, tau, sigma = candidates[0]
            simplices[dim].remove(tau)
            simplices[dim - 1].remove(sigma)
            for face in facets(tau):
                cofaces[dim - 1][face].discard(tau)
            if dim - 1 > 0:
                for face in facets(sigma):
                    cofaces[dim - 2][face].discard(sigma)
            steps.append(
                {
                    "dim": dim,
                    "simplex": [list(vertex) for vertex in simplex_key(tau)],
                    "free_face": [list(vertex) for vertex in simplex_key(sigma)],
                }
            )
            progressed = True
    remaining_vertices = {next(iter(simplex)) for simplex in simplices[0]}
    remaining_edges = set(simplices[1])
    if remaining_vertices != protected_vertices or remaining_edges != protected_edges:
        raise AssertionError(
            "collapse did not retract onto the spine: "
            f"V {len(remaining_vertices)}/{len(protected_vertices)}, "
            f"E {len(remaining_edges)}/{len(protected_edges)}, "
            f"faces {len(simplices[2])}, tets {len(simplices[3])}"
        )
    if graph_rank(remaining_vertices, remaining_edges) != 3:
        raise AssertionError("collapsed spine does not have graph rank 3")
    return steps


def replay_collapse(
    tets: list[list[Vertex]],
    steps: list[dict[str, Any]],
    protected_vertices: set[Vertex],
    protected_edges: set[Simplex],
) -> None:
    simplices = build_downward(tets)
    for step in steps:
        dim = int(step["dim"])
        tau = frozenset(tuple(vertex) for vertex in step["simplex"])
        sigma = frozenset(tuple(vertex) for vertex in step["free_face"])
        if tau not in simplices[dim]:
            raise AssertionError("collapse step removes a missing simplex")
        if sigma not in simplices[dim - 1]:
            raise AssertionError("collapse step removes a missing free face")
        if sigma not in facets(tau):
            raise AssertionError("recorded free face is not a facet")
        hosts = [host for host in simplices[dim] if sigma <= host]
        if hosts != [tau]:
            raise AssertionError("recorded free face is not free")
        if tau in {frozenset((vertex,)) for vertex in protected_vertices} or tau in protected_edges:
            raise AssertionError("collapse deletes a spine simplex")
        if sigma in {frozenset((vertex,)) for vertex in protected_vertices} or sigma in protected_edges:
            raise AssertionError("collapse deletes a spine face")
        simplices[dim].remove(tau)
        simplices[dim - 1].remove(sigma)
    if {next(iter(simplex)) for simplex in simplices[0]} != protected_vertices:
        raise AssertionError("replay does not leave the spine vertices")
    if simplices[1] != protected_edges:
        raise AssertionError("replay does not leave the spine edges")
    if simplices[2] or simplices[3]:
        raise AssertionError("replay leaves higher simplices")


def face_map(tets: list[list[Vertex]], qv_fn) -> dict[tuple[Vertex, ...], list[int]]:
    faces: dict[tuple[Vertex, ...], list[int]] = defaultdict(list)
    for index, tet in enumerate(tets):
        wrapped = [qv_fn(vertex) for vertex in tet]
        for omitted in range(4):
            face = tuple(sorted(wrapped[j] for j in range(4) if j != omitted))
            faces[face].append(index)
    return faces


def boundary_faces(tets: list[list[Vertex]], qv_fn) -> set[tuple[Vertex, ...]]:
    counts: Counter[tuple[Vertex, ...]] = Counter()
    for tet in tets:
        wrapped = [qv_fn(vertex) for vertex in tet]
        for omitted in range(4):
            face = tuple(sorted(wrapped[j] for j in range(4) if j != omitted))
            counts[face] += 1
    extra = {face: count for face, count in counts.items() if count not in (1, 2)}
    if extra:
        raise AssertionError(f"non-manifold face multiplicity: {extra}")
    return {face for face, count in counts.items() if count == 1}


def surface_genus(faces: set[tuple[Vertex, ...]]) -> tuple[int, dict[str, int]]:
    vertices: set[Vertex] = set()
    edges: set[tuple[Vertex, Vertex]] = set()
    for face in faces:
        vertices.update(face)
        for i, j in itertools.combinations(range(3), 2):
            edges.add(tuple(sorted((face[i], face[j]))))  # type: ignore[arg-type]
    chi = len(vertices) - len(edges) + len(faces)
    if chi % 2:
        raise AssertionError("surface Euler characteristic is odd")
    genus = (2 - chi) // 2
    return genus, {"V": len(vertices), "E": len(edges), "F": len(faces), "chi": chi}


def euler(tets: list[list[Vertex]], qv_fn) -> dict[str, int]:
    vertices: set[Vertex] = set()
    edges: set[tuple[Vertex, Vertex]] = set()
    faces: set[tuple[Vertex, ...]] = set()
    for tet in tets:
        wrapped = [qv_fn(vertex) for vertex in tet]
        vertices.update(wrapped)
        for i, j in itertools.combinations(range(4), 2):
            edges.add(tuple(sorted((wrapped[i], wrapped[j]))))  # type: ignore[arg-type]
        for omitted in range(4):
            faces.add(tuple(sorted(wrapped[j] for j in range(4) if j != omitted)))
    chi = len(vertices) - len(edges) + len(faces) - len(tets)
    return {"V": len(vertices), "E": len(edges), "F": len(faces), "T": len(tets), "chi": chi}


def pack_tets(tets: list[list[Vertex]], qv_fn) -> list[list[list[int]]]:
    return [[list(qv_fn(vertex)) for vertex in tet] for tet in tets]


def pack_graph(vertices: set[Vertex], edges: set[Simplex]) -> dict[str, Any]:
    return {
        "vertices": [list(vertex) for vertex in sorted(vertices)],
        "edges": [sorted(list(vertex) for vertex in edge) for edge in sorted(edges, key=simplex_key)],
        "vertex_count": len(vertices),
        "edge_count": len(edges),
        "graph_rank": graph_rank(vertices, edges),
    }


def build_side(
    name: str,
    origins: Iterable[Vertex],
    bases: tuple[Vertex, Vertex],
    qv_fn,
) -> dict[str, Any]:
    family_0 = coarse_spine_vertices(bases[0])
    family_1 = coarse_spine_vertices(bases[1])
    if set(family_0) & set(family_1):
        raise AssertionError(f"{name} coarse spine vertices meet")
    cubes_0: list[Vertex] = []
    cubes_1: list[Vertex] = []
    cube_records: list[dict[str, Any]] = []
    tets_0: list[list[Vertex]] = []
    tets_1: list[list[Vertex]] = []
    for origin in origins:
        owner = cube_owner(origin, family_0, family_1)
        block = nearest_coarse(origin, family_0 if owner == 0 else family_1)
        cube_records.append(
            {
                "origin": list(origin),
                "owner": owner,
                "dual_block_vertex": list(qv_fn(block)),
            }
        )
        (cubes_0 if owner == 0 else cubes_1).append(origin)
        target = tets_0 if owner == 0 else tets_1
        target.extend(freudenthal_cube(origin))
    if len(cubes_0) != 32 or len(cubes_1) != 32:
        raise AssertionError(f"{name} dual 3-blocks are not 32+32 unit cubes")
    if len(tets_0) != 192 or len(tets_1) != 192:
        raise AssertionError(f"{name} dual 3-blocks are not 192+192 tetrahedra")
    ids_0 = {tuple(sorted(qv_fn(vertex) for vertex in tet)) for tet in tets_0}
    ids_1 = {tuple(sorted(qv_fn(vertex) for vertex in tet)) for tet in tets_1}
    if len(ids_0) != len(tets_0) or len(ids_1) != len(tets_1):
        raise AssertionError(f"{name} dual-block tetrahedra are not unique after quotient")
    if ids_0 & ids_1:
        raise AssertionError(f"{name} handlebodies share a tetrahedron")
    if len(ids_0) + len(ids_1) != 384:
        raise AssertionError(f"{name} handlebodies do not fill T^3")
    boundary_0 = boundary_faces(tets_0, qv_fn)
    boundary_1 = boundary_faces(tets_1, qv_fn)
    if boundary_0 != boundary_1:
        raise AssertionError(f"{name} handlebodies do not share a common boundary")
    genus, surface = surface_genus(boundary_0)
    if genus != 3:
        raise AssertionError(f"{name} Heegaard surface is not genus 3")
    euler_0 = euler(tets_0, qv_fn)
    euler_1 = euler(tets_1, qv_fn)
    if euler_0["chi"] != -2 or euler_1["chi"] != -2:
        raise AssertionError(f"{name} handlebody Euler characteristic is not -2")
    spine_0_v, spine_0_e = spine_graph(bases[0], qv_fn)
    spine_1_v, spine_1_e = spine_graph(bases[1], qv_fn)
    if graph_rank(spine_0_v, spine_0_e) != 3 or graph_rank(spine_1_v, spine_1_e) != 3:
        raise AssertionError(f"{name} spine is not rank 3")
    collapse_0 = collapse_relative(
        [[qv_fn(vertex) for vertex in tet] for tet in tets_0], spine_0_v, spine_0_e
    )
    collapse_1 = collapse_relative(
        [[qv_fn(vertex) for vertex in tet] for tet in tets_1], spine_1_v, spine_1_e
    )
    replay_collapse(
        [[qv_fn(vertex) for vertex in tet] for tet in tets_0],
        collapse_0,
        spine_0_v,
        spine_0_e,
    )
    replay_collapse(
        [[qv_fn(vertex) for vertex in tet] for tet in tets_1],
        collapse_1,
        spine_1_v,
        spine_1_e,
    )
    return {
        "name": name,
        "bases": [list(base) for base in bases],
        "coarse_vertices_0": [list(qv_fn(vertex)) for vertex in family_0],
        "coarse_vertices_1": [list(qv_fn(vertex)) for vertex in family_1],
        "unit_cubes": cube_records,
        "handlebody_0_tets": pack_tets(tets_0, qv_fn),
        "handlebody_1_tets": pack_tets(tets_1, qv_fn),
        "spine_0": pack_graph(spine_0_v, spine_0_e),
        "spine_1": pack_graph(spine_1_v, spine_1_e),
        "collapse_0": collapse_0,
        "collapse_1": collapse_1,
        "euler_0": euler_0,
        "euler_1": euler_1,
        "interface_genus": genus,
        "interface_surface": surface,
        "fills_torus": True,
        "cells_disjoint": True,
    }


def gluings_for(tets: list[list[list[int]]]) -> dict[str, Any]:
    """Internal face gluings for a Regina triangulation with boundary."""

    tets_v = [[tuple(vertex) for vertex in tet] for tet in tets]
    faces: dict[tuple[Vertex, ...], list[tuple[int, int]]] = defaultdict(list)
    for index, tet in enumerate(tets_v):
        for omitted in range(4):
            face = tuple(sorted(tet[j] for j in range(4) if j != omitted))
            faces[face].append((index, omitted))
    gluings: list[list[Any]] = []
    seen: set[tuple[int, int]] = set()
    for hits in faces.values():
        if len(hits) == 1:
            continue
        if len(hits) != 2:
            raise AssertionError("handlebody face is not manifold")
        (a, fa), (b, fb) = hits
        key = tuple(sorted(((a, fa), (b, fb))))
        if key in seen:
            continue
        seen.add(key)  # type: ignore[arg-type]
        perm = [None] * 4
        perm[fa] = fb
        for i in range(4):
            if i == fa:
                continue
            matches = [j for j in range(4) if j != fb and tets_v[b][j] == tets_v[a][i]]
            if len(matches) != 1:
                raise AssertionError("gluing permutation is not unique")
            perm[i] = matches[0]
        gluings.append([a, fa, b, perm])
    return {"simplex_count": len(tets), "gluings": gluings, "boundary_triangles": sum(1 for hits in faces.values() if len(hits) == 1)}


def generate() -> dict[str, Any]:
    johnson_origins = tuple(itertools.product(range(0, PERIOD), repeat=3))
    ar_origins = tuple(itertools.product(range(-2, 2), repeat=3))
    johnson = build_side("johnson", johnson_origins, JOHNSON_BASES, qv_johnson)
    ar = build_side("ar", ar_origins, AR_BASES, qv_ar)

    mapped_0 = {
        tuple(sorted(qv_ar(scaled_s(vertex)) for vertex in tet))
        for tet in johnson["handlebody_0_tets"]
    }
    mapped_1 = {
        tuple(sorted(qv_ar(scaled_s(vertex)) for vertex in tet))
        for tet in johnson["handlebody_1_tets"]
    }
    ar_0 = {tuple(sorted(tuple(vertex) for vertex in tet)) for tet in ar["handlebody_0_tets"]}
    ar_1 = {tuple(sorted(tuple(vertex) for vertex in tet)) for tet in ar["handlebody_1_tets"]}
    if mapped_0 != ar_0 or mapped_1 != ar_1:
        raise AssertionError("S does not carry the Johnson dual-block pair onto the AR pair")

    gluings = {
        "H_J_0": gluings_for(johnson["handlebody_0_tets"]),
        "H_J_1": gluings_for(johnson["handlebody_1_tets"]),
        "H_AR_0": gluings_for(ar["handlebody_0_tets"]),
        "H_AR_1": gluings_for(ar["handlebody_1_tets"]),
    }
    return {
        "schema": "t73_common_heegaard_complex/v1",
        "assignment": (
            "barycentric dual 3-blocks of the 2x2x2 cubulation vertices; "
            "unit cubes belong to the unique l_infinity dual 3-block of a spine vertex"
        ),
        "forbidden_assignment": "tetrahedron barycenter distance to the two spines",
        "formula_original": "S(u)=2u-(1/2,1/2,1/2)",
        "formula_scaled": "T(v)=v-(1,1,1) on the period-4 integer Johnson mesh",
        "period_scaled": PERIOD,
        "johnson": johnson,
        "ar": ar,
        "s_maps_johnson_pair_onto_ar_pair": True,
        "gluings": gluings,
    }


def split_artifacts(model: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    torus = {
        "schema": "t73_common_torus_triangulation/v1",
        "period_scaled": PERIOD,
        "assignment": model["assignment"],
        "forbidden_assignment": model["forbidden_assignment"],
        "johnson_unit_cubes": model["johnson"]["unit_cubes"],
        "ar_unit_cubes": model["ar"]["unit_cubes"],
        "johnson_tetrahedra": {
            "H0": model["johnson"]["handlebody_0_tets"],
            "H1": model["johnson"]["handlebody_1_tets"],
        },
        "ar_tetrahedra": {
            "H0": model["ar"]["handlebody_0_tets"],
            "H1": model["ar"]["handlebody_1_tets"],
        },
        "gluings": model["gluings"],
        "s_maps_johnson_pair_onto_ar_pair": model["s_maps_johnson_pair_onto_ar_pair"],
        "formula_original": model["formula_original"],
        "formula_scaled": model["formula_scaled"],
    }
    torus["sha256"] = canonical_sha(torus)
    johnson_spines = {
        "schema": "t73_johnson_spines/v1",
        "K_J_0": model["johnson"]["spine_0"],
        "K_J_1": model["johnson"]["spine_1"],
        "collapse_H_J_0": model["johnson"]["collapse_0"],
        "collapse_H_J_1": model["johnson"]["collapse_1"],
        "euler_H_J_0": model["johnson"]["euler_0"],
        "euler_H_J_1": model["johnson"]["euler_1"],
        "interface_genus": model["johnson"]["interface_genus"],
        "interface_surface": model["johnson"]["interface_surface"],
    }
    johnson_spines["sha256"] = canonical_sha(johnson_spines)
    ar_spines = {
        "schema": "t73_ar_spines/v1",
        "K_AR_0": model["ar"]["spine_0"],
        "K_AR_1": model["ar"]["spine_1"],
        "collapse_H_AR_0": model["ar"]["collapse_0"],
        "collapse_H_AR_1": model["ar"]["collapse_1"],
        "euler_H_AR_0": model["ar"]["euler_0"],
        "euler_H_AR_1": model["ar"]["euler_1"],
        "interface_genus": model["ar"]["interface_genus"],
        "interface_surface": model["ar"]["interface_surface"],
    }
    ar_spines["sha256"] = canonical_sha(ar_spines)
    return torus, johnson_spines, ar_spines


def write_artifacts(model: dict[str, Any]) -> tuple[Path, Path, Path]:
    GEOM.mkdir(parents=True, exist_ok=True)
    torus, johnson_spines, ar_spines = split_artifacts(model)
    paths = (
        GEOM / "t73_common_torus_triangulation.json",
        GEOM / "t73_johnson_spines.json",
        GEOM / "t73_ar_spines.json",
    )
    payloads = (torus, johnson_spines, ar_spines)
    for path, payload in zip(paths, payloads):
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    model = generate()
    if args.write:
        paths = write_artifacts(model)
        for path in paths:
            print(f"WROTE={path}")
    if args.check:
        print("T73_COMMON_HEEGAARD_COMPLEX=PASS")
        print(f"JOHNSON_INTERFACE_GENUS={model['johnson']['interface_genus']}")
        print(f"AR_INTERFACE_GENUS={model['ar']['interface_genus']}")
        print(f"H_J_0_COLLAPSE_STEPS={len(model['johnson']['collapse_0'])}")
        print(f"H_J_1_COLLAPSE_STEPS={len(model['johnson']['collapse_1'])}")
        print(f"H_AR_0_COLLAPSE_STEPS={len(model['ar']['collapse_0'])}")
        print(f"H_AR_1_COLLAPSE_STEPS={len(model['ar']['collapse_1'])}")
        print(f"S_MAPS_PAIR={model['s_maps_johnson_pair_onto_ar_pair']}")
        print(f"SPINE_RANK_J0={model['johnson']['spine_0']['graph_rank']}")
        print(f"SPINE_RANK_J1={model['johnson']['spine_1']['graph_rank']}")
        return
    if not args.write:
        summary = {
            key: value
            for key, value in model.items()
            if key not in {"johnson", "ar", "gluings"}
        }
        print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
