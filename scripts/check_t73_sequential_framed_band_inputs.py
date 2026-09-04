#!/usr/bin/env python3
"""Fail-closed readiness gate for the sequential framed Kirby band movie.

The committed cancellation files are legacy centerline schedules.  This gate
names the first missing geometric field and refuses to infer a framed slide
from relative_twist, PASS, a band core, or a distinct target point.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
T_BANDS = ROOT / "geometry" / "t73_cancel_t_hcs.json"
X_BANDS = ROOT / "geometry" / "t73_cancel_x_m1.json"
SCHEMA = ROOT / "audit" / "t73_sequential_framed_bands_schema.json"

REQUIRED_BAND_FIELDS = [
    "current_link_before",
    "source_attaching_interval",
    "target_attaching_interval",
    "band_vertices",
    "band_triangles",
    "band_boundary",
    "band_push_off_vertices",
    "band_push_off_triangles",
    "separation_certificates",
    "updated_link_after",
]


def first_gap(t_data: dict[str, Any], x_data: dict[str, Any]) -> dict[str, Any] | None:
    movies = [("t_hcs", t_data), ("x_m1", x_data)]
    for movie_name, movie in movies:
        bands = movie.get("slide_bands")
        if not isinstance(bands, list):
            return {
                "movie": movie_name,
                "band_index": None,
                "field": "slide_bands",
                "reason": "the slide list is absent",
            }
        for position, band in enumerate(bands):
            if not isinstance(band, dict):
                return {
                    "movie": movie_name,
                    "band_index": position,
                    "field": "band_record",
                    "reason": "the band record is not an object",
                }
            for field in REQUIRED_BAND_FIELDS:
                if field not in band:
                    return {
                        "movie": movie_name,
                        "band_index": position,
                        "field": field,
                        "reason": {
                            "current_link_before": (
                                "the entire current framed link is required because "
                                "earlier slides change the obstacle set"
                            ),
                            "source_attaching_interval": (
                                "a passage label or whole lambda/mu arc does not specify "
                                "the attaching subinterval of the moved component"
                            ),
                            "target_attaching_interval": (
                                "a target point does not specify an interval on the "
                                "framed parallel of the cancelling component"
                            ),
                            "band_vertices": "a centerline does not define an embedded rectangle",
                            "band_triangles": "the rectangle has no finite PL surface",
                            "band_boundary": "the four sides are not identified",
                            "band_push_off_vertices": (
                                "no normal-field extension exists from which twist can be derived"
                            ),
                            "band_push_off_triangles": "the pushed-off band is not triangulated",
                            "separation_certificates": (
                                "no exact proof excludes intersections with the current link"
                            ),
                            "updated_link_after": (
                                "the next step has no complete framed-link input"
                            ),
                        }[field],
                    }
    return None


def check(
    t_path: Path = T_BANDS, x_path: Path = X_BANDS
) -> dict[str, Any]:
    json.loads(SCHEMA.read_text(encoding="utf-8"))
    t_data = json.loads(t_path.read_text(encoding="utf-8"))
    x_data = json.loads(x_path.read_text(encoding="utf-8"))
    gap = first_gap(t_data, x_data)
    if gap is not None:
        return {
            "schema": "t73_sequential_framed_band_input_gate/v1",
            "verdict": "OPEN",
            "first_missing": gap,
            "self_attested_fields_ignored": [
                "status",
                "reason",
                "relative_twist",
                "framing_parity",
                "replacement_is_z_handle_lane",
            ],
            "required_band_fields_in_order": REQUIRED_BAND_FIELDS,
        }
    return {
        "schema": "t73_sequential_framed_band_input_gate/v1",
        "verdict": "READY_FOR_EXACT_GEOMETRIC_VERIFICATION",
        "band_counts": [
            len(t_data["slide_bands"]),
            len(x_data["slide_bands"]),
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--t-bands", type=Path, default=T_BANDS)
    parser.add_argument("--x-bands", type=Path, default=X_BANDS)
    parser.add_argument("--allow-open", action="store_true")
    args = parser.parse_args()
    result = check(args.t_bands, args.x_bands)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["verdict"] == "OPEN" and not args.allow_open:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
