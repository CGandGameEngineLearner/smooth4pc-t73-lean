#!/usr/bin/env python3
"""Extract linking(m2,r_yz) from an explicit labelled reduced-link PD ledger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "audit" / "t73_reduced_link_pd.json"


def compute(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("schema") != "t73_reduced_link_pd/v1":
        raise AssertionError("wrong reduced-link PD schema")
    crossings = data.get("crossings")
    if not isinstance(crossings, list):
        raise AssertionError("crossings must be a list")
    signed_sum = 0
    selected = []
    for index, crossing in enumerate(crossings):
        if not isinstance(crossing, dict):
            raise AssertionError(f"crossing {index} is not an object")
        over, under, sign = crossing.get("over_owner"), crossing.get("under_owner"), crossing.get("sign")
        if sign not in (-1, 1):
            raise AssertionError(f"crossing {index} has invalid sign")
        if not isinstance(over, str) or not isinstance(under, str) or over == under:
            continue
        if {over, under} == {"m_2", "r_yz"}:
            signed_sum += sign
            selected.append(index)
    if signed_sum % 2:
        raise AssertionError("mixed crossing-sign sum is odd; PD orientation ledger is inconsistent")
    linking = signed_sum // 2
    normal = data.get("normal_field_transport")
    if not isinstance(normal, dict) or normal.get("status") != "PASS":
        raise AssertionError("normal_field_transport PASS receipt is required")
    return {
        "schema": "t73_ryz_linking_result/v1",
        "selected_crossing_indices": selected,
        "mixed_crossing_sign_sum": signed_sum,
        "linking_m2_ryz": linking,
        "normal_field_transport_status": "PASS",
        "verdict": "PASS",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()
    if not args.input.is_file():
        print("T73_RYZ_LINKING=OPEN")
        print(f"REASON=missing explicit reduced-link PD ledger: {args.input}")
        raise SystemExit(2)
    try:
        result = compute(json.loads(args.input.read_text()))
    except (json.JSONDecodeError, AssertionError) as exc:
        print("T73_RYZ_LINKING=OPEN")
        print(f"REASON={exc}")
        raise SystemExit(2)
    print("T73_RYZ_LINKING=PASS")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
