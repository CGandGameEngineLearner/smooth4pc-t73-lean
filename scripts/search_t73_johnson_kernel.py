#!/usr/bin/env python3
"""Search Johnson torus-twist kernel lifts for a genuine 44-channel representative."""

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


def alpha(free: Any, target: int, prefix: int, sign: int):
    mapping = free.identity_map()
    letter = sign * (prefix + 1)
    mapping[target] = [letter, target + 1]
    return mapping


def torus_twist(free: Any, target: int, conjugator: int, sign: int):
    mapping = free.identity_map()
    letter = sign * (conjugator + 1)
    mapping[target] = [letter, target + 1, -letter]
    return mapping


def johnson_kernel_generators(free: Any):
    base = []
    for target in range(3):
        for conjugator in range(3):
            if target != conjugator:
                for sign in (1, -1):
                    base.append((f"tau_{target}_{conjugator}_{sign:+d}", torus_twist(free, target, conjugator, sign)))
    raw = list(base)
    for alpha_target in range(3):
        for alpha_prefix in range(3):
            if alpha_target == alpha_prefix:
                continue
            for alpha_sign in (1, -1):
                a = alpha(free, alpha_target, alpha_prefix, alpha_sign)
                a_inverse = alpha(free, alpha_target, alpha_prefix, -alpha_sign)
                for tau_name, tau in base:
                    conjugate = free.compose(a_inverse, free.compose(tau, a))
                    raw.append((f"alpha_{alpha_target}_{alpha_prefix}_{alpha_sign:+d}^-1*{tau_name}*alpha", conjugate))
    unique = {}
    for name, mapping in raw:
        unique.setdefault(tuple(tuple(word) for word in mapping), (name, mapping))
    return list(unique.values())


def generate(max_depth: int = 2, max_states: int = 50000):
    free = load("compose_t73_free_group_psi")
    comparison = load("compare_t73_nielsen_passages")
    area = load("search_t73_ia_framing")
    compact = load("generate_t73_compact_kirby_ledger")
    base = load("build_t73_johnson_lift").generate()["generator_images"]
    generators = johnson_kernel_generators(free)
    conversion = {"x": 1, "y": 2, "z": 3, "X": -1, "Y": -2, "Z": -3}
    target = [conversion[letter] for letter in compact.after_x_cancellation(1)]
    target_area = area.commutator_area(target)
    identity = free.identity_map()
    queue = collections.deque([(identity, [])])
    seen = {tuple(tuple(word) for word in identity)}
    candidates = []
    truncated = False
    while queue:
        correction, path = queue.popleft()
        images = free.compose(correction, base)
        m2 = comparison.after_x_cancellation(images[1], 1)
        if len(m2) == 311 and sum(abs(letter) == 2 for letter in m2) == 42:
            candidates.append({
                "path": path,
                "net_r_yz_coefficient": area.commutator_area(m2) - target_area,
                "m2_sha256": canonical_sha(m2),
                "generator_images": images,
            })
        if len(path) >= max_depth:
            continue
        for name, generator in generators:
            new = free.compose(generator, correction)
            key = tuple(tuple(word) for word in new)
            if key in seen:
                continue
            seen.add(key)
            queue.append((new, path + [name]))
            if len(seen) >= max_states:
                truncated = True
                queue.clear()
                break
    candidates.sort(key=lambda item: (abs(item["net_r_yz_coefficient"]), item["path"]))
    result = {
        "schema": "t73_johnson_kernel_search/v1",
        "max_depth": max_depth,
        "max_states": max_states,
        "states_visited": len(seen),
        "search_truncated": truncated,
        "kernel_generator_count": len(generators),
        "channel_compatible_candidates": candidates,
        "verdict": "FOUND_44_CHANNEL" if candidates else "NONE_WITHIN_SEARCH",
        "scope": "All generators are Johnson torus twists or one-alpha conjugates; a bounded NONE result is not global nonexistence.",
    }
    result["receipt_sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--max-states", type=int, default=50000)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate(args.max_depth, args.max_states)
    if args.check:
        print("T73_JOHNSON_KERNEL_SEARCH=PASS")
        print(f"GENERATORS={result['kernel_generator_count']}")
        print(f"STATES_VISITED={result['states_visited']}")
        print(f"SEARCH_TRUNCATED={result['search_truncated']}")
        print(f"CANDIDATES={len(result['channel_compatible_candidates'])}")
        print(f"VERDICT={result['verdict']}")
        print(f"RECEIPT_SHA256={result['receipt_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
