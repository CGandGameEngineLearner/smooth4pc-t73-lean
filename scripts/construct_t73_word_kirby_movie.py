#!/usr/bin/env python3
"""Construct an exact relator movie between Nielsen and compact m2 words."""

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


def normalize(word: list[int]) -> tuple[list[int], list[dict[str, Any]]]:
    current = word[:]
    moves: list[dict[str, Any]] = []
    changed = True
    while changed:
        changed = False
        for index in range(len(current) - 1):
            if abs(current[index]) == 3 and abs(current[index + 1]) == 2:
                before = current[index : index + 2]
                current[index], current[index + 1] = current[index + 1], current[index]
                moves.append({
                    "kind": "commute_y_z",
                    "index": index,
                    "before": before,
                    "after": current[index : index + 2],
                    "relator_owner": "r_yz",
                })
                changed = True
    index = 0
    while index < len(current) - 1:
        if current[index] == -current[index + 1]:
            pair = current[index : index + 2]
            del current[index : index + 2]
            moves.append({"kind": "free_bigon", "index": index, "pair": pair})
            index = max(0, index - 1)
        else:
            index += 1
    return current, moves


def replay(word: list[int], moves: list[dict[str, Any]], reverse: bool = False) -> list[int]:
    current = word[:]
    iterable = reversed(moves) if reverse else moves
    for move in iterable:
        index = move["index"]
        if move["kind"] == "commute_y_z":
            expected = move["after"] if reverse else move["before"]
            replacement = move["before"] if reverse else move["after"]
            if current[index : index + 2] != expected:
                raise AssertionError("commutation replay mismatch")
            current[index : index + 2] = replacement
        elif move["kind"] == "free_bigon":
            if reverse:
                current[index:index] = move["pair"]
            else:
                if current[index : index + 2] != move["pair"]:
                    raise AssertionError("bigon replay mismatch")
                del current[index : index + 2]
        else:
            raise AssertionError(f"unknown word movie move {move}")
    return current


def words() -> tuple[list[int], list[int]]:
    comparison = load("compare_t73_nielsen_passages")
    free_map = load("compose_t73_free_group_psi").generate()
    compact = load("generate_t73_compact_kirby_ledger")
    nielsen = comparison.after_x_cancellation(free_map["generator_images"][1], 1)
    conversion = {"x": 1, "y": 2, "z": 3, "X": -1, "Y": -2, "Z": -3}
    compact_word = [conversion[letter] for letter in compact.after_x_cancellation(1)]
    return nielsen, compact_word


def generate() -> dict[str, Any]:
    nielsen, compact = words()
    normal_nielsen, moves_nielsen = normalize(nielsen)
    normal_compact, moves_compact = normalize(compact)
    if normal_nielsen != normal_compact:
        raise AssertionError("representatives do not normalize to the same abelian word")
    if replay(nielsen, moves_nielsen) != normal_nielsen:
        raise AssertionError("Nielsen normalization replay failed")
    if replay(normal_compact, moves_compact, reverse=True) != compact:
        raise AssertionError("compact denormalization replay failed")
    movie = (
        [{"direction": "forward", **move} for move in moves_nielsen]
        + [{"direction": "reverse", **move} for move in reversed(moves_compact)]
    )
    current = replay(nielsen, moves_nielsen)
    current = replay(current, moves_compact, reverse=True)
    if current != compact:
        raise AssertionError("combined word-level Kirby movie failed")
    result: dict[str, Any] = {
        "schema": "t73_word_kirby_movie/v1",
        "nielsen_length": len(nielsen),
        "compact_length": len(compact),
        "normal_form": normal_nielsen,
        "normal_form_length": len(normal_nielsen),
        "nielsen_normalization_moves": moves_nielsen,
        "compact_normalization_moves": moves_compact,
        "combined_movie": movie,
        "r_yz_commutation_count": sum(move["kind"] == "commute_y_z" for move in movie),
        "free_bigon_move_count": sum(move["kind"] == "free_bigon" for move in movie),
        "word_movie_status": "PASS",
        "geometric_band_status": "OPEN: r_yz slide bands, owner transport, and product framing have not yet been embedded",
    }
    result["movie_sha256"] = canonical_sha(result)
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
        print("T73_WORD_KIRBY_MOVIE=PASS")
        print(f"NIELSEN_LENGTH={result['nielsen_length']}")
        print(f"COMPACT_LENGTH={result['compact_length']}")
        print(f"RYZ_COMMUTATIONS={result['r_yz_commutation_count']}")
        print(f"FREE_BIGONS={result['free_bigon_move_count']}")
        print(f"GEOMETRIC_BAND_STATUS={result['geometric_band_status']}")
        print(f"MOVIE_SHA256={result['movie_sha256']}")
    elif not args.output:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
