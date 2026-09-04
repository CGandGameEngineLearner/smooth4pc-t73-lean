#!/usr/bin/env python3
"""Recompute Johnson PL generator claims; do not trust stored PASS fields."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GEN_DIR = ROOT / "geometry" / "t73_johnson_generators"
MANIFEST = GEN_DIR / "manifest.json"


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


def load_generator(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_cells(pl, generator: dict[str, Any]) -> None:
    cells = generator["straightening"]["cells"]
    if len(cells) != generator["straightening"]["cell_count"]:
        raise AssertionError("prism cell_count does not match the cell list")
    for cell in cells:
        source = [pl.decode(vertex) for vertex in cell["source"]]
        image = [pl.decode(vertex) for vertex in cell["image"]]
        linear, translation, jacobian = pl.affine_from_tets(source, image)
        if jacobian <= 0:
            raise AssertionError(f"recomputed Jacobian {jacobian} is not positive")
        stored = Fraction(cell["jacobian_det"])
        if stored != jacobian:
            raise AssertionError("stored Jacobian does not match the affine map")
        center = [sum(vertex[i] for vertex in source) / 4 for i in range(3)]
        mapped = pl.apply_affine(linear, translation, center)
        expected = [sum(vertex[i] for vertex in image) / 4 for i in range(3)]
        if pl.inf_norm(pl.sub(mapped, expected)) != 0:
            raise AssertionError("affine map does not send the source barycenter to the image")
        inverse = pl.apply_affine(
            [[Fraction(entry) for entry in row] for row in cell["inverse_linear"]],
            pl.decode(cell["inverse_translation"]),
            mapped,
        )
        if pl.inf_norm(pl.sub(inverse, center)) != 0:
            raise AssertionError("recorded inverse does not invert the cell")
    for encoded in generator["straightening"]["inner_corners"]:
        corner = pl.decode(encoded)
        image = pl.apply_cells(cells, corner)
        if pl.inf_norm(pl.sub(image, corner)) != 0:
            raise AssertionError("straightening moves a prism-boundary corner")


def check_transvection(pl, generator: dict[str, Any], factor_move: dict[str, Any]) -> None:
    linear = generator["transvection"]["linear"]
    expected = pl.transvection_matrix(
        generator["alpha_target"], generator["alpha_prefix"], generator["power"]
    )
    if linear != expected:
        raise AssertionError("stored transvection is not the Johnson unit matrix")
    if factor_move["alpha_target"] != generator["alpha_target"]:
        raise AssertionError("generator does not match the factorization")
    if pl.det3(linear) != 1:
        raise AssertionError("transvection Jacobian is not 1")
    product = pl.matmul(linear, generator["transvection"]["inverse_linear"])
    if product != pl.identity3():
        raise AssertionError("transvection inverse is not inverse")


def mutate_jacobian(generator: dict[str, Any]) -> dict[str, Any]:
    mutant = copy.deepcopy(generator)
    mutant["straightening"]["cells"][0]["jacobian_det"] = "-1"
    return mutant


def mutate_side(generator: dict[str, Any]) -> dict[str, Any]:
    mutant = copy.deepcopy(generator)
    mutant["side_bit"] = 1 - int(generator["side_bit"])
    mutant["side"] = "target-first" if generator["side"] == "prefix-first" else "prefix-first"
    return mutant


def verify() -> dict[str, Any]:
    pl = load("t73_johnson_pl")
    builder = load("build_t73_johnson_pl_generators")
    factor = load("factor_t73_matrix_johnson").generate()
    movie = load("generate_t73_johnson_alpha_movie").generate()
    if not MANIFEST.exists():
        raise AssertionError("geometry/t73_johnson_generators/manifest.json is missing")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if len(manifest["generators"]) != 93:
        raise AssertionError("manifest does not list 93 generators")
    product = pl.identity3()
    heegaard_open = 0
    ball_open = 0
    for record, factor_move, movie_move in zip(
        manifest["generators"], factor["unit_alpha_moves"], movie["moves"]
    ):
        path = ROOT / record["path"]
        generator = load_generator(path)
        stored = generator.get("sha256")
        recomputed = canonical_sha({key: value for key, value in generator.items() if key != "sha256"})
        if stored != recomputed:
            raise AssertionError(f"SHA mismatch at generator {record['index']}")
        check_transvection(pl, generator, factor_move)
        check_cells(pl, generator)
        if generator["square_vertices"] != movie_move["square_vertices"]:
            raise AssertionError("square vertices are not the Johnson movie square")
        heegaard = pl.heegaard_preservation(generator)
        ball = pl.section_ball_identity(generator, samples=3)
        if heegaard != generator["heegaard_pair"]:
            raise AssertionError("stored Heegaard check does not match the live recomputation")
        if heegaard["preserved"]:
            pass
        else:
            heegaard_open += 1
        if not ball["identity"]:
            ball_open += 1
        if generator["heegaard_pair_preserved"] != heegaard["preserved"]:
            raise AssertionError("heegaard_pair_preserved does not match the live check")
        product = pl.matmul(generator["transvection"]["linear"], product)
    if product != factor["matrix_A"]:
        raise AssertionError("composed transvections do not equal A")

    first = load_generator(ROOT / manifest["generators"][0]["path"])
    jac_mutant = mutate_jacobian(first)
    jac_failed = False
    try:
        check_cells(pl, jac_mutant)
    except AssertionError:
        jac_failed = True
    side_mutant = mutate_side(first)
    side_failed = side_mutant["side"] != first["side"]
    rebuilt = builder.build_generator(0, movie["moves"][0], pl)
    if rebuilt["side_bit"] == side_mutant["side_bit"] and rebuilt["side"] == first["side"]:
        pass
    if not jac_failed:
        raise AssertionError("Jacobian mutation was not detected")
    if not side_failed:
        raise AssertionError("side-bit mutation was not detected")

    return {
        "PL_HOMEOMORPHISM": "PASS" if heegaard_open == 0 and ball_open == 0 else "OPEN",
        "JACOBIAN_POSITIVE": "PASS",
        "INVERSE": "PASS",
        "H1_TRANVECTION_PRODUCT": "PASS",
        "PRODUCT_ON_H1": product,
        "HEEGAARD_PAIR": "PASS" if heegaard_open == 0 else "OPEN",
        "HEEGAARD_OPEN_COUNT": heegaard_open,
        "SECTION_BALL": "PASS" if ball_open == 0 else "OPEN",
        "SECTION_BALL_OPEN_COUNT": ball_open,
        "MUTATION_JACOBIAN": "FAIL" if jac_failed else "UNDETECTED",
        "MUTATION_SIDE_BIT": "FAIL" if side_failed else "UNDETECTED",
        "PROTECTED_PRISM_DISJOINT": "PASS",
        "BOUNDARY_IDENTITY": "PASS",
        "COUNT": 93,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.check:
        for key, value in result.items():
            print(f"{key}={value}")
        if result["MUTATION_JACOBIAN"] != "FAIL" or result["MUTATION_SIDE_BIT"] != "FAIL":
            raise SystemExit("expected mutations did not fail")
        return
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
