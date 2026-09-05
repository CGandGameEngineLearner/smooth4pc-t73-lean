#!/usr/bin/env python3
"""Verify the uniform outward framing of the final x-local link."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from build_t73_x_band_local_movie import initial_segment_state, update_segment_state
from verify_t73_x_band_local_movie import expand_band, homotopy_hits_zero

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_framing_exteriorization.json"
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
STATE0 = ROOT / "geometry/t73_x_positive_belt_state0.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    local_movie = json.loads(LOCAL_MOVIE.read_text(encoding="utf-8"))
    state0 = json.loads(STATE0.read_text(encoding="utf-8"))
    cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    if data["completion_status"] != "X_FINAL_LINK_UNIFORM_OUTWARD_FRAMING_CONSTRUCTED":
        raise AssertionError("x/m1 framing-exteriorization scope changed")
    if data["x_local_movie_sha256"] != local_movie["sha256"] or data["x_cancellation_sha256"] != cancellation["sha256"]:
        raise AssertionError("x/m1 framing exteriorization has stale sources")
    arcs = {item["source_id"]: item for item in state0["arcs"]}
    segments = initial_segment_state(arcs)
    framing_vectors = set()
    maximum_nu = Fraction(1)
    for band in cancellation["slide_bands"]:
        vertices, _, normals, _, _, source_normal, target_normal, _, _, _ = expand_band(band)
        update_segment_state(segments, band, {"vertices": vertices}, arcs[band["source_id"]])
        framing_vectors.update(normals)
        framing_vectors.add(source_normal)
        framing_vectors.add(target_normal)
        maximum_nu = max(maximum_nu, *(value[3] for value in vertices))
    remaining = {
        key: segment for key, segment in segments.items() if not key.startswith("m_1:C_i:")
    }
    push_vector = point(data["uniform_push_vector"])
    if maximum_nu != Fraction(data["maximum_core_nu"]):
        raise AssertionError("saved maximum x-collar height changed")
    if any(homotopy_hits_zero(vector, push_vector) for vector in framing_vectors):
        raise AssertionError("a local framing vector cannot homotope to the outward push")
    if any(not (vector[1] or vector[2]) for vector in framing_vectors):
        raise AssertionError("a local framing vector could be opposite the nu push")
    pure_nu_segments = 0
    for segment in remaining.values():
        direction = tuple(segment[1][axis] - segment[0][axis] for axis in range(4))
        if not any(direction[axis] for axis in range(3)):
            pure_nu_segments += 1
    if pure_nu_segments:
        raise AssertionError("uniform nu push is tangent to a remaining core segment")
    minimum_push_nu = min(
        value[3] + push_vector[3]
        for segment in remaining.values()
        for value in segment
    )
    if minimum_push_nu <= maximum_nu:
        raise AssertionError("uniform framed push does not clear the full core link")
    return {
        "verdict": "PASS_X_FINAL_LINK_UNIFORM_OUTWARD_FRAMING",
        "remaining_core_segments": len(remaining),
        "framing_vector_types": len(framing_vectors),
        "pure_nu_core_segments": pure_nu_segments,
        "maximum_core_nu": str(maximum_nu),
        "minimum_push_nu": str(minimum_push_nu),
        "strict_nu_separation": str(minimum_push_nu - maximum_nu),
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
