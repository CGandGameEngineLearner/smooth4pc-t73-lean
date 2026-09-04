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


def build_generator(index: int, movie_move: dict[str, Any], pl) -> dict[str, Any]:
    source = int(movie_move["alpha_target"])
    prefix = int(movie_move["alpha_prefix"])
    power = int(movie_move["power"])
    side = movie_move["side"]
    linear = pl.transvection_matrix(source, prefix, power)
    inverse_linear = pl.transvection_matrix(source, prefix, -power)
    if pl.det3(linear) != 1:
        raise AssertionError(f"generator {index} transvection is not Jacobian 1")
    square = movie_move["square_vertices"]
    target_vector = square[1]
    prefix_vector = square[2]
    straightening = pl.square_fan_cells(target_vector, prefix_vector, side)
    section_restore = pl.section_restore_certificate(source, prefix, power)
    generator = {
        "schema": "t73_johnson_pl_generator/v1",
        "index": index,
        "alpha_target": source,
        "alpha_prefix": prefix,
        "power": power,
        "side_bit": 0 if side == "prefix-first" else 1,
        "side": side,
        "cell_decomposition": {
            "complement": {
                "region": "T^3 minus the straightening prism",
                "affine": {
                    "linear": linear,
                    "translation": ["0", "0", "0"],
                    "jacobian_det": "1",
                    "inverse_linear": inverse_linear,
                },
            },
            "prism_cell_count": straightening["cell_count"],
            "section_restore_cell_count": section_restore["cell_count"],
        },
        "transvection": {
            "linear": linear,
            "inverse_linear": inverse_linear,
            "jacobian_det": 1,
        },
        "straightening": straightening,
        "section_restore": section_restore,
        "explicit_inverse": {
            "application_order": [
                "section_restore_inverse",
                "straightening_inverse",
                "transvection_inverse",
            ],
            "transvection": inverse_linear,
            "straightening_cells": straightening["inverse_cells"],
            "section_restore": section_restore["explicit_inverse"],
        },
        "jacobian_det_min": straightening["jacobian_det_min"],
        "jacobian_positive": True,
        "support": (
            "global affine transvection, relative square-fan prism, and a "
            "fixed-boundary section cutoff; the arm restore remains open"
        ),
        "protected_ball_disjointness": {
            "prism_misses_protected_ball": True,
            "clearance": straightening["protected_clearance"],
            "protected_radius": str(pl.PROTECTED_RADIUS),
        },
        "induced_transvection_on_H1": linear,
        "basis_matrix_before": movie_move["basis_matrix_before"],
        "square_vertices": movie_move["square_vertices"],
        "square_normal": movie_move["square_normal"],
    }
    heegaard = pl.heegaard_preservation(generator)
    ball = pl.section_ball_identity(generator)
    generator["heegaard_pair"] = heegaard
    generator["section_ball"] = ball
    generator["heegaard_pair_preserved"] = heegaard["preserved"]
    generator["fixes_section_ball"] = ball["identity"]
    generator["sha256"] = canonical_sha(
        {key: value for key, value in generator.items() if key != "sha256"}
    )
    return generator


def build_all(write: bool = False) -> dict[str, Any]:
    pl = load("t73_johnson_pl")
    movie = load("generate_t73_johnson_alpha_movie").generate()
    factor = load("factor_t73_matrix_johnson").generate()
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
        generator = build_generator(index, move, pl)
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
                "prism_cell_count": generator["straightening"]["cell_count"],
                "section_restore_cell_count": generator["section_restore"]["cell_count"],
                "jacobian_det_min": generator["jacobian_det_min"],
                "heegaard_pair_preserved": generator["heegaard_pair_preserved"],
                "fixes_section_ball": generator["fixes_section_ball"],
                "h0_centers_left": generator["heegaard_pair"]["left_h0"],
            }
        )
        if write:
            write_json(ROOT / path, generator)
    if product != factor["matrix_A"]:
        raise AssertionError("unit transvections no longer multiply to A")
    manifest = {
        "schema": "t73_johnson_pl_generators/v1",
        "count": 93,
        "protected_radius": str(pl.PROTECTED_RADIUS),
        "generators": records,
        "product_on_H1": product,
        "prism_cells_per_generator": records[0]["prism_cell_count"] if records else 0,
        "section_restore_cells_per_generator": (
            records[0]["section_restore_cell_count"] if records else 0
        ),
        "heegaard_preserved_count": heegaard_count,
        "section_ball_identity_count": ball_count,
        "heegaard_preserving_representative": "PASS" if heegaard_count == 93 else "OPEN",
        "section_ball_identity": "PASS" if ball_count == 93 else "OPEN",
        "construction": (
            "each generator currently has a global A_ij, the legacy relative "
            "square-fan prism, and an exact fixed-boundary PL cutoff that cancels "
            "A_ij on the protected ball. The missing arm-supported Johnson "
            "Restore is still required for setwise dual-block preservation."
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
        print(f"PRISM_CELLS={manifest['prism_cells_per_generator']}")
        print(f"SECTION_RESTORE_CELLS={manifest['section_restore_cells_per_generator']}")
        print(f"HEEGAARD_PRESERVING={manifest['heegaard_preserving_representative']}")
        print(f"HEEGAARD_PRESERVED_COUNT={manifest['heegaard_preserved_count']}")
        print(f"SECTION_BALL_IDENTITY={manifest['section_ball_identity']}")
        print(f"MANIFEST_SHA256={manifest['sha256']}")
        return
    print(json.dumps({"count": manifest["count"], "sha256": manifest["sha256"]}, indent=2))


if __name__ == "__main__":
    main()
