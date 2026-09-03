#!/usr/bin/env python3
"""Show that the committed word/framing ledger does not determine linking."""

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


def pd_fixture(word_hashes: dict[str, str], signs: list[int]) -> dict[str, Any]:
    return {
        "schema": "t73_reduced_link_pd/v1",
        "components": ["m_2", "r_yz"],
        "component_word_hashes": word_hashes,
        "component_framings": {"m_2": "same-product-framing", "r_yz": 0},
        "crossings": [
            {
                "over_owner": "m_2",
                "under_owner": "r_yz",
                "sign": sign,
                "over_segment": index,
                "under_segment": index,
                "local_clasp_control": True,
            }
            for index, sign in enumerate(signs)
        ],
        "normal_field_transport": {"status": "PASS", "scope": "synthetic local-clasp control"},
    }


def generate() -> dict[str, Any]:
    comparison = load("compare_t73_nielsen_passages").generate()
    extractor = load("extract_t73_ryz_linking")
    word_hashes = {
        "m_2": comparison["compact_representative"]["m2_word_sha256"],
        "r_yz": canonical_sha([2, 3, -2, -3]),
    }
    zero_pd = pd_fixture(word_hashes, [1, -1])
    one_pd = pd_fixture(word_hashes, [1, 1])
    zero = extractor.compute(zero_pd)
    one = extractor.compute(one_pd)
    if zero_pd["component_word_hashes"] != one_pd["component_word_hashes"]:
        raise AssertionError("control word ledgers differ")
    if zero["linking_m2_ryz"] == one["linking_m2_ryz"]:
        raise AssertionError("local clasp mutant did not change linking")
    result: dict[str, Any] = {
        "schema": "t73_linking_nonidentifiability/v1",
        "shared_component_word_hashes": word_hashes,
        "shared_component_framings": zero_pd["component_framings"],
        "zero_linking_control": zero,
        "unit_linking_control": one,
        "word_ledger_determines_linking": False,
        "current_public_data_determines_framing_gate": False,
        "verdict": "FALSIFIED: linking cannot be inferred from the committed word/framing ledger",
        "scope": "This does not decide the actual AR linking; it proves that the missing embedded PD data are necessary.",
    }
    result["witness_sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.check:
        print("T73_LINKING_FROM_WORDS_FALSIFICATION=PASS")
        print(f"ZERO_CONTROL={result['zero_linking_control']['linking_m2_ryz']}")
        print(f"UNIT_CONTROL={result['unit_linking_control']['linking_m2_ryz']}")
        print(f"WORD_LEDGER_DETERMINES_LINKING={result['word_ledger_determines_linking']}")
        print(f"WITNESS_SHA256={result['witness_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
