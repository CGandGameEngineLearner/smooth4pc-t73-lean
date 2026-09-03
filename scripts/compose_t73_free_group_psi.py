#!/usr/bin/env python3
"""Compose the trace-73 Nielsen moves as an exact F_3 automorphism."""

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


def inverse_word(word: list[int]) -> list[int]:
    return [-letter for letter in reversed(word)]


def reduce_word(word: list[int]) -> list[int]:
    stack: list[int] = []
    for letter in word:
        if stack and stack[-1] == -letter:
            stack.pop()
        else:
            stack.append(letter)
    return stack


def apply_map(mapping: list[list[int]], word: list[int]) -> list[int]:
    out: list[int] = []
    for letter in word:
        image = mapping[abs(letter) - 1]
        out.extend(image if letter > 0 else inverse_word(image))
    return reduce_word(out)


def compose(outer: list[list[int]], inner: list[list[int]]) -> list[list[int]]:
    return [apply_map(outer, image) for image in inner]


def identity_map() -> list[list[int]]:
    return [[1], [2], [3]]


def factor_map(operation: dict[str, Any]) -> list[list[int]]:
    images = identity_map()
    if operation["kind"] == "add":
        target, source, coefficient = operation["target"], operation["source"], operation["coefficient"]
        prefix = [target + 1] * coefficient if coefficient > 0 else [-(target + 1)] * (-coefficient)
        images[source] = prefix + [source + 1]
    elif operation["kind"] == "swap":
        i, j = operation["rows"]
        images[i], images[j] = images[j], images[i]
    elif operation["kind"] == "negate":
        row = operation["row"]
        images[row] = [-(row + 1)]
    else:
        raise AssertionError(f"unknown Nielsen operation {operation}")
    return images


def inverse_operation(operation: dict[str, Any]) -> dict[str, Any]:
    if operation["kind"] == "add":
        return {**operation, "coefficient": -operation["coefficient"]}
    return dict(operation)


def abelianization(mapping: list[list[int]]) -> list[list[int]]:
    matrix = [[0, 0, 0] for _ in range(3)]
    for column, image in enumerate(mapping):
        for letter in image:
            matrix[abs(letter) - 1][column] += 1 if letter > 0 else -1
    return matrix


def generate() -> dict[str, Any]:
    factor = load("factor_t73_matrix_nielsen")
    witness = factor.generate()
    total = identity_map()
    steps = []
    for index, operation in enumerate(witness["construction_operations"]):
        local = factor_map(operation)
        local_matrix = abelianization(local)
        expected_matrix = factor.apply(factor.identity(), operation)
        if local_matrix != expected_matrix:
            raise AssertionError(f"free-group factor has wrong abelianization at step {index}")
        total = compose(local, total)
        steps.append({
            "index": index,
            "operation": operation,
            "generator_images": local,
            "partial_images": total,
            "partial_abelianization": abelianization(total),
        })
    if abelianization(total) != factor.A:
        raise AssertionError("composed free-group automorphism does not abelianize to A")

    inverse_total = identity_map()
    for operation in reversed(witness["construction_operations"]):
        inverse_total = compose(factor_map(inverse_operation(operation)), inverse_total)
    left_inverse = compose(inverse_total, total)
    right_inverse = compose(total, inverse_total)
    if left_inverse != identity_map() or right_inverse != identity_map():
        raise AssertionError("constructed inverse does not invert the F_3 map")
    result: dict[str, Any] = {
        "schema": "t73_free_group_psi/v1",
        "generator_images": total,
        "inverse_generator_images": inverse_total,
        "abelianization": abelianization(total),
        "steps": steps,
        "left_inverse_check": left_inverse,
        "right_inverse_check": right_inverse,
        "free_group_automorphism_status": "PASS",
        "spine_thickening_status": "OPEN: the graph automorphism and route tubes are not yet assembled into a simplicial handlebody homeomorphism",
    }
    result["witness_sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = generate()
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check:
        print("T73_FREE_GROUP_PSI=PASS")
        print(f"AUTOMORPHISM_STATUS={result['free_group_automorphism_status']}")
        print(f"SPINE_THICKENING_STATUS={result['spine_thickening_status']}")
        print(f"WITNESS_SHA256={result['witness_sha256']}")
    elif not args.output:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
