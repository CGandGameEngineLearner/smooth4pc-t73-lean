#!/usr/bin/env python3
"""Search IA/inner corrections of the Nielsen AR representative for 44 channels."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
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


def reduced_words(max_length: int):
    letters = (1, -1, 2, -2, 3, -3)
    for length in range(1, max_length + 1):
        for raw in itertools.product(letters, repeat=length):
            if all(raw[i] != -raw[i + 1] for i in range(length - 1)):
                yield list(raw)


def generate(max_length: int = 2, gap_timeout: int = 300) -> dict[str, Any]:
    free = load("compose_t73_free_group_psi")
    comparison = load("compare_t73_nielsen_passages")
    compact = load("generate_t73_compact_kirby_ledger")
    gap = load("check_t73_compact_free_basis")
    base = free.generate()["generator_images"]
    conversion = {"x": 1, "y": 2, "z": 3, "X": -1, "Y": -2, "Z": -3}
    compact_m2 = [conversion[letter] for letter in compact.after_x_cancellation(1)]
    candidate = None
    for conjugator in reduced_words(max_length):
        inverse = free.inverse_word(conjugator)
        images = [free.reduce_word(conjugator + image + inverse) for image in base]
        m2 = comparison.after_x_cancellation(images[1], 1)
        if len(m2) == 311 and sum(abs(letter) == 2 for letter in m2) == 42:
            candidate = (conjugator, images, m2)
            break
    if candidate is None:
        raise AssertionError("no short IA/inner representative restores 44 channels")
    conjugator, images, m2 = candidate
    if free.abelianization(images) != free.abelianization(base):
        raise AssertionError("inner correction changed abelianization")
    gap_result = gap.gap_check(gap.int_words_to_letters(images), gap_timeout)
    if not gap_result["is_bijective"]:
        raise AssertionError("GAP rejected the IA-corrected representative")
    result: dict[str, Any] = {
        "schema": "t73_ia_representative_search/v1",
        "conjugator": conjugator,
        "generator_images": images,
        "abelianization": free.abelianization(images),
        "gap_is_bijective": True,
        "m2_after_cancellation": m2,
        "m2_length": len(m2),
        "m2_y_passages": sum(abs(letter) == 2 for letter in m2),
        "r_xy_y_passages": 2,
        "total_y_channels": sum(abs(letter) == 2 for letter in m2) + 2,
        "exact_compact_m2_match": m2 == compact_m2,
        "m2_sha256": canonical_sha(m2),
        "compact_m2_sha256": canonical_sha(compact_m2),
        "automorphism_channel_status": "PASS",
        "exact_public_representative_status": "PASS" if m2 == compact_m2 else "OPEN",
        "geometric_status": "OPEN: inner conjugation and subsequent word movie need an owner/framing-preserving embedded realization",
    }
    result["witness_sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-length", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate(args.max_length, args.timeout)
    if args.check:
        print("T73_IA_REPRESENTATIVE_SEARCH=PASS")
        print(f"CONJUGATOR={result['conjugator']}")
        print(f"GAP_IS_BIJECTIVE={result['gap_is_bijective']}")
        print(f"M2_LENGTH={result['m2_length']}")
        print(f"TOTAL_Y_CHANNELS={result['total_y_channels']}")
        print(f"EXACT_COMPACT_MATCH={result['exact_compact_m2_match']}")
        print(f"WITNESS_SHA256={result['witness_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
