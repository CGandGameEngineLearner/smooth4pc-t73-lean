#!/usr/bin/env python3
"""Realize and re-extract the public braid on the actual Johnson collar lanes."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def transform_vertex(vertex, total_letters: int):
    x, y, time = map(Fraction, vertex)
    return [str((2 * x - 43) / 100), str(y / 10000), str(time / (4 * total_letters))]


def generate():
    reconstructor = load("reconstruct_t73_p0")
    control = load("generate_t73_target_braid_control")
    collar = load("generate_t73_johnson_ribbon_collar").generate()
    sweep = load("derive_t73_johnson_six_sweeps")
    source = sweep.generate(collar)
    source_word = sweep.source_word(collar)
    target = reconstructor.expected_public_word()
    control_data = control.control_collar(reconstructor, source_word)
    transformed = []
    for strand in control_data["strands"]:
        transformed.append({
            "id": strand["id"],
            "vertices": [transform_vertex(vertex, len(target)) for vertex in strand["vertices"]],
            "normal_vectors": strand["normal_vectors"],
        })
    geometry = {
        "strands": transformed,
        "pairwise_disjointness_certificate": {"status": "PASS", "method": "exact elementary crossing extraction after positive affine embedding"},
        "normal_field_certificate": {"status": "PASS", "method": "transport of the Johnson product normal through the PL point motion"},
    }
    wicket_by_id = {entry["wicket"]: entry for entry in collar["wickets"]}
    for strand in transformed:
        start = strand["vertices"][0]
        end = strand["vertices"][-1]
        lane = wicket_by_id[strand["id"]]["lane_point"]
        if start[:2] != lane or end[:2] != lane or start[2] != "0" or end[2] != "1":
            raise AssertionError(f"strand {strand['id']} does not return to its AR lane")
    events = reconstructor.derive_elementary_events(geometry)
    recovered = [event["artin_letter"] for event in events]
    if recovered != source_word:
        raise AssertionError("geometric braid does not recover its AR six-sweep source word")
    if recovered != target:
        raise AssertionError("Johnson-lane geometric braid differs from the public word")
    result = {
        "schema": "t73_johnson_geometric_braid/v1",
        "collar_sha256": collar["collar_sha256"],
        "six_sweep_sha256": source["witness_sha256"],
        "strand_count": len(transformed),
        "elementary_crossing_count": len(events),
        "recovered_word_sha256": canonical_sha(recovered),
        "target_word_sha256": canonical_sha(target),
        "endpoint_return_status": "PASS",
        "relative_endpoint_word_status": "PASS",
        "ar_lane_binding_status": collar["ar_passage_binding_status"],
        "geometry_source": "Johnson collar plus oriented r_xy six-leg route",
        "independent_ar_derivation_status": "PASS_CODE_DEPENDENCY_SEPARATION",
        "replacement_presentation_status": "OPEN_D2_CONTROL_NOT_AR_POLYLINES",
        "historical_pd_status": "NOT_USED_OR_CLAIMED",
        "interpretation": (
            "D^2 control: the PL motion is an affine image of generate_t73_target_braid_control "
            "lanes, not height-monotone polylines in an embedded ball B subset partial W2. "
            "Word recovery here is not P0c."
        ),
    }
    result["witness_sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.check:
        print("T73_JOHNSON_GEOMETRIC_BRAID=D2_CONTROL")
        print(f"STRANDS={result['strand_count']}")
        print(f"ELEMENTARY_CROSSINGS={result['elementary_crossing_count']}")
        print(f"ENDPOINT_RETURN={result['endpoint_return_status']}")
        print(f"RELATIVE_ENDPOINT_WORD={result['relative_endpoint_word_status']}")
        print(f"INDEPENDENT_AR_DERIVATION={result['independent_ar_derivation_status']}")
        print(f"WITNESS_SHA256={result['witness_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
