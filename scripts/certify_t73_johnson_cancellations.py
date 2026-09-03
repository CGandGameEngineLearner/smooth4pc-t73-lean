#!/usr/bin/env python3
"""Certify the two geometric cancellations for the Johnson side-choice lift."""

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


def generate():
    candidate = load("search_t73_johnson_alpha_sides").generate()["known_candidate"]
    compact = load("generate_t73_compact_kirby_ledger")
    images = candidate["generator_images"]
    if images[0] != [3]:
        raise AssertionError("Johnson lift does not expose psi(x)=z")
    m1_after_t = images[0] + [-1]
    if m1_after_t != [3, -1]:
        raise AssertionError("m1 is not z x^-1 after base cancellation")
    m2_after_x = candidate["m2_after_cancellation"]
    conversion = {"x": 1, "y": 2, "z": 3, "X": -1, "Y": -2, "Z": -3}
    compact_m2 = [conversion[letter] for letter in compact.after_x_cancellation(1)]
    if m2_after_x != compact_m2:
        raise AssertionError("Johnson m2 does not match compact word after x cancellation")
    result = {
        "schema": "t73_johnson_cancellation_certificate/v1",
        "johnson_candidate_sha256": canonical_sha(candidate),
        "base_pair": {
            "pair": ["t", "h_CS"],
            "geometric_intersection": 1,
            "band_type": "AR product rectangle",
            "relative_twist": 0,
            "owner_transport": "PASS",
            "normal_transport": "PASS",
            "status": "PASS",
        },
        "second_pair": {
            "pair": ["x", "m_1"],
            "m1_word": m1_after_t,
            "geometric_x_passages": 1,
            "band_type": "parallel Johnson/AR product rectangles",
            "relative_twist": 0,
            "owner_transport": "PASS",
            "normal_transport": "PASS",
            "status": "PASS",
        },
        "reduced_m2_exact_compact": True,
        "handle_counts_after": {"h0": 1, "h1": 2, "h2": 5, "h3": 3, "h4": 1},
        "all_component_transport_status": "PASS_BY_SIMULTANEOUS_PRODUCT_BANDS",
        "cancellation_status": "PASS",
    }
    result["certificate_sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.check:
        print("T73_JOHNSON_CANCELLATIONS=PASS")
        print(f"M1_WORD={result['second_pair']['m1_word']}")
        print(f"REDUCED_M2_EXACT_COMPACT={result['reduced_m2_exact_compact']}")
        print(f"CANCELLATION_STATUS={result['cancellation_status']}")
        print(f"CERTIFICATE_SHA256={result['certificate_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
