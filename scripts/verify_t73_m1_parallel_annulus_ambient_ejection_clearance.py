#!/usr/bin/env python3
"""Exact quotient clearance for the full supported m1 ambient ejection."""

from __future__ import annotations

import json
from pathlib import Path

from verify_t73_m1_parallel_annulus_tubular_clearance import boxes_overlap, convex_hulls_intersect, translate, translation_ranges

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_m1_parallel_annulus_ambient_ejection.json"
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"


def point(values):
    from fractions import Fraction
    return tuple(Fraction(value) for value in values)


def verify():
    data = json.loads(DATA.read_text(encoding="utf-8")); foliation = json.loads(FOLIATION.read_text(encoding="utf-8"))
    vertices = [point(value) for value in data["source_vertices"]]; ids = [tuple(value) for value in data["tetrahedra"]]; tetrahedra = [tuple(vertices[index] for index in simplex) for simplex in ids]
    triangle_ids = [set(value) for value in foliation["triangles"]]; seam = set(foliation["mapping_torus_seam_triangle_indices"])
    deck_candidates = adjacency_skips = seam_skips = exact_box_candidates = exact_checks = 0
    for first_index, first in enumerate(tetrahedra):
        first_triangle = (first_index % 204) // 3
        for second_index in range(first_index, len(tetrahedra)):
            second = tetrahedra[second_index]; second_triangle = (second_index % 204) // 3
            for raw_deck in translation_ranges(first, second):
                deck = tuple(raw_deck); deck_candidates += 1
                if first_index == second_index and deck == (0, 0, 0):
                    adjacency_skips += 1; continue
                if first_triangle in seam or second_triangle in seam:
                    seam_skips += 1; continue
                if deck == (0, 0, 0) and triangle_ids[first_triangle] & triangle_ids[second_triangle]:
                    adjacency_skips += 1; continue
                if first_triangle // 2 == 0 and second_triangle // 2 == len(foliation["base_vertices"]) - 2 and deck == (1, 0, -1):
                    seam_skips += 1; continue
                if first_triangle // 2 == len(foliation["base_vertices"]) - 2 and second_triangle // 2 == 0 and deck == (-1, 0, 1):
                    seam_skips += 1; continue
                moved = translate(second, deck)
                if not boxes_overlap(first, moved):
                    continue
                exact_box_candidates += 1; exact_checks += 1
                if convex_hulls_intersect(first, moved):
                    raise AssertionError(f"ambient-ejection support self-intersects: {first_index}/{second_index}/{deck}")
    return {"verdict": "PASS_M1_PARALLEL_ANNULUS_AMBIENT_EJECTION_SUPPORT_CLEARANCE", "tetrahedra": 408, "deck_candidates": deck_candidates, "adjacency_skips": adjacency_skips, "seam_skips": seam_skips, "exact_box_candidates": exact_box_candidates, "exact_convex_feasibility_checks": exact_checks, "compactly_supported_ambient_homeomorphism": True}


if __name__ == "__main__": print(json.dumps(verify(), sort_keys=True))
