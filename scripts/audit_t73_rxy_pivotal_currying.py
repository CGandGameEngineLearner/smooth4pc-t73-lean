#!/usr/bin/env python3
"""Classify the eight r_xy exterior intervals under pivotal currying."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "geometry" / "t73_selected_source_exterior.json"


def classify(data):
    occurrence = {
        item["occurrence_id"]: item
        for cycle in data["cycles"]
        for item in cycle["occurrences"]
    }
    records = []
    for interval in data["exterior_intervals"]:
        if not interval["cycle_id"].startswith("r_xy:"):
            continue
        start = occurrence[interval["from_occurrence_id"]]
        end = occurrence[interval["to_occurrence_id"]]
        if {start["handle"], end["handle"]} != {"Y", "Z"}:
            raise AssertionError("r_xy interval is not a Y-Z connector")
        record = {
            "interval_id": interval["interval_id"],
            "copy_sign": interval["copy_sign"],
            "from": [start["handle"], start["exit_sphere"].split("_")[1]],
            "to": [end["handle"], end["entry_sphere"].split("_")[1]],
            "effective_orientations": [
                start["effective_orientation"], end["effective_orientation"]
            ],
            "matching_class": (
                "same_variance"
                if start["exit_sphere"].split("_")[1]
                == end["entry_sphere"].split("_")[1]
                else "opposite_variance"
            ),
            "pivotal_operation": (
                "bend one endpoint using the appropriate duality "
                "evaluation/coevaluation"
            ),
        }
        records.append(record)
    if len(records) != 8:
        raise AssertionError("expected exactly eight r_xy connectors")
    counts = {
        kind: sum(record["matching_class"] == kind for record in records)
        for kind in ("same_variance", "opposite_variance")
    }
    if counts != {"same_variance": 4, "opposite_variance": 4}:
        raise AssertionError("r_xy pivotal matching-class counts changed")
    return {
        "schema": "t73_rxy_pivotal_currying_audit/v1",
        "records": records,
        "matching_class_counts": counts,
        "topological_operation": (
            "pivotal currying changes the boundary presentation; it is not "
            "an ambient isotopy pointwise relative to the four spheres"
        ),
        "normalized_pivotal_degree": 0,
        "external_one_cup": {
            "source": "P86",
            "target": "P88",
            "role": "separate noninvertible cup after currying",
        },
        "can_restore_494": False,
        "reason": (
            "degree-zero pivotal equivalences cannot supply the missing +271; "
            "the two-representable MWW degree remains 223"
        ),
    }


def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    print(json.dumps(classify(data), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
