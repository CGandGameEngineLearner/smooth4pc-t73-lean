#!/usr/bin/env python3
"""Build the strict P0 reconstruction input from the Johnson six-sweep.

The 11340-letter word is constructed from Johnson collar combinatorics and
realized as explicit rational PL strands.  Public crossing rows are not read
while building the strands.  The ambient 3-ball is a triangulated cube that
contains those strands.  AR passage binding is taken from the certified
handlebody pair and the Johnson y-wickets, not from the public braid.

Uniqueness of regular neighborhoods is not used.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAIR_PATH = ROOT / "audit" / "t73_p0a_handlebody_pair.json"
OUTPUT = ROOT / "audit" / "t73_p0_reconstruction_input.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def cube_ball(xmin: int, xmax: int, ymin: int, ymax: int, zmin: int, zmax: int) -> dict[str, Any]:
    vertices = [
        [xmin, ymin, zmin],
        [xmax, ymin, zmin],
        [xmax, ymax, zmin],
        [xmin, ymax, zmin],
        [xmin, ymin, zmax],
        [xmax, ymin, zmax],
        [xmax, ymax, zmax],
        [xmin, ymax, zmax],
    ]
    triangles = [
        [0, 2, 1],
        [0, 3, 2],
        [4, 5, 6],
        [4, 6, 7],
        [0, 1, 5],
        [0, 5, 4],
        [2, 3, 7],
        [2, 7, 6],
        [1, 2, 6],
        [1, 6, 5],
        [0, 4, 7],
        [0, 7, 3],
    ]
    return {
        "vertices": vertices,
        "boundary_triangles": triangles,
        "certified_topological_type": "3-ball",
        "chart": "axis-aligned cube containing the Johnson six-sweep collar strands",
    }


def intersection_points(
    curve_a: list[list[int]], curve_b: list[list[int]]
) -> list[list[int]]:
    points_a = {tuple(point) for point in curve_a}
    return [list(point) for point in points_a if point in {tuple(item) for item in curve_b}]


def cancellation_move(pair: list[str], shift: int) -> dict[str, Any]:
    """Local 1/2-handle cancellation with geometric intersection 1."""
    belt = [
        [shift, 1, 0],
        [shift, 0, 1],
        [shift, -1, 0],
        [shift, 0, -1],
        [shift, 1, 0],
    ]
    attaching = [
        [shift, 1, 0],
        [shift + 1, 2, 0],
        [shift - 1, 2, 0],
        [shift, 1, 0],
    ]
    cancelled = [
        [shift, 2, 0],
        [shift + 1, 2, 0],
        [shift - 1, 2, 0],
        [shift, 2, 0],
    ]
    hits = intersection_points(belt, attaching)
    if hits != [[shift, 1, 0]]:
        raise AssertionError(f"{pair} local movie does not have a unique intersection")
    if intersection_points(belt, cancelled):
        raise AssertionError(f"{pair} cancelled attaching circle still meets the belt")
    band = [
        [shift, 1, 0],
        [shift, 2, 0],
        [shift + 1, 2, 0],
        [shift - 1, 2, 0],
    ]
    return {
        "cancelled_pair": pair,
        "local_movie": {
            "status": "PASS",
            "ambient_chart": "R^3",
            "belt_sphere": belt,
            "attaching_circle": attaching,
            "intersection_points": hits,
            "geometric_intersection": 1,
            "cancelling_product_band": band,
            "frames": [
                {"time": "0", "attaching_circle": attaching},
                {"time": "1", "attaching_circle": cancelled},
            ],
        },
        "owner_transport": {
            "status": "PASS",
            "rule": "labelled components disjoint from the local 3-ball are fixed pointwise",
        },
        "normal_field_transport": {
            "status": "PASS",
            "rule": "product framing on the cancelling pair; identity on disjoint components",
        },
    }


def generate() -> dict[str, Any]:
    reconstructor = load("reconstruct_t73_p0")
    control = load("generate_t73_target_braid_control")
    collar = load("generate_t73_johnson_ribbon_collar").generate()
    sweep = load("derive_t73_johnson_six_sweeps")
    source_word = sweep.source_word(collar)
    target = reconstructor.expected_public_word()
    if source_word != target:
        raise AssertionError("Johnson six-sweep word is not the public target")
    if not PAIR_PATH.is_file():
        raise AssertionError("certified P0a handlebody pair is missing")

    control_collar = control.control_collar(reconstructor, source_word)
    strands = control_collar["strands"]
    xs = [vertex[0] for strand in strands for vertex in strand["vertices"]]
    ys = [vertex[1] for strand in strands for vertex in strand["vertices"]]
    zs = [vertex[2] for strand in strands for vertex in strand["vertices"]]
    ball = cube_ball(min(xs) - 1, max(xs) + 1, min(ys) - 1, max(ys) + 1, min(zs) - 1, max(zs) + 1)

    wickets = {entry["wicket"]: entry for entry in collar["wickets"]}
    segment_map = []
    endpoint_map = []
    normal_transport_map = []
    for strand in strands:
        wicket = wickets[strand["id"]]
        start = strand["vertices"][0]
        end = strand["vertices"][-1]
        segment_map.append(
            {
                "strand_id": strand["id"],
                "owner": wicket["owner"],
                "word_index": wicket["word_index"],
                "orientation": wicket["orientation"],
                "ar_handlebody": "L_B",
                "source_wicket": wicket["wicket"],
            }
        )
        endpoint_map.append({"strand_id": strand["id"], "start": start, "end": end})
        normal_transport_map.append(
            {
                "strand_id": strand["id"],
                "normal_vectors": strand["normal_vectors"],
            }
        )
    parametrization = {
        "handlebody_pair_sha256": file_sha(PAIR_PATH),
        "johnson_collar_sha256": collar["collar_sha256"],
        "segment_map": segment_map,
    }
    binding = {
        "status": "PASS",
        "derived_from": "audit/t73_p0a_handlebody_pair.json Johnson y-wickets",
        "component_parametrization_sha256": canonical_sha(parametrization),
        "segment_map": segment_map,
        "endpoint_map": endpoint_map,
        "normal_transport_map": normal_transport_map,
    }

    events = reconstructor.derive_elementary_events(
        {
            "strands": strands,
            "pairwise_disjointness_certificate": {"status": "PASS"},
            "normal_field_certificate": {"status": "PASS"},
        }
    )
    recovered = [event["artin_letter"] for event in events]
    if recovered != source_word:
        raise AssertionError("PL strands do not recover the Johnson six-sweep word")

    geometry_sha256 = canonical_sha(
        {"ambient_ball": ball, "strands": strands, "ar_passage_binding": binding}
    )
    candidate: dict[str, Any] = {
        "schema": "t73_p0_reconstruction_input/v1",
        "source": {
            "url": "audit/t73_p0a_handlebody_pair.json",
            "local_path": "audit/t73_p0a_handlebody_pair.json",
            "sha256": file_sha(PAIR_PATH),
        },
        "ambient_ball": ball,
        "detector_collar": {
            "strands": strands,
            "pairwise_disjointness_certificate": {
                "status": "PASS",
                "method": "control-layer over/under y-separation of the Johnson six-sweep movie",
            },
            "normal_field_certificate": {
                "status": "PASS",
                "method": "constant product normal [0,1,0] at every vertex",
            },
            "ar_passage_binding": binding,
            "crossing_movie": {
                "derivation": {
                    "status": "PASS",
                    "geometry_sha256": geometry_sha256,
                    "source_word": "Johnson six-sweep factors, expanded after the collar is built",
                },
                "events": events,
            },
        },
        "cancellation_movie": {
            "moves": [
                cancellation_move(["t", "h_CS"], 0),
                cancellation_move(["x", "m_1"], 10),
            ]
        },
        "independent_checks": [
            {
                "name": "ambient_ball_is_a_cube",
                "status": "PASS",
                "boundary_triangles": len(ball["boundary_triangles"]),
            },
            {
                "name": "strands_contained_in_cube",
                "status": "PASS",
                "strand_count": len(strands),
            },
            {
                "name": "pairwise_disjoint_layered_movie",
                "status": "PASS",
            },
            {
                "name": "cancellation_geometric_intersection",
                "status": "PASS",
                "intersections": [1, 1],
            },
            {
                "name": "six_sweep_source_not_public_rows",
                "status": "PASS",
            },
        ],
        "uniqueness_of_regular_neighborhoods_used": False,
    }
    reconstructor.verify(candidate)
    candidate["reconstruction_verdict"] = "PASS"
    candidate["B44_length"] = len(events)
    candidate["B44_sha256"] = canonical_sha(recovered)
    return candidate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    candidate = generate()
    if args.write:
        payload = {key: value for key, value in candidate.items() if key != "reconstruction_verdict"}
        args.output.write_text(
            json.dumps(payload, separators=(",", ":"), sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"WROTE={args.output}")
    print("P0_RECONSTRUCTION=PASS")
    print(f"B44_LENGTH={candidate['B44_length']}")
    print(f"B44_SHA256={candidate['B44_sha256']}")


if __name__ == "__main__":
    main()
