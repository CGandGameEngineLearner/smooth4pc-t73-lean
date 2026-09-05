#!/usr/bin/env python3
"""Build canonical rational attachment intervals around the six t-band locators."""

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
LOCATORS = ROOT / "geometry/t73_t_band_attachment_locators.json"
OUTPUT = ROOT / "geometry/t73_t_band_attachment_intervals.json"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values: list[str]) -> tuple[Fraction, ...]:
    return tuple(Fraction(value) for value in values)


def interpolate(origin: tuple[Fraction, ...], neighbour: tuple[Fraction, ...], parameter: Fraction) -> tuple[Fraction, ...]:
    return tuple(origin[i] + parameter * (neighbour[i] - origin[i]) for i in range(len(origin)))


def encode(values: tuple[Fraction, ...]) -> list[str]:
    return [str(value) for value in values]


def build() -> dict[str, Any]:
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    cancellation = json.loads(T_CANCELLATION.read_text(encoding="utf-8"))
    locators = json.loads(LOCATORS.read_text(encoding="utf-8"))
    bands = {band["index"]: band for band in cancellation["slide_bands"]}
    intervals = []
    for locator in locators["locators"]:
        band = bands[locator["band_index"]]
        width = Fraction(band["band_width"])
        if not 0 < width < 1:
            raise AssertionError("t-band width is not an interior segment parameter")
        core = [point(value) for value in ar_link["components"][locator["component"]]["core_polyline_T3xI"]]
        index = locator["source_core_vertex_index"]
        center = core[index]
        source_interval = [interpolate(center, core[index - 1], width), interpolate(center, core[index + 1], width)]
        target_center = point(locator["target_parallel_h_CS_point"])
        target_interval = [(*target_center[:3], target_center[3] - width), (*target_center[:3], target_center[3] + width)]
        if not 0 < target_interval[0][3] < target_interval[1][3] < 1:
            raise AssertionError("target interval leaves the mapping-torus parameter range")
        intervals.append({
            "band_index": locator["band_index"],
            "component": locator["component"],
            "source_core_vertex_index": index,
            "source_interval": [encode(value) for value in source_interval],
            "source_parameter_from_vertex": str(width),
            "target_interval": [encode(value) for value in target_interval],
            "target_center": encode(target_center),
            "choice_status": "CANONICAL_RATIONAL_INTERVAL_CANDIDATE",
        })
    result = {
        "schema": "t73_t_band_attachment_intervals/v1",
        "ar_link_sha256": ar_link["sha256"],
        "t_cancellation_sha256": cancellation["sha256"],
        "locators_sha256": locators["sha256"],
        "intervals": intervals,
        "completion_status": "VERIFIED_LOCATORS_WITH_CANDIDATE_INTERVALS",
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
        raise AssertionError("t-band attachment interval artifact is stale")
    print(f"T73_T_BAND_ATTACHMENT_INTERVALS={result['completion_status']}")


if __name__ == "__main__":
    main()
