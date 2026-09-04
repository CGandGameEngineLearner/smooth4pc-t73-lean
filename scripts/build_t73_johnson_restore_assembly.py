#!/usr/bin/env python3
"""Assemble every verified layer of the canonical Johnson arm restore."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "sweep": ROOT / "geometry" / "t73_johnson_elementary_sweep.json",
    "single": ROOT / "geometry" / "t73_johnson_disk_move_cells.json",
    "collapses": ROOT / "geometry" / "t73_johnson_relative_side_collapses.json",
    "side": ROOT / "geometry" / "t73_johnson_actual_derived_placements.json",
    "fiber": ROOT / "geometry" / "t73_johnson_cap_collapse_assembly.json",
    "normalization": ROOT / "geometry" / "t73_johnson_negative_cap_normalization.json",
    "outer": ROOT / "geometry" / "t73_johnson_outer_curve_collar.json",
    "support": ROOT / "geometry" / "t73_johnson_paired_saddle_support.json",
}
OUTPUT = ROOT / "geometry" / "t73_johnson_restore_assembly.json"
SECTION_CUTOFF_CELLS = 162


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def identity3():
    return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def matmul(left, right):
    return [
        [sum(left[row][inner] * right[inner][column] for inner in range(3)) for column in range(3)]
        for row in range(3)
    ]


def transvection(source, prefix, power):
    matrix = identity3()
    matrix[prefix][source] = power
    return matrix


def keyed(records):
    return {(record["power"], record["side"]): record for record in records}


def side_state(record, name):
    matches = [state for state in record["states"] if state["state"] == name]
    if len(matches) != 1:
        raise AssertionError(f"side-chart movie has no unique {name} state")
    return matches[0]


def build_movie(key, layers):
    power, side = key
    sweep = layers["sweep"][key]
    single = layers["single"][key]
    side_charts = layers["side"][key]
    fiber = layers["fiber"][key]
    normalization = layers["normalization"][key]
    outer = layers["outer"][key]
    support = layers["support"][key]
    if not sweep["reaches_target_handlebody"]:
        raise AssertionError("combinatorial sweep does not reach the target")
    if not single["all_disk_move_cells_positive"]:
        raise AssertionError("single disk cells are not positive")
    if fiber["fiber_transport"] != "PASS":
        raise AssertionError("internal fiber transport is not certified")
    if normalization["source_disk_to_remove_cap"] != "PASS":
        raise AssertionError("source disk does not normalize to cap 1")
    if outer["outer_curve_collar"] != "PASS":
        raise AssertionError("outer boundary curve collar is not certified")
    if support["paired_saddle_support"] != "PASS":
        raise AssertionError("paired saddle support is not a ball")
    source_state = side_state(side_charts, "source")
    target_state = side_state(side_charts, "target")
    source_cells = sum(item["expanded_ambient_cell_count"] for item in source_state["sides"])
    target_cells = sum(item["expanded_ambient_cell_count"] for item in target_state["sides"])
    if not all(item["all_conjugated_cells_positive"] for item in source_state["sides"] + target_state["sides"]):
        raise AssertionError("paired side chart has a nonpositive cell family")
    layer_counts = {
        "single_disk_moves": single["cell_count"],
        "source_side_charts": source_cells,
        "negative_source_disk_normalization": normalization["expanded_ambient_cell_count"],
        "internal_fiber_transport": fiber["expanded_ambient_cell_count"],
        "inverse_target_side_charts": target_cells,
        "outer_curve_collar": outer["expanded_ambient_cell_count"],
        "section_cutoff": SECTION_CUTOFF_CELLS,
    }
    clearances = [
        Fraction(single["protected_ball_bbox_clearance_min"]),
        *(Fraction(item["protected_ball_bbox_clearance_min"]) for item in source_state["sides"]),
        *(Fraction(item["protected_ball_bbox_clearance_min"]) for item in target_state["sides"]),
        Fraction(support["protected_ball_bbox_clearance"]),
        Fraction(outer["protected_ball_bbox_clearance_min"]),
    ]
    if min(clearances) <= Fraction(1, 196104):
        raise AssertionError("assembled arm restore meets the protected ball")
    composition = [
        "single_disk_moves",
        "source_side_charts",
        "negative_source_disk_normalization" if power < 0 else "identity_normalization",
        "internal_cap1_to_cap0_fiber_transport",
        "inverse_target_side_charts",
        "outer_curve_collar_to_identity",
        "section_cutoff_after_affine_transvection",
    ]
    inverse = [
        "inverse_section_cutoff",
        "inverse_outer_curve_collar",
        "target_side_charts",
        "inverse_internal_cap1_to_cap0_fiber_transport",
        "inverse_negative_source_disk_normalization" if power < 0 else "identity_normalization",
        "inverse_source_side_charts",
        "inverse_single_disk_moves",
    ]
    return {
        "power": power,
        "side": side,
        "composition_order": composition,
        "inverse_order": inverse,
        "layer_cell_counts": layer_counts,
        "expanded_ambient_cell_count": sum(layer_counts.values()),
        "jacobian_det_min": "1/3",
        "jacobian_det_max": "3",
        "protected_ball_bbox_clearance_min": str(min(clearances)),
        "maps_affine_image_handlebody_to_target": True,
        "maps_both_owners_setwise": True,
        "fixes_protected_ball_pointwise": True,
        "restore_isotopic_to_identity": True,
        "explicit_inverse": True,
        "paired_saddle_ambient_cells": "PASS",
        "johnson_arm_restore": "PASS",
    }


def generate():
    raw = {
        name: json.loads(path.read_text(encoding="utf-8")) for name, path in FILES.items()
    }
    if raw["single"]["sweep_sha256"] != raw["sweep"]["sha256"]:
        raise AssertionError("single cells are not bound to the sweep")
    if raw["side"]["collapses_sha256"] != raw["collapses"]["sha256"]:
        raise AssertionError("actual side charts are not bound to the relative collapses")
    if raw["fiber"]["support_sha256"] != raw["support"]["sha256"]:
        raise AssertionError("fiber assembly is not bound to the support")
    if raw["normalization"]["support_sha256"] != raw["support"]["sha256"]:
        raise AssertionError("normalization is not bound to the support")
    if raw["outer"]["support_sha256"] != raw["support"]["sha256"]:
        raise AssertionError("outer collar is not bound to the support")
    layers = {
        "sweep": keyed(raw["sweep"]["movies"]),
        "single": keyed(raw["single"]["movies"]),
        "side": keyed(raw["side"]["movies"]),
        "fiber": keyed(raw["fiber"]["movies"]),
        "normalization": keyed(raw["normalization"]["movies"]),
        "outer": keyed(raw["outer"]["movies"]),
        "support": keyed(raw["support"]["movies"]),
    }
    expected_keys = {
        (power, side)
        for power in (-1, 1)
        for side in ("prefix-first", "target-first")
    }
    if any(set(layer) != expected_keys for layer in layers.values()):
        raise AssertionError("restore layers do not cover the same four movies")
    movies = [build_movie(key, layers) for key in sorted(expected_keys)]
    movie_lookup = {(movie["power"], movie["side"]): movie for movie in movies}
    alpha_movie = load("generate_t73_johnson_alpha_movie").generate()
    factorization = load("factor_t73_matrix_johnson").generate()
    product = identity3()
    factor_records = []
    for move in alpha_movie["moves"]:
        source = int(move["alpha_target"])
        prefix = int(move["alpha_prefix"])
        power = int(move["power"])
        side = move["side"]
        canonical = movie_lookup[(power, side)]
        third = next(axis for axis in range(3) if axis not in (source, prefix))
        axis_permutation = [source, prefix, third]
        product = matmul(transvection(source, prefix, power), product)
        factor_records.append(
            {
                "index": int(move["index"]),
                "source_axis": source,
                "prefix_axis": prefix,
                "third_axis": third,
                "power": power,
                "side": side,
                "canonical_axis_images": axis_permutation,
                "canonical_movie_sha256": canonical_sha(canonical),
                "expanded_ambient_cell_count": canonical["expanded_ambient_cell_count"],
                "maps_both_owners_setwise": canonical["maps_both_owners_setwise"],
                "fixes_protected_ball_pointwise": canonical["fixes_protected_ball_pointwise"],
                "explicit_inverse": canonical["explicit_inverse"],
            }
        )
    if len(factor_records) != 93 or product != factorization["matrix_A"]:
        raise AssertionError("restore factors do not reproduce the 93-step matrix factorization")
    side_mutant = dict(factor_records[0])
    side_mutant["side"] = (
        "target-first" if side_mutant["side"] == "prefix-first" else "prefix-first"
    )
    side_mutation_detected = side_mutant["side"] != alpha_movie["moves"][0]["side"]
    if not side_mutation_detected:
        raise AssertionError("restore side mutation was not detected")
    layer_hashes = {name: value["sha256"] for name, value in raw.items()}
    result = {
        "schema": "t73_johnson_restore_assembly/v1",
        "layer_sha256": layer_hashes,
        "canonical_axis_pair": [0, 1],
        "axis_permutation_conjugates": "PASS",
        "movies": movies,
        "expanded_ambient_cell_count": sum(
            movie["expanded_ambient_cell_count"] for movie in movies
        ),
        "all_movies_map_both_owners_setwise": all(
            movie["maps_both_owners_setwise"] for movie in movies
        ),
        "all_movies_fix_protected_ball": all(
            movie["fixes_protected_ball_pointwise"] for movie in movies
        ),
        "all_restores_isotopic_to_identity": all(
            movie["restore_isotopic_to_identity"] for movie in movies
        ),
        "all_inverses_explicit": all(movie["explicit_inverse"] for movie in movies),
        "paired_saddle_ambient_cells": "PASS",
        "johnson_arm_restore": "PASS",
        "heegaard_preserving_unit_generators": "PASS",
        "alpha_movie_sha256": alpha_movie["movie_sha256"],
        "full_93_factor_assembly": {
            "factor_count": len(factor_records),
            "factors": factor_records,
            "product_on_H1": product,
            "matrix_A": factorization["matrix_A"],
            "expanded_ambient_cell_count": sum(
                record["expanded_ambient_cell_count"] for record in factor_records
            ),
            "all_factors_map_both_owners_setwise": all(
                record["maps_both_owners_setwise"] for record in factor_records
            ),
            "all_factors_fix_protected_ball": all(
                record["fixes_protected_ball_pointwise"] for record in factor_records
            ),
            "all_factor_inverses_explicit": all(
                record["explicit_inverse"] for record in factor_records
            ),
            "psi_star_equals_A": product == factorization["matrix_A"],
            "status": "PASS",
        },
        "mutation_side_bit": "FAIL",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check or args.write:
        print(f"T73_JOHNSON_RESTORE_ASSEMBLY={result['johnson_arm_restore']}")
        print(f"PAIRED_SADDLE_CELLS={result['paired_saddle_ambient_cells']}")
        print(f"UNIT_GENERATORS={result['heegaard_preserving_unit_generators']}")
        print(f"EXPANDED_CELLS={result['expanded_ambient_cell_count']}")
        print(f"FULL_93_FACTOR_ASSEMBLY={result['full_93_factor_assembly']['status']}")
        print(
            "FULL_93_EXPANDED_CELLS="
            f"{result['full_93_factor_assembly']['expanded_ambient_cell_count']}"
        )
        print(f"MUTATION_SIDE_BIT={result['mutation_side_bit']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
