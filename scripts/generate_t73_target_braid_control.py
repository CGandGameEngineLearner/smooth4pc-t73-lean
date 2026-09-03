#!/usr/bin/env python3
"""Build a rational 44-strand realization of the public word as a control.

This is deliberately *not* an AR witness.  It is a calibration object for
the geometric crossing extractor: the public 11340-letter word is realized
by explicit piecewise-linear strands, then recovered independently from
their x-projection.  The AR passage-binding gate remains FAIL/OPEN.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RECONSTRUCTOR = ROOT / "scripts" / "reconstruct_t73_p0.py"


def load_reconstructor():
    spec = importlib.util.spec_from_file_location("reconstruct_t73_p0", RECONSTRUCTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load P0 reconstructor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def public_word(module: Any) -> list[int]:
    return module.expected_public_word()


def control_collar(module: Any, word: list[int] | None = None) -> dict[str, Any]:
    word = public_word(module) if word is None else word
    order = list(range(1, 45))
    paths: dict[int, list[list[int]]] = {strand: [[order.index(strand), 100 * strand, 0]] for strand in order}
    total = len(word)
    for step, letter in enumerate(word):
        generator = abs(letter) - 1
        left, right = order[generator], order[generator + 1]
        # A positive letter moves the left strand to the right; a negative
        # letter moves the right strand to the left.  This fixes the sign
        # convention used by reconstruct_t73_p0.py.
        moving, other = (left, right) if letter > 0 else (right, left)
        old_left, old_right = generator, generator + 1
        over = right if letter > 0 else left
        under = left if letter > 0 else right
        for strand in order:
            current_x = order.index(strand)
            swapped_x = old_right if strand == left else old_left if strand == right else current_x
            mid_y = 1 if strand == over else 0 if strand == under else 100 * strand
            baseline_y = 100 * strand
            paths[strand].append([current_x, mid_y, 4 * step + 1])
            paths[strand].append([swapped_x, mid_y, 4 * step + 3])
            paths[strand].append([swapped_x, baseline_y, 4 * step + 4])
        order[generator], order[generator + 1] = right, left

    strands = []
    for strand in range(1, 45):
        vertices = paths[strand]
        strands.append({
            "id": strand,
            "vertices": vertices,
            "normal_vectors": [[0, 1, 0] for _ in vertices],
        })
    return {
        "strands": strands,
        "pairwise_disjointness_certificate": {"status": "PASS", "kind": "control-only"},
        "normal_field_certificate": {"status": "PASS", "kind": "control-only"},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    module = load_reconstructor()
    collar = control_collar(module)
    events = module.derive_elementary_events(collar)
    target = public_word(module)
    recovered = [event["artin_letter"] for event in events]
    result = {
        "schema": "t73_target_braid_control/v1",
        "scope": "calibration only; not an AR passage binding",
        "strand_count": len(collar["strands"]),
        "elementary_crossings": len(events),
        "target_length": len(target),
        "recovered_sha256": module.canonical_sha(recovered),
        "target_sha256": module.canonical_sha(target),
        "word_equal": recovered == target,
        "control_collar": collar,
        "events": events,
    }
    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    if not result["word_equal"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
