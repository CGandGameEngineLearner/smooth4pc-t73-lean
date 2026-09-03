#!/usr/bin/env python3
"""Search IA candidates satisfying a strict dual-meridian extension test."""

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


def disk_system_match(free: Any, cyclic: Any, mapping: list[list[int]]) -> dict[str, Any]:
    relators = [[1, 2, -1, -2], [2, 3, -2, -3], [3, 1, -3, -1]]
    images = [free.apply_map(mapping, relator) for relator in relators]
    matches = []
    for image in images:
        options = []
        for index, relator in enumerate(relators):
            if cyclic.cyclic_equivalent(image, relator):
                options.append([index, 1])
            if cyclic.cyclic_equivalent(image, free.inverse_word(relator)):
                options.append([index, -1])
        matches.append(options)
    permutations = []
    for first in matches[0]:
        for second in matches[1]:
            for third in matches[2]:
                if len({first[0], second[0], third[0]}) == 3:
                    permutations.append([first, second, third])
    return {
        "relator_images": images,
        "matches": matches,
        "signed_permutations": permutations,
        "sufficient_extension_pass": bool(permutations),
    }


def generate(max_depth: int = 3, max_states: int = 200000) -> dict[str, Any]:
    free = load("compose_t73_free_group_psi")
    search = load("search_t73_ia_framing")
    comparison = load("compare_t73_nielsen_passages")
    cyclic = load("audit_t73_inner_conjugation_geometry")
    compact = load("generate_t73_compact_kirby_ledger")
    base = free.generate()["generator_images"]
    inner = load("search_t73_ia_representative").generate(max_length=1)
    inner_m2 = inner["m2_after_cancellation"]
    generators = search.ia_generators(free)
    generator_by_name = dict(generators)
    inner_map = [[-1, 1, 1], [-1, 2, 1], [-1, 3, 1]]
    inner_control = disk_system_match(free, cyclic, inner_map)
    if not inner_control["sufficient_extension_pass"]:
        raise AssertionError("simultaneous inner-conjugation control failed disk-system test")

    conversion = {"x": 1, "y": 2, "z": 3, "X": -1, "Y": -2, "Z": -3}
    target = [conversion[letter] for letter in compact.after_x_cancellation(1)]
    target_area = search.commutator_area(target)
    queue = collections.deque([(free.identity_map(), [])])
    seen = {tuple(tuple(word) for word in free.identity_map())}
    detector_candidates = 0
    extension_candidates = []
    truncated = False
    while queue:
        correction, path = queue.popleft()
        images = free.compose(correction, base)
        m2 = comparison.after_x_cancellation(images[1], 1)
        detector_cyclic_class_changed = not cyclic.cyclic_equivalent(base[1], images[1])
        if (
            m2 != inner_m2
            and detector_cyclic_class_changed
            and len(m2) == 311
            and sum(abs(letter) == 2 for letter in m2) == 42
        ):
            detector_candidates += 1
            extension = disk_system_match(free, cyclic, correction)
            if extension["sufficient_extension_pass"]:
                extension_candidates.append({
                    "path": path,
                    "net_r_yz_coefficient": search.commutator_area(m2) - target_area,
                    "m2_sha256": canonical_sha(m2),
                    "extension": extension,
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
    result: dict[str, Any] = {
        "schema": "t73_dual_meridian_ia_search/v1",
        "max_depth": max_depth,
        "states_visited": len(seen),
        "search_truncated": truncated,
        "inner_positive_control": inner_control,
        "detector_cyclic_class_changed_44_channel_candidates": detector_candidates,
        "sufficient_dual_meridian_extension_candidates": extension_candidates,
        "verdict": "FOUND_SUFFICIENT_EXTENSION" if extension_candidates else "NONE_WITHIN_SEARCH",
        "scope": "The signed-permutation/conjugacy test is sufficient but not necessary; NONE does not prove global non-extension.",
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
        print("T73_DUAL_MERIDIAN_IA_SEARCH=PASS")
        print(f"STATES_VISITED={result['states_visited']}")
        print(f"DETECTOR_CANDIDATES={result['detector_cyclic_class_changed_44_channel_candidates']}")
        print(f"SUFFICIENT_EXTENSION_CANDIDATES={len(result['sufficient_dual_meridian_extension_candidates'])}")
        print(f"VERDICT={result['verdict']}")
        print(f"RECEIPT_SHA256={result['receipt_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
