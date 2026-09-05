#!/usr/bin/env python3
"""Build the standard x/m1 cancelling pair and five-component post-link state."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BELTS = ROOT / "geometry/t73_belt_spheres.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
HYBRID_MOVIE = ROOT / "geometry/t73_x_band_hybrid_movie.json"
FRAMING = ROOT / "geometry/t73_x_m1_framing_exteriorization.json"
COLLAR = ROOT / "geometry/t73_x_m1_collar_ejection_map.json"
CHARTS = ROOT / "geometry/t73_x_band0_chart_transitions.json"
OUTPUT = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def monotone_paths(first_dimension, second_dimension):
    steps = [0] * first_dimension + [1] * second_dimension
    for permutation in sorted(set(itertools.permutations(steps))):
        first = second = 0
        path = [(first, second)]
        for step in permutation:
            if step == 0:
                first += 1
            else:
                second += 1
            path.append((first, second))
        yield path


def product_simplices(first_dimension, second_dimension, vertex):
    return [
        [vertex(first, second) for first, second in path]
        for path in monotone_paths(first_dimension, second_dimension)
    ]


def standard_pair():
    h1_vertices = {(first, second): 4 * first + second for first in range(2) for second in range(4)}
    h2_vertices = {}
    next_vertex = 8
    for first in range(3):
        for second in range(3):
            if first < 2:
                h2_vertices[first, second] = h1_vertices[first, second + 1]
            else:
                h2_vertices[first, second] = next_vertex
                next_vertex += 1
    h1 = product_simplices(1, 3, lambda first, second: h1_vertices[first, second])
    h2 = product_simplices(2, 2, lambda first, second: h2_vertices[first, second])
    interface = product_simplices(1, 2, lambda first, second: h1_vertices[first, second + 1])
    return h1, h2, interface, next_vertex


def build() -> dict:
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    hybrid = json.loads(HYBRID_MOVIE.read_text(encoding="utf-8"))
    framing = json.loads(FRAMING.read_text(encoding="utf-8"))
    collar = json.loads(COLLAR.read_text(encoding="utf-8"))
    charts = json.loads(CHARTS.read_text(encoding="utf-8"))
    h1, h2, interface, vertex_count = standard_pair()
    belt_vertices = belts["x_handle"]["belt_sphere"]["vertices"]
    square_indices = [1, 3, 7, 5]
    square = [belt_vertices[index] for index in square_indices]
    center = ["2", "0", "0", "1"]
    actual_refinement_vertices = [*square, center]
    standard_refinement_vertices = [
        ["0", "0"],
        ["1", "0"],
        ["0", "1"],
        ["0", "1/2"],
        ["1/3", "1/3"],
    ]
    refinement_triangles = [[4, 0, 1], [4, 1, 2], [4, 2, 3], [4, 3, 0]]
    remaining_components = {
        component: {
            "hybrid_state_sha256": hybrid["final_component_states"][component]["state_sha256"],
            "replacement_count": hybrid["final_component_states"][component]["replacement_count"],
            "image_under_collar_map": f"components/{component}",
            "uniform_outward_framing_ref": "geometry/t73_x_m1_framing_exteriorization.json",
        }
        for component in ("m_2", "m_3", "r_xy", "r_zx")
    }
    remaining_components["r_yz"] = {
        "source_ref": "geometry/t73_actual_ar_link.json#/components/r_yz",
        "replacement_count": 0,
        "image_under_collar_map": "components/r_yz",
        "uniform_outward_framing_ref": "geometry/t73_x_m1_framing_exteriorization.json",
    }
    result = {
        "schema": "t73_x_m1_handle_pair_deletion/v1",
        "belt_spheres_sha256": belts["sha256"],
        "x_cancellation_sha256": cancellation["sha256"],
        "x_hybrid_movie_sha256": hybrid["sha256"],
        "x_framing_exteriorization_sha256": framing["sha256"],
        "x_collar_ejection_map_sha256": collar["sha256"],
        "x_band0_chart_transitions_sha256": charts["sha256"],
        "standard_pair": {
            "h1_model": "Delta1 x Delta3",
            "h2_model": "Delta2 x Delta2",
            "h1_four_simplices": h1,
            "h2_four_simplices": h2,
            "glued_attaching_patch_tetrahedra": interface,
            "union_four_simplices": [*h1, *h2],
            "glued_vertex_count": vertex_count,
        },
        "actual_cell_binding": {
            "positive_nu_square_vertex_indices": square_indices,
            "actual_refinement_vertices": actual_refinement_vertices,
            "standard_face_refinement_vertices": standard_refinement_vertices,
            "refinement_triangles": refinement_triangles,
            "actual_m1_crossing_arc": [
                [*point, "1"] for point in cancellation["attaching_polyline"]
            ],
            "actual_belt_intersection": center,
            "standard_crossing_arc": [
                ["0", "1/3", "1/3"],
                ["1/2", "1/3", "1/3"],
                ["1", "1/3", "1/3"],
            ],
            "actual_local_framing_vector": charts["framing_transport"][
                "common_normal_quotient_vector"
            ],
            "relative_twist": cancellation["relative_twist"],
        },
        "deletion": {
            "deleted_handles": ["x", "m_1"],
            "remaining_one_handles": ["y", "z"],
            "remaining_components": remaining_components,
            "post_cancel_component_count": 5,
            "consumer": "unified five-component Kirby presentation and kappa_AR",
        },
        "completion_status": "X_M1_STANDARD_PAIR_AND_ACTUAL_CUBICAL_BINDING_CONSTRUCTED",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("x/m1 handle-pair deletion data is stale")
    print("T73_X_M1_DELETION=X_M1_STANDARD_PAIR_AND_ACTUAL_CUBICAL_BINDING_CONSTRUCTED")


if __name__ == "__main__":
    main()
