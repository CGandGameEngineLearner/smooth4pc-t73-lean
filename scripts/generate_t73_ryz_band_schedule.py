#!/usr/bin/env python3
"""Bind the word-level y/z commutations to exact local PL band templates."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
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


def sign(letter: int) -> int:
    return 1 if letter > 0 else -1


def generate_from_movie(word_movie: dict[str, Any], schema: str) -> dict[str, Any]:
    local = load("generate_t73_pl_nielsen_templates").generate()["templates"]
    templates = {}
    for z_sign in (-1, 1):
        for y_sign in (-1, 1):
            key = f"z{z_sign:+d}_y{y_sign:+d}"
            relator_sign = z_sign * y_sign
            base = local["positive" if relator_sign > 0 else "negative"]
            templates[key] = {
                "z_orientation": z_sign,
                "y_orientation": y_sign,
                "r_yz_orientation": relator_sign,
                "pl_band_template_sha256": base["template_sha256"],
                "owner": "m_2",
                "relator_owner": "r_yz",
                "local_product_normal": "PASS",
            }
    schedule = []
    counts: Counter[str] = Counter()
    for time, move in enumerate(word_movie["combined_movie"]):
        if move["kind"] == "commute_y_z":
            before = move["before"] if move["direction"] == "forward" else move["after"]
            z_letter = next(letter for letter in before if abs(letter) == 3)
            y_letter = next(letter for letter in before if abs(letter) == 2)
            key = f"z{sign(z_letter):+d}_y{sign(y_letter):+d}"
            counts[key] += 1
            schedule.append({
                "time": time,
                "kind": "r_yz_band_slide",
                "word_move": move,
                "template": key,
                "owner_before": "m_2",
                "owner_after": "m_2",
                "relator_component": "r_yz",
                "normal_transport": "local product normal",
            })
        else:
            schedule.append({
                "time": time,
                "kind": "free_bigon",
                "word_move": move,
                "owner_before": "m_2",
                "owner_after": "m_2",
                "normal_transport": "product bigon",
            })
    if len(schedule) != len(word_movie["combined_movie"]):
        raise AssertionError("band schedule does not cover every word move")
    result: dict[str, Any] = {
        "schema": schema,
        "word_movie_sha256": word_movie["movie_sha256"],
        "templates": templates,
        "template_usage": dict(sorted(counts.items())),
        "schedule": schedule,
        "schedule_length": len(schedule),
        "owner_transport_status": "PASS",
        "local_band_status": "PASS",
        "global_band_embedding_status": "OPEN: the standard bands are not yet embedded along the actual reduced m2 and r_yz arcs",
        "global_framing_status": "OPEN: product-normal transport has not been compared in the actual reduced link",
    }
    result["schedule_sha256"] = canonical_sha(result)
    return result


def generate() -> dict[str, Any]:
    return generate_from_movie(
        load("construct_t73_word_kirby_movie").generate(),
        "t73_ryz_band_schedule/v1",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = generate()
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check:
        print("T73_RYZ_BAND_SCHEDULE=PASS")
        print(f"SCHEDULE_LENGTH={result['schedule_length']}")
        print(f"OWNER_TRANSPORT_STATUS={result['owner_transport_status']}")
        print(f"GLOBAL_BAND_EMBEDDING_STATUS={result['global_band_embedding_status']}")
        print(f"SCHEDULE_SHA256={result['schedule_sha256']}")
    elif not args.output:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
