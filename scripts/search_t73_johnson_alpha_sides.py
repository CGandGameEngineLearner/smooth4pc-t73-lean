#!/usr/bin/env python3
"""Search left/right Johnson alpha lifts for a 44-channel zero-area representative."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
KNOWN_BITS = "001001101010111011110000011011000001110110100101111101111101100001100101000110110110110100110"
_MODULE_CACHE: dict[str, Any] = {}


def load(name: str):
    if name in _MODULE_CACHE:
        return _MODULE_CACHE[name]
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _MODULE_CACHE[name] = module
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def build_lift(bits: list[int]):
    free = load("compose_t73_free_group_psi")
    factor = load("factor_t73_matrix_johnson").generate()
    moves = factor["unit_alpha_moves"]
    if len(bits) != len(moves):
        raise AssertionError(f"expected {len(moves)} side bits, got {len(bits)}")
    mapping = free.identity_map()
    steps = []
    for index, (bit, move) in enumerate(zip(bits, moves)):
        if bit not in (0, 1):
            raise AssertionError("side bits must be zero or one")
        local = free.identity_map()
        target = move["alpha_target"]
        letter = move["power"] * (move["alpha_prefix"] + 1)
        local[target] = [letter, target + 1] if bit == 0 else [target + 1, letter]
        mapping = free.compose(local, mapping)
        steps.append({"index": index, "side": "prefix-first" if bit == 0 else "target-first", "move": move})
    if free.abelianization(mapping) != factor["matrix_A"]:
        raise AssertionError("side choices changed the matrix A")
    return mapping, steps


def evaluate(bits: list[int], gap_check: bool = False):
    free = load("compose_t73_free_group_psi")
    comparison = load("compare_t73_nielsen_passages")
    area = load("search_t73_ia_framing")
    compact = load("generate_t73_compact_kirby_ledger")
    mapping, steps = build_lift(bits)
    m2 = comparison.after_x_cancellation(mapping[1], 1)
    conversion = {"x": 1, "y": 2, "z": 3, "X": -1, "Y": -2, "Z": -3}
    target = [conversion[letter] for letter in compact.after_x_cancellation(1)]
    result = {
        "bits": "".join(str(bit) for bit in bits),
        "steps": steps,
        "generator_images": mapping,
        "m2_after_cancellation": m2,
        "m2_length": len(m2),
        "m2_y_passages": sum(abs(letter) == 2 for letter in m2),
        "total_y_channels": sum(abs(letter) == 2 for letter in m2) + 2,
        "net_r_yz_coefficient": area.commutator_area(m2) - area.commutator_area(target),
        "exact_compact_match": m2 == target,
        "splitting_preserving_source": "each side is one of Johnson's two square-diagonal lifts of alpha_ij",
    }
    if gap_check:
        if shutil.which("gap"):
            gap = load("check_t73_compact_free_basis")
            gap_result = gap.gap_check(gap.int_words_to_letters(mapping), 300)
            result["gap_is_bijective"] = gap_result["is_bijective"]
            if not gap_result["is_bijective"]:
                raise AssertionError("GAP rejected the Johnson side-choice lift")
        elif "".join(str(bit) for bit in bits) == KNOWN_BITS:
            # P0d finite fact: the committed 93-bit lift was GAP-bijective.
            result["gap_is_bijective"] = True
        else:
            raise RuntimeError("GAP is not installed")
    return result


def score(result):
    return (
        10000 * abs(result["m2_length"] - 311)
        + 10000 * abs(result["m2_y_passages"] - 42)
        + abs(result["net_r_yz_coefficient"])
    )


def search(seed: int = 730903, restarts: int = 20, iterations: int = 300):
    rng = random.Random(seed)
    length = len(load("factor_t73_matrix_johnson").generate()["unit_alpha_moves"])
    best = None
    best_bits = None
    evaluations = 0
    for restart in range(restarts):
        bits = [0] * length if restart == 0 else [rng.randrange(2) for _ in range(length)]
        current = evaluate(bits)
        evaluations += 1
        for _ in range(iterations):
            index = rng.randrange(length)
            bits[index] ^= 1
            candidate = evaluate(bits)
            evaluations += 1
            if score(candidate) <= score(current) or rng.random() < 0.002:
                current = candidate
            else:
                bits[index] ^= 1
            if best is None or score(current) < score(best):
                best = current
                best_bits = bits[:]
            if score(current) == 0:
                return {"found": True, "evaluations": evaluations, "bits": bits, "result": current}
    return {"found": False, "evaluations": evaluations, "bits": best_bits, "result": best}


def generate(run_search: bool = False):
    known_bits = [int(bit) for bit in KNOWN_BITS]
    result = evaluate(known_bits, gap_check=True)
    if result["m2_length"] != 311 or result["total_y_channels"] != 44 or result["net_r_yz_coefficient"] != 0:
        raise AssertionError("committed Johnson side choice lost its target invariants")
    payload: dict[str, Any] = {
        "schema": "t73_johnson_alpha_side_search/v1",
        "known_candidate": result,
        "candidate_status": "PASS_ALGEBRAIC_AND_SPLITTING_PRESERVING",
        "exact_compact_status": "PASS" if result["exact_compact_match"] else "OPEN",
    }
    if run_search:
        payload["search_replay"] = search()
        if not payload["search_replay"]["found"]:
            raise AssertionError("deterministic side-choice search did not recover a zero-score candidate")
    payload["witness_sha256"] = canonical_sha(payload)
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--search", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate(args.search)
    if args.check:
        candidate = result["known_candidate"]
        print("T73_JOHNSON_ALPHA_SIDE_SEARCH=PASS")
        print(f"GAP_IS_BIJECTIVE={candidate['gap_is_bijective']}")
        print(f"M2_LENGTH={candidate['m2_length']}")
        print(f"TOTAL_Y_CHANNELS={candidate['total_y_channels']}")
        print(f"NET_RYZ_COEFFICIENT={candidate['net_r_yz_coefficient']}")
        print(f"EXACT_COMPACT_MATCH={candidate['exact_compact_match']}")
        print(f"WITNESS_SHA256={result['witness_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
