#!/usr/bin/env python3
"""Build the splitting-preserving F3 lift from Johnson alpha_ij moves."""

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
    factor = load("factor_t73_matrix_johnson").generate()
    free = load("compose_t73_free_group_psi")
    comparison = load("compare_t73_nielsen_passages")
    mapping = free.identity_map()
    steps = []
    for index, move in enumerate(factor["unit_alpha_moves"]):
        local = free.identity_map()
        target = move["alpha_target"]
        prefix = move["alpha_prefix"] + 1
        if move["power"] > 0:
            local[target] = [prefix, target + 1]
        else:
            local[target] = [-prefix, target + 1]
        mapping = free.compose(local, mapping)
        steps.append({"index": index, "move": move, "partial_images": mapping})
    if free.abelianization(mapping) != factor["matrix_A"]:
        raise AssertionError("Johnson lift has wrong abelianization")
    m2 = comparison.after_x_cancellation(mapping[1], 1)
    result = {
        "schema": "t73_johnson_handlebody_lift/v1",
        "factorization_sha256": factor["witness_sha256"],
        "generator_images": mapping,
        "steps": steps,
        "abelianization": free.abelianization(mapping),
        "m2_after_cancellation": m2,
        "m2_length": len(m2),
        "m2_y_passages": sum(abs(letter) == 2 for letter in m2),
        "total_y_channels": sum(abs(letter) == 2 for letter in m2) + 2,
        "splitting_preserving_status": "PASS_BY_JOHNSON_ALPHA_GENERATORS",
        "public_44_channel_status": "PASS" if sum(abs(letter) == 2 for letter in m2) + 2 == 44 else "FAIL",
    }
    result["witness_sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.check:
        print("T73_JOHNSON_LIFT=PASS")
        print(f"M2_LENGTH={result['m2_length']}")
        print(f"TOTAL_Y_CHANNELS={result['total_y_channels']}")
        print(f"PUBLIC_44_CHANNEL_STATUS={result['public_44_channel_status']}")
        print(f"WITNESS_SHA256={result['witness_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
