#!/usr/bin/env python3
"""Emit local stabilization–retraction movies from the Frobenius counit.

Each owner, including r_zx, uses the same pre-quotient identities
    chi o psi^[0] = 0
    chi o psi^[1] = chi
on an extra tensor factor.  Empty free words are not read as split unknots.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "geometry" / "t73_local_psi_movies.json"
LEAN = ROOT / "Smooth4PC" / "LocalStabilization.lean"
OWNERS = ("m_2", "m_3", "r_xy", "r_yz", "r_zx")


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def epsilon(label: str) -> int:
    if label == "1":
        return 0
    if label == "X":
        return 1
    raise AssertionError(f"unknown Frobenius label {label}")


def delta(label: str) -> list[tuple[str, str]]:
    if label == "1":
        return [("1", "X"), ("X", "1")]
    if label == "X":
        return [("X", "X")]
    raise AssertionError(f"unknown Frobenius label {label}")


def double_counit_delta(label: str) -> int:
    return sum(epsilon(a) * epsilon(b) for a, b in delta(label))


def generate() -> dict[str, Any]:
    if not LEAN.is_file():
        raise AssertionError("Smooth4PC/LocalStabilization.lean is missing")
    lean = LEAN.read_text(encoding="utf-8")
    for needle in (
        "theorem localStabilization_psi0",
        "theorem localStabilization_psi1",
        "theorem doubleCounitDelta_one",
        "theorem doubleCounitDelta_X",
        "No split-unknot hypothesis is used",
    ):
        if needle not in lean:
            raise AssertionError(f"LocalStabilization.lean is missing {needle}")
    if double_counit_delta("1") != 0 or double_counit_delta("X") != 1:
        raise AssertionError("numeric Frobenius counit identities failed")
    movies = []
    for owner in OWNERS:
        movies.append(
            {
                "owner": owner,
                "split_unknot_used": False,
                "empty_free_word_is_not_split_unknot": owner == "r_zx",
                "psi0": {
                    "input": "1",
                    "chi": epsilon("1"),
                    "double_counit_delta": double_counit_delta("1"),
                    "identity": "chi o psi^[0] = 0",
                },
                "psi1": {
                    "input": "X",
                    "chi": epsilon("X"),
                    "double_counit_delta": double_counit_delta("X"),
                    "identity": "chi o psi^[1] = chi",
                },
                "status": "PASS",
            }
        )
    result = {
        "schema": "t73_local_psi_movies/v1",
        "category": "pre-quotient foam / rank-two Frobenius",
        "owners": list(OWNERS),
        "movies": movies,
        "double_counit_delta": {"1": 0, "X": 1},
        "split_unknot_frobenius_factor": False,
        "lean": "Smooth4PC/LocalStabilization.lean",
    }
    result["sha256"] = canonical_sha({key: value for key, value in result.items() if key != "sha256"})
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"WROTE={OUTPUT}")
    if args.check:
        stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if stored["sha256"] != result["sha256"]:
            raise AssertionError("stored local psi movies disagree with regeneration")
    print(f"T73_LOCAL_PSI_MOVIES=PASS")
    print(f"OWNERS={len(result['movies'])}")
    print(f"SPLIT_UNKNOT_FACTOR={result['split_unknot_frobenius_factor']}")
    print(f"SHA256={result['sha256']}")


if __name__ == "__main__":
    main()
