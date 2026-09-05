#!/usr/bin/env python3
"""Normalize legacy cancellation centerlines into a candidate T3 x I chart.

Fraction arithmetic is deliberate: these are exact PL coordinates, so NumPy's
floating-point arrays would weaken the invariant being recorded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
T_CANCELLATION = ROOT / "geometry/t73_cancel_t_hcs.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
OUTPUT = ROOT / "geometry/t73_candidate_band_chart_normalization.json"
STATUS = "CANDIDATE_UNVERIFIED"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def lift_t_belt(point: list[str]) -> list[str]:
    """Use the documented t-belt slice (x,y,z) -> (x,y,z,1/2)."""
    if len(point) == 4:
        return point
    if len(point) != 3:
        raise AssertionError("unexpected t-band coordinate arity")
    return [*point, "1/2"]


def lift_x_belt(point: list[str]) -> list[str]:
    """Use the declared candidate x-belt lift (y,z,nu) -> (2,y,z,1/2+nu)."""
    if len(point) == 4:
        return point
    if len(point) != 3:
        raise AssertionError("unexpected x-band coordinate arity")
    return ["2", point[0], point[1], str(Fraction(1, 2) + Fraction(point[2]))]


def normalized_rows(kind: str, cancellation: dict[str, Any], centerline_key: str,
                    lift: Callable[[list[str]], list[str]], formula: str) -> list[dict[str, Any]]:
    return [{"kind": kind, "index": band["index"], "raw_centerline": band[centerline_key],
             "candidate_centerline_T3xI": [lift(point) for point in band[centerline_key]],
             "lift_formula": formula, "status": STATUS} for band in cancellation["slide_bands"]]


def build() -> dict[str, Any]:
    t_cancellation = json.loads(T_CANCELLATION.read_text(encoding="utf-8"))
    x_cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    bands = normalized_rows("t", t_cancellation, "band_core_on_belt_sphere", lift_t_belt, "(x,y,z)->(x,y,z,1/2)")
    bands += normalized_rows("x", x_cancellation, "band_core_on_positive_belt_face", lift_x_belt, "(y,z,nu)->(2,y,z,1/2+nu)")
    result = {"schema": "t73_candidate_band_chart_normalization/v1", "t_cancellation_sha256": t_cancellation["sha256"],
              "x_cancellation_sha256": x_cancellation["sha256"], "bands": bands,
              "scope": "candidate coordinate lifts only; not an actual chart transition", "status": STATUS}
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("candidate normalization stale")
    print(f"T73_CANDIDATE_BAND_NORMALIZATION={STATUS}")


if __name__ == "__main__":
    main()
