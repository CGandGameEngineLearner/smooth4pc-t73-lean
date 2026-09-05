#!/usr/bin/env python3
"""Verify the cubical x/m1 core-collar ejection map and final core domain."""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from build_t73_x_band_local_movie import initial_segment_state, update_segment_state
from verify_t73_x_band_local_movie import expand_band

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_collar_ejection_map.json"
BELTS = ROOT / "geometry/t73_belt_spheres.json"
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
HYBRID_MOVIE = ROOT / "geometry/t73_x_band_hybrid_movie.json"
STATE0 = ROOT / "geometry/t73_x_positive_belt_state0.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def determinant3(columns):
    first, second, third = columns
    return (
        first[0] * (second[1] * third[2] - second[2] * third[1])
        - second[0] * (first[1] * third[2] - first[2] * third[1])
        + third[0] * (first[1] * second[2] - first[2] * second[1])
    )


def tetrahedron_determinant(vertices, tetrahedron):
    origin = vertices[tetrahedron[0]][1:]
    columns = [
        tuple(vertices[index][axis + 1] - origin[axis] for axis in range(3))
        for index in tetrahedron[1:]
    ]
    return determinant3(columns)


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    local_movie = json.loads(LOCAL_MOVIE.read_text(encoding="utf-8"))
    hybrid_movie = json.loads(HYBRID_MOVIE.read_text(encoding="utf-8"))
    state0 = json.loads(STATE0.read_text(encoding="utf-8"))
    cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    if data["completion_status"] != "X_M1_CORE_COLLAR_EJECTION_CELL_MAP_CONSTRUCTED":
        raise AssertionError("x/m1 collar-map scope changed")
    if data["belt_spheres_sha256"] != belts["sha256"] or data["x_local_movie_sha256"] != local_movie["sha256"] or data["x_hybrid_movie_sha256"] != hybrid_movie["sha256"]:
        raise AssertionError("x/m1 collar map has stale sources")
    source = [point(value) for value in data["source_vertices"]]
    target = [point(value) for value in data["target_vertex_images"]]
    tetrahedra = data["tetrahedra"]
    if len(source) != 16 or len(tetrahedra) != 36:
        raise AssertionError("cubical collar has the wrong cell counts")
    ratios = []
    for tetrahedron in tetrahedra:
        first = tetrahedron_determinant(source, tetrahedron)
        second = tetrahedron_determinant(target, tetrahedron)
        if not first or not second or second / first <= 0:
            raise AssertionError("cubical collar contains a degenerate/reversing cell")
        ratios.append(second / first)
    face_counts = Counter(
        tuple(sorted(face))
        for tetrahedron in tetrahedra
        for face in combinations(tetrahedron, 3)
    )
    if set(face_counts.values()) - {1, 2}:
        raise AssertionError("cubical collar is not a tetrahedral 3-manifold")
    boundary = {face for face, count in face_counts.items() if count == 1}
    expected_boundary = {
        *[tuple(sorted(face)) for face in data["source_inner_boundary_triangles"]],
        *[tuple(sorted(face)) for face in data["source_outer_boundary_triangles"]],
    }
    if boundary != expected_boundary:
        raise AssertionError("cubical collar has the wrong two boundary spheres")

    arcs = {item["source_id"]: item for item in state0["arcs"]}
    segments = initial_segment_state(arcs)
    for band in cancellation["slide_bands"]:
        vertices, _, _, _, _, _, _, _, _, _ = expand_band(band)
        update_segment_state(segments, band, {"vertices": vertices}, arcs[band["source_id"]])
    remaining = {
        key: segment for key, segment in segments.items() if not key.startswith("m_1:C_i:")
    }
    if len(remaining) != 12104:
        raise AssertionError("wrong number of remaining local core segments")
    for segment_id, segment in remaining.items():
        if any(value[3] < 1 for value in segment):
            raise AssertionError(f"remaining segment {segment_id} enters transverse D3")
    return {
        "verdict": "PASS_X_M1_CORE_COLLAR_EJECTION_MAP",
        "vertices": len(source),
        "tetrahedra": len(tetrahedra),
        "boundary_triangles": len(boundary),
        "minimum_determinant_ratio": str(min(ratios)),
        "remaining_core_segments_in_domain": len(remaining),
        "cancelling_m1_segments_excluded": 2,
        "framed_neighborhood_status": "OPEN_SEPARATE_CHECK_REQUIRED",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
