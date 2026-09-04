#!/usr/bin/env python3
"""Rebuild the Johnson H1 compression-disk movie and reject local mutations."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MOVIE = ROOT / "geometry" / "t73_johnson_dual_disk_movie.json"


def load(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(data):
    builder = load("build_t73_johnson_dual_disk_movie")
    free = load("compose_t73_free_group_psi")
    current = builder.identity()
    disk_words = free.identity_map()
    if data["factor_count"] != 93 or len(data["factors"]) != 93:
        raise AssertionError("dual disk movie does not have 93 factors")
    for index, factor in enumerate(data["factors"]):
        if factor["index"] != index or not factor["maps_H1_setwise"]:
            raise AssertionError("dual disk factor order or H1 ownership changed")
        expected = builder.identity()
        expected[int(factor["source_axis"])][int(factor["prefix_axis"])] = -int(factor["power"])
        if factor["local_H2_matrix"] != expected or factor["dual_disk_slide_multiple"] != -int(factor["power"]):
            raise AssertionError("dual disk slide is not inverse-transpose to its H1 transvection")
        current = builder.matmul(expected, current)
        local_words = free.identity_map()
        letter = -int(factor["power"]) * (int(factor["source_axis"]) + 1)
        prefix = int(factor["prefix_axis"])
        local_words[prefix] = (
            [letter, prefix + 1]
            if factor["side"] == "prefix-first"
            else [prefix + 1, letter]
        )
        disk_words = free.compose(local_words, disk_words)
        if factor["after_H2_matrix_sha256"] != builder.canonical_sha(current):
            raise AssertionError("dual disk partial product changed")
    if current != data["final_H2_matrix"] or current != data["wedge2_A_equals_A_inverse_transpose"]:
        raise AssertionError("dual disk movie has the wrong final H2 action")
    sphere = [[int(i == j) - current[i][j] for j in range(3)] for i in range(3)]
    if sphere != data["mapping_torus_sphere_columns"]:
        raise AssertionError("mapping-torus sphere columns are not I-wedge^2(A)")
    if data["final_dual_disk_word_lengths"] != [len(word) for word in data["final_dual_disk_words"]]:
        raise AssertionError("dual disk word lengths changed")
    if disk_words != data["final_dual_disk_words"]:
        raise AssertionError("dual disk words do not replay from the 93 side choices")
    expected_sphere_words = [
        free.reduce_word([axis + 1] + free.inverse_word(word))
        for axis, word in enumerate(disk_words)
    ]
    if expected_sphere_words != data["mapping_torus_sphere_boundary_words"]:
        raise AssertionError("mapping-torus boundary words changed")
    if data["mapping_torus_sphere_geometric_core_counts"] != [len(word) for word in data["mapping_torus_sphere_boundary_words"]]:
        raise AssertionError("geometric core-disk counts changed")
    for disk in data["initial_H1_compression_disks"]:
        if not disk["topological_disk"] or disk["triangle_count"] != 2 * len(disk["squares"]):
            raise AssertionError("initial H1 compression disk is not triangulated")


def verify():
    builder = load("build_t73_johnson_dual_disk_movie")
    stored = json.loads(MOVIE.read_text(encoding="utf-8"))
    rebuilt = builder.build(write=False)
    if stored != rebuilt:
        raise AssertionError("stored dual disk movie does not match a live rebuild")
    validate(stored)
    mutant = copy.deepcopy(stored)
    mutant["factors"][0]["dual_disk_slide_multiple"] *= -1
    failed = False
    try:
        validate(mutant)
    except AssertionError:
        failed = True
    if not failed:
        raise AssertionError("dual disk orientation mutation was not detected")
    side_mutant = copy.deepcopy(stored)
    side_mutant["factors"][0]["side"] = (
        "target-first" if side_mutant["factors"][0]["side"] == "prefix-first" else "prefix-first"
    )
    side_failed = False
    try:
        validate(side_mutant)
    except AssertionError:
        side_failed = True
    if not side_failed:
        raise AssertionError("dual disk side mutation was not detected")
    return {
        "ACTUAL_H1_DISK_TRANSPORT": "PASS",
        "FACTORS": stored["factor_count"],
        "FINAL_H2": stored["final_H2_matrix"],
        "SPHERE_COLUMNS": stored["mapping_torus_sphere_columns"],
        "GEOMETRIC_CORE_COUNTS": stored["mapping_torus_sphere_geometric_core_counts"],
        "MUTATION_DISK_SLIDE_ORIENTATION": "FAIL",
        "MUTATION_DISK_SLIDE_SIDE": "FAIL",
        "POST_CANCELLATION_SURFACE_MAP": stored["post_cancellation_relative_surface_map"],
        "SHA256": stored["sha256"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.check:
        for key, value in result.items():
            print(f"{key}={value}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
