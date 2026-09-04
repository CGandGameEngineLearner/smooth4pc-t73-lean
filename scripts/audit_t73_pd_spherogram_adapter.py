#!/usr/bin/env python3
"""Audit whether the reduced crossing ledger determines a Spherogram link."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PD = ROOT / "audit" / "t73_reduced_link_pd.json"
OUTPUT = ROOT / "audit" / "t73_pd_spherogram_adapter_report.json"


def inspect(data: dict[str, Any]) -> dict[str, Any]:
    crossings = data.get("crossings", [])
    segment_occurrences: dict[tuple[str, int], list[int]] = defaultdict(list)
    for crossing_index, crossing in enumerate(crossings):
        for strand in ("over", "under"):
            owner = crossing.get(f"{strand}_owner")
            segment = crossing.get(f"{strand}_segment")
            if isinstance(owner, str) and isinstance(segment, int):
                segment_occurrences[(owner, segment)].append(crossing_index)
    repeated = {
        f"{owner}:{segment}": indices
        for (owner, segment), indices in segment_occurrences.items()
        if len(indices) > 1
    }
    required = {
        "standard_pd_code": (
            "one four-half-edge incidence row per crossing, with every arc "
            "label appearing exactly twice"
        ),
        "component_halfedge_cycles": (
            "cyclic successor order through every over/under half-edge, "
            "including order among crossings on the same railroad segment"
        ),
        "self_crossings": "all self-crossings, not only mixed-owner crossings",
        "r_zx_embedding": "an explicit zero-crossing component rather than an empty word",
        "dotted_one_handle_components": (
            "the two dotted y/z components or an equivalent explicit "
            "genus-two handlebody triangulation"
        ),
        "integer_surgery_framings": (
            "integer diagram framings for m_2 and m_3 after comparison of "
            "product and blackboard framings"
        ),
    }
    present = {
        key: key in data and data[key] not in (None, [], {})
        for key in required
    }
    # Existing over_segment/under_segment values do not order multiple
    # crossings along one segment, so they cannot reconstruct successors.
    reasons = [
        f"missing {key}: {meaning}" for key, meaning in required.items()
        if not present[key]
    ]
    if repeated:
        reasons.append(
            f"{len(repeated)} railroad segments contain multiple crossings "
            "with no along-segment order"
        )
    component_incidence = Counter({name: 0 for name in data.get("components", [])})
    for crossing in crossings:
        component_incidence[crossing.get("over_owner")] += 1
        component_incidence[crossing.get("under_owner")] += 1
    if component_incidence.get("r_zx", 0) == 0:
        reasons.append("r_zx has no crossing incidence and no embedded component record")
    return {
        "schema": "t73_pd_spherogram_adapter_audit/v1",
        "input_crossings": len(crossings),
        "component_incidence": dict(component_incidence),
        "repeated_segment_count": len(repeated),
        "repeated_segment_examples": dict(list(sorted(repeated.items()))[:10]),
        "required_fields": required,
        "present": present,
        "spherogram_link": "OPEN",
        "snappy_complement": "OPEN",
        "regina_triangulation": "OPEN",
        "verdict": "OPEN",
        "reasons": reasons,
    }


def validate_standard_pd_code(pd_code: Any) -> None:
    if not isinstance(pd_code, list) or not pd_code:
        raise ValueError("standard_pd_code must be a nonempty list")
    labels = []
    for index, crossing in enumerate(pd_code):
        if (
            not isinstance(crossing, list)
            or len(crossing) != 4
            or not all(isinstance(label, int) for label in crossing)
        ):
            raise ValueError(f"standard_pd_code[{index}] is not four integer labels")
        labels.extend(crossing)
    counts = Counter(labels)
    if set(counts.values()) != {2}:
        raise ValueError("every standard PD arc label must occur exactly twice")


def attempt_complete(data: dict[str, Any]) -> dict[str, Any]:
    audit = inspect(data)
    if audit["reasons"]:
        return audit
    validate_standard_pd_code(data["standard_pd_code"])
    try:
        import spherogram
        import snappy
        import regina
    except ImportError as error:
        audit["reasons"] = [f"topology engine unavailable: {error}"]
        return audit
    link = spherogram.Link([tuple(row) for row in data["standard_pd_code"]])
    if len(link.link_components) != 7:
        raise ValueError("complete Kirby diagram must contain five attaching and two dotted components")
    manifold = link.exterior()
    isosig = manifold.triangulation_isosig()
    triangulation = regina.Triangulation3.fromIsoSig(isosig)
    audit.update(
        {
            "spherogram_link": "CONSTRUCTED",
            "snappy_complement": "CONSTRUCTED",
            "regina_triangulation": "CONSTRUCTED",
            "component_count": len(link.link_components),
            "snappy_isosig": isosig,
            "regina_tetrahedra": triangulation.size(),
            "verdict": "PREFIX_PASS",
        }
    )
    return audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = json.loads(PD.read_text(encoding="utf-8"))
    result = attempt_complete(data)
    if args.write:
        OUTPUT.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    if args.check:
        if not OUTPUT.is_file() or json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
            raise AssertionError("committed PD adapter report differs from live audit")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
