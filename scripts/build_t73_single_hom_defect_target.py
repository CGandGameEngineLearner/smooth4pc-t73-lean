#!/usr/bin/env python3
"""Build the explicit P86-to-P88 one-cup target; do not invent the source map."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "geometry" / "t73_selected_source_exterior.json"
PIVOTAL = ROOT / "data" / "T73_C_PIVOTAL_GRADING_INPUT.json"
OUTPUT = ROOT / "geometry" / "t73_single_hom_defect_target.json"


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def build():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    pivotal = json.loads(PIVOTAL.read_text(encoding="utf-8"))
    charts = sorted(pivotal["endpoint_duality_charts"], key=lambda item: item["tensor_position"])
    if len(charts) != 88 or [item["tensor_position"] for item in charts] != list(range(88)):
        raise AssertionError("pivotal target does not have positions 0 through 87")
    top = [
        {
            "top_index": item["tensor_position"],
            "physical_endpoint_id": item["physical_endpoint_id"],
            "orientation": item["orientation"],
            "variance": item["variance"],
            "point": item["standard_vertical_arc"]["target"],
        }
        for item in charts
    ]
    bottom = [
        {
            "bottom_index": index,
            "top_index": chart["tensor_position"],
            "physical_endpoint_id": chart["physical_endpoint_id"],
            "orientation": chart["orientation"],
            "variance": chart["variance"],
            "point": chart["standard_vertical_arc"]["source"],
        }
        for index, chart in enumerate(charts[2:])
    ]
    through = [
        {
            "cell_id": f"through:{item['bottom_index']}",
            "kind": "through_strand",
            "bottom_index": item["bottom_index"],
            "top_index": item["top_index"],
            "physical_endpoint_id": item["physical_endpoint_id"],
            "vertices": [item["point"], top[item["top_index"]]["point"]],
            "product_normal": ["0", "1", "0"],
        }
        for item in bottom
    ]
    p0 = tuple(Fraction(value) for value in top[0]["point"])
    p1 = tuple(Fraction(value) for value in top[1]["point"])
    cup_bend = [
        str((p0[0] + p1[0]) / 2),
        "0",
        "3/4",
    ]
    cup = {
        "cell_id": "cup:0",
        "kind": "one_cup",
        "top_indices": [0, 1],
        "ordered_physical_endpoint_ids": [
            top[0]["physical_endpoint_id"],
            top[1]["physical_endpoint_id"],
        ],
        "vertices": [top[0]["point"], cup_bend, top[1]["point"]],
        "product_normal": ["0", "1", "0"],
        "bpw_A6_terms": pivotal["selected_cup_cap"]["cup"]["terms"],
    }
    result = {
        "schema": "t73_single_hom_defect_target/v1",
        "source_exterior_sha256": source["sha256"],
        "pivotal_input_sha256": canonical_sha(pivotal),
        "morphism_type": {"source": "P86", "target": "P88"},
        "bottom_endpoint_count": 86,
        "top_endpoint_count": 88,
        "bottom_endpoints": bottom,
        "top_endpoints": top,
        "cells": through + [cup],
        "through_strand_count": 86,
        "cup_count": 1,
        "source_exterior_interval_count": source["exterior_interval_count"],
        "source_to_target_interval_map": [],
        "z_coend_gluing_cells": [],
        "pivotal_currying_cells": [cup],
        "source_to_target_status": "OPEN",
        "first_missing_map": (
            "glue the 1084 Z-sphere endpoints through arbitrary C_271 "
            "insertions and map all 630 source intervals to the 86 through "
            "strands, one cup, and internal closed factors"
        ),
        "grading": {
            "target_cup_terms_recorded": True,
            "gluing_cobordism_euler": "UNDETERMINED",
            "additional_quantum_shift": "UNDETERMINED",
        },
    }
    result["sha256"] = canonical_sha(
        {key: value for key, value in result.items() if key != "sha256"}
    )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"WROTE={OUTPUT}")
    print("T73_SINGLE_HOM_DEFECT_TARGET=BUILT")
    print("MORPHISM=P86_TO_P88")
    print(f"CELLS={len(result['cells'])}")
    print(f"SOURCE_TO_TARGET={result['source_to_target_status']}")
    print(f"SHA256={result['sha256']}")


if __name__ == "__main__":
    main()
