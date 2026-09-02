#!/usr/bin/env python3
"""Exact degree-three Artin--Magnus certificate for the public pure braid."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np


REPOSITORY = Path(__file__).resolve().parents[1]
DIMENSION = 44


def load_recompute() -> ModuleType:
    path = REPOSITORY / "scripts" / "recompute_t73_delta3.py"
    spec = importlib.util.spec_from_file_location("recompute_delta3", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import public recomputation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def public_word() -> list[int]:
    module = load_recompute()
    data = json.loads(
        (REPOSITORY / "data" / "T73_DELTA3_PUBLIC_INPUT.json").read_text(
            encoding="utf-8"
        )
    )
    word, _ = module.build_oriented_b44(data)
    return word


def multiply(left, right):
    l1, q1, c1 = left
    l2, q2, c2 = right
    return (
        l1 + l2,
        q1 + q2 + np.einsum("i,j->ij", l1, l2, optimize=True),
        c1
        + c2
        + np.einsum("i,jk->ijk", l1, q2, optimize=True)
        + np.einsum("ij,k->ijk", q1, l2, optimize=True),
    )


def inverse(value):
    linear, quadratic, cubic = value
    return (
        -linear,
        -quadratic + np.einsum("i,j->ij", linear, linear, optimize=True),
        -cubic
        + np.einsum("i,jk->ijk", linear, quadratic, optimize=True)
        + np.einsum("ij,k->ijk", quadratic, linear, optimize=True)
        - np.einsum("i,j,k->ijk", linear, linear, linear, optimize=True),
    )


def copy_expansion(value):
    return tuple(coefficient.copy() for coefficient in value)


def artin_magnus(word: list[int]) -> tuple[list[tuple[np.ndarray, ...]], int]:
    images = []
    for generator in range(DIMENSION):
        linear = np.zeros(DIMENSION, dtype=np.int64)
        linear[generator] = 1
        images.append(
            (
                linear,
                np.zeros((DIMENSION, DIMENSION), dtype=np.int64),
                np.zeros((DIMENSION, DIMENSION, DIMENSION), dtype=np.int64),
            )
        )

    maximum = 1
    for letter in word:
        index = abs(letter) - 1
        left = images[index]
        right = images[index + 1]
        if letter > 0:
            new_left = multiply(multiply(left, right), inverse(left))
            new_right = copy_expansion(left)
        else:
            new_left = copy_expansion(right)
            new_right = multiply(multiply(inverse(right), left), right)
        images[index], images[index + 1] = new_left, new_right
        local_maximum = max(
            int(np.max(np.abs(coefficient))) for coefficient in new_left
        )
        maximum = max(maximum, local_maximum)
        if maximum >= np.iinfo(np.int64).max // 16:
            raise OverflowError("Magnus coefficient safety margin exhausted")
    return images, maximum


def verify() -> dict[str, Any]:
    word = public_word()
    images, maximum = artin_magnus(word)
    bad = {"linear": 0, "quadratic": 0, "cubic": 0}
    for generator, (linear, quadratic, cubic) in enumerate(images):
        expected = np.zeros(DIMENSION, dtype=np.int64)
        expected[generator] = 1
        bad["linear"] += int(np.count_nonzero(linear - expected))
        bad["quadratic"] += int(np.count_nonzero(quadratic))
        bad["cubic"] += int(np.count_nonzero(cubic))
    if any(bad.values()):
        raise AssertionError(f"Artin action is nontrivial through degree three: {bad}")
    return {
        "schema": "t73_exact_artin_magnus_gamma3/v1",
        "strand_count": DIMENSION,
        "artin_word_length": len(word),
        "free_generators_checked": DIMENSION,
        "magnus_degrees_checked": [1, 2, 3],
        "nonidentity_coefficients": bad,
        "maximum_intermediate_absolute_coefficient": maximum,
        "integer_storage_limit": int(np.iinfo(np.int64).max),
        "overflow_safety_factor_lower_bound": int(
            np.iinfo(np.int64).max // max(maximum, 1)
        ),
        "andreadakis_conclusion": (
            "the Artin automorphism is identity modulo Gamma_4(F_44)"
        ),
        "pure_braid_conclusion": (
            "by Darne Theorem 6.2 (Andreadakis equality), W lies in Gamma_3(P_44)"
        ),
        "cabling_conclusion": (
            "every physical cabling homomorphism sends W into Gamma_3 of the target pure braid group"
        ),
        "verdict": "PASS",
    }


def main() -> None:
    print(json.dumps(verify(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
