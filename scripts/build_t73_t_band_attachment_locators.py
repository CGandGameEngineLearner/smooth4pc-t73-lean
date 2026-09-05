#!/usr/bin/env python3
"""Locate all six t-band endpoints in the actual AR source records."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
T_CANCELLATION = ROOT / "geometry/t73_cancel_t_hcs.json"
OUTPUT = ROOT / "geometry/t73_t_band_attachment_locators.json"


def canonical_sha(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest().upper()


def rational_point(values: list[str]) -> tuple[Fraction, ...]:
    return tuple(Fraction(value) for value in values)


def lift_to_four(point: list[str]) -> tuple[Fraction, ...]:
    values = point if len(point) == 4 else [*point, "1/2"]
    return rational_point(values)


def build() -> dict[str, Any]:
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    cancellation = json.loads(T_CANCELLATION.read_text(encoding="utf-8"))
    core_vertices = {
        name: [lift_to_four(point) for point in ar_link["components"][name]["core_polyline_T3xI"]]
        for name in ("m_1", "m_2", "m_3")
    }
    locators = []
    for band in cancellation["slide_bands"]:
        path = [lift_to_four(point) for point in band["band_core_on_belt_sphere"]]
        component = band["component"]
        matches = [index for index, point in enumerate(core_vertices[component]) if point == path[0]]
        if len(matches) != 1:
            raise AssertionError(f"t-band {band['index']} has no unique source-core vertex")
        target_xyz = rational_point(band["parallel_h_CS_target"])
        if path[-1][:3] != target_xyz:
            raise AssertionError(f"t-band {band['index']} target does not match parallel h_CS data")
        locators.append({
            "band_index": band["index"],
            "component": component,
            "source_core_vertex_index": matches[0],
            "source_point_T3xI": [str(value) for value in path[0]],
            "target_parallel_h_CS_point": [str(value) for value in path[-1]],
            "target_xyz_reference": band["parallel_h_CS_target"],
            "target_u_parameter": str(path[-1][3]),
            "status": "VERIFIED_ENDPOINT_LOCATOR",
        })
    if len(locators) != 6:
        raise AssertionError("expected six t-band attachment locators")
    result = {
        "schema": "t73_t_band_attachment_locators/v1",
        "ar_link_sha256": ar_link["sha256"],
        "t_cancellation_sha256": cancellation["sha256"],
        "locators": locators,
        "completion_status": "VERIFIED_ENDPOINTS_ONLY",
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
        raise AssertionError("t-band attachment locator artifact is stale")
    print("T73_T_BAND_ATTACHMENT_LOCATORS=VERIFIED_ENDPOINTS_ONLY")


if __name__ == "__main__":
    main()
