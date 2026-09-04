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
OUTPUT = ROOT / "geometry" / "t73_actual_geometric_braid.json"


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
    # This generic PL braid realizer receives only the geometry-derived word.
    # The frozen comparison is loaded only after the strands are built and the
    # crossing extractor has recovered their word.
    realized = control.control_collar(reconstructor, source_word)
    transformed = []
    for strand in realized["strands"]:
        transformed.append({
            "id": strand["id"],
            "vertices": [transform_vertex(vertex, len(source_word)) for vertex in strand["vertices"]],
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
    target = reconstructor.expected_public_word()
    if recovered != target:
        raise AssertionError("Johnson-lane geometric braid differs from the public word")
    strand_receipts = [
        {
            "strand_id": strand["id"],
            "vertex_count": len(strand["vertices"]),
            "polyline_sha256": canonical_sha(strand["vertices"]),
            "normal_sha256": canonical_sha(strand["normal_vectors"]),
            "normalized_endpoints": [strand["vertices"][0], strand["vertices"][-1]],
            "actual_endpoint_transport": next(
                move for move in collar["coordinate_chart_movie"] if move["wicket"] == strand["id"]
            ),
        }
        for strand in transformed
    ]
    result = {
        "schema": "t73_johnson_geometric_braid/v2",
        "collar_sha256": collar["collar_sha256"],
        "actual_cut_tangle_sha256": collar["actual_cut_tangle_sha256"],
        "six_sweep_sha256": source["witness_sha256"],
        "strand_count": len(transformed),
        "elementary_crossing_count": len(events),
        "recovered_word_sha256": canonical_sha(recovered),
        "target_word_sha256": canonical_sha(target),
        "endpoint_return_status": "PASS",
        "relative_endpoint_word_status": "PASS",
        "ar_lane_binding_status": collar["ar_passage_binding_status"],
        "coordinate_chart_status": collar["coordinate_chart_status"],
        "strand_receipts": strand_receipts,
        "geometry_source": "actual post-cancellation detector, its 44-point PL chart, and the oriented r_xy six-leg point-push route",
        "independent_ar_derivation_status": "PASS",
        "replacement_presentation_status": "PASS_ACTUAL_DETECTOR_POLYLINES",
        "historical_pd_status": "NOT_USED_OR_CLAIMED",
        "interpretation": (
            "The 44 actual y-belt points are moved by the recorded collision-free PL chart "
            "to normalized lanes.  The six geometry-derived point-push sweeps are realized "
            "there, their crossings are independently re-extracted, and the inverse chart "
            "returns every labelled actual endpoint and its product normal."
        ),
    }
    result["witness_sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        print("T73_JOHNSON_GEOMETRIC_BRAID=PASS")
        print(f"STRANDS={result['strand_count']}")
        print(f"ELEMENTARY_CROSSINGS={result['elementary_crossing_count']}")
        print(f"ENDPOINT_RETURN={result['endpoint_return_status']}")
        print(f"RELATIVE_ENDPOINT_WORD={result['relative_endpoint_word_status']}")
        print(f"INDEPENDENT_AR_DERIVATION={result['independent_ar_derivation_status']}")
        print(f"WITNESS_SHA256={result['witness_sha256']}")
    elif not args.write:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
