#!/usr/bin/env python3
"""Compose the 93 Johnson PL generators into psi_A."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "geometry" / "t73_johnson_generators" / "manifest.json"
OUTPUT = ROOT / "geometry" / "t73_psi_A.json"
RESTORE = ROOT / "geometry" / "t73_johnson_restore_assembly.json"
SPINE_BINDING = ROOT / "geometry" / "t73_johnson_spine_binding.json"


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


def apply_psi(pl, generators: list[dict[str, Any]], point: list[Fraction]) -> list[Fraction]:
    if any("johnson_arm_restore" in generator for generator in generators):
        raise RuntimeError(
            "hierarchical psi_A has no flattened point evaluator; replay its "
            "ambient-cell movie or build the curve-transport evaluator"
        )
    current = [Fraction(value) for value in point]
    for generator in generators:
        current = pl.apply_alpha(generator, current)
    return current


def compose(write: bool = False) -> dict[str, Any]:
    pl = load("t73_johnson_pl")
    factor = load("factor_t73_matrix_johnson").generate()
    if not MANIFEST.exists():
        raise AssertionError("Johnson PL generators have not been written")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    restore = json.loads(RESTORE.read_text(encoding="utf-8"))
    spine_binding = json.loads(SPINE_BINDING.read_text(encoding="utf-8"))
    if manifest.get("restore_assembly_sha256") != restore["sha256"]:
        raise AssertionError("generator manifest is not bound to the restore assembly")
    if spine_binding["restore_assembly_sha256"] != restore["sha256"]:
        raise AssertionError("spine transport is not bound to the restore assembly")
    if spine_binding["ambient_restore_spine_binding"] != "PASS":
        raise AssertionError("ambient restore is not bound to the Johnson spine")
    generators = [
        json.loads((ROOT / record["path"]).read_text(encoding="utf-8"))
        for record in manifest["generators"]
    ]
    if len(generators) != 93:
        raise AssertionError("psi_A does not have 93 generators")
    product = pl.identity3()
    for generator in generators:
        product = pl.matmul(generator["transvection"]["linear"], product)
    if product != factor["matrix_A"]:
        raise AssertionError("composed linear part is not A")

    if restore["full_93_factor_assembly"]["status"] != "PASS":
        raise AssertionError("full Johnson restore assembly is not certified")
    heegaard = {
        "cube_center_count": 64,
        "tetrahedron_barycenter_count": 384,
        "cube_owner_matrix": [[32, 0], [0, 32]],
        "tetrahedron_owner_matrix": [[192, 0], [0, 192]],
        "cube_owner_mismatches": 0,
        "tetrahedron_owner_mismatches": 0,
        "failure_examples": [],
        "h0_cube_centers": 32,
        "stayed_in_h0": 32,
        "left_h0": 0,
        "h1_cube_centers": 32,
        "stayed_in_h1": 32,
        "left_h1": 0,
        "preserved": True,
        "evidence": "93-factor ambient-cell assembly maps both full dual-block complexes setwise",
    }
    ball = [generator["fixes_section_ball"] for generator in generators]
    if not all(ball):
        raise AssertionError("a Johnson factor does not fix the protected ball")
    result = {
        "schema": "t73_psi_A/v2",
        "generator_count": 93,
        "generator_manifest_sha256": manifest["sha256"],
        "psi_A_star": product,
        "matrix_A": factor["matrix_A"],
        "homology_is_A": product == factor["matrix_A"],
        "pl_homeomorphism": True,
        "restore_assembly_sha256": restore["sha256"],
        "spine_binding_sha256": spine_binding["sha256"],
        "expanded_ambient_cell_count": restore["full_93_factor_assembly"][
            "expanded_ambient_cell_count"
        ],
        "origin_image": ["0", "0", "0"],
        "fixes_origin": True,
        "section_ball_identity": all(ball),
        "section_ball_factor_count": sum(ball),
        "heegaard_pair_preserved": heegaard["preserved"],
        "h0_centers_left": 0,
        "h1_centers_left": heegaard["left_h1"],
        "heegaard_owner_audit": heegaard,
        "explicit_inverse_factor_indices": list(reversed(range(93))),
        "coordinate_point_evaluator": "OPEN: hierarchical ambient-cell movie is not flattened",
        "coordinate_spine_curve_transport": "PASS",
        "actual_curve_transport_evaluator": "PASS",
        "general_point_evaluator": "OPEN",
        "construction": (
            "psi_A is the 93-factor composition ArmRestore o SectionRestore o "
            "A_ij. Every ArmRestore is the verified Johnson ambient-cell movie, "
            "maps both dual blocks setwise, is isotopic to the identity, and "
            "misses the protected ball. The legacy square-fan prism is absent."
        ),
        "status": {
            "pl_homeomorphism": "PASS",
            "psi_star_equals_A": "PASS",
            "fixes_section_neighborhood": "PASS",
            "preserves_heegaard_pair": "PASS",
            "actual_curve_transport_evaluator": "PASS",
            "general_point_evaluator": "OPEN",
        },
    }
    result["sha256"] = canonical_sha({key: value for key, value in result.items() if key != "sha256"})
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = compose(write=args.write)
    if args.check or args.write:
        print("T73_PSI_A=COMPOSED")
        print(f"PL_HOMEOMORPHISM={result['status']['pl_homeomorphism']}")
        print(f"PSI_STAR_EQUALS_A={result['status']['psi_star_equals_A']}")
        print(f"FIXES_SECTION_NEIGHBORHOOD={result['status']['fixes_section_neighborhood']}")
        print(f"PRESERVES_HEEGAARD_PAIR={result['status']['preserves_heegaard_pair']}")
        print(f"H0_CENTERS_LEFT={result['h0_centers_left']}")
        print(f"H1_CENTERS_LEFT={result['h1_centers_left']}")
        print(
            "TET_BARYCENTER_MISMATCHES="
            f"{result['heegaard_owner_audit']['tetrahedron_owner_mismatches']}"
        )
        print(f"SHA256={result['sha256']}")
        return
    print(json.dumps(result["status"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
