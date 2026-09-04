#!/usr/bin/env python3
"""Apply a band slide of remaining AR components off a cancellation ball.

Components whose polylines miss the local 3-ball are transported by the
identity.  Components that enter the ball are reported OPEN rather than
assumed to slide.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LINK = ROOT / "geometry" / "t73_actual_ar_link.json"
CANCEL_T = ROOT / "geometry" / "t73_cancel_t_hcs.json"
CANCEL_X = ROOT / "geometry" / "t73_cancel_x_m1.json"
OUTPUT = ROOT / "geometry" / "t73_band_slides.json"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def decode_point(point: list[str], coords: int = 3) -> list[Fraction]:
    return [Fraction(value) for value in point[:coords]]


def inf_dist(point: list[Fraction], center: list[Fraction]) -> Fraction:
    return max(abs(point[i] - center[i]) for i in range(len(center)))


def polyline_misses_ball(polyline: list[list[str]], center: list[Fraction], radius: Fraction) -> bool:
    return all(inf_dist(decode_point(point), center) > radius for point in polyline)


def component_polyline(component: dict[str, Any]) -> list[list[str]]:
    if "core_polyline_T3xI" in component:
        return component["core_polyline_T3xI"]
    return component["polyline"]


def slide_record(name: str, component: dict[str, Any], cancel: dict[str, Any]) -> dict[str, Any]:
    center = [Fraction(value) for value in cancel["local_3_ball"]["center"][:3]]
    radius = Fraction(cancel["local_3_ball"]["radius"])
    polyline = component_polyline(component)
    misses = polyline_misses_ball(polyline, center, radius)
    return {
        "component": name,
        "misses_cancellation_ball": misses,
        "transport": "identity" if misses else "OPEN",
        "band_interior_disjoint": misses,
        "status": "PASS" if misses else "OPEN",
    }


def build(write: bool = False) -> dict[str, Any]:
    if not LINK.exists() or not CANCEL_T.exists() or not CANCEL_X.exists():
        raise AssertionError("AR link and cancellation records are required")
    link = json.loads(LINK.read_text(encoding="utf-8"))
    cancel_t = json.loads(CANCEL_T.read_text(encoding="utf-8"))
    cancel_x = json.loads(CANCEL_X.read_text(encoding="utf-8"))
    names = ("m_1", "m_2", "m_3", "r_xy", "r_yz", "r_zx")
    slides = {
        "after_t_hcs": [slide_record(name, link["components"][name], cancel_t) for name in names],
        "after_x_m1": [slide_record(name, link["components"][name], cancel_x) for name in names if name != "m_1"],
    }
    result = {
        "schema": "t73_band_slides/v1",
        "ar_link_sha256": link["sha256"],
        "t_hcs_sha256": cancel_t["sha256"],
        "x_m1_sha256": cancel_x["sha256"],
        "slides": slides,
        "all_identity_transports": all(
            item["status"] == "PASS" for item in slides["after_t_hcs"] + slides["after_x_m1"]
        ),
    }
    result["status"] = "PASS" if result["all_identity_transports"] else "OPEN"
    result["sha256"] = canonical_sha({key: value for key, value in result.items() if key != "sha256"})
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
        print("T73_BAND_SLIDE=WRITTEN" if args.write else "T73_BAND_SLIDE=CHECKED")
        print(f"STATUS={result['status']}")
        print(f"SHA256={result['sha256']}")
        return
    print(json.dumps({"status": result["status"], "sha256": result["sha256"]}, indent=2))


if __name__ == "__main__":
    main()
