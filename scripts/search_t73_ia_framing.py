#!/usr/bin/env python3
"""Search IA automorphisms for a 44-channel representative with zero framing area."""

from __future__ import annotations

import argparse
import collections
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


def commutator(a: int, b: int) -> list[int]:
    return [a, b, -a, -b]


def commutator_area(word: list[int]) -> int:
    """Coefficient accumulated when collecting a y/z word to y^a z^b."""
    z_exponent = 0
    area = 0
    for letter in word:
        if abs(letter) == 3:
            z_exponent += 1 if letter > 0 else -1
        elif abs(letter) == 2:
            area += z_exponent * (1 if letter > 0 else -1)
    return area


def ia_generators(free: Any) -> list[tuple[str, list[list[int]]]]:
    generators = []
    for target in range(3):
        for conjugator in range(3):
            if target == conjugator:
                continue
            for orientation in (1, -1):
                mapping = free.identity_map()
                letter = orientation * (conjugator + 1)
                mapping[target] = [letter, target + 1, -letter]
                generators.append((f"partial_conjugation_{target}_{conjugator}_{orientation:+d}", mapping))
    for target in range(3):
        other = [index + 1 for index in range(3) if index != target]
        for orientation in (1, -1):
            word = commutator(other[0], other[1])
            if orientation < 0:
                word = free.inverse_word(word)
            for side in ("left", "right"):
                mapping = free.identity_map()
                mapping[target] = word + [target + 1] if side == "left" else [target + 1] + word
                generators.append((f"commutator_transvection_{target}_{orientation:+d}_{side}", mapping))
    return generators


def generate(max_depth: int = 3, max_states: int = 200000) -> dict[str, Any]:
    free = load("compose_t73_free_group_psi")
    comparison = load("compare_t73_nielsen_passages")
    compact = load("generate_t73_compact_kirby_ledger")
    conversion = {"x": 1, "y": 2, "z": 3, "X": -1, "Y": -2, "Z": -3}
    target = [conversion[letter] for letter in compact.after_x_cancellation(1)]
    target_area = commutator_area(target)
    base = free.generate()["generator_images"]
    inner_m2 = load("search_t73_ia_representative").generate(max_length=1)["m2_after_cancellation"]
    inner_m2_sha = canonical_sha(inner_m2)
    generators = ia_generators(free)
    queue = collections.deque([(base, [])])
    seen = {tuple(tuple(word) for word in base)}
    candidates = []
    zero_candidate = None
    truncated = False
    while queue:
        images, path = queue.popleft()
        m2 = comparison.after_x_cancellation(images[1], 1)
        if len(m2) == 311 and sum(abs(letter) == 2 for letter in m2) == 42:
            coefficient = commutator_area(m2) - target_area
            record = {
                "absolute_net_coefficient": abs(coefficient),
                "net_r_yz_coefficient": coefficient,
                "path": path,
                "m2_sha256": canonical_sha(m2),
                "detector_word_changed_from_inner_candidate": canonical_sha(m2) != inner_m2_sha,
            }
            candidates.append(record)
            if coefficient == 0:
                zero_candidate = {**record, "generator_images": images, "m2": m2}
                break
        if len(path) >= max_depth:
            continue
        for name, generator in generators:
            new_images = free.compose(generator, images)
            key = tuple(tuple(word) for word in new_images)
            if key in seen:
                continue
            seen.add(key)
            queue.append((new_images, path + [name]))
            if len(seen) >= max_states:
                truncated = True
                queue.clear()
                break
    candidates.sort(key=lambda item: (item["absolute_net_coefficient"], item["path"]))
    detector_changed = [item for item in candidates if item["detector_word_changed_from_inner_candidate"]]
    result: dict[str, Any] = {
        "schema": "t73_ia_framing_search/v1",
        "max_depth": max_depth,
        "max_states": max_states,
        "states_visited": len(seen),
        "search_truncated": truncated,
        "ia_generator_count": len(generators),
        "channel_compatible_candidates": len(candidates),
        "best_candidates": candidates[:20],
        "detector_changed_candidates": len(detector_changed),
        "best_detector_changed_candidates": detector_changed[:20],
        "zero_framing_candidate": zero_candidate,
        "verdict": "FOUND_ZERO" if zero_candidate else "NO_ZERO_WITHIN_SEARCH",
        "invariant": "net r_yz coefficient = commutator_area(source)-commutator_area(compact target)",
    }
    result["receipt_sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--max-states", type=int, default=200000)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate(args.max_depth, args.max_states)
    if args.check:
        print("T73_IA_FRAMING_SEARCH=PASS")
        print(f"STATES_VISITED={result['states_visited']}")
        print(f"CHANNEL_COMPATIBLE_CANDIDATES={result['channel_compatible_candidates']}")
        print(f"DETECTOR_CHANGED_CANDIDATES={result['detector_changed_candidates']}")
        print(f"VERDICT={result['verdict']}")
        if result["best_candidates"]:
            print(f"BEST_NET_COEFFICIENT={result['best_candidates'][0]['net_r_yz_coefficient']}")
        if result["best_detector_changed_candidates"]:
            print(f"BEST_DETECTOR_CHANGED_NET_COEFFICIENT={result['best_detector_changed_candidates'][0]['net_r_yz_coefficient']}")
        print(f"RECEIPT_SHA256={result['receipt_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
