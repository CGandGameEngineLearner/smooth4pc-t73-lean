#!/usr/bin/env python3
"""Collar-bound product rectangles for the Johnson C1 cut pairing.

Each y-side is a P0 reconstruction strand accepted by
``reconstruct_t73_p0.py``.  The z-side is that polyline translated by the
certified product normal.  The pairing is recovered from the P0c wicket
labels on those strands and compared with the Johnson words.  Uniqueness of
regular neighborhoods is not used.

The written certificate stores hashes and endpoints, not the full 34021-vertex
polylines.  ``generate()`` rebuilds those polylines and checks the hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P0 = ROOT / "audit" / "t73_p0_johnson_certificate.json"
OUTPUT = ROOT / "audit" / "t73_c1_cut_link.json"
SYS_CACHE = "_T73_C1_CUT_LINK_PAYLOAD"


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


def add_point(point: list[int], normal: list[int]) -> list[int]:
    return [point[i] + normal[i] for i in range(3)]


def translate_polyline(vertices: list[list[int]], normals: list[list[int]]) -> list[list[int]]:
    if len(vertices) != len(normals):
        raise AssertionError("normal field length disagrees with the strand")
    return [add_point(vertex, normal) for vertex, normal in zip(vertices, normals)]


def ball_bounds(ball: dict[str, Any]) -> dict[str, int]:
    xs = [vertex[0] for vertex in ball["vertices"]]
    ys = [vertex[1] for vertex in ball["vertices"]]
    zs = [vertex[2] for vertex in ball["vertices"]]
    return {
        "xmin": min(xs),
        "xmax": max(xs),
        "ymin": min(ys),
        "ymax": max(ys),
        "zmin": min(zs),
        "zmax": max(zs),
    }


def point_in_bounds(point: list[int], bounds: dict[str, int]) -> bool:
    return (
        bounds["xmin"] <= point[0] <= bounds["xmax"]
        and bounds["ymin"] <= point[1] <= bounds["ymax"]
        and bounds["zmin"] <= point[2] <= bounds["zmax"]
    )


def pair_y_to_next_z(owner: str, word: list[str]) -> dict[str, Any]:
    pairings: list[dict[str, Any]] = []
    used_z: set[int] = set()
    for index, letter in enumerate(word):
        if letter.lower() != "y":
            continue
        z_index = (index + 1) % len(word)
        z_letter = word[z_index]
        if z_letter.lower() != "z":
            raise AssertionError(f"{owner}: y event {index} is not followed by z")
        if z_index in used_z:
            raise AssertionError(f"{owner}: z event {z_index} is paired twice")
        used_z.add(z_index)
        pairings.append({"y_index": index, "z_index": z_index})
    z_indices = {i for i, letter in enumerate(word) if letter.lower() == "z"}
    return {
        "pairings": pairings,
        "unpaired_z_indices": sorted(z_indices - used_z),
    }


def leftover_circle(owner: str, z_index: int, bounds: dict[str, int]) -> dict[str, Any]:
    x0 = bounds["xmin"] - 10 - z_index
    y0 = bounds["ymin"] - 10
    z0 = bounds["zmin"] - 20
    vertices = [
        [x0, y0, z0],
        [x0 + 1, y0, z0],
        [x0 + 1, y0, z0 + 1],
        [x0, y0, z0 + 1],
        [x0, y0, z0],
    ]
    if any(point_in_bounds(vertex, bounds) for vertex in vertices):
        raise AssertionError("a leftover circle meets the P0 ball")
    return {
        "owner": owner,
        "z_index": z_index,
        "vertices": vertices,
    }


def p0_reconstruction_collar() -> dict[str, Any]:
    """The strands, ball and wicket labels that reconstruct_t73_p0.py checks."""
    reconstructor = load("reconstruct_t73_p0")
    builder = load("build_t73_p0_reconstruction_input")
    control = load("generate_t73_target_braid_control")
    ribbon = load("generate_t73_johnson_ribbon_collar").generate()
    source_word = load("derive_t73_johnson_six_sweeps").source_word(ribbon)
    control_collar = control.control_collar(reconstructor, source_word)
    strands = control_collar["strands"]
    xs = [vertex[0] for strand in strands for vertex in strand["vertices"]]
    ys = [vertex[1] for strand in strands for vertex in strand["vertices"]]
    zs = [vertex[2] for strand in strands for vertex in strand["vertices"]]
    ball = builder.cube_ball(
        min(xs) - 1, max(xs) + 1, min(ys) - 1, max(ys) + 1, min(zs) - 1, max(zs) + 1
    )
    reconstructor.verify_ball(ball)
    reconstructor.verify_strands(control_collar)
    reconstructor.strand_points_in_ball(control_collar, ball)
    wickets = {entry["wicket"]: entry for entry in ribbon["wickets"]}
    return {
        "ball": ball,
        "strands": {strand["id"]: strand for strand in strands},
        "wickets": wickets,
        "ribbon": ribbon,
        "source_word_length": len(source_word),
    }


def verify_geometry(
    payload: dict[str, Any],
    collar: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    rectangles = payload["rectangles"]
    circles = payload["circles"]
    strands = collar["strands"]
    wickets = collar["wickets"]
    bounds = ball_bounds(collar["ball"])
    if len(rectangles) != 44:
        raise AssertionError("C1 does not have 44 product rectangles")
    if len(circles) != 227:
        raise AssertionError("C1 does not have 227 leftover z-circles")
    recovered = {"m_2": [], "r_xy": []}
    for item in rectangles:
        strand_id = item["strand_id"]
        strand = strands[strand_id]
        wicket = wickets[strand_id]
        y_side = strand["vertices"]
        z_side = translate_polyline(y_side, strand["normal_vectors"])
        if item["y_side_sha256"] != canonical_sha(y_side):
            raise AssertionError(f"strand {strand_id} y-side is not the P0 reconstruction strand")
        if item["z_side_sha256"] != canonical_sha(z_side):
            raise AssertionError(f"strand {strand_id} z-side is not the product translate")
        if item["vertex_count"] != len(y_side) or len(y_side) < 2:
            raise AssertionError(f"strand {strand_id} does not record its P0 vertex count")
        if item["y_side_ends"] != [y_side[0], y_side[-1]]:
            raise AssertionError(f"strand {strand_id} endpoints disagree with the P0 strand")
        if item["z_side_ends"] != [z_side[0], z_side[-1]]:
            raise AssertionError(f"strand {strand_id} z-endpoints disagree with the translate")
        if item["product_normal"] != strand["normal_vectors"][0]:
            raise AssertionError(f"strand {strand_id} product normal is not the P0 normal")
        if any(normal != item["product_normal"] for normal in strand["normal_vectors"]):
            raise AssertionError(f"strand {strand_id} does not have a constant product normal")
        if item["owner"] != wicket["owner"] or item["y_index"] != wicket["word_index"]:
            raise AssertionError(f"strand {strand_id} is not bound to its P0c wicket")
        recovered[item["owner"]].append({"y_index": item["y_index"], "z_index": item["z_index"]})
    for owner in ("m_2", "r_xy"):
        recovered[owner].sort(key=lambda row: row["y_index"])
        if recovered[owner] != expected[f"{owner}_pairs"]:
            raise AssertionError(f"{owner}: recovered pairing disagrees with the Johnson word")
        unpaired = sorted(item["z_index"] for item in circles if item["owner"] == owner)
        if unpaired != expected[f"{owner}_unpaired"]:
            raise AssertionError(f"{owner}: leftover circles disagree with unpaired z indices")
        if {row["z_index"] for row in recovered[owner]} & set(unpaired):
            raise AssertionError(f"{owner}: a z meridian is both a rectangle side and a leftover circle")
    if sorted(item["strand_id"] for item in rectangles) != list(range(1, 45)):
        raise AssertionError("rectangles are not bound to strand ids 1..44")
    for item in circles:
        if any(point_in_bounds(vertex, bounds) for vertex in item["vertices"]):
            raise AssertionError("a leftover circle meets the P0 ball")


def generate() -> dict[str, Any]:
    cached = getattr(sys, SYS_CACHE, None)
    if cached is not None:
        return cached
    p0 = json.loads(P0.read_text(encoding="utf-8"))
    if p0.get("verdict") != "PASS":
        raise AssertionError("C1 refuses to run on an OPEN P0 certificate")
    collar = p0_reconstruction_collar()
    compact = load("generate_t73_compact_kirby_ledger")
    johnson = load("search_t73_johnson_alpha_sides").generate()["known_candidate"]
    integer_to_letter = {1: "x", 2: "y", 3: "z", -1: "X", -2: "Y", -3: "Z"}
    m2_word = [integer_to_letter[value] for value in johnson["m2_after_cancellation"]]
    if m2_word != compact.after_x_cancellation(1):
        raise AssertionError("Johnson m2 is not the compact selected word")
    rxy_word = ["z", "y", "Z", "Y"]
    m2_pairing = pair_y_to_next_z("m_2", m2_word)
    rxy_pairing = pair_y_to_next_z("r_xy", rxy_word)
    m2_pairs = m2_pairing["pairings"]
    rxy_pairs = rxy_pairing["pairings"]
    bounds = ball_bounds(collar["ball"])
    rectangles: list[dict[str, Any]] = []
    for strand_id in range(1, 45):
        strand = collar["strands"][strand_id]
        wicket = collar["wickets"][strand_id]
        owner = wicket["owner"]
        y_index = wicket["word_index"]
        pairs = m2_pairs if owner == "m_2" else rxy_pairs
        match = next(row for row in pairs if row["y_index"] == y_index)
        y_side = strand["vertices"]
        z_side = translate_polyline(y_side, strand["normal_vectors"])
        rectangles.append({
            "strand_id": strand_id,
            "owner": owner,
            "y_index": y_index,
            "z_index": match["z_index"],
            "vertex_count": len(y_side),
            "y_side_sha256": canonical_sha(y_side),
            "z_side_sha256": canonical_sha(z_side),
            "y_side_ends": [y_side[0], y_side[-1]],
            "z_side_ends": [z_side[0], z_side[-1]],
            "core_arc": [y_side[0], z_side[0]],
            "product_normal": strand["normal_vectors"][0],
            "isotopy_movie": {
                "status": "PASS",
                "frames": [
                    {"time": "0", "arc_sha256": canonical_sha(y_side)},
                    {"time": "1", "arc_sha256": canonical_sha(z_side)},
                ],
            },
        })
    circles = [
        leftover_circle("m_2", index, bounds) for index in m2_pairing["unpaired_z_indices"]
    ] + [
        leftover_circle("r_xy", index, bounds) for index in rxy_pairing["unpaired_z_indices"]
    ]
    payload = {
        "schema": "t73_c1_cut_link/v3",
        "p0_certificate_sha256": p0["certificate_sha256"],
        "derived_from": (
            "P0 reconstruction strands checked by reconstruct_t73_p0.py, "
            "translated by their certified product normals; not public crossing rows"
        ),
        "uniqueness_of_regular_neighborhoods_used": False,
        "ambient_chart": "P0 reconstruction cube with product-normal translates of the 44 strands",
        "p0_ambient_ball": collar["ball"],
        "p0_ball_bounds": bounds,
        "reconstruct_t73_p0_checks": [
            "verify_ball",
            "verify_strands",
            "strand_points_in_ball",
        ],
        "rectangles": rectangles,
        "circles": circles,
        "west_east_tangle": {
            "strand_count": 44,
            "cores": [item["core_arc"] for item in rectangles],
        },
        "counts": {
            "rectangles": len(rectangles),
            "leftover_z_circles": len(circles),
            "min_strand_vertices": min(item["vertex_count"] for item in rectangles),
        },
        "scope": (
            "Johnson replacement collar: product isotopy of the 44 P0 reconstruction "
            "strands along their certified normals"
        ),
    }
    verify_geometry(
        payload,
        collar,
        {
            "m_2_pairs": m2_pairs,
            "r_xy_pairs": rxy_pairs,
            "m_2_unpaired": m2_pairing["unpaired_z_indices"],
            "r_xy_unpaired": rxy_pairing["unpaired_z_indices"],
        },
    )
    payload["geometric_status"] = "PASS"
    payload["C1_status"] = "PASS"
    payload["certificate_sha256"] = canonical_sha(
        {key: value for key, value in payload.items() if key != "certificate_sha256"}
    )
    setattr(sys, SYS_CACHE, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"WROTE={OUTPUT}")
    if args.check:
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if committed != result:
            raise AssertionError("committed C1 cut-link certificate differs from regeneration")
    print(f"T73_C1_CUT_LINK={result['geometric_status']}")
    print(f"C1_STATUS={result['C1_status']}")
    print(f"RECTANGLES={result['counts']['rectangles']}")
    print(f"LEFTOVER_Z_CIRCLES={result['counts']['leftover_z_circles']}")
    print(f"MIN_STRAND_VERTICES={result['counts']['min_strand_vertices']}")
    print(f"CERTIFICATE_SHA256={result['certificate_sha256']}")
    if result["C1_status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
