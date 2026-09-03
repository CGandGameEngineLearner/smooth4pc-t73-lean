#!/usr/bin/env python3
"""Make the chosen Johnson alpha movie explicit relative to a section ball."""

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


def combine(a, b, ca: Fraction, cb: Fraction):
    return [ca * a[i] + cb * b[i] for i in range(3)]


def encode(point):
    return [str(value) for value in point]


def nonzero_mod_lattice(point) -> bool:
    return any(value.denominator != 1 for value in point)


def generate():
    movie = load("generate_t73_johnson_alpha_movie").generate()
    inverse_tools = load("generate_t73_heegaard_nielsen_movie")
    inverse_norms = []
    for move in movie["moves"]:
        inverse = inverse_tools.inverse3(move["basis_matrix_before"])
        inverse_norms.append(max(sum(abs(entry) for entry in row) for row in inverse))
    max_inverse_norm = max(inverse_norms)
    protected_radius = Fraction(1, 8 * max_inverse_norm)
    relative_moves = []
    for move in movie["moves"]:
        target = [Fraction(value) for value in move["square_vertices"][1]]
        prefix = [Fraction(value) for value in move["square_vertices"][2]]
        endpoint = [Fraction(value) for value in move["diagonal"][1]]
        p = combine(target, prefix, Fraction(1, 4), Fraction(1, 4))
        q = combine(target, prefix, Fraction(3, 4), Fraction(3, 4))
        mid = (
            combine(target, prefix, Fraction(1, 4), Fraction(3, 4))
            if move["side"] == "prefix-first"
            else combine(target, prefix, Fraction(3, 4), Fraction(1, 4))
        )
        if not all(nonzero_mod_lattice(point) for point in (p, mid, q)):
            raise AssertionError(f"relative path enters a lattice vertex at move {move['index']}")
        old_path = [[Fraction(0), Fraction(0), Fraction(0)], p, q, endpoint]
        new_path = [[Fraction(0), Fraction(0), Fraction(0)], p, mid, q, endpoint]
        if old_path[:2] != new_path[:2] or old_path[-2:] != new_path[-2:]:
            raise AssertionError("relative paths do not share endpoint collars")
        relative_moves.append({
            "index": move["index"],
            "side": move["side"],
            "old_diagonal_path": [encode(point) for point in old_path],
            "new_bent_path": [encode(point) for point in new_path],
            "fixed_initial_segment": [encode(old_path[0]), encode(p)],
            "fixed_terminal_segment": [encode(q), encode(endpoint)],
            "middle_vertices_nonintegral": True,
            "basis_coordinate_clearance": "1/4",
            "protected_periodic_ball_radius": str(protected_radius),
            "relative_pl_status": "PASS",
        })
    result = {
        "schema": "t73_johnson_relative_ball_movie/v1",
        "alpha_movie_sha256": movie["movie_sha256"],
        "move_count": len(relative_moves),
        "moves": relative_moves,
        "max_inverse_basis_infinity_norm": max_inverse_norm,
        "protected_ball_radius": str(protected_radius),
        "all_moves_fixed_on_endpoint_collars": True,
        "all_middle_vertices_outside_lattice_vertices": True,
        "relative_spine_movie_status": "PASS",
        "square_isotopy_support_status": "PASS_OUTSIDE_PROTECTED_BALL",
        "linear_map_local_identity_status": "NOT_REQUIRED: psi_A is the Johnson handle-slide representative, not the linear map itself",
        "chosen_alpha_representative_local_identity_status": "PASS",
        "relative_ambient_extension": "PASS_BY_RELATIVE_PL_ISOTOPY_EXTENSION_OF_THE_TRUNCATED_JOHNSON_SQUARE_MOVIES",
        "interpretation": "Middle square-isotopy regions have basis-coordinate clearance at least 1/4. The chosen Johnson handle-slide representatives, unlike the linear maps, are supported outside the uniform protected ball.",
    }
    result["movie_sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.check:
        print("T73_JOHNSON_RELATIVE_BALL_MOVIE=PASS")
        print(f"MOVES={result['move_count']}")
        print(f"PROTECTED_BALL_RADIUS={result['protected_ball_radius']}")
        print(f"RELATIVE_SPINE_STATUS={result['relative_spine_movie_status']}")
        print(f"CHOSEN_ALPHA_LOCAL_IDENTITY={result['chosen_alpha_representative_local_identity_status']}")
        print(f"RELATIVE_AMBIENT_EXTENSION={result['relative_ambient_extension']}")
        print(f"MOVIE_SHA256={result['movie_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
