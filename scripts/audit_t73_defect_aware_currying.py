#!/usr/bin/env python3
"""Classify the eight mixed-orientation C-H1 currying exceptions."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "geometry" / "t73_selected_source_exterior.json"
PRIMITIVES = ROOT / "geometry" / "t73_all_owner_product_primitives.json"
PIVOTAL = ROOT / "data" / "T73_C_PIVOTAL_GRADING_INPUT.json"
OUTPUT = ROOT / "audit" / "t73_defect_aware_currying.json"


def build() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    primitives = json.loads(PRIMITIVES.read_text(encoding="utf-8"))
    pivotal = json.loads(PIVOTAL.read_text(encoding="utf-8"))
    endpoint_sphere = {
        endpoint["endpoint_id"]: sphere["name"]
        for sphere in source["insertion_spheres"]
        for endpoint in sphere["endpoints"]
    }
    active = []
    for interval in source["exterior_intervals"]:
        first = endpoint_sphere[interval["from_endpoint_id"]]
        second = endpoint_sphere[interval["to_endpoint_id"]]
        if first.startswith("Y") or second.startswith("Y"):
            active.append({**interval, "from_sphere": first, "to_sphere": second})
    desired = {
        frozenset(("Y_minus", "Z_plus")),
        frozenset(("Y_plus", "Z_minus")),
    }
    correct = [
        item
        for item in active
        if frozenset((item["from_sphere"], item["to_sphere"])) in desired
    ]
    wrong = [item for item in active if item not in correct]
    negative_y = sorted(
        event["source_id"]
        for owner in ("m_2", "r_xy")
        for event in primitives["primitive_geometry"][owner]["reduced_events"]
        if event["label"] == "y" and int(event["orientation"]) == -1
    )
    by_transition = Counter(
        "--".join(sorted((item["from_sphere"], item["to_sphere"])))
        for item in active
    )
    yminus_wrong = sorted(
        (
            item["from_endpoint_id"]
            if item["from_sphere"] == "Y_minus"
            else item["to_endpoint_id"],
            item["to_endpoint_id"]
            if item["from_sphere"] == "Y_minus"
            else item["from_endpoint_id"],
            item["interval_id"],
        )
        for item in wrong
        if "Y_minus" in (item["from_sphere"], item["to_sphere"])
    )
    yplus_wrong = sorted(
        (
            item["from_endpoint_id"]
            if item["from_sphere"] == "Y_plus"
            else item["to_endpoint_id"],
            item["to_endpoint_id"]
            if item["from_sphere"] == "Y_plus"
            else item["from_endpoint_id"],
            item["interval_id"],
        )
        for item in wrong
        if "Y_plus" in (item["from_sphere"], item["to_sphere"])
    )
    if len(yminus_wrong) != 4 or len(yplus_wrong) != 4:
        raise AssertionError("wrong-side endpoints do not split four plus four")
    proposed_reconnections = [
        {
            "index": index,
            "old_Yminus_Zminus_interval": minus[2],
            "old_Yplus_Zplus_interval": plus[2],
            "new_cross_pairs": [
                [minus[0], plus[1]],
                [plus[0], minus[1]],
            ],
            "required_operation": "pivotal mate/reconnection, not ambient isotopy relative endpoints",
            "left_or_right_mate": "UNDETERMINED",
            "Blanchet_sign": "UNDETERMINED",
            "Euler_quantum_degree": "UNDETERMINED",
        }
        for index, (minus, plus) in enumerate(zip(yminus_wrong, yplus_wrong))
    ]
    selected_feet = {
        endpoint_id
        for part in (pivotal["selected_cup_cap"]["cup"], pivotal["selected_cup_cap"]["cap"])
        for endpoint_id in part["ordered_feet"]
    }
    result = {
        "schema": "t73_defect_aware_currying_audit/v1",
        "source_exterior_sha256": source["sha256"],
        "all_owner_primitives_sha256": primitives["sha256"],
        "pivotal_input_scope": pivotal["scope"],
        "active_interval_count": len(active),
        "correct_side_count": len(correct),
        "wrong_side_count": len(wrong),
        "transition_counts": dict(sorted(by_transition.items())),
        "negative_base_y_sources": negative_y,
        "wrong_side_intervals": [
            {
                key: item[key]
                for key in (
                    "interval_id",
                    "owner",
                    "copy_sign",
                    "from_source_id",
                    "to_source_id",
                    "from_endpoint_id",
                    "to_endpoint_id",
                    "from_sphere",
                    "to_sphere",
                )
            }
            for item in wrong
        ],
        "minimum_independent_reconnections": 4,
        "proposed_endpoint_reconnections": proposed_reconnections,
        "active_boundary_endpoints_before_mates": 176,
        "active_boundary_endpoints_after_pivotal_mates": 176,
        "P86_to_P88_boundary_endpoints": 174,
        "pivotal_mates_preserve_total_endpoint_count": True,
        "one_defect_origin": "external chosen cup E86 -> E88 / weight-86 endpoint sector",
        "one_defect_derived_from_eight_wrong_intervals": False,
        "selected_pivotal_feet": sorted(selected_feet),
        "verdict": "NO_SINGLE_DEFECT_CURRYING_FROM_CURRENT_INCIDENCE",
    }
    if (
        result["active_interval_count"] != 176
        or result["correct_side_count"] != 168
        or result["wrong_side_count"] != 8
        or negative_y != ["m_2:C_i", "r_xy:vertex:1"]
    ):
        raise AssertionError("defect-aware incidence classification changed")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        if json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
            raise AssertionError("committed defect-aware currying audit differs")
    print(f"VERDICT={result['verdict']}")
    print(f"ACTIVE={result['active_interval_count']}")
    print(f"WRONG_SIDE={result['wrong_side_count']}")
    print(f"RECONNECTIONS={result['minimum_independent_reconnections']}")


if __name__ == "__main__":
    main()
