#!/usr/bin/env python3
"""Build the standard simplicial t/h_CS cancelling pair and post-link state."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANCELLATION = ROOT / "geometry/t73_cancel_t_hcs.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
BELTS = ROOT / "geometry/t73_belt_spheres.json"
MOVIE = ROOT / "geometry/t73_t_band_sequential_movie.json"
FRAMING = ROOT / "geometry/t73_t_hcs_framing_exteriorization.json"
COLLAR = ROOT / "geometry/t73_t_hcs_collar_ejection_map.json"
OUTPUT = ROOT / "geometry/t73_t_hcs_handle_pair_deletion.json"


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


def build() -> dict:
    cancellation = json.loads(CANCELLATION.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    movie = json.loads(MOVIE.read_text(encoding="utf-8"))
    framing = json.loads(FRAMING.read_text(encoding="utf-8"))
    collar = json.loads(COLLAR.read_text(encoding="utf-8"))

    h1_vertices = {(first, second): 4 * first + second for first in range(2) for second in range(4)}
    next_vertex = 8
    h2_vertices = {}
    for first in range(3):
        for second in range(3):
            if first < 2:
                h2_vertices[first, second] = h1_vertices[first, second + 1]
            else:
                h2_vertices[first, second] = next_vertex
                next_vertex += 1
    h1_simplices = product_simplices(1, 3, lambda first, second: h1_vertices[first, second])
    h2_simplices = product_simplices(2, 2, lambda first, second: h2_vertices[first, second])
    interface = product_simplices(1, 2, lambda first, second: h1_vertices[first, second + 1])

    belt = belts["t_handle"]["belt_sphere"]
    actual_face = [0, 2, 4]
    actual_vertices = [
        tuple(Fraction(value) for value in belt["vertices"][index])
        for index in actual_face
    ]
    actual_barycenter = tuple(
        sum(vertex[axis] for vertex in actual_vertices) / 3 for axis in range(4)
    )
    attaching = [
        tuple(Fraction(value) for value in point)
        for point in cancellation["attaching_polyline"]
    ]
    if attaching[0][:3] != actual_barycenter[:3] or attaching[1][:3] != actual_barycenter[:3]:
        raise AssertionError("h_CS does not cross the selected positive belt face at its barycenter")

    remaining_components = {}
    for component in ("m_1", "m_2", "m_3"):
        remaining_components[component] = {
            "state6_core_sha256": movie["final_component_manifest"][component]["final_polyline_sha256"],
            "exteriorized_normal_field_sha256": framing["components"][component]["exteriorized_normal_field_sha256"],
            "exteriorized_push_off_sha256": framing["components"][component]["exteriorized_push_off_sha256"],
            "image_under_collar_map": f"components/{component}",
        }
    for component in ("r_xy", "r_yz", "r_zx"):
        remaining_components[component] = {
            "source_ref": f"geometry/t73_actual_ar_link.json#/components/{component}",
            "image_under_collar_map": f"components/{component}",
        }

    result = {
        "schema": "t73_t_hcs_handle_pair_deletion/v1",
        "legacy_cancellation_sha256": cancellation["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "belt_spheres_sha256": belts["sha256"],
        "sequential_movie_sha256": movie["sha256"],
        "framing_exteriorization_sha256": framing["sha256"],
        "collar_ejection_map_sha256": collar["sha256"],
        "standard_pair": {
            "h1_model": "Delta1 x Delta3",
            "h2_model": "Delta2 x Delta2",
            "h1_four_simplices": h1_simplices,
            "h2_four_simplices": h2_simplices,
            "glued_attaching_patch_tetrahedra": interface,
            "glued_vertex_count": next_vertex,
            "union_four_simplices": [*h1_simplices, *h2_simplices],
            "h2_attaching_patch": "edge [0,1] of first Delta2 times second Delta2",
            "h1_lateral_patch": "Delta1 times face [1,2,3] of Delta3",
        },
        "actual_cell_binding": {
            "actual_belt_face_vertex_indices": actual_face,
            "actual_belt_face_vertices": [[str(value) for value in vertex] for vertex in actual_vertices],
            "actual_hcs_belt_intersection": [
                str(value) for value in (*actual_barycenter[:3], Fraction(1, 2))
            ],
            "actual_hcs_attaching_endpoints": [
                [str(value) for value in point] for point in attaching
            ],
            "standard_h1_face_vertices": [1, 2, 3],
            "standard_crossing_arc": {
                "source": ["0", "1/3", "1/3", "1/3"],
                "belt_intersection": ["1/2", "1/3", "1/3", "1/3"],
                "target": ["1", "1/3", "1/3", "1/3"],
            },
            "relative_twist": cancellation["relative_twist"],
            "actual_hcs_framing_offset": ar_link["components"]["h_CS"]["framing_annulus"]["offset"],
        },
        "deletion": {
            "deleted_handles": ["t", "h_CS"],
            "deleted_standard_pair_is_union_4_ball": True,
            "boundary_carrying_map": "geometry/t73_t_hcs_collar_ejection_map.json",
            "remaining_one_handles": ["x", "y", "z"],
            "remaining_components": remaining_components,
            "consumer": "1513-step x-m1 sequential movie",
        },
        "completion_status": "T_HCS_STANDARD_PAIR_AND_ACTUAL_CELL_BINDING_CONSTRUCTED",
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
        raise AssertionError("t-h_CS handle-pair deletion data is stale")
    print(f"T73_T_HCS_DELETION={result['completion_status']}")


if __name__ == "__main__":
    main()
