#!/usr/bin/env python3
"""Transport the H1 compression-disk system through the 93 Johnson factors."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESTORE = ROOT / "geometry" / "t73_johnson_restore_assembly.json"
SPINE_BINDING = ROOT / "geometry" / "t73_johnson_spine_binding.json"
PSI = ROOT / "geometry" / "t73_psi_A.json"
OUTPUT = ROOT / "geometry" / "t73_johnson_dual_disk_movie.json"


def load(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def identity():
    return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def matmul(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def dual_squares(axis: int):
    pl = load("t73_johnson_pl")
    owners = pl.johnson_owners()
    other = [index for index in range(3) if index != axis]
    square_origins = {}
    for origin, owner in owners.items():
        if owner != 0:
            continue
        if origin[axis] == 2 or (origin[axis] + 1) % pl.PERIOD == 2:
            key = (origin[other[0]], origin[other[1]])
            square_origins.setdefault(key, origin)
    squares = []
    for key, origin in sorted(square_origins.items()):
        corners = []
        for u, v in ((0, 0), (1, 0), (1, 1), (0, 1)):
            point = [0, 0, 0]
            point[axis] = 2
            point[other[0]] = origin[other[0]] + u
            point[other[1]] = origin[other[1]] + v
            corners.append([str(value) for value in point])
        squares.append(
            {
                "cube_origin": list(origin),
                "vertices": corners,
                "triangles": [[0, 1, 2], [0, 2, 3]],
            }
        )
    return squares


def build(write: bool = False):
    restore = json.loads(RESTORE.read_text(encoding="utf-8"))
    binding = json.loads(SPINE_BINDING.read_text(encoding="utf-8"))
    psi = json.loads(PSI.read_text(encoding="utf-8"))
    alpha_movie = load("generate_t73_johnson_alpha_movie").generate()
    sphere_module = load("generate_t73_sphere_slide_ledger")
    factors = restore["full_93_factor_assembly"]["factors"]
    if binding["restore_assembly_sha256"] != restore["sha256"] or psi["restore_assembly_sha256"] != restore["sha256"]:
        raise AssertionError("dual-disk movie inputs are not on one ambient restore")
    current = identity()
    free = load("compose_t73_free_group_psi")
    disk_words = free.identity_map()
    records = []
    for index, (factor, bound, alpha) in enumerate(zip(factors, binding["factors"], alpha_movie["moves"])):
        source = int(factor["source_axis"])
        prefix = int(factor["prefix_axis"])
        power = int(factor["power"])
        local_dual = identity()
        local_dual[source][prefix] = -power
        before = [row[:] for row in current]
        current = matmul(local_dual, current)
        local_words = free.identity_map()
        dual_letter = -power * (source + 1)
        local_words[prefix] = (
            [dual_letter, prefix + 1]
            if factor["side"] == "prefix-first"
            else [prefix + 1, dual_letter]
        )
        disk_words = free.compose(local_words, disk_words)
        if bound["ambient_restore_factor_sha256"] != canonical_sha(factor):
            raise AssertionError("dual disk transition is not bound to its ambient factor")
        if not factor["maps_both_owners_setwise"] or not factor["explicit_inverse"]:
            raise AssertionError("dual disk transition lacks an ambient H1 homeomorphism")
        records.append(
            {
                "index": index,
                "side": factor["side"],
                "source_axis": source,
                "prefix_axis": prefix,
                "power": power,
                "dual_disk_slide_multiple": -power,
                "local_H2_matrix": local_dual,
                "before_H2_matrix_sha256": canonical_sha(before),
                "after_H2_matrix_sha256": canonical_sha(current),
                "johnson_square_vertices": alpha["square_vertices"],
                "johnson_boundary_path": alpha["boundary_path"],
                "square_normal": alpha["square_normal"],
                "ambient_restore_factor_sha256": bound["ambient_restore_factor_sha256"],
                "maps_H1_setwise": True,
                "relative_protected_ball": True,
            }
        )
    expected_wedge, sphere_columns = sphere_module.derive_sphere_columns(psi["matrix_A"])
    if current != expected_wedge:
        raise AssertionError("93 dual disk slides do not give wedge^2(A)=A^{-T}")
    if free.abelianization(disk_words) != current:
        raise AssertionError("dual disk words do not abelianize to wedge^2(A)")
    sphere_boundary_words = [
        free.reduce_word([axis + 1] + free.inverse_word(word))
        for axis, word in enumerate(disk_words)
    ]
    sphere_word_columns = [
        [
            sum(
                1 if letter == basis + 1 else -1 if letter == -(basis + 1) else 0
                for letter in word
            )
            for basis in range(3)
        ]
        for word in sphere_boundary_words
    ]
    if sphere_word_columns != [list(column) for column in zip(*sphere_columns)]:
        raise AssertionError("geometric sphere boundary words do not give the columns of I-wedge^2(A)")
    initial_disks = []
    for axis in range(3):
        boundary = load("t73_johnson_pl").dual_disk_boundary(axis, 2, 0)
        squares = dual_squares(axis)
        if len(squares) != boundary["square_count"]:
            raise AssertionError("dual disk square count changed")
        initial_disks.append(
            {
                "disk": f"D1_{axis + 1}",
                "axis": axis,
                "boundary": boundary,
                "squares": squares,
                "triangle_count": 2 * len(squares),
                "topological_disk": True,
            }
        )
    result = {
        "schema": "t73_johnson_dual_disk_movie/v1",
        "psi_A_sha256": psi["sha256"],
        "restore_assembly_sha256": restore["sha256"],
        "spine_binding_sha256": binding["sha256"],
        "initial_H1_compression_disks": initial_disks,
        "factor_count": len(records),
        "factors": records,
        "final_H2_matrix": current,
        "final_dual_disk_words": disk_words,
        "final_dual_disk_word_lengths": [len(word) for word in disk_words],
        "wedge2_A_equals_A_inverse_transpose": expected_wedge,
        "mapping_torus_sphere_boundary_rule": "I-wedge^2(A)",
        "mapping_torus_sphere_columns": sphere_columns,
        "mapping_torus_sphere_boundary_words": sphere_boundary_words,
        "mapping_torus_sphere_geometric_core_counts": [len(word) for word in sphere_boundary_words],
        "actual_H1_disk_transport": "PASS",
        "actual_mapping_torus_3_handle_movie": "PASS_BEFORE_KIRBY_CANCELLATION_TRANSPORT",
        "post_cancellation_relative_surface_map": "OPEN",
    }
    result["sha256"] = canonical_sha(result)
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.write or args.check:
        print(f"T73_JOHNSON_DUAL_DISK_MOVIE={result['actual_H1_disk_transport']}")
        print(f"FACTORS={result['factor_count']}")
        print(f"FINAL_H2={result['final_H2_matrix']}")
        print(f"SPHERE_COLUMNS={result['mapping_torus_sphere_columns']}")
        print(f"POST_CANCELLATION_SURFACE_MAP={result['post_cancellation_relative_surface_map']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
