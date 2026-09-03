#!/usr/bin/env python3
"""Audit whether the IA 44-channel correction is geometric or only based."""

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


def cyclic_reduce(word: list[int]) -> list[int]:
    out = word[:]
    while len(out) >= 2 and out[0] == -out[-1]:
        out = out[1:-1]
    return out


def cyclic_equivalent(left: list[int], right: list[int]) -> bool:
    left = cyclic_reduce(left)
    right = cyclic_reduce(right)
    return len(left) == len(right) and any(
        left == right[offset:] + right[:offset] for offset in range(max(1, len(right)))
    )


def generate() -> dict[str, Any]:
    free = load("compose_t73_free_group_psi")
    base = free.generate()["generator_images"]
    ia = load("search_t73_ia_representative").generate(max_length=1)
    conjugator = ia["conjugator"]
    inverse = free.inverse_word(conjugator)
    expected = [free.reduce_word(conjugator + image + inverse) for image in base]
    simultaneous = expected == ia["generator_images"]
    if not simultaneous:
        raise AssertionError("IA candidate is not the claimed simultaneous inner conjugate")
    cyclic_checks = []
    for index, (before, after) in enumerate(zip(base, ia["generator_images"])):
        before_cyclic = cyclic_reduce(before)
        after_cyclic = cyclic_reduce(after)
        cyclic_checks.append({
            "generator": index + 1,
            "before_cyclic": before_cyclic,
            "after_cyclic": after_cyclic,
            "same_cyclic_word": cyclic_equivalent(before_cyclic, after_cyclic),
        })
    if not all(check["same_cyclic_word"] for check in cyclic_checks):
        raise AssertionError("simultaneous conjugation changed a cyclic class")
    passage = load("compare_t73_nielsen_passages").generate()
    result: dict[str, Any] = {
        "schema": "t73_inner_conjugation_geometry_audit/v1",
        "conjugator": conjugator,
        "simultaneous_inner_conjugation": simultaneous,
        "cyclic_class_checks": cyclic_checks,
        "outer_automorphism_unchanged": True,
        "base_total_channels": passage["nielsen_representative"]["total_y_channels"],
        "based_ia_total_channels": ia["total_y_channels"],
        "channel_count_invariant_under_basepoint_change": passage["nielsen_representative"]["total_y_channels"] == ia["total_y_channels"],
        "geometric_verdict": "BASEPOINT_CHANGE_ONLY_NOT_AN_EMBEDDED_44_CHANNEL_WITNESS",
        "P0_global_status": "OPEN",
        "interpretation": "A simultaneous inner conjugation changes the based Aut(F3) representative but not the unbased outer class; the extra word passages are whisker data until an embedded movie proves otherwise.",
    }
    result["audit_sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.check:
        print("T73_INNER_CONJUGATION_GEOMETRY_AUDIT=PASS")
        print(f"OUTER_AUTOMORPHISM_UNCHANGED={result['outer_automorphism_unchanged']}")
        print(f"BASE_CHANNELS={result['base_total_channels']}")
        print(f"BASED_IA_CHANNELS={result['based_ia_total_channels']}")
        print(f"GEOMETRIC_VERDICT={result['geometric_verdict']}")
        print(f"AUDIT_SHA256={result['audit_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
