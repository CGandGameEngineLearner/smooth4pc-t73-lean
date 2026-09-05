#!/usr/bin/env python3
"""Extend the x/m1 transverse collar map as an explicit x-product."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLAR = ROOT / "geometry/t73_x_m1_collar_ejection_map.json"
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
POST_X = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
FRAMING = ROOT / "geometry/t73_x_m1_framing_exteriorization.json"
OUTPUT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def encode(value):
    return [str(coordinate) for coordinate in value]


def build():
    collar = json.loads(COLLAR.read_text(encoding="utf-8"))
    local = json.loads(LOCAL_MOVIE.read_text(encoding="utf-8"))
    post_x = json.loads(POST_X.read_text(encoding="utf-8"))
    framing = json.loads(FRAMING.read_text(encoding="utf-8"))
    source_transverse = [[Fraction(value) for value in point[1:]] for point in collar["source_vertices"]]
    target_transverse = [[Fraction(value) for value in point[1:]] for point in collar["target_vertex_images"]]
    source_vertices = []
    target_vertices = []
    for x_value in (Fraction(1), Fraction(3)):
        source_vertices.extend([(x_value, *value) for value in source_transverse])
        target_vertices.extend([(x_value, *value) for value in target_transverse])
    four_simplices = []
    offset = len(source_transverse)
    for tetrahedron in collar["tetrahedra"]:
        a, b, c, d = sorted(tetrahedron)
        four_simplices.extend((
            (a, b, c, d, d + offset),
            (a, b, c, c + offset, d + offset),
            (a, b, b + offset, c + offset, d + offset),
            (a, a + offset, b + offset, c + offset, d + offset),
        ))
    result = {
        "schema": "t73_x_m1_collar_product_extension/v1",
        "x_m1_collar_ejection_map_sha256": collar["sha256"],
        "x_band_local_movie_sha256": local["sha256"],
        "post_x_framed_replacement_cells_receipt_sha256": post_x["sha256"],
        "x_m1_framing_exteriorization_sha256": framing["sha256"],
        "exteriorized_uniform_push_vector": framing["uniform_push_vector"],
        "x_interval": ["1", "3"],
        "source_vertices": [encode(value) for value in source_vertices],
        "target_vertex_images": [encode(value) for value in target_vertices],
        "four_simplices": [list(value) for value in four_simplices],
        "vertex_count": len(source_vertices),
        "four_simplex_count": len(four_simplices),
        "map_rule": "x coordinate fixed; transverse cubical-shell map affine on each tetrahedron and product-simplex",
        "fixed_outer_rule": "identity on transverse L-infinity radius two and outside the collar",
        "completion_status": "X_M1_COLLAR_PRODUCT_EXTENSION_WITH_OUTWARD_FRAMING_DOMAIN_CONSTRUCTED",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true"); parser.add_argument("--check", action="store_true")
    args = parser.parse_args(); result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("x/m1 collar product extension is stale")
    print(f"T73_X_M1_PRODUCT_COLLAR={result['completion_status']}")


if __name__ == "__main__":
    main()
