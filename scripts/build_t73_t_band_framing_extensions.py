#!/usr/bin/env python3
"""Extend actual source/target framing normals across the six candidate t-bands."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from t73_pl_kirby_moves import as_point, encode

ROOT = Path(__file__).resolve().parents[1]
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
T_MOVIE = ROOT / "geometry/t73_candidate_t_band_movie.json"
OUTPUT = ROOT / "geometry/t73_t_band_framing_extensions.json"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def scale(value: Fraction, vector: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(value * coordinate for coordinate in vector)


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def interpolate(left, right, parameter: Fraction):
    return tuple(left[i] + parameter * (right[i] - left[i]) for i in range(len(left)))


def band_centerline(band: dict[str, Any]) -> list[tuple[Fraction, ...]]:
    segments = band["rectangle_segments"]
    points = [as_point(segments[0]["centerline"][0])]
    points.extend(as_point(segment["centerline"][1]) for segment in segments)
    return points


def build() -> dict[str, Any]:
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    movie = json.loads(T_MOVIE.read_text(encoding="utf-8"))
    target_offset = as_point([*ar_link["components"]["h_CS"]["framing_annulus"]["offset"], "0"])
    extensions = []
    for band in movie["bands"]:
        component = ar_link["components"][band["component"]]
        width = Fraction(component["full_framing_annulus"]["width"])
        source_direction = as_point([*component["full_framing_annulus"]["product_direction"], "0"])
        source_normal = scale(width, source_direction)
        if max(abs(value) for value in target_offset) != width:
            raise AssertionError("h_CS target framing width differs from source band width")
        centerline = band_centerline(band)
        denominator = len(centerline) - 1
        normals = [interpolate(source_normal, target_offset, Fraction(index, denominator)) for index in range(len(centerline))]
        push_off = [add(point, normal) for point, normal in zip(centerline, normals)]
        if normals[0] != source_normal or normals[-1] != target_offset:
            raise AssertionError("t-band normal extension lost its boundary values")
        extensions.append({
            "band_index": band["index"],
            "component": band["component"],
            "centerline": [encode(point) for point in centerline],
            "normal_field": [encode(normal) for normal in normals],
            "push_off_centerline": [encode(point) for point in push_off],
            "source_normal": encode(source_normal),
            "target_h_CS_normal": encode(target_offset),
            "extension_rule": "linear interpolation by ordered centerline vertex index",
            "status": "CANDIDATE_INTERIOR_EXTENSION_BOUNDARY_VERIFIED",
        })
    result = {
        "schema": "t73_t_band_framing_extensions/v1",
        "ar_link_sha256": ar_link["sha256"],
        "candidate_t_movie_sha256": movie["sha256"],
        "extensions": extensions,
        "completion_status": "CANDIDATE_INTERIOR_EXTENSIONS_BOUNDARY_VERIFIED",
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
        raise AssertionError("t-band framing extensions are stale")
    print(f"T73_T_BAND_FRAMING={result['completion_status']}")


if __name__ == "__main__":
    main()
