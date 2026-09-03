#!/usr/bin/env python3
"""Compare passage counts for the explicit Nielsen and compact AR words."""

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


def reduce_word(word: list[int]) -> list[int]:
    stack: list[int] = []
    for letter in word:
        if stack and stack[-1] == -letter:
            stack.pop()
        else:
            stack.append(letter)
    return stack


def after_x_cancellation(image: list[int], generator: int) -> list[int]:
    word = image + [-(generator + 1)]
    replaced = [3 if letter == 1 else -3 if letter == -1 else letter for letter in word]
    return reduce_word(replaced)


def count_axis(word: list[int], axis: int) -> int:
    return sum(abs(letter) == axis for letter in word)


def generate() -> dict[str, Any]:
    free_map = load("compose_t73_free_group_psi").generate()
    compact = load("generate_t73_compact_kirby_ledger")
    nielsen_m2 = after_x_cancellation(free_map["generator_images"][1], 1)
    compact_m2 = compact.after_x_cancellation(1)
    compact_m2_int = [{"x": 1, "y": 2, "z": 3, "X": -1, "Y": -2, "Z": -3}[letter] for letter in compact_m2]
    r_xy = [3, 2, -3, -2]
    nielsen = {
        "m2_length": len(nielsen_m2),
        "m2_y_passages": count_axis(nielsen_m2, 2),
        "r_xy_y_passages": count_axis(r_xy, 2),
        "total_y_channels": count_axis(nielsen_m2, 2) + count_axis(r_xy, 2),
        "m2_word_sha256": canonical_sha(nielsen_m2),
    }
    compact_record = {
        "m2_length": len(compact_m2_int),
        "m2_y_passages": count_axis(compact_m2_int, 2),
        "r_xy_y_passages": count_axis(r_xy, 2),
        "total_y_channels": count_axis(compact_m2_int, 2) + count_axis(r_xy, 2),
        "m2_word_sha256": canonical_sha(compact_m2_int),
    }
    if nielsen["m2_length"] != 309 or nielsen["total_y_channels"] != 42:
        raise AssertionError("unexpected Nielsen representative passage count")
    if compact_record["m2_length"] != 311 or compact_record["total_y_channels"] != 44:
        raise AssertionError("unexpected compact representative passage count")
    result: dict[str, Any] = {
        "schema": "t73_nielsen_passage_comparison/v1",
        "nielsen_representative": nielsen,
        "compact_representative": compact_record,
        "same_reduced_word": nielsen_m2 == compact_m2_int,
        "same_44_channel_count": nielsen["total_y_channels"] == compact_record["total_y_channels"],
        "current_nielsen_route_status": "FALSIFIED_FOR_PUBLIC_44_CHANNEL_COLLAR",
        "P0_global_status": "OPEN",
        "interpretation": "This falsifies the current explicit Nielsen representative as the public collar source; it does not rule out another AR representative connected by an explicit geometric movie.",
    }
    result["comparison_sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.check:
        print("T73_NIELSEN_PASSAGE_COMPARISON=PASS")
        print(f"NIELSEN_CHANNELS={result['nielsen_representative']['total_y_channels']}")
        print(f"COMPACT_CHANNELS={result['compact_representative']['total_y_channels']}")
        print(f"NIELSEN_ROUTE_STATUS={result['current_nielsen_route_status']}")
        print(f"P0_GLOBAL_STATUS={result['P0_global_status']}")
        print(f"COMPARISON_SHA256={result['comparison_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
