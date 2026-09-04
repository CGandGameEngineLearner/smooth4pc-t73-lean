#!/usr/bin/env python3
"""Largest currently constructible prefix of a common reduced-boundary model.

This builds a labelled triangulation of #2(S1 x S2), the boundary of the
post-cancellation 4-dimensional 0/1-handlebody, and two labelled generator
edge loops.  It also implements a deterministic simplicial Dehn-filling
primitive.  It does not claim that the five committed railroad components or
their framing annuli are embedded in this triangulation: the required
railroad-to-boundary subdivision map is absent.
"""

from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_gate():
    path = ROOT / "scripts" / "verify_t73_gs1_gp3.py"
    spec = importlib.util.spec_from_file_location("t73_gs1_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def staircase_prism(
    triangles: list[list[int]], lower: dict[int, int], upper: dict[int, int]
) -> list[list[int]]:
    tetrahedra: list[list[int]] = []
    for triangle in triangles:
        a, b, c = sorted(triangle)
        la, lb, lc = lower[a], lower[b], lower[c]
        ua, ub, uc = upper[a], upper[b], upper[c]
        tetrahedra.extend(
            [
                sorted((la, lb, lc, uc)),
                sorted((la, lb, ub, uc)),
                sorted((la, ua, ub, uc)),
            ]
        )
    return tetrahedra


def s2_times_s1(offset: int) -> tuple[list[Any], list[list[int]], list[dict[int, int]]]:
    sphere = [[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]]
    layers = [
        {vertex: offset + 4 * layer + vertex for vertex in range(4)}
        for layer in range(3)
    ]
    vertices = [
        {"summand_vertex": offset + index} for index in range(12)
    ]
    tetrahedra = (
        staircase_prism(sphere, layers[0], layers[1])
        + staircase_prism(sphere, layers[1], layers[2])
        + staircase_prism(sphere, layers[2], layers[0])
    )
    return vertices, tetrahedra, layers


def edge_set(tetrahedra: list[list[int]]) -> set[tuple[int, int]]:
    result: set[tuple[int, int]] = set()
    for tet in tetrahedra:
        for left in range(4):
            for right in range(left + 1, 4):
                result.add(tuple(sorted((tet[left], tet[right]))))
    return result


def build_boundary() -> dict[str, Any]:
    gate = load_gate()
    vertices_1, tetrahedra_1, layers_1 = s2_times_s1(0)
    vertices_2, tetrahedra_2, layers_2 = s2_times_s1(12)
    removed_1 = tetrahedra_1[0]
    removed_2 = tetrahedra_2[0]
    identify = {
        removed_2[index]: removed_1[3 - index] for index in range(4)
    }
    next_vertex = 12
    second_map = dict(identify)
    for old_vertex in range(12, 24):
        if old_vertex not in second_map:
            second_map[old_vertex] = next_vertex
            next_vertex += 1
    vertices = list(vertices_1)
    inverse_second = {new: old for old, new in second_map.items() if old not in identify}
    for new_vertex in range(12, next_vertex):
        vertices.append({"summand_vertex": inverse_second[new_vertex]})
    tetrahedra = tetrahedra_1[1:] + [
        sorted(second_map[vertex] for vertex in tet)
        for tet in tetrahedra_2[1:]
    ]
    complex_raw = {"vertices": vertices, "tetrahedra": tetrahedra}
    checked = gate.validate_closed_3_complex(complex_raw, "reduced_one_handle_boundary")
    edges = edge_set(tetrahedra)
    y_loop = [layers_1[0][0], layers_1[1][0], layers_1[2][0], layers_1[0][0]]
    z_loop = [
        second_map[layers_2[0][0]],
        second_map[layers_2[1][0]],
        second_map[layers_2[2][0]],
        second_map[layers_2[0][0]],
    ]
    for name, loop in (("y", y_loop), ("z", z_loop)):
        if len(set(loop[:-1])) != 3 or any(
            tuple(sorted(edge)) not in edges for edge in zip(loop, loop[1:])
        ):
            raise AssertionError(f"{name} generator is not an embedded edge loop")
    return {
        "schema": "t73_reduced_one_handle_boundary_prefix/v1",
        "construction": {
            "operation": "simplicial connected sum",
            "summands": ["S2 x S1", "S2 x S1"],
            "deleted_tetrahedra": [removed_1, removed_2],
            "orientation_reversing_boundary_vertex_identification": [
                [old, new] for old, new in sorted(identify.items())
            ],
        },
        "boundary_complex": complex_raw,
        "boundary_sha256": checked["sha256"],
        "labelled_generator_edge_loops": {"y": y_loop, "z": z_loop},
        "attaching_components": {
            "labels": ["m_2", "m_3", "r_xy", "r_yz", "r_zx"],
            "simplicial_edge_cycles": None,
            "framing_annulus_triangle_subcomplexes": None,
        },
        "first_unavailable_embedding_field": (
            "an explicit common subdivision and simplicial embedding from the "
            "five-component post-cancellation railroad link, including its "
            "framing annuli, into boundary_complex"
        ),
    }


def canonical_solid_torus() -> dict[str, Any]:
    """Triangulate (cone on a 3-cycle) x S1 with three cyclic interval layers."""
    disk_triangles = [[3, 0, 1], [3, 1, 2], [3, 2, 0]]
    layers = [
        {vertex: 4 * layer + vertex for vertex in range(4)}
        for layer in range(3)
    ]
    tetrahedra = (
        staircase_prism(disk_triangles, layers[0], layers[1])
        + staircase_prism(disk_triangles, layers[1], layers[2])
        + staircase_prism(disk_triangles, layers[2], layers[0])
    )
    return {
        "vertices": [{"solid_torus_vertex": index} for index in range(12)],
        "tetrahedra": tetrahedra,
        "meridian": [0, 1, 2, 0],
        "longitude": [0, 4, 8, 0],
        "core": [3, 7, 11, 3],
    }


def boundary_faces(tetrahedra: list[tuple[int, ...]], gate) -> set[tuple[int, ...]]:
    counts = Counter(face for tet in tetrahedra for face in gate.faces(tet))
    if set(counts.values()) - {1, 2}:
        raise gate.WitnessError("3-complex has nonmanifold face multiplicity")
    return {face for face, count in counts.items() if count == 1}


def replay_dehn_filling_step(
    current_raw: dict[str, Any], step: dict[str, Any]
) -> dict[str, Any]:
    """Replace an explicitly standard solid-torus neighbourhood by another."""
    gate = load_gate()
    current = gate.validate_closed_3_complex(current_raw, "dehn.source")
    required = [
        "component",
        "removed_tetrahedra",
        "removal_vertex_map",
        "attaching_curve",
        "filling_vertex_map",
        "new_vertices",
        "result_vertex_reindex",
        "framing_curve",
        "result",
    ]
    gate.require_fields(step, required, "dehn")
    standard = canonical_solid_torus()
    standard_tets = [tuple(sorted(tet)) for tet in standard["tetrahedra"]]
    standard_boundary = boundary_faces(standard_tets, gate)
    if len(standard_boundary) == 0:
        raise gate.WitnessError("canonical solid torus has empty boundary")

    def parse_removal_map(raw: Any, where: str) -> list[int]:
        if (
            not isinstance(raw, list)
            or len(raw) != 12
            or not all(
                isinstance(vertex, int)
                and 0 <= vertex < len(current["vertices"])
                for vertex in raw
            )
            or len(set(raw)) != 12
        ):
            raise gate.WitnessError(f"{where} is not an injective 12-vertex map")
        return raw

    removal_map = parse_removal_map(step["removal_vertex_map"], "dehn.removal_vertex_map")
    expected_removed = {
        tuple(sorted(removal_map[vertex] for vertex in tet))
        for tet in standard_tets
    }
    removed_indices = step["removed_tetrahedra"]
    if (
        not isinstance(removed_indices, list)
        or len(set(removed_indices)) != len(removed_indices)
        or not all(
            isinstance(index, int)
            and 0 <= index < len(current["tetrahedra"])
            for index in removed_indices
        )
    ):
        raise gate.WitnessError("dehn.removed_tetrahedra has invalid indices")
    actual_removed = {
        tuple(sorted(current["tetrahedra"][index])) for index in removed_indices
    }
    if actual_removed != expected_removed:
        raise gate.WitnessError("removed neighbourhood is not the canonical solid torus")
    removed_boundary = {
        tuple(sorted(removal_map[vertex] for vertex in face))
        for face in standard_boundary
    }

    expected_attaching = [removal_map[vertex] for vertex in standard["core"]]
    if step["attaching_curve"] != expected_attaching:
        raise gate.WitnessError("attaching_curve is not the removed solid-torus core")
    standard_boundary_vertices = {
        vertex for face in standard_boundary for vertex in face
    }
    standard_interior_vertices = sorted(set(range(12)) - standard_boundary_vertices)
    if standard_interior_vertices != [3, 7, 11]:
        raise gate.WitnessError("canonical solid-torus interior vertices changed")
    filling_raw = step["filling_vertex_map"]
    if not isinstance(filling_raw, list) or len(filling_raw) != 12:
        raise gate.WitnessError("dehn.filling_vertex_map must have twelve entries")
    filling_boundary_old: dict[int, int] = {}
    interior_slots: dict[int, int] = {}
    for standard_vertex, target in enumerate(filling_raw):
        if standard_vertex in standard_boundary_vertices:
            if (
                not isinstance(target, int)
                or target < 0
                or target >= len(current["vertices"])
            ):
                raise gate.WitnessError(
                    "dehn.filling_vertex_map boundary entries must be source vertices"
                )
            filling_boundary_old[standard_vertex] = target
        else:
            expected = f"new:{standard_interior_vertices.index(standard_vertex)}"
            if target != expected:
                raise gate.WitnessError(
                    "dehn.filling_vertex_map interior entries must use fresh new:k slots"
                )
            interior_slots[standard_vertex] = int(expected.split(":")[1])
    if len(set(filling_boundary_old.values())) != len(filling_boundary_old):
        raise gate.WitnessError("dehn filling boundary map is not injective")
    filling_boundary = {
        tuple(sorted(filling_boundary_old[vertex] for vertex in face))
        for face in standard_boundary
    }
    if filling_boundary != removed_boundary:
        raise gate.WitnessError("filling map is not a simplicial boundary identification")
    expected_framing = [
        filling_boundary_old[vertex] for vertex in standard["meridian"]
    ]
    if step["framing_curve"] != expected_framing:
        raise gate.WitnessError("framing_curve is not the filling meridian")

    removed_set = set(removed_indices)
    retained_old = [
        tuple(sorted(tet))
        for index, tet in enumerate(current["tetrahedra"])
        if index not in removed_set
    ]
    surviving_old_vertices = sorted(
        {vertex for tet in retained_old for vertex in tet}
    )
    old_to_new = {
        old_vertex: new_vertex
        for new_vertex, old_vertex in enumerate(surviving_old_vertices)
    }
    if any(
        old_vertex not in old_to_new
        for old_vertex in filling_boundary_old.values()
    ):
        raise gate.WitnessError(
            "dehn filling boundary map reuses a removed interior vertex"
        )
    expected_reindex = [
        [old_vertex, old_to_new[old_vertex]]
        for old_vertex in surviving_old_vertices
    ]
    if step["result_vertex_reindex"] != expected_reindex:
        raise gate.WitnessError(
            "dehn.result_vertex_reindex is not the canonical surviving-vertex reindex"
        )
    new_vertices = step["new_vertices"]
    if (
        not isinstance(new_vertices, list)
        or len(new_vertices) != len(standard_interior_vertices)
    ):
        raise gate.WitnessError(
            "dehn.new_vertices must contain the three fresh filling-core vertices"
        )
    existing_encodings = {
        json.dumps(vertex, sort_keys=True, separators=(",", ":"))
        for vertex in current["vertices"]
    }
    new_encodings = [
        json.dumps(vertex, sort_keys=True, separators=(",", ":"))
        for vertex in new_vertices
    ]
    if len(set(new_encodings)) != len(new_encodings) or any(
        encoded in existing_encodings for encoded in new_encodings
    ):
        raise gate.WitnessError("dehn.new_vertices are not fresh and distinct")
    retained = [
        sorted(old_to_new[vertex] for vertex in tet) for tet in retained_old
    ]
    filling_map: dict[int, int] = {
        standard_vertex: old_to_new[old_vertex]
        for standard_vertex, old_vertex in filling_boundary_old.items()
    }
    filling_map.update(
        {
            standard_vertex: len(surviving_old_vertices) + slot
            for standard_vertex, slot in interior_slots.items()
        }
    )
    filling_tets = [
        sorted(filling_map[vertex] for vertex in tet) for tet in standard_tets
    ]
    generated = {
        "vertices": [
            current["vertices"][old_vertex] for old_vertex in surviving_old_vertices
        ] + new_vertices,
        "tetrahedra": retained + filling_tets,
    }
    gate.validate_closed_3_complex(generated, "dehn.generated")
    result = gate.require_object(step["result"], "dehn.result")
    if generated != {
        "vertices": result.get("vertices"),
        "tetrahedra": result.get("tetrahedra"),
    }:
        raise gate.WitnessError("dehn.result does not equal the replayed filling")
    return generated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    result = build_boundary()
    if args.summary:
        print(f"VERTICES={len(result['boundary_complex']['vertices'])}")
        print(f"TETRAHEDRA={len(result['boundary_complex']['tetrahedra'])}")
        print(f"BOUNDARY_SHA256={result['boundary_sha256']}")
        print(f"FIRST_UNAVAILABLE={result['first_unavailable_embedding_field']}")
        return
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
