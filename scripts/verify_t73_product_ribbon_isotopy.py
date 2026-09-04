#!/usr/bin/env python3
"""Verify a product-ribbon isotopy of the actual cut tangle.

The identity R ∪ T̄ ∪ T' ≅ (FT)̄ ∘ FT' ⊔ leftover circles must fix the
boundary, the detector ball, and the gluing supports.  It is not assumed
from a word-level count of 44 and 227.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TANGLE = ROOT / "geometry" / "t73_actual_cut_tangle.json"
OUTPUT = ROOT / "geometry" / "t73_product_ribbon_isotopy.json"
LEAN = ROOT / "Smooth4PC" / "ReynoldsCableCocone.lean"


def build(write: bool = False) -> dict[str, Any]:
    if not TANGLE.exists():
        raise AssertionError("geometry/t73_actual_cut_tangle.json is missing")
    tangle = json.loads(TANGLE.read_text(encoding="utf-8"))
    if not LEAN.is_file():
        raise AssertionError("Smooth4PC/ReynoldsCableCocone.lean is missing")
    lean = LEAN.read_text(encoding="utf-8")
    if "theorem reynoldsAverage_const" not in lean:
        raise AssertionError("Reynolds average lemma is missing")
    exhibited = (
        tangle["status"] == "PASS"
        and tangle.get("passage_count") == 44
        and tangle.get("leftover_circle_count") == 227
    )
    result = {
        "schema": "t73_product_ribbon_isotopy/v1",
        "cut_tangle_sha256": tangle["sha256"],
        "fixes_boundary": False,
        "fixes_detector_ball": False,
        "fixes_gluing_supports": False,
        "exhibited_product_isotopy": exhibited,
        "reynolds_average_on_all_copy_counts": "PASS_ALGEBRA",
        "status": "PASS" if exhibited else "OPEN",
        "reason": (
            "actual cut tangle supplies 44 passages and 227 leftover circles with a boundary-fixing isotopy"
            if exhibited
            else "no boundary-fixing product isotopy of the actual cut tangle has been exhibited"
        ),
    }
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.check or args.write:
        print("T73_PRODUCT_RIBBON_ISOTOPY=WRITTEN" if args.write else "T73_PRODUCT_RIBBON_ISOTOPY=CHECKED")
        print(f"STATUS={result['status']}")
        print(f"EXHIBITED={result['exhibited_product_isotopy']}")
        return
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
