#!/usr/bin/env python3
"""Lift the three dual-cell cores after the explicit candidate choice u=1/2."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from build_t73_ar_core_universal_lifts import lift_polyline

ROOT = Path(__file__).resolve().parents[1]
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
OUTPUT = ROOT / "geometry/t73_candidate_dual_core_lifts.json"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def build() -> dict[str, Any]:
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    components = {}
    for name in ("r_xy", "r_yz", "r_zx"):
        polyline = ar_link["components"][name]["polyline"]
        lifted_input = [[*point, "1/2"] for point in polyline]
        components[name] = lift_polyline(lifted_input)
        components[name]["fiber_level_choice"] = "1/2"
        components[name]["choice_status"] = "CANDIDATE_UNVERIFIED"
    result = {
        "schema": "t73_candidate_dual_core_lifts/v1",
        "ar_link_sha256": ar_link["sha256"],
        "components": components,
        "scope": "candidate fiber level u=1/2; no actual AR chart transition claimed",
        "completion_status": "CANDIDATE_UNVERIFIED",
    }
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
        raise AssertionError("candidate dual-core lifts are stale")
    print("T73_CANDIDATE_DUAL_CORE_LIFTS=CANDIDATE_UNVERIFIED")


if __name__ == "__main__":
    main()
