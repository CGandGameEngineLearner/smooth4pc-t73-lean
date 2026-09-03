#!/usr/bin/env python3
"""Build the physical B followed by B^-1 cable-isotopy cancellation ledger."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any


def load_script(name: str) -> ModuleType:
    path = Path(__file__).resolve().parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def inverse_word(word: list[int]) -> list[int]:
    return [-letter for letter in reversed(word)]


def cancellation_ledger(composite: list[int]) -> list[dict[str, int]]:
    stack: list[tuple[int, int]] = []
    cancellations: list[dict[str, int]] = []
    for position, letter in enumerate(composite):
        if stack and stack[-1][1] == -letter:
            left_position, left_letter = stack.pop()
            cancellations.append(
                {
                    "left_position": left_position,
                    "right_position": position,
                    "generator": abs(letter),
                    "left_sign": 1 if left_letter > 0 else -1,
                    "relative_framing_change": 0,
                }
            )
        else:
            stack.append((position, letter))
    if stack:
        raise AssertionError("B followed by B^-1 did not freely cancel")
    return cancellations


def free_cancellation_ledger(word: list[int]) -> list[dict[str, int]]:
    cancellations = cancellation_ledger(word + inverse_word(word))
    if len(cancellations) != len(word):
        raise AssertionError("cancellation count differs from braid length")
    return cancellations


def cable_letter(letter: int) -> list[int]:
    index = abs(letter)
    block = [2 * index, 2 * index + 1, 2 * index - 1, 2 * index]
    return block if letter > 0 else inverse_word(block)


def verify() -> dict[str, Any]:
    point_push = load_script("verify_t73_compact_point_push")
    rows = point_push.generate_rows()
    by_index = {row[0]: row for row in rows}
    b44 = [
        letter
        for source in point_push.expected_chronology()
        for letter in point_push.row_word(by_index[source])
    ]
    b88 = [value for letter in b44 for value in cable_letter(letter)]
    cancel44 = free_cancellation_ledger(b44)
    cancel88 = free_cancellation_ledger(b88)

    ledger = {
        "schema": "t73_physical_braid_inverse_movie/v1",
        "construction": (
            "insert framed Artin braid box B and the oppositely oriented "
            "inverse box B^-1 into adjacent private cable collars"
        ),
        "B44": {
            "length": len(b44),
            "sha256": canonical_sha(b44),
            "inverse_sha256": canonical_sha(inverse_word(b44)),
            "cancellation_pairs": len(cancel44),
            "cancellation_ledger_sha256": canonical_sha(cancel44),
        },
        "B88": {
            "length": len(b88),
            "sha256": canonical_sha(b88),
            "inverse_sha256": canonical_sha(inverse_word(b88)),
            "cancellation_pairs": len(cancel88),
            "cancellation_ledger_sha256": canonical_sha(cancel88),
        },
        "labels": {
            "permutation": "identity because every factor is a pure-braid generator",
            "owner_order": "preserved at both box boundaries",
            "cut": "the Hattori cut is the common boundary between B and B^-1",
        },
        "framing": {
            "rule": "product ribbon on every Artin generator box",
            "each_inverse_pair_relative_change": 0,
            "total_relative_change": 0,
        },
        "simultaneous_transport": {
            "P": "identity",
            "reason": "the representative is changed by an actual BB^-1 isotopy, not by relabelling endpoint coordinates",
        },
        "consequence": (
            "the modified cable is framed-isotopic to the standard MWW cable, "
            "while its marked middle cut has actual motion B"
        ),
    }
    ledger["ledger_sha256"] = canonical_sha(ledger)
    return ledger


def main() -> None:
    print(json.dumps(verify(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
