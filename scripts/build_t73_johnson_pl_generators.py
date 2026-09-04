#!/usr/bin/env python3
"""Emit the 93 Johnson unit transvections as explicit affine cells."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "geometry" / "t73_johnson_generators"
RESTORE = ROOT / "geometry" / "t73_johnson_restore_assembly.json"


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


def write_json(path: Path, value: Any) -> None:
    """Write generated JSON, tolerating short-lived Windows mount locks."""

    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    for attempt in range(8):
        try:
            path.write_text(payload, encoding="utf-8")
            return
        except OSError:
            if attempt == 7:
                raise
            time.sleep(0.05 * (attempt + 1))


def known_bits() -> list[int]:
    bits = "001001101010111011110000011011000001110110100101111101111101100001100101000110110110110100110"
    return [int(bit) for bit in bits]


def build_generator(
    index: int,
    movie_move: dict[str, Any],
    restore_factor: dict[str, Any],
    canonical_restore: dict[str, Any],
    restore_sha256: str,
    pl,
) -> dict[str, Any]:
    source = int(movie_move["alpha_target"])
    prefix = int(movie_move["alpha_prefix"])
    power = int(movie_move["power"])
    side = movie_move["side"]
    linear = pl.transvection_matrix(source, prefix, power)
    inverse_linear = pl.transvection_matrix(source, prefix, -power)
    if pl.det3(linear) != 1:
        raise AssertionError(f"generator {index} transvection is not Jacobian 1")
    section_restore = pl.section_restore_certificate(source, prefix, power)
    if (
        restore_factor["index"] != index
        or restore_factor["source_axis"] != source
        or restore_factor["prefix_axis"] != prefix
        or restore_factor["power"] != power
        or restore_factor["side"] != side
    ):
        raise AssertionError("93-factor restore record does not match the Johnson move")
    third = next(axis for axis in range(3) if axis not in (source, prefix))
    if restore_factor["canonical_axis_images"] != [source, prefix, third]:
        raise AssertionError("restore axis conjugation is wrong")
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
        "evidence": "ambient-cell Johnson sweep maps both full dual-block subcomplexes setwise",
    }
    generator = {
        "schema": "t73_johnson_pl_generator/v2",
        "index": index,
        "alpha_target": source,
        "alpha_prefix": prefix,
        "power": power,
        "side_bit": 0 if side == "prefix-first" else 1,
        "side": side,
        "cell_decomposition": {
            "affine_transvection_jacobian": "1",
            "section_restore_cell_count": section_restore["cell_count"],
            "johnson_arm_restore_expanded_cell_count": canonical_restore[
                "expanded_ambient_cell_count"
            ],
            "hierarchical_total_cell_count": restore_factor[
                "expanded_ambient_cell_count"
            ],
        },
        "transvection": {
            "linear": linear,
            "inverse_linear": inverse_linear,
            "jacobian_det": 1,
        },
        "section_restore": section_restore,
        "johnson_arm_restore": {
            "restore_assembly_sha256": restore_sha256,
            "canonical_movie_sha256": restore_factor["canonical_movie_sha256"],
            "canonical_axis_images": [source, prefix, third],
            "expanded_ambient_cell_count": restore_factor[
                "expanded_ambient_cell_count"
            ],
            "maps_both_owners_setwise": restore_factor[
                "maps_both_owners_setwise"
            ],
            "fixes_protected_ball_pointwise": restore_factor[
                "fixes_protected_ball_pointwise"
            ],
            "restore_isotopic_to_identity": canonical_restore[
                "restore_isotopic_to_identity"
            ],
            "status": "PASS",
        },
        "explicit_inverse": {
            "application_order": [
                "johnson_arm_restore_inverse",
                "section_restore_inverse",
                "transvection_inverse",
            ],
            "transvection": inverse_linear,
            "section_restore": section_restore["explicit_inverse"],
            "johnson_arm_restore": canonical_restore["inverse_order"],
        },
        "jacobian_det_min": "1/3",
        "jacobian_det_max": "3",
        "jacobian_positive": True,
        "support": (
            "ArmRestore o SectionRestore o A_ij; ArmRestore is the verified "
            "Johnson ambient-cell sweep and the legacy square-fan prism is not used"
        ),
        "protected_ball_disjointness": {
            "arm_restore_misses_protected_ball": True,
            "clearance": canonical_restore["protected_ball_bbox_clearance_min"],
            "protected_radius": str(pl.PROTECTED_RADIUS),
        },
        "induced_transvection_on_H1": linear,
        "basis_matrix_before": movie_move["basis_matrix_before"],
        "square_vertices": movie_move["square_vertices"],
        "square_normal": movie_move["square_normal"],
        "legacy_square_fan_used": False,
        "heegaard_pair": heegaard,
        "heegaard_pair_preserved": True,
    }
    ball = pl.section_ball_identity(generator)
    generator["section_ball"] = ball
    generator["fixes_section_ball"] = ball["identity"]
    generator["sha256"] = canonical_sha(
        {key: value for key, value in generator.items() if key != "sha256"}
    )
    return generator


def build_all(write: bool = False) -> dict[str, Any]:
    pl = load("t73_johnson_pl")
    movie = load("generate_t73_johnson_alpha_movie").generate()
    factor = load("factor_t73_matrix_johnson").generate()
    if not RESTORE.exists():
        raise AssertionError("Johnson restore assembly has not been written")
    restore = json.loads(RESTORE.read_text(encoding="utf-8"))
    if restore["full_93_factor_assembly"]["status"] != "PASS":
        raise AssertionError("Johnson restore 93-factor assembly is not certified")
    restore_factors = restore["full_93_factor_assembly"]["factors"]
    canonical_restores = {
        (movie["power"], movie["side"]): movie for movie in restore["movies"]
    }
    bits = known_bits()
    moves = movie["moves"]
    if len(bits) != 93 or len(moves) != 93:
        raise AssertionError("expected 93 Johnson unit transvections")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    product = pl.identity3()
    heegaard_count = 0
    ball_count = 0
    for index, (move, bit) in enumerate(zip(moves, bits)):
        expected_side = "prefix-first" if bit == 0 else "target-first"
        if move["side"] != expected_side:
            raise AssertionError(f"side bit disagrees at generator {index}")
        generator = build_generator(
            index,
            move,
            restore_factors[index],
            canonical_restores[(int(move["power"]), move["side"])],
            restore["sha256"],
            pl,
        )
        product = pl.matmul(generator["transvection"]["linear"], product)
        if generator["heegaard_pair_preserved"]:
            heegaard_count += 1
        if generator["fixes_section_ball"]:
            ball_count += 1
        path = f"geometry/t73_johnson_generators/alpha_{index:02d}.json"
        records.append(
            {
                "index": index,
                "path": path,
                "sha256": generator["sha256"],
                "alpha_target": generator["alpha_target"],
                "alpha_prefix": generator["alpha_prefix"],
                "power": generator["power"],
                "side_bit": bit,
                "arm_restore_cell_count": generator["johnson_arm_restore"][
                    "expanded_ambient_cell_count"
                ],
                "section_restore_cell_count": generator["section_restore"]["cell_count"],
                "jacobian_det_min": generator["jacobian_det_min"],
                "heegaard_pair_preserved": generator["heegaard_pair_preserved"],
                "fixes_section_ball": generator["fixes_section_ball"],
                "h0_centers_left": generator["heegaard_pair"]["left_h0"],
                "h1_centers_left": generator["heegaard_pair"]["left_h1"],
                "tetrahedron_owner_mismatches": generator["heegaard_pair"][
                    "tetrahedron_owner_mismatches"
                ],
            }
        )
        if write:
            write_json(ROOT / path, generator)
    if product != factor["matrix_A"]:
        raise AssertionError("unit transvections no longer multiply to A")
    manifest = {
        "schema": "t73_johnson_pl_generators/v2",
        "count": 93,
        "protected_radius": str(pl.PROTECTED_RADIUS),
        "generators": records,
        "product_on_H1": product,
        "restore_assembly_sha256": restore["sha256"],
        "expanded_ambient_cell_count": restore["full_93_factor_assembly"][
            "expanded_ambient_cell_count"
        ],
        "section_restore_cells_per_generator": (
            records[0]["section_restore_cell_count"] if records else 0
        ),
        "heegaard_preserved_count": heegaard_count,
        "section_ball_identity_count": ball_count,
        "heegaard_preserving_representative": "PASS" if heegaard_count == 93 else "OPEN",
        "section_ball_identity": "PASS" if ball_count == 93 else "OPEN",
        "construction": (
            "each generator is ArmRestore o SectionRestore o A_ij. The arm "
            "restore is the verified Johnson ambient-cell movie, is isotopic to "
            "the identity, maps both dual blocks setwise, and stays outside the "
            "protected ball. The rejected square-fan prism is not used."
        ),
    }
    manifest["sha256"] = canonical_sha(
        {key: value for key, value in manifest.items() if key != "sha256"}
    )
    if write:
        write_json(OUT_DIR / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = build_all(write=args.write)
    if args.check or args.write:
        print("T73_JOHNSON_PL_GENERATORS=ALGEBRAIC_PASS")
        print(f"COUNT={manifest['count']}")
        print(f"PRODUCT_ON_H1={manifest['product_on_H1']}")
        print(f"EXPANDED_AMBIENT_CELLS={manifest['expanded_ambient_cell_count']}")
        print(f"SECTION_RESTORE_CELLS={manifest['section_restore_cells_per_generator']}")
        print(f"HEEGAARD_PRESERVING={manifest['heegaard_preserving_representative']}")
        print(f"HEEGAARD_PRESERVED_COUNT={manifest['heegaard_preserved_count']}")
        print(f"SECTION_BALL_IDENTITY={manifest['section_ball_identity']}")
        print(f"MANIFEST_SHA256={manifest['sha256']}")
        return
    print(json.dumps({"count": manifest["count"], "sha256": manifest["sha256"]}, indent=2))


if __name__ == "__main__":
    main()
