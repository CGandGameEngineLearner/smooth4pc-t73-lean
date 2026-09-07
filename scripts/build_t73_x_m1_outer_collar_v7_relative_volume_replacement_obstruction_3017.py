#!/usr/bin/env python3
"""Save the first exact replacement-volume collision for relative movie 3017."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_t73_x_m1_outer_collar_v7_replacement_ribbon_candidate_matrix as replacement_module
from t73_exact_simplex import tetrahedron_intersection_witness

ROOT = Path(__file__).resolve().parents[1]
VOLUME = ROOT / "geometry/t73_x_m1_outer_collar_v7_relative_ribbon_volume_3017.json"
OUTPUT = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_relative_volume_replacement_obstruction_3017.json"
)
TRANSITION = 11
MOVING_TETRAHEDRON = 26
REPLACEMENT_RECTANGLE = 67225
STATIC_TETRAHEDRON = 5
PRISM = ((0, 1, 2, 5), (0, 1, 4, 5), (0, 3, 4, 5))


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def static_tetrahedron(rectangle, local):
    triangle = rectangle["triangles"][local // 3]
    vertices = [(*value, Fraction(0)) for value in triangle] + [
        (*value, Fraction(1)) for value in triangle
    ]
    return tuple(vertices[index] for index in PRISM[local % 3])


def build():
    volume = json.loads(VOLUME.read_text())
    replacements_receipt = json.loads(replacement_module.REPLACEMENTS.read_text())
    replacement_verify = json.loads(replacement_module.REPLACEMENT_VERIFY.read_text())
    if (
        replacement_verify["construction_receipt_sha256"]
        != replacements_receipt["sha256"]
        or not replacement_verify["full_result"]["globally_embedded_complete_framing"]
        or volume["external_ribbon_volume_clearance_status"] != "OPEN"
    ):
        raise AssertionError("replacement obstruction inputs are stale or overclaimed")
    replacements = replacement_module.load_replacements(replacements_receipt)
    rectangle = replacements[REPLACEMENT_RECTANGLE]
    transition = volume["transitions"][TRANSITION]
    start, end = (Fraction(value) for value in transition["global_time_interval"])
    vertices = [point(value) for value in transition["spacetime_vertices"]]
    normalized = [
        (*value[:3], (value[3] - start) / (end - start)) for value in vertices
    ]
    moving_ids = transition["tetrahedra"][MOVING_TETRAHEDRON]
    moving = tuple(normalized[index] for index in moving_ids)
    static = static_tetrahedron(rectangle, STATIC_TETRAHEDRON)
    if set(moving) & set(static):
        raise AssertionError("replacement obstruction tetrahedra are incident")
    witness = tetrahedron_intersection_witness(moving, static)
    if witness is None:
        raise AssertionError("replacement volume collision disappeared")
    result = {
        "schema": "t73_x_m1_outer_collar_v7_relative_volume_replacement_obstruction/v1",
        "relative_ribbon_volume_sha256": volume["sha256"],
        "replacement_framing_receipt_sha256": replacements_receipt["sha256"],
        "replacement_framing_verification_sha256": replacement_verify["sha256"],
        "interface_index": 3017,
        "transition_index": TRANSITION,
        "moving_tetrahedron_index": MOVING_TETRAHEDRON,
        "moving_tetrahedron_vertex_indices": moving_ids,
        "replacement_rectangle_index": REPLACEMENT_RECTANGLE,
        "replacement_band": rectangle["band"],
        "replacement_segment": rectangle["segment"],
        "replacement_piece": rectangle["piece"],
        "replacement_system": rectangle["system"],
        "static_tetrahedron_index": STATIC_TETRAHEDRON,
        "shared_vertex_count": 0,
        "affine_rank": witness["affine_rank"],
        "active_constraints": list(witness["active_constraints"]),
        "moving_barycentric_coordinates": [
            str(value) for value in witness["first_barycentric"]
        ],
        "static_barycentric_coordinates": [
            str(value) for value in witness["second_barycentric"]
        ],
        "intersection_point": [str(value) for value in witness["point"]],
        "retained_external_volume_status": "PROBE_PASS_592_EXACT_CANDIDATES_NOT_RECEIPTED",
        "replacement_external_volume_status": "CANDIDATE_REFUTED",
        "relative_framed_one_skeleton_status": "RETAINED",
        "relative_ribbon_volume_self_status": "RETAINED",
        "required_repair": "CHANGE_TRANSITION_11_VOLUME_AWARE_NORMAL_MODE_OR_ADD_REPLACEMENT_AVOIDING_MIDPOINT",
        "verdict": "REFUTED_X_M1_OUTER_COLLAR_V7_RELATIVE_VOLUME_REPLACEMENT_3017",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("relative replacement obstruction 3017 is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "transition": result["transition_index"],
                "moving": result["moving_tetrahedron_index"],
                "replacement": result["replacement_rectangle_index"],
                "band": result["replacement_band"],
                "segment": result["replacement_segment"],
                "rank": result["affine_rank"],
                "repair": result["required_repair"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
