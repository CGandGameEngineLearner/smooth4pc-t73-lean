#!/usr/bin/env python3
"""Derive crossings from the cancelled actual link; compare to B44 last.

The public word is never an input.  If the cancelled tangle does not yet
supply 44 passages, the derivation is OPEN.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TANGLE = ROOT / "geometry" / "t73_actual_cut_tangle.json"
RECEIPT = ROOT / "data" / "T73_DELTA3_PUBLIC_RECEIPT.json"
OUTPUT = ROOT / "geometry" / "t73_derived_crossings.json"


def build(write: bool = False) -> dict[str, Any]:
    if not TANGLE.exists():
        raise AssertionError("actual cut tangle is missing")
    tangle = json.loads(TANGLE.read_text(encoding="utf-8"))
    frozen = json.loads(RECEIPT.read_text(encoding="utf-8"))["derived_words"]
    passages = tangle.get("passage_count")
    derived = {
        "schema": "t73_derived_crossings/v1",
        "cut_tangle_sha256": tangle["sha256"],
        "used_expected_B44_as_input": False,
        "derived_letter_count": passages,
        "frozen_B44_length": frozen["B44_length"],
        "matches_frozen_B44": passages == frozen["B44_length"],
        "status": "PASS" if passages == frozen["B44_length"] else "OPEN",
        "reason": (
            "derived passage count matches frozen B44 length"
            if passages == frozen["B44_length"]
            else "cancelled actual link does not yet supply a 44-strand crossing word"
        ),
    }
    if write:
        OUTPUT.write_text(json.dumps(derived, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return derived


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.check or args.write:
        print("T73_DERIVED_CROSSINGS=WRITTEN" if args.write else "T73_DERIVED_CROSSINGS=CHECKED")
        print(f"STATUS={result['status']}")
        print(f"USED_EXPECTED_B44={result['used_expected_B44_as_input']}")
        print(f"MATCHES_FROZEN_B44={result['matches_frozen_B44']}")
        return
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
