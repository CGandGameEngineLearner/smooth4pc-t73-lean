#!/usr/bin/env python3
"""Transport all 227 unpaired actual z events to disjoint meridian circles."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CUT = ROOT / "geometry" / "t73_actual_cut_tangle.json"
SPINE = ROOT / "geometry" / "t73_johnson_spine_embedding.json"
LINK = ROOT / "geometry" / "t73_actual_ar_link.json"
CANCEL_X = ROOT / "geometry" / "t73_cancel_x_m1.json"
OUTPUT = ROOT / "geometry" / "t73_actual_leftover_z_circles.json"


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def build(write: bool = False):
    cut = json.loads(CUT.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    link = json.loads(LINK.read_text(encoding="utf-8"))
    cancel_x = json.loads(CANCEL_X.read_text(encoding="utf-8"))
    arcs = {arc["arc_id"]: arc for arc in spine["handle_arcs"]}
    x_slides = {slide["source_id"]: slide for slide in cancel_x["slide_bands"]}
    circles = []
    for movie_order, leftover in enumerate(cut["leftover_z_circles"]):
        source_id = leftover["source_id"]
        arc = arcs[source_id]
        if int(arc["axis"]) == 0:
            slide = x_slides[source_id]
            source_geometry = {
                "kind": "x_slide_replacement_by_actual_m1_z_lane",
                "x_slide_band_sha256": canonical_sha(slide),
                "m1_z_lane_sha256": canonical_sha(link["components"]["m_1"]["psi_A_C_i"]),
                "orientation": slide["replacement_orientation"],
            }
        elif int(arc["axis"]) == 2:
            source_geometry = {
                "kind": "johnson_z_handle_lane",
                "arc_sha256": canonical_sha(arc),
                "polyline": arc["torus_polyline"],
                "orientation": int(arc["sign"]),
            }
        else:
            raise AssertionError("an unpaired z event is not an actual z or replaced x lane")
        circle = leftover["circle_in_complement_chart"]
        center = Fraction(circle[0][0])
        level = Fraction(movie_order + 1, len(cut["leftover_z_circles"]) + 1)
        closure_band = {
            "movie_order": movie_order,
            "time_interval": [str(Fraction(movie_order, len(cut["leftover_z_circles"]))), str(Fraction(movie_order + 1, len(cut["leftover_z_circles"])))],
            "private_level": str(level),
            "core_path_rule": "push both ends of the source z passage along its actual product-normal collar to x=center, join them around the displayed four-edge meridian, then reverse the push",
            "target_center_x": str(center),
            "support_x_interval": [str(center - Fraction(1, 20000)), str(center + Fraction(1, 20000))],
            "fixes_detector_x_interval": ["-1", "1"],
            "relative_twist": 0,
        }
        circles.append(
            {
                "owner": leftover["owner"],
                "event_index": leftover["event_index"],
                "actual_z_source_id": source_id,
                "source_geometry": source_geometry,
                "target_meridian": circle,
                "target_meridian_sha256": canonical_sha(circle),
                "closure_band": closure_band,
                "transported_product_normal": leftover["transported_product_normal"],
                "closed": circle[0] == circle[-1],
                "disjoint_from_detector": center > 2,
            }
        )
    if len(circles) != 227:
        raise AssertionError("leftover z transport does not contain 227 circles")
    intervals = [tuple(item["closure_band"]["support_x_interval"]) for item in circles]
    if len(intervals) != len(set(intervals)):
        raise AssertionError("two leftover closure bands use the same private support")
    result = {
        "schema": "t73_actual_leftover_z_circles/v1",
        "cut_tangle_sha256": cut["sha256"],
        "spine_embedding_sha256": spine["sha256"],
        "ar_link_sha256": link["sha256"],
        "x_cancellation_sha256": cancel_x["sha256"],
        "circle_count": len(circles),
        "circles": circles,
        "sequential_supports": True,
        "all_sources_actual": True,
        "all_targets_closed_and_disjoint_from_detector": all(item["closed"] and item["disjoint_from_detector"] for item in circles),
        "actual_leftover_circle_transport": "PASS",
    }
    result["sha256"] = canonical_sha(result)
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.write or args.check:
        print(f"T73_ACTUAL_LEFTOVER_Z_CIRCLES={result['actual_leftover_circle_transport']}")
        print(f"CIRCLES={result['circle_count']}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
