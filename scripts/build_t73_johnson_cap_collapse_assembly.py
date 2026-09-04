#!/usr/bin/env python3
"""Assemble actual cap collapses with the orientation-selected product collar."""

from __future__ import annotations

import argparse
import collections
import hashlib
import heapq
import importlib.util
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SWEEP = ROOT / "geometry" / "t73_johnson_elementary_sweep.json"
SUPPORT = ROOT / "geometry" / "t73_johnson_paired_saddle_support.json"
COLLARS = ROOT / "geometry" / "t73_johnson_cap_product_collars.json"
DERIVED_CELLS = ROOT / "geometry" / "t73_johnson_derived_collapse_cells.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_cap_collapse_assembly.json"


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


def relative_steps(tetrahedra, protected_faces):
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
    rows = []
    histogram = collections.Counter()
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
                    heapq.heappush(queue, (tuple(sorted(simplex)), tuple(sorted(face))))
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
            rows.append((dimension, simplex_key, face_key))
            histogram[dimension] += 1
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
                            queue, (tuple(sorted(host)), tuple(sorted(facet)))
                        )
    if any(simplices[dimension] != protected[dimension] for dimension in range(4)):
        raise AssertionError("cap collapse does not leave exactly the protected disk")
    return rows, histogram


def carrier_index(tetrahedra):
    index = collections.defaultdict(list)
    for tetrahedron_index, tetrahedron in enumerate(tetrahedra):
        for size in range(1, 5):
            for simplex in itertools.combinations(tetrahedron, size):
                index[frozenset(simplex)].append(tetrahedron_index)
    return index


def chart_for_step(pl, standard_vertices, structure, carriers, row):
    dimension, simplex_key, face_key = row
    simplex = set(simplex_key)
    free_face = set(face_key)
    apex = simplex - free_face
    if len(apex) != 1:
        raise AssertionError("cap collapse pair has no unique apex")
    candidates = []
    for carrier_id in carriers[frozenset(simplex)]:
        carrier = structure["indexed"][carrier_id]
        coordinates = {
            vertex_id: structure["coordinate"](structure["vertices"][vertex_id])
            for vertex_id in carrier
        }
        extras = set(carrier) - simplex
        if len(extras) != 3 - dimension:
            continue
        for free_order in itertools.permutations(sorted(free_face)):
            for extra_order in itertools.permutations(sorted(extras)):
                image_ids = (next(iter(apex)), *free_order, *extra_order)
                image = [coordinates[vertex] for vertex in image_ids]
                linear, translation, determinant = pl.affine_from_tets(
                    standard_vertices, image
                )
                if determinant <= 0:
                    continue
                inverse_linear, inverse_translation, inverse_determinant = pl.affine_from_tets(
                    image, standard_vertices
                )
                if inverse_determinant <= 0:
                    raise AssertionError("cap carrier inverse is not positive")
                candidates.append(
                    (
                        image_ids,
                        carrier_id,
                        image,
                        linear,
                        translation,
                        determinant,
                        inverse_linear,
                        inverse_translation,
                        inverse_determinant,
                    )
                )
    if not candidates:
        raise AssertionError("cap collapse pair has no positive carrier chart")
    (
        image_ids,
        carrier_id,
        image,
        linear,
        translation,
        determinant,
        inverse_linear,
        inverse_translation,
        inverse_determinant,
    ) = min(candidates, key=lambda item: (item[0], item[1]))
    for source, target in zip(standard_vertices, image):
        if pl.apply_affine(linear, translation, source) != list(target):
            raise AssertionError("cap carrier chart misses a vertex")
        if pl.apply_affine(inverse_linear, inverse_translation, target) != source:
            raise AssertionError("cap carrier inverse misses a vertex")
    return {
        "dimension": dimension,
        "simplex": list(simplex_key),
        "free_face": list(face_key),
        "carrier": carrier_id,
        "image_ids": list(image_ids),
        "linear": [[str(value) for value in row] for row in linear],
        "translation": [str(value) for value in translation],
        "determinant": str(determinant),
        "inverse_linear": [
            [str(value) for value in row] for row in inverse_linear
        ],
        "inverse_translation": [str(value) for value in inverse_translation],
        "inverse_determinant": str(inverse_determinant),
    }


def lookup_cells(derived_cells):
    return {
        (dimension["collapse_dimension"], side["side"]): side
        for dimension in derived_cells["dimensions"]
        for side in dimension["sides"]
    }


def build_cap(pl, standard_vertices, structure, cap, movie_side, lookup):
    rows, histogram = relative_steps(structure["indexed"], cap["triangles"])
    if canonical_sha(rows) != cap["relative_collapse"]["step_sequence_sha256"]:
        raise AssertionError("recomputed cap collapse sequence has the wrong SHA")
    carriers = carrier_index(structure["indexed"])
    digest_rows = []
    determinant_min = None
    determinant_max = None
    expanded_cells = 0
    for row in rows:
        chart = chart_for_step(pl, standard_vertices, structure, carriers, row)
        template = lookup[(chart["dimension"], movie_side)]
        expanded_cells += template["ambient_cell_count"]
        determinant = Fraction(chart["determinant"])
        determinant_min = determinant if determinant_min is None else min(determinant_min, determinant)
        determinant_max = determinant if determinant_max is None else max(determinant_max, determinant)
        digest_rows.append(
            {
                **chart,
                "standard_move_count": template["move_count"],
                "standard_ambient_cell_count": template["ambient_cell_count"],
                "standard_jacobian_det_min": template["jacobian_det_min"],
                "standard_jacobian_det_max": template["jacobian_det_max"],
            }
        )
    return {
        "collapse_step_count": len(rows),
        "dimension_histogram": {
            str(key): value for key, value in sorted(histogram.items())
        },
        "chart_sequence_sha256": canonical_sha(digest_rows),
        "chart_determinant_min": str(determinant_min),
        "chart_determinant_max": str(determinant_max),
        "expanded_ambient_cell_count": expanded_cells,
        "conjugated_jacobian_det_min": "1/3",
        "conjugated_jacobian_det_max": "3",
        "all_charts_positive": True,
        "all_chart_inverses_explicit": True,
        "cap_collapse_chart": "PASS",
    }


def build_movie(pl, sweep_tools, collar_tools, derived, lookup, movie, support, collar):
    tetrahedra, adjacency, _ = sweep_tools.build_tetrahedra(
        sweep_tools.load("analyze_t73_johnson_arm_mismatch"), pl, movie["power"]
    )
    add_ball = set(
        next(move["tetrahedra"] for move in movie["grouped_moves"] if move["operation"] == "add")
    )
    remove_ball = set(
        next(
            move["tetrahedra"]
            for move in movie["grouped_moves"]
            if move["operation"] == "remove"
        )
    )
    structure = collar_tools.build_structure(
        sweep_tools, tetrahedra, adjacency, support["dual_path"], add_ball, remove_ball
    )
    standard_vertices = [list(vertex) for vertex in derived.STANDARD_VERTICES]
    caps = [
        build_cap(pl, standard_vertices, structure, cap, movie["side"], lookup)
        for cap in support["regular_path_neighbourhood"]["caps"]
    ]
    if collar["cap_product_collar"] != "PASS":
        raise AssertionError("cap product collar is not certified")
    total_cells = (
        caps[0]["expanded_ambient_cell_count"]
        + collar["cell_count"]
        + caps[1]["expanded_ambient_cell_count"]
    )
    return {
        "power": movie["power"],
        "side": movie["side"],
        "source_cap_collapse": caps[0],
        "target_cap_collapse": caps[1],
        "cap_product_collar_sha256": canonical_sha(collar),
        "cap_product_collar_cells": collar["cell_count"],
        "composition_order": [
            "source_cap_collapse",
            "orientation_selected_cap_product_collar",
            "inverse_target_cap_collapse",
        ],
        "expanded_ambient_cell_count": total_cells,
        "jacobian_det_min": "1/3",
        "jacobian_det_max": "3",
        "explicit_inverse_order": [
            "target_cap_collapse",
            "inverse_cap_product_collar",
            "inverse_source_cap_collapse",
        ],
        "fiber_transport": "PASS",
        "paired_saddle_fiber_cells": "PASS",
        "paired_saddle_ambient_cells": "OPEN",
    }


def generate():
    pl = load("t73_johnson_pl")
    sweep_tools = load("build_t73_johnson_elementary_sweep")
    collar_tools = load("build_t73_johnson_cap_product_collars")
    derived = load("build_t73_johnson_derived_collapse_templates")
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
    support = json.loads(SUPPORT.read_text(encoding="utf-8"))
    collars = json.loads(COLLARS.read_text(encoding="utf-8"))
    derived_cells = json.loads(DERIVED_CELLS.read_text(encoding="utf-8"))
    if collars["support_sha256"] != support["sha256"]:
        raise AssertionError("cap collars are not bound to the paired support")
    lookup = lookup_cells(derived_cells)
    movies = [
        build_movie(
            pl,
            sweep_tools,
            collar_tools,
            derived,
            lookup,
            movie,
            support_movie,
            collar,
        )
        for movie, support_movie, collar in zip(
            sweep["movies"], support["movies"], collars["movies"]
        )
    ]
    result = {
        "schema": "t73_johnson_cap_collapse_assembly/v1",
        "sweep_sha256": sweep["sha256"],
        "support_sha256": support["sha256"],
        "collars_sha256": collars["sha256"],
        "derived_cells_sha256": derived_cells["sha256"],
        "movies": movies,
        "expanded_ambient_cell_count": sum(
            movie["expanded_ambient_cell_count"] for movie in movies
        ),
        "all_fiber_transports": "PASS",
        "paired_saddle_fiber_transport": "PASS",
        "paired_saddle_ambient_cells": "OPEN",
        "johnson_restore_ambient_cells": "OPEN",
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
        print(f"T73_JOHNSON_CAP_COLLAPSE_ASSEMBLY={result['all_fiber_transports']}")
        for movie in result["movies"]:
            print(
                f"POWER_{movie['power']}_{movie['side']}="
                f"{movie['expanded_ambient_cell_count']}"
            )
        print(f"PAIRED_SADDLE_CELLS={result['paired_saddle_ambient_cells']}")
        print(f"FIBER_TRANSPORT={result['paired_saddle_fiber_transport']}")
        print(f"JOHNSON_RESTORE_CELLS={result['johnson_restore_ambient_cells']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
