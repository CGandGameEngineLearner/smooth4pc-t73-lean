#!/usr/bin/env python3
"""Exact polyhedral decomposition of the unit Johnson arm mismatch.

This is an input to the missing ``Restore`` construction, not a certificate
that the restore exists.  Each affine image of a Johnson Freudenthal
tetrahedron is clipped against the period-four unit cubes using rational
half-spaces.  A resulting three-dimensional polytope is a mismatch piece
exactly when the source tetrahedron and target cube have different owners.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "geometry" / "t73_johnson_arm_mismatch.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def solve3(pl, rows, rhs):
    inverse = pl.invert3([[Fraction(entry) for entry in row] for row in rows])
    return pl.matvec_frac(inverse, [Fraction(entry) for entry in rhs])


def rank3(pl, vertices) -> bool:
    if len(vertices) < 4:
        return False
    base = vertices[0]
    differences = [pl.sub(vertex, base) for vertex in vertices[1:]]
    for first, second, third in itertools.combinations(differences, 3):
        matrix = [[first[row], second[row], third[row]] for row in range(3)]
        if pl.det3(matrix) != 0:
            return True
    return False


def tetrahedron_halfspaces(pl, vertices):
    base = vertices[0]
    columns = [[vertices[j][i] - base[i] for j in range(1, 4)] for i in range(3)]
    inverse = pl.invert3(columns)
    inequalities = []
    for row in inverse:
        inequalities.append(([-entry for entry in row], -sum(row[i] * base[i] for i in range(3))))
    total = [sum(inverse[row][column] for row in range(3)) for column in range(3)]
    inequalities.append((total, Fraction(1) + sum(total[i] * base[i] for i in range(3))))
    return inequalities


def cube_halfspaces(origin):
    inequalities = []
    for axis in range(3):
        upper = [Fraction(0), Fraction(0), Fraction(0)]
        upper[axis] = 1
        inequalities.append((upper, Fraction(origin[axis] + 1)))
        lower = [Fraction(0), Fraction(0), Fraction(0)]
        lower[axis] = -1
        inequalities.append((lower, Fraction(-origin[axis])))
    return inequalities


def intersection_vertices(pl, tetrahedron, cube_origin):
    inequalities = tetrahedron_halfspaces(pl, tetrahedron) + cube_halfspaces(cube_origin)
    vertices = set()
    for selected in itertools.combinations(inequalities, 3):
        rows = [item[0] for item in selected]
        if pl.det3(rows) == 0:
            continue
        point = solve3(pl, rows, [item[1] for item in selected])
        if all(sum(row[i] * point[i] for i in range(3)) <= bound for row, bound in inequalities):
            vertices.add(tuple(point))
    return sorted(vertices)


def source_tetrahedra():
    pl = load("t73_johnson_pl")
    owners = pl.johnson_owners()
    axes = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    owner_indices = [0, 0]
    result = []
    for origin in itertools.product(range(pl.PERIOD), repeat=3):
        owner = owners[origin]
        for permutation in itertools.permutations(range(3)):
            tetrahedron = [origin]
            current = origin
            for axis in permutation:
                current = tuple(current[i] + axes[axis][i] for i in range(3))
                tetrahedron.append(current)
            index = owner_indices[owner]
            owner_indices[owner] += 1
            result.append((owner, index, tetrahedron))
    if owner_indices != [192, 192]:
        raise AssertionError("unwrapped Johnson lift is not 192+192 tetrahedra")
    return result


def analyze_template(pl, source: int, prefix: int, power: int) -> dict[str, Any]:
    matrix = pl.transvection_matrix(source, prefix, power)
    owners = pl.johnson_owners()
    pieces = []
    source_counts = [0, 0]
    for owner, index, encoded_tetrahedron in source_tetrahedra():
        tetrahedron = [pl.matvec(matrix, vertex) for vertex in encoded_tetrahedron]
        lows = [math.floor(min(vertex[axis] for vertex in tetrahedron)) for axis in range(3)]
        highs = [math.ceil(max(vertex[axis] for vertex in tetrahedron)) for axis in range(3)]
        for cube_origin in itertools.product(
            *(range(lows[axis], highs[axis]) for axis in range(3))
        ):
            vertices = intersection_vertices(pl, tetrahedron, cube_origin)
            if not rank3(pl, vertices):
                continue
            target_owner = owners[tuple(value % pl.PERIOD for value in cube_origin)]
            if target_owner == owner:
                continue
            source_counts[owner] += 1
            pieces.append(
                {
                    "source_owner": owner,
                    "target_owner": target_owner,
                    "source_tetrahedron": index,
                    "target_cube_origin": list(cube_origin),
                    "vertices": [pl.encode(vertex) for vertex in vertices],
                }
            )
    origin_star_hits = [
        piece
        for piece in pieces
        if all(value % pl.PERIOD in (0, 3) for value in piece["target_cube_origin"])
    ]
    if origin_star_hits:
        raise AssertionError("an exact mismatch polytope meets the origin eight-cube star")
    payload = {
        "source_axis": source,
        "prefix_axis": prefix,
        "power": power,
        "matrix": matrix,
        "piece_count": len(pieces),
        "piece_count_by_source_owner": source_counts,
        "origin_star_piece_count": 0,
        "mismatch_disjoint_from_origin_star": True,
        "pieces": pieces,
        "restore_status": "OPEN",
    }
    payload["sha256"] = canonical_sha(payload)
    return payload


def generate() -> dict[str, Any]:
    pl = load("t73_johnson_pl")
    templates = [
        analyze_template(pl, source, prefix, power)
        for source, prefix in itertools.permutations(range(3), 2)
        for power in (-1, 1)
    ]
    result = {
        "schema": "t73_johnson_arm_mismatch/v1",
        "period": pl.PERIOD,
        "source": (
            "exact rational clipping of the unwrapped period-four affine-image "
            "tetrahedra against target unit cubes"
        ),
        "template_count": len(templates),
        "templates": templates,
        "all_mismatch_pieces_disjoint_from_origin_star": all(
            template["mismatch_disjoint_from_origin_star"] for template in templates
        ),
        "johnson_restore_status": "OPEN: mismatch polytopes are decomposed but no fixed-boundary arm homeomorphism has yet been attached",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check or args.write:
        print("T73_JOHNSON_ARM_MISMATCH=DECOMPOSED")
        print(f"TEMPLATES={result['template_count']}")
        print(
            "DISJOINT_FROM_ORIGIN_STAR="
            f"{result['all_mismatch_pieces_disjoint_from_origin_star']}"
        )
        print(f"RESTORE_STATUS={result['johnson_restore_status']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
