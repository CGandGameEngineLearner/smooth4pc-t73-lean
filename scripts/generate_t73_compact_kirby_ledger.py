#!/usr/bin/env python3
"""Generate a compact marked word/framing ledger for the T73 handle link.

The ledger starts with the linear Cappell--Shaneson product-ribbon model.  It
uses rational crossing times to generate the three coordinate-image words,
performs the two registered product cancellations, and records the surviving
genus-two attaching words.  Geometry outside these word and product-framing
rules is deliberately not inferred from a planar blackboard projection.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any


MATRIX_A = (
    (0, 269, 1240),
    (0, 41, 189),
    (1, 0, 32),
)
AXES = ("x", "y", "z")


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def linear_crossing_word(column: int) -> list[str]:
    """Crossing word of the straight segment from 0 to ``A e_column``.

    Coincident integer-face events are separated by a fixed product
    perturbation: the terminal coordinate comes first and the remaining axes
    occur in descending cyclic order.  This keeps the terminal inverse visible
    before the registered cancellations.
    """

    vector = tuple(MATRIX_A[row][column] for row in range(3))
    tie_order = tuple((column - offset) % 3 for offset in range(3))
    rank = {axis: index for index, axis in enumerate(tie_order)}
    events: list[tuple[Fraction, int, str]] = []
    for axis, amount in enumerate(vector):
        if amount < 0:
            raise ValueError("this compact generator expects nonnegative A entries")
        for level in range(1, amount + 1):
            events.append((Fraction(level, amount), rank[axis], AXES[axis]))
    events.sort()
    return [letter for _, _, letter in events]


def inverse(letter: str) -> str:
    return letter.swapcase()


def free_reduce(word: list[str]) -> list[str]:
    stack: list[str] = []
    for letter in word:
        if stack and stack[-1] == inverse(letter):
            stack.pop()
        else:
            stack.append(letter)
    return stack


def exponent_sums(word: list[str]) -> dict[str, int]:
    counts = Counter()
    for letter in word:
        counts[letter.lower()] += 1 if letter.islower() else -1
    return {axis: counts[axis] for axis in AXES}


def mapping_torus_word(column: int) -> list[str]:
    terminal = AXES[column]
    return ["t"] + linear_crossing_word(column) + ["T", inverse(terminal)]


def after_base_cancellation(column: int) -> list[str]:
    return [letter for letter in mapping_torus_word(column) if letter.lower() != "t"]


def after_x_cancellation(column: int) -> list[str]:
    replaced = [
        ("z" if letter == "x" else "Z" if letter == "X" else letter)
        for letter in after_base_cancellation(column)
    ]
    return free_reduce(replaced)


def commutator(left: str, right: str) -> list[str]:
    return [left, right, inverse(left), inverse(right)]


def word_record(word: list[str]) -> dict[str, Any]:
    return {
        "length": len(word),
        "exponent_sums": exponent_sums(word),
        "sha256": canonical_sha(word),
        "prefix": word[:12],
        "suffix": word[-12:],
    }


def generate_ledger() -> dict[str, Any]:
    before = {f"m_{column + 1}": mapping_torus_word(column) for column in range(3)}
    after_t = {f"m_{column + 1}": after_base_cancellation(column) for column in range(3)}
    after_x = {f"m_{column + 1}": after_x_cancellation(column) for column in range(3)}

    if after_t["m_1"] != ["z", "X"]:
        raise AssertionError("first cancellation did not expose m_1=z x^-1")
    if after_x["m_1"]:
        raise AssertionError("second cancellation did not remove m_1")
    if len(after_x["m_2"]) != 311 or exponent_sums(after_x["m_2"]) != {
        "x": 0,
        "y": 40,
        "z": 269,
    }:
        raise AssertionError("unexpected reduced m_2 ledger")
    if len(after_x["m_3"]) != 1460 or exponent_sums(after_x["m_3"]) != {
        "x": 0,
        "y": 189,
        "z": 1271,
    }:
        raise AssertionError("unexpected reduced m_3 ledger")

    r_xy = ["z" if value == "x" else "Z" if value == "X" else value
            for value in commutator("x", "y")]
    r_yz = commutator("y", "z")
    r_zx = free_reduce([
        "z" if value == "x" else "Z" if value == "X" else value
        for value in commutator("z", "x")
    ])
    if r_zx:
        raise AssertionError("r_zx did not reduce by the two product bigons")

    ledger = {
        "schema": "t73_compact_marked_kirby_ledger/v1",
        "matrix": [list(row) for row in MATRIX_A],
        "linear_word_rule": {
            "events": "axis k occurs at rational time k/(A e_j)_axis",
            "tie_break": "terminal axis j first, then axes j-1,j-2 modulo 3",
            "framing": "Aitchison--Rubinstein product-annulus normal",
        },
        "mapping_torus_words": {name: word_record(word) for name, word in before.items()},
        "cancellations": [
            {
                "pair": ["t", "h_CS"],
                "rule": "delete t/T passages through product rerouting strips",
                "relative_twist": 0,
            },
            {
                "pair": ["x", "m_1"],
                "exposed_word": ["z", "X"],
                "rule": "replace x/X by z/Z and freely cancel the product bigon",
                "relative_twist": 0,
            },
        ],
        "surviving_components": {
            "r_xy": word_record(r_xy),
            "r_yz": word_record(r_yz),
            "r_zx": {
                "word": [],
                "framing": "zero relative to the transported product disk",
                "empty_free_word": True,
                "split_unknot": False,
                "embedding": "OPEN: an empty cancelled word is not an embedded split unknot",
            },
            "m_2": word_record(after_x["m_2"]),
            "m_3": word_record(after_x["m_3"]),
        },
        "marking_policy": {
            "component_labels": ["r_xy", "r_yz", "r_zx", "m_2", "m_3"],
            "owner_cocore_labels": "transported with each product ribbon",
            "blackboard_framing_used": False,
        },
        "scope": (
            "compact AR-side marked word and product-framing ledger; the local "
            "six-sweep collar is verified separately"
        ),
    }
    ledger["ledger_sha256"] = canonical_sha(ledger)
    return ledger


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    ledger = generate_ledger()
    if args.check:
        print("T73_COMPACT_KIRBY_LEDGER=PASS")
        print(f"LEDGER_SHA256={ledger['ledger_sha256']}")
        return
    print(json.dumps(ledger, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
