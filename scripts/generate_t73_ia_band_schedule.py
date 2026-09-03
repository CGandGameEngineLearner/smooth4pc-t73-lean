#!/usr/bin/env python3
"""Generate local PL bands for the IA-to-compact word movie."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate():
    helper = load("generate_t73_ryz_band_schedule")
    movie = load("construct_t73_ia_to_compact_movie").generate()
    return helper.generate_from_movie(movie, "t73_ia_band_schedule/v1")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.check:
        print("T73_IA_BAND_SCHEDULE=PASS")
        print(f"SCHEDULE_LENGTH={result['schedule_length']}")
        print(f"GLOBAL_BAND_EMBEDDING_STATUS={result['global_band_embedding_status']}")
        print(f"SCHEDULE_SHA256={result['schedule_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
