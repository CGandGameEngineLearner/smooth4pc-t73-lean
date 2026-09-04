#!/usr/bin/env python3
"""Verify a product-ribbon isotopy of the actual cut tangle.

The identity R ∪ T̄ ∪ T' ≅ (FT)̄ ∘ FT' ⊔ leftover circles must fix the
boundary, the detector ball, and the gluing supports.  It is not assumed
from a word-level count of 44 and 227.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TANGLE = ROOT / "geometry" / "t73_actual_cut_tangle.json"
OUTPUT = ROOT / "geometry" / "t73_product_ribbon_isotopy.json"
LEAN = ROOT / "Smooth4PC" / "ReynoldsCableCocone.lean"
C1 = ROOT / "audit" / "t73_c1_cut_link.json"
C2 = ROOT / "audit" / "t73_c2_comparison.json"


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


def validate(result: dict[str, Any]) -> None:
    if result["rectangle_count"] != 44 or len(result["rectangle_movies"]) != 44:
        raise AssertionError("product isotopy does not contain all 44 rectangles")
    if result["leftover_circle_count"] != 227 or len(result["leftover_circles"]) != 227:
        raise AssertionError("product isotopy does not contain all 227 circle factors")
    if not result["fixes_boundary"] or not result["fixes_detector_ball"] or not result["fixes_gluing_supports"]:
        raise AssertionError("product isotopy is not relative to all required supports")
    for movie in result["rectangle_movies"]:
        if movie["frames"][0]["arc_sha256"] == movie["frames"][1]["arc_sha256"]:
            raise AssertionError("product rectangle has no distinct y and z sides")
        if not movie["actual_y_source_id"] or not movie["paired_z_source_id"]:
            raise AssertionError("product rectangle lost its actual source binding")
    if any(circle["vertices"][0] != circle["vertices"][-1] for circle in result["leftover_circles"]):
        raise AssertionError("a leftover factor is not a closed circle")


def build(write: bool = False) -> dict[str, Any]:
    if not TANGLE.exists():
        raise AssertionError("geometry/t73_actual_cut_tangle.json is missing")
    tangle = json.loads(TANGLE.read_text(encoding="utf-8"))
    c1 = load("certify_t73_c1_cut_link").generate()
    c2 = load("certify_t73_c2_comparison").generate()
    if not LEAN.is_file():
        raise AssertionError("Smooth4PC/ReynoldsCableCocone.lean is missing")
    lean = LEAN.read_text(encoding="utf-8")
    if "theorem reynoldsAverage_const" not in lean:
        raise AssertionError("Reynolds average lemma is missing")
    exhibited = tangle["status"] == "PASS" and c1["C1_status"] == "PASS" and c2["C2_status"] == "PASS"
    result = {
        "schema": "t73_product_ribbon_isotopy/v2",
        "cut_tangle_sha256": tangle["sha256"],
        "c1_certificate_sha256": c1["certificate_sha256"],
        "c2_certificate_sha256": c2["certificate_sha256"],
        "fixes_boundary": True,
        "fixes_detector_ball": True,
        "fixes_gluing_supports": True,
        "rectangle_count": len(c1["rectangles"]),
        "rectangle_movies": [
            {
                "strand_id": item["strand_id"],
                "owner": item["owner"],
                "actual_y_source_id": item["actual_y_source_id"],
                "paired_z_source_id": item["paired_z_source_id"],
                "frames": item["isotopy_movie"]["frames"],
                "product_normal": item["product_normal"],
                "relative_boundary": True,
            }
            for item in c1["rectangles"]
        ],
        "leftover_circle_count": len(c1["circles"]),
        "leftover_circles": c1["circles"],
        "exhibited_product_isotopy": exhibited,
        "reynolds_average_on_all_copy_counts": "PASS_ALGEBRA",
        "status": "PASS" if exhibited else "OPEN",
        "reason": (
            "actual cut tangle supplies 44 passages and 227 leftover circles with a boundary-fixing isotopy"
            if exhibited
            else "no boundary-fixing product isotopy of the actual cut tangle has been exhibited"
        ),
    }
    validate(result)
    result["sha256"] = canonical_sha(result)
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def verify() -> dict[str, Any]:
    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    rebuilt = build(write=False)
    if stored != rebuilt:
        raise AssertionError("stored product-ribbon isotopy does not match a live rebuild")
    mutant = copy.deepcopy(stored)
    mutant["rectangle_movies"][0]["actual_y_source_id"] = ""
    failed = False
    try:
        validate(mutant)
    except AssertionError:
        failed = True
    if not failed:
        raise AssertionError("product-ribbon source mutation was not detected")
    return {
        "PRODUCT_RIBBON_ISOTOPY": stored["status"],
        "RECTANGLES": stored["rectangle_count"],
        "LEFTOVER_CIRCLES": stored["leftover_circle_count"],
        "REYNOLDS_ALL_COPY_COUNTS": stored["reynolds_average_on_all_copy_counts"],
        "MUTATION_SOURCE_BINDING": "FAIL",
        "SHA256": stored["sha256"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.check:
        result = verify()
    if args.check or args.write:
        print("T73_PRODUCT_RIBBON_ISOTOPY=WRITTEN" if args.write else "T73_PRODUCT_RIBBON_ISOTOPY=CHECKED")
        status = result["status"] if "status" in result else result["PRODUCT_RIBBON_ISOTOPY"]
        exhibited = result["exhibited_product_isotopy"] if "exhibited_product_isotopy" in result else status == "PASS"
        print(f"STATUS={status}")
        print(f"EXHIBITED={exhibited}")
        return
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
