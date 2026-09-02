#!/usr/bin/env python3
"""Verify rho(W)-I is uniformly order three on the full 88-space."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any


REPOSITORY = Path(__file__).resolve().parents[1]


def load_recompute() -> ModuleType:
    path = REPOSITORY / "scripts" / "recompute_t73_delta3.py"
    spec = importlib.util.spec_from_file_location("recompute_delta3", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import public recomputation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def full_word(module: ModuleType) -> list[int]:
    data = json.loads(
        (REPOSITORY / "data" / "T73_DELTA3_PUBLIC_INPUT.json").read_text(
            encoding="utf-8"
        )
    )
    word44, _ = module.build_oriented_b44(data)
    return module.cable_word(word44)


def low_order_failures(
    module: ModuleType, word: list[int], stop_after: int | None = None
) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for source in range(88):
        vector = module.sparse_vector(88, 3, [(source, 1)])
        output = module.delta_apply(word, vector)
        for target, polynomial in enumerate(output):
            if any(polynomial[degree] for degree in range(3)):
                failures.append(
                    {
                        "target": target,
                        "source": source,
                        "coefficients_0_to_2": polynomial[:3],
                    }
                )
                if stop_after is not None and len(failures) >= stop_after:
                    return failures
    return failures


def verify() -> dict[str, Any]:
    module = load_recompute()
    word = full_word(module)
    failures: list[dict[str, Any]] = []
    cubic_matrix = [[0 for _ in range(88)] for _ in range(88)]
    for source in range(88):
        vector = module.sparse_vector(88, 3, [(source, 1)])
        output = module.delta_apply(word, vector)
        for target, polynomial in enumerate(output):
            if any(polynomial[degree] for degree in range(3)):
                failures.append(
                    {
                        "target": target,
                        "source": source,
                        "coefficients_0_to_2": polynomial[:3],
                    }
                )
            cubic_matrix[target][source] = polynomial[3]
    if failures:
        raise AssertionError(f"rho(W)-I has a term below order three: {failures[0]}")
    nonzero = sum(value != 0 for row in cubic_matrix for value in row)
    return {
        "schema": "t73_uniform_endpoint_order3/v1",
        "dimension": 88,
        "basis_vectors_checked": 88,
        "matrix_entries_checked": 88 * 88,
        "orders_0_1_2_nonzero_entries": 0,
        "cubic_nonzero_entries": nonzero,
        "cubic_matrix_sha256": canonical_sha(cubic_matrix),
        "conclusion": "rho(W)-I lies in h^3 End(E_88) modulo h^4",
        "verdict": "PASS",
    }


def main() -> None:
    print(json.dumps(verify(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
