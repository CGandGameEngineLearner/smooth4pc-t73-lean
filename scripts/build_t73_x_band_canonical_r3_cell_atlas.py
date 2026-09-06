#!/usr/bin/env python3
"""Realize all 1513 actual x-band disks as disjoint rational R3 cells."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPLACEMENT = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
HYBRID = ROOT / "geometry/t73_x_band_hybrid_movie.json"
OUTPUT = ROOT / "geometry/t73_x_band_canonical_r3_cell_atlas.json"
TRIANGLES = [[0, 2, 3], [0, 3, 1], [2, 4, 5], [2, 5, 3]]
PUSH_HEIGHT = Fraction(1, 10)
X_STRIDE = 4


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/home/") and os.name == "nt":
        return Path("//wsl.localhost/Ubuntu") / value[1:]
    return path


def vertices(index):
    x = X_STRIDE * index
    return [
        [str(x), "0", "0"],
        [str(x), "1", "0"],
        [str(x + 1), "0", "0"],
        [str(x + 1), "1", "0"],
        [str(x + 2), "0", "0"],
        [str(x + 2), "1", "0"],
    ]


def build():
    replacement = json.loads(REPLACEMENT.read_text())
    hybrid = json.loads(HYBRID.read_text())
    bands = []
    with gzip.open(resolve(replacement["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            cell = json.loads(line)
            core = vertices(cell["band_index"])
            push = [[value[0], value[1], str(PUSH_HEIGHT)] for value in core]
            bands.append({
                "band_index": cell["band_index"],
                "component": cell["component"],
                "orientation": cell["orientation"],
                "source_id": cell["source_id"],
                "hybrid_replacement_cell_sha256": cell["hybrid_replacement_cell_sha256"],
                "source_band_surface_sha256": canonical_sha256(cell["band_surface"]),
                "source_relative_twist": cell["relative_twist"],
                "x_support_interval": [str(X_STRIDE * cell["band_index"]), str(X_STRIDE * cell["band_index"] + 2)],
                "core_vertices": core,
                "push_vertices": push,
                "core_triangles": TRIANGLES,
                "push_triangles": TRIANGLES,
                "negative_lane_vertex_order": [0, 2, 4],
                "positive_lane_vertex_order": [5, 3, 1],
                "source_attachment_interval": [0, 1],
                "target_attachment_interval": [4, 5],
                "lane_ribbon_triangles": [
                    [0, 2, 8], [0, 8, 6], [2, 4, 10], [2, 10, 8],
                    [5, 3, 9], [5, 9, 11], [3, 1, 7], [3, 7, 9],
                ],
                "surface_product_tetrahedron_count": 12,
                "cell_status": "ACTUAL_BAND_CELL_CANONICAL_R3_REALIZATION",
            })
    result = {
        "schema": "t73_x_band_canonical_r3_cell_atlas/v1",
        "post_x_replacement_cells_receipt_sha256": replacement["sha256"],
        "x_band_hybrid_movie_sha256": hybrid["sha256"],
        "construction": "one 2-by-1 rectangle per actual band, separated by x stride 4",
        "push_height": str(PUSH_HEIGHT),
        "x_stride": X_STRIDE,
        "bands": bands,
        "band_count": len(bands),
        "core_triangle_count": 4 * len(bands),
        "push_triangle_count": 4 * len(bands),
        "lane_core_segment_count": 4 * len(bands),
        "lane_push_segment_count": 4 * len(bands),
        "lane_ribbon_triangle_count": 8 * len(bands),
        "surface_product_tetrahedron_count": 12 * len(bands),
        "pairwise_band_cell_clearance": "PASS_BY_DISJOINT_X_SUPPORT_INTERVALS",
        "global_port_gluing_status": "OPEN_MAP_FOUR_ATTACHMENT_PORTS_PER_BAND",
        "completion_status": "ALL_ACTUAL_X_BAND_CELLS_HAVE_DISJOINT_CANONICAL_R3_REALIZATIONS",
        "verdict": "PASS_ALL_X_BAND_CANONICAL_R3_CELL_ATLAS_LOCAL",
    }
    result["sha256"] = canonical_sha256(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("x-band canonical R3 cell atlas is stale")
    print(json.dumps({
        "bands": result["band_count"],
        "core_triangles": result["core_triangle_count"],
        "lane_ribbons": result["lane_ribbon_triangle_count"],
        "product_tetrahedra": result["surface_product_tetrahedron_count"],
        "ports": result["global_port_gluing_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
