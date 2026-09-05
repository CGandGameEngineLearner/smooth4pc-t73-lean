#!/usr/bin/env python3
"""Build one quotient annulus containing every x-slide m1 parallel level."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from build_t73_t_hcs_cancellation_readiness import final_states

ROOT = Path(__file__).resolve().parents[1]
EXTERIOR = ROOT / "geometry/t73_t_hcs_framing_exteriorization.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
OUTPUT = ROOT / "geometry/t73_x_m1_parallel_foliation.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def expanded_normals(normals, exterior):
    replacements = {
        item["vertex_index"]: point(item["new_normal"])
        for item in exterior["components"]["m_1"]["normal_replacements"]
    }
    return [replacements.get(index, value) for index, value in enumerate(normals)]


def build() -> dict:
    exterior = json.loads(EXTERIOR.read_text(encoding="utf-8"))
    cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    local_movie = json.loads(LOCAL_MOVIE.read_text(encoding="utf-8"))
    base, original_normals, seams = final_states()["m_1"]
    unit_normals = expanded_normals(original_normals, exterior)
    width = Fraction(cancellation["slide_bands"][0]["band_width"])
    for index in range(2, 5):
        unit_normals[index] = (Fraction(0), width, Fraction(0), Fraction(0))
    levels = [record["target_parallel_coefficient"] for record in local_movie["bands"]]
    maximum = max(levels)
    outer = [
        tuple(value[axis] + maximum * normal[axis] for axis in range(4))
        for value, normal in zip(base, unit_normals)
    ]
    vertex_count = len(base)
    triangles = []
    for index in range(vertex_count - 1):
        triangles.extend([
            [index, index + 1, vertex_count + index + 1],
            [index, vertex_count + index + 1, vertex_count + index],
        ])
    seam_triangles = sorted(
        triangle_index
        for seam in seams
        for triangle_index in (2 * seam, 2 * seam + 1)
    )
    result = {
        "schema": "t73_x_m1_parallel_foliation/v1",
        "framing_exteriorization_sha256": exterior["sha256"],
        "x_cancellation_sha256": cancellation["sha256"],
        "x_local_movie_sha256": local_movie["sha256"],
        "base_vertices": [encode(value) for value in base],
        "unit_normal_field": [encode(value) for value in unit_normals],
        "outer_vertices": [encode(value) for value in outer],
        "triangles": triangles,
        "mapping_torus_seam_segment_indices": sorted(seams),
        "mapping_torus_seam_triangle_indices": seam_triangles,
        "parallel_levels": levels,
        "maximum_parallel_coefficient": maximum,
        "level_rule": "L_k(v_i)=base(v_i)+k*unit_normal(v_i)",
        "completion_status": "ALL_1513_M1_PARALLELS_IN_ONE_QUOTIENT_ANNULUS",
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
        raise AssertionError("m1 parallel foliation is stale")
    print("T73_X_M1_FOLIATION=ALL_1513_M1_PARALLELS_IN_ONE_QUOTIENT_ANNULUS")


if __name__ == "__main__":
    main()
