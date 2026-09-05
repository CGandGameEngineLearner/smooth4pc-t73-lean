#!/usr/bin/env python3
"""Independently verify the two affine x-band 0 chart germs."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from build_t73_t_hcs_cancellation_readiness import final_states

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_band0_chart_transitions.json"
SURFACE = ROOT / "geometry/t73_x_band0_attachment_surface.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def affine(matrix, translation, value):
    return tuple(
        sum(Fraction(entry) * coordinate for entry, coordinate in zip(row, value))
        + translation[index]
        for index, row in enumerate(matrix)
    )


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    surface = json.loads(SURFACE.read_text(encoding="utf-8"))
    if data["completion_status"] != "X_BAND0_SOURCE_TARGET_CHART_GERMS_AND_FRAMING_BOUND":
        raise AssertionError("x-band chart-germ scope changed")
    if data["surface_sha256"] != surface["sha256"]:
        raise AssertionError("x-band chart germs are stale")
    states = final_states()
    source = data["source_germ"]
    target = data["target_germ"]
    source_global = [point(value) for value in source["global_arc"]]
    target_global = [point(value) for value in target["global_arc"]]
    source_start, source_end = source["global_vertex_range"]
    target_start, target_end = target["global_vertex_range"]
    if source_global != states["m_2"][0][source_start : source_end + 1]:
        raise AssertionError("source germ is not on post-cancel m2")
    if target_global != states["m_1"][0][target_start : target_end + 1]:
        raise AssertionError("target germ is not on post-cancel m1")
    source_matrix = source["linear_part"]
    target_matrix = target["linear_part"]
    source_translation = (Fraction(-1076), Fraction(-160), Fraction(0), Fraction(1))
    target_translation = (Fraction(0), Fraction(0), Fraction(-4), Fraction(1))
    if [affine(source_matrix, source_translation, value) for value in source_global] != [
        point(value) for value in source["local_arc"]
    ]:
        raise AssertionError("source affine formula changed")
    if [affine(target_matrix, target_translation, value) for value in target_global] != [
        point(value) for value in target["local_arc"]
    ]:
        raise AssertionError("target reflection formula changed")
    framing = data["framing_transport"]
    common = point(framing["common_normal_quotient_vector"])
    chosen = point(framing["chosen_target_parallel_vector"])
    if common[0] or common[3] or not common[1] or not common[2]:
        raise AssertionError("common boundary normal is not transverse to the x arc")
    if chosen != (Fraction(0), common[1], Fraction(0), Fraction(0)):
        raise AssertionError("chosen target representative changed framing class")
    for numerator in range(17):
        parameter = Fraction(numerator, 16)
        value = (
            Fraction(0),
            common[1],
            (1 - parameter) * common[2],
            Fraction(0),
        )
        if not any(value):
            raise AssertionError("framing quotient homotopy meets zero")
    return {
        "verdict": "PASS_X_BAND0_ACTUAL_CHART_GERMS_AND_FRAMING_TRANSPORT",
        "source_global_range": [source_start, source_end],
        "target_global_range": [target_start, target_end],
        "source_translation": [-1076, -160, 0],
        "target_reflection": "x_local=-x_global",
        "framing_homotopy_nonzero": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
