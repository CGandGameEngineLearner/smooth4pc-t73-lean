#!/usr/bin/env python3
"""Audit the framing condition for the Nielsen-to-compact r_yz slide movie."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def generate(linking: int | None = None, relator_framing: int = 0) -> dict[str, Any]:
    schedule = load("generate_t73_ryz_band_schedule").generate()
    net = 0
    for event in schedule["schedule"]:
        if event["kind"] != "r_yz_band_slide":
            continue
        orientation = schedule["templates"][event["template"]]["r_yz_orientation"]
        direction = 1 if event["word_move"]["direction"] == "forward" else -1
        net += orientation * direction
    if net != 1:
        raise AssertionError(f"unexpected net r_yz slide coefficient: {net}")
    known = linking is not None
    change = None if not known else net * (relator_framing + 2 * linking)
    status = "OPEN" if not known else "PASS" if change == 0 else "FAIL"
    result: dict[str, Any] = {
        "schema": "t73_ryz_framing_audit/v1",
        "band_schedule_sha256": schedule["schedule_sha256"],
        "net_oriented_r_yz_slide_coefficient": net,
        "framing_change_formula": "net * (framing(r_yz) + 2*linking(m2,r_yz))",
        "input_linking_m2_ryz": linking,
        "input_framing_ryz": relator_framing,
        "computed_framing_change": change,
        "framing_status": status,
        "missing_input": None if known else "actual reduced Kirby-diagram value of linking(m2,r_yz)",
        "relator_framing_source": "the standard fiber two-handle r_yz has AR product framing zero",
        "interpretation": "Local zero-twist bands do not settle global framing because the net relator slide coefficient is one.",
    }
    result["audit_sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--linking", type=int)
    parser.add_argument("--relator-framing", type=int, default=0)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate(args.linking, args.relator_framing)
    if args.check:
        print("T73_RYZ_FRAMING_AUDIT=PASS")
        print(f"NET_RYZ_SLIDE_COEFFICIENT={result['net_oriented_r_yz_slide_coefficient']}")
        print(f"FRAMING_STATUS={result['framing_status']}")
        print(f"MISSING_INPUT={result['missing_input']}")
        print(f"AUDIT_SHA256={result['audit_sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
