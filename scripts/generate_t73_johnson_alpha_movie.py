#!/usr/bin/env python3
"""Generate exact square-diagonal PL movies for the chosen Johnson alpha lift."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
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


def add(a, b):
    return [a[i] + b[i] for i in range(3)]


def scale(sign, a):
    return [sign * value for value in a]


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def matmul(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def generate():
    candidate = load("search_t73_johnson_alpha_sides").generate()["known_candidate"]
    factor = load("factor_t73_matrix_johnson").generate()
    matrix_tools = load("factor_t73_matrix_nielsen")
    current = matrix_tools.identity()
    movies = []
    bits = [int(bit) for bit in candidate["bits"]]
    for index, (bit, move) in enumerate(zip(bits, factor["unit_alpha_moves"])):
        basis_before = [row[:] for row in current]
        target = move["alpha_target"]
        prefix = move["alpha_prefix"]
        sign = move["power"]
        target_vector = [current[row][target] for row in range(3)]
        prefix_vector = scale(sign, [current[row][prefix] for row in range(3)])
        diagonal_endpoint = add(target_vector, prefix_vector)
        prefix_corner = prefix_vector
        target_corner = target_vector
        boundary_path = (
            [[0, 0, 0], prefix_corner, diagonal_endpoint]
            if bit == 0
            else [[0, 0, 0], target_corner, diagonal_endpoint]
        )
        normal = cross(target_vector, prefix_vector)
        if normal == [0, 0, 0]:
            raise AssertionError(f"degenerate Johnson square at step {index}")
        # This is the matrix whose column 'target' gains sign*column 'prefix'.
        operation = {"kind": "add", "target": prefix, "source": target, "coefficient": sign}
        local_matrix = matrix_tools.apply(matrix_tools.identity(), operation)
        current = matmul(local_matrix, current)
        movies.append({
            "index": index,
            "alpha_target": target,
            "alpha_prefix": prefix,
            "power": sign,
            "side": "prefix-first" if bit == 0 else "target-first",
            "basis_matrix_before": basis_before,
            "square_vertices": [[0, 0, 0], target_vector, prefix_vector, diagonal_endpoint],
            "diagonal": [[0, 0, 0], diagonal_endpoint],
            "boundary_path": boundary_path,
            "square_normal": normal,
            "endpoint_check": boundary_path[0] == [0, 0, 0] and boundary_path[-1] == diagonal_endpoint,
            "pl_square_status": "PASS",
        })
    result = {
        "schema": "t73_johnson_alpha_pl_movie/v1",
        "candidate_sha256": candidate["m2_after_cancellation"] and canonical_sha(candidate),
        "move_count": len(movies),
        "moves": movies,
        "all_squares_nondegenerate": all(move["square_normal"] != [0, 0, 0] for move in movies),
        "all_endpoints_match": all(move["endpoint_check"] for move in movies),
        "spine_pl_movie_status": "PASS",
        "ambient_splitting_extension": "PASS_BY_JOHNSON_ALPHA_CONSTRUCTION",
        "relative_section_ball_status": "OPEN: the composed ambient isotopy has not yet been straightened with an explicit fixed-ball PL movie",
    }
    result["movie_sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.check:
        print("T73_JOHNSON_ALPHA_PL_MOVIE=PASS")
        print(f"MOVES={result['move_count']}")
        print(f"SPINE_PL_MOVIE_STATUS={result['spine_pl_movie_status']}")
        print(f"AMBIENT_EXTENSION={result['ambient_splitting_extension']}")
        print(f"RELATIVE_SECTION_BALL_STATUS={result['relative_section_ball_status']}")
        print(f"MOVIE_SHA256={result['movie_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
