#!/usr/bin/env python3
"""Construct the word-level Kirby movie from the IA AR candidate to compact m2."""

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


def generate() -> dict[str, Any]:
    ia = load("search_t73_ia_representative").generate(max_length=1)
    compact = load("generate_t73_compact_kirby_ledger")
    word_tools = load("construct_t73_word_kirby_movie")
    conversion = {"x": 1, "y": 2, "z": 3, "X": -1, "Y": -2, "Z": -3}
    source = ia["m2_after_cancellation"]
    target = [conversion[letter] for letter in compact.after_x_cancellation(1)]
    normal_source, source_moves = word_tools.normalize(source)
    normal_target, target_moves = word_tools.normalize(target)
    if normal_source != normal_target:
        raise AssertionError("IA and compact words have different collected forms")
    if word_tools.replay(source, source_moves) != normal_source:
        raise AssertionError("IA normalization replay failed")
    if word_tools.replay(normal_target, target_moves, reverse=True) != target:
        raise AssertionError("compact reverse replay failed")
    combined = (
        [{"direction": "forward", **move} for move in source_moves]
        + [{"direction": "reverse", **move} for move in reversed(target_moves)]
    )
    replayed = word_tools.replay(word_tools.replay(source, source_moves), target_moves, reverse=True)
    if replayed != target:
        raise AssertionError("IA-to-compact movie replay failed")
    result: dict[str, Any] = {
        "schema": "t73_ia_to_compact_movie/v1",
        "ia_witness_sha256": ia["witness_sha256"],
        "source_length": len(source),
        "target_length": len(target),
        "normal_form": normal_source,
        "source_moves": source_moves,
        "target_moves": target_moves,
        "combined_movie": combined,
        "r_yz_commutation_count": sum(move["kind"] == "commute_y_z" for move in combined),
        "free_bigon_move_count": sum(move["kind"] == "free_bigon" for move in combined),
        "word_movie_status": "PASS",
        "geometric_status": "OPEN: IA inner conjugation and r_yz bands need embedded owner/framing transport",
    }
    result["movie_sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.check:
        print("T73_IA_TO_COMPACT_MOVIE=PASS")
        print(f"SOURCE_LENGTH={result['source_length']}")
        print(f"TARGET_LENGTH={result['target_length']}")
        print(f"RYZ_COMMUTATIONS={result['r_yz_commutation_count']}")
        print(f"FREE_BIGONS={result['free_bigon_move_count']}")
        print(f"MOVIE_SHA256={result['movie_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
