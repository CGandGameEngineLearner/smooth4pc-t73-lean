#!/usr/bin/env python3
"""Build the two actual affine chart germs used by x-band 0."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from build_t73_t_hcs_cancellation_readiness import final_states

ROOT = Path(__file__).resolve().parents[1]
SURFACE = ROOT / "geometry/t73_x_band0_attachment_surface.json"
POST_CANCEL = ROOT / "geometry/t73_t_hcs_handle_pair_deletion.json"
EXTERIOR = ROOT / "geometry/t73_t_hcs_framing_exteriorization.json"
OUTPUT = ROOT / "geometry/t73_x_band0_chart_transitions.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def expanded_exterior_normals(component, original_normals, exterior):
    replacements = {
        item["vertex_index"]: point(item["new_normal"])
        for item in exterior["components"][component]["normal_replacements"]
    }
    return [
        replacements.get(index, normal)
        for index, normal in enumerate(original_normals)
    ]


def source_to_local(value):
    return (
        value[0] - 1076,
        value[1] - 160,
        value[2],
        Fraction(1),
    )


def target_to_local(value):
    return (-value[0], value[1], value[2] - 4, Fraction(1))


def source_vector_to_local(value):
    return value


def target_vector_to_local(value):
    return (-value[0], value[1], value[2], value[3])


def remove_x_tangent(value):
    return (Fraction(0), value[1], value[2], value[3])


def build() -> dict:
    surface = json.loads(SURFACE.read_text(encoding="utf-8"))
    post_cancel = json.loads(POST_CANCEL.read_text(encoding="utf-8"))
    exterior = json.loads(EXTERIOR.read_text(encoding="utf-8"))
    states = final_states()
    m2_points, m2_normals, _ = states["m_2"]
    m1_points, m1_normals, _ = states["m_1"]
    m1_normals = expanded_exterior_normals("m_1", m1_normals, exterior)

    source_range = surface["source_arc_current_state_vertex_range"]
    source_global = m2_points[source_range[0] : source_range[1] + 1]
    source_local = [source_to_local(value) for value in source_global]
    expected_local = [point(value) for value in surface["source_arc_local"]]
    if source_local != expected_local:
        raise AssertionError("source affine germ does not recover the Johnson x-arc")

    target_range = [2, 4]
    target_global = m1_points[target_range[0] : target_range[1] + 1]
    target_local = [target_to_local(value) for value in target_global]
    expected_target = [
        (Fraction(1), Fraction(0), Fraction(0), Fraction(1)),
        (Fraction(2), Fraction(0), Fraction(0), Fraction(1)),
        (Fraction(3), Fraction(0), Fraction(0), Fraction(1)),
    ]
    if target_local != expected_target:
        raise AssertionError("target reflection germ does not recover the m1 x-arc")

    source_actual = source_vector_to_local(m2_normals[source_range[0] + 1])
    target_actual = target_vector_to_local(m1_normals[target_range[0] + 1])
    source_quotient = remove_x_tangent(source_actual)
    target_quotient = remove_x_tangent(target_actual)
    chosen_target = point(surface["target_parallel_normal"])
    if source_quotient != point(surface["source_normal_mod_x_tangent"]):
        raise AssertionError("source chart derivative lost the saved boundary framing")
    if target_quotient != source_quotient:
        raise AssertionError("source and reflected target framings differ in the normal quotient")
    if chosen_target[1] != target_quotient[1] or any(
        chosen_target[axis] for axis in (0, 2, 3)
    ):
        raise AssertionError("chosen m1 parallel is not the y representative of its framing class")

    local_target_interval = [
        point(value) for value in surface["target_parallel_m1_interval_local"]
    ]
    global_target_interval = [
        (-value[0], value[1], value[2] + 4, Fraction(0))
        for value in local_target_interval
    ]
    result = {
        "schema": "t73_x_band0_chart_transitions/v1",
        "surface_sha256": surface["sha256"],
        "post_t_hcs_deletion_sha256": post_cancel["sha256"],
        "framing_exteriorization_sha256": exterior["sha256"],
        "source_germ": {
            "component": "m_2",
            "global_vertex_range": source_range,
            "domain_slice": "u=1",
            "formula": "(x,y,z,1)->(x-1076,y-160,z,nu=1)",
            "linear_part": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]],
            "global_arc": [encode(value) for value in source_global],
            "local_arc": [encode(value) for value in source_local],
        },
        "target_germ": {
            "component": "m_1",
            "global_vertex_range": target_range,
            "domain_slice": "u=0",
            "formula": "(x,y,z,0)->(-x,y,z-4,nu=1)",
            "linear_part": [[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]],
            "global_arc": [encode(value) for value in target_global],
            "local_arc": [encode(value) for value in target_local],
            "global_parallel_interval": [
                encode(value) for value in global_target_interval
            ],
        },
        "framing_transport": {
            "source_actual_local_vector": encode(source_actual),
            "target_actual_reflected_local_vector": encode(target_actual),
            "common_normal_quotient_vector": encode(source_quotient),
            "chosen_target_parallel_vector": encode(chosen_target),
            "quotient_homotopy": "(0,w,(1-t)w,0), t in [0,1]",
            "zero_section_avoided": True,
        },
        "completion_status": "X_BAND0_SOURCE_TARGET_CHART_GERMS_AND_FRAMING_BOUND",
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
        raise AssertionError("x-band 0 chart transitions are stale")
    print("T73_X_BAND0_CHARTS=X_BAND0_SOURCE_TARGET_CHART_GERMS_AND_FRAMING_BOUND")


if __name__ == "__main__":
    main()
