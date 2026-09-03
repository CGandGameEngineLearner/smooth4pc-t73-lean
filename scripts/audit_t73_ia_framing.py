#!/usr/bin/env python3
"""Audit the net framing coefficient of the IA-to-compact band movie."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate(linking: int | None = None):
    schedule = load("generate_t73_ia_band_schedule").generate()
    net = 0
    for event in schedule["schedule"]:
        if event["kind"] != "r_yz_band_slide":
            continue
        orientation = schedule["templates"][event["template"]]["r_yz_orientation"]
        direction = 1 if event["word_move"]["direction"] == "forward" else -1
        net += orientation * direction
    if net != -40:
        raise AssertionError(f"unexpected IA net coefficient {net}")
    change = None if linking is None else 2 * net * linking
    return {
        "schema": "t73_ia_framing_audit/v1",
        "schedule_sha256": schedule["schedule_sha256"],
        "net_oriented_r_yz_slide_coefficient": net,
        "input_linking_m2_ryz": linking,
        "computed_framing_change": change,
        "framing_status": "OPEN" if linking is None else "PASS" if change == 0 else "FAIL",
        "condition": "linking(m2,r_yz)=0",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--linking", type=int)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate(args.linking)
    if args.check:
        print("T73_IA_FRAMING_AUDIT=PASS")
        print(f"NET_RYZ_SLIDE_COEFFICIENT={result['net_oriented_r_yz_slide_coefficient']}")
        print(f"FRAMING_STATUS={result['framing_status']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
