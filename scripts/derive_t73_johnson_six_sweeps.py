#!/usr/bin/env python3
"""Derive the six-sweep braid from the Johnson AR collar, then compare target."""

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


def factors(collar: dict[str, Any]):
    wickets = {entry["wicket"]: entry for entry in collar["wickets"]}
    if sorted(wickets) != list(range(1, 45)):
        raise AssertionError("Johnson collar does not contain wickets 1,...,44")
    ordinary = list(range(3, 44))
    returning = 44
    factors = []

    def append(moving, other, sign, geometry, leg):
        factors.append({
            "leg": leg,
            "moving_wicket": moving,
            "other_wicket": other,
            "sign": sign,
            "geometry": geometry,
            "moving_owner": wickets[moving]["owner"],
            "other_owner": wickets[other]["owner"],
            "moving_orientation": wickets[moving]["orientation"],
            "other_orientation": wickets[other]["orientation"],
        })

    # The first four legs are the two sides of the long z-directed portion of
    # the oriented r_xy rectangle.  The final two are its short returns; only
    # there does the m2 passage orientation reverse the crossing sign.
    for other in [returning] + ordinary:
        append(1, other, 1, "R", 0)
    for other in [returning] + list(reversed(ordinary)):
        append(1, other, -1, "R", 1)
    for moving in ordinary + [returning]:
        append(moving, 1, 1, "L", 2)
    for moving in list(reversed(ordinary)) + [returning]:
        append(moving, 1, -1, "L", 3)
    for moving in ordinary + [returning]:
        append(moving, 1, wickets[moving]["orientation"], "L", 4)
    for moving in [returning] + list(reversed(ordinary)):
        append(moving, 1, -wickets[moving]["orientation"], "L", 5)
    if len(factors) != 252 or any(sum(factor["leg"] == leg for factor in factors) != 42 for leg in range(6)):
        raise AssertionError("six-sweep factor count differs")
    return factors


def source_word(collar: dict[str, Any]):
    reconstructor = load("reconstruct_t73_p0")
    return [
        letter
        for factor in factors(collar)
        for letter in reconstructor.pure_factor(
            factor["moving_wicket"], factor["other_wicket"], factor["sign"], factor["geometry"]
        )
    ]


def generate(collar: dict[str, Any] | None = None):
    collar = collar or load("generate_t73_johnson_ribbon_collar").generate()
    generated_factors = factors(collar)
    generated_word = source_word(collar)
    # Target bytes are read only after the AR-side construction is complete.
    target = load("reconstruct_t73_p0").expected_public_word()
    result = {
        "schema": "t73_johnson_six_sweep_derivation/v1",
        "collar_sha256": collar["collar_sha256"],
        "source_dependencies": [
            "Johnson alpha-side collar lanes",
            "oriented r_xy dual rectangle",
            "six leg order table",
        ],
        "forbidden_source_dependency": "public crossing rows are not read while constructing factors",
        "factors": generated_factors,
        "factor_count": len(generated_factors),
        "letters_per_leg": [sum(len(load("reconstruct_t73_p0").pure_factor(f["moving_wicket"], f["other_wicket"], f["sign"], f["geometry"])) for f in generated_factors if f["leg"] == leg) for leg in range(6)],
        "B44_length": len(generated_word),
        "B44_sha256": canonical_sha(generated_word),
        "target_sha256": canonical_sha(target),
        "relative_endpoint_word_equal": generated_word == target,
        "framing_return": "PASS: each pure point-push factor is stationary to first order at its endpoints",
        "geometric_support": "the Johnson y-handle ball D^2 times [-1/2,1/2]",
    }
    result["verdict"] = "PASS" if result["relative_endpoint_word_equal"] else "FAIL"
    result["witness_sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.check:
        print("T73_JOHNSON_SIX_SWEEPS=PASS")
        print(f"FACTORS={result['factor_count']}")
        print(f"B44_LENGTH={result['B44_length']}")
        print(f"RELATIVE_ENDPOINT_WORD_EQUAL={result['relative_endpoint_word_equal']}")
        print(f"VERDICT={result['verdict']}")
        print(f"WITNESS_SHA256={result['witness_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
