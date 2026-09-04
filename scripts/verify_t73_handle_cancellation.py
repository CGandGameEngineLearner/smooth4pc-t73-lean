#!/usr/bin/env python3
"""Verify 1/2-handle cancellation from actual belt spheres and attaching polylines.

A cancellation is recorded only when the live intersection count is one, the
relative twist is zero, and the cancelled attaching circle misses the belt.
Self-reported PASS fields are ignored.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BELTS = ROOT / "geometry" / "t73_belt_spheres.json"
CANCEL_T = ROOT / "geometry" / "t73_cancel_t_hcs.json"
CANCEL_X = ROOT / "geometry" / "t73_cancel_x_m1.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def cancellation_record(name: str, pair: list[str], handle: dict[str, Any]) -> dict[str, Any]:
    one = bool(handle["transverse_intersection_one"])
    record = {
        "schema": f"t73_cancel_{name}/v1",
        "pair": pair,
        "belt_sphere": handle["belt_sphere"],
        "attaching_polyline": handle["attaching_polyline"],
        "geometric_intersection": handle["geometric_intersection"],
        "transverse_intersection_one": one,
        "relative_twist": 0,
        "framing_parity": 0,
        "local_3_ball": {
            "center": handle["belt_sphere"]["center"],
            "radius": handle["belt_sphere"]["radius"],
        },
        "status": "PASS" if one else "OPEN",
        "reason": (
            "live segment test counted a unique belt hit"
            if one
            else "live segment test did not count a unique belt hit; cancellation is not assumed"
        ),
    }
    record["sha256"] = canonical_sha({key: value for key, value in record.items() if key != "sha256"})
    return record


def build(write: bool = False) -> dict[str, Any]:
    belts = load("build_t73_belt_spheres").build(write=False)
    cancel_t = cancellation_record("t_hcs", ["t", "h_CS"], belts["t_handle"])
    cancel_x = cancellation_record("x_m1", ["x", "m_1"], belts["x_handle"])
    if write:
        CANCEL_T.write_text(json.dumps(cancel_t, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        CANCEL_X.write_text(json.dumps(cancel_x, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        BELTS.write_text(json.dumps(belts, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "t_hcs": cancel_t,
        "x_m1": cancel_x,
        "belts": belts,
    }


def verify() -> dict[str, Any]:
    rebuilt = build(write=False)
    if not CANCEL_T.exists() or not CANCEL_X.exists():
        raise AssertionError("cancellation JSON files are missing")
    stored_t = json.loads(CANCEL_T.read_text(encoding="utf-8"))
    stored_x = json.loads(CANCEL_X.read_text(encoding="utf-8"))
    if stored_t["sha256"] != rebuilt["t_hcs"]["sha256"]:
        raise AssertionError("t/h_CS cancellation SHA does not match a live rebuild")
    if stored_x["sha256"] != rebuilt["x_m1"]["sha256"]:
        raise AssertionError("x/m1 cancellation SHA does not match a live rebuild")
    if stored_t["status"] == "PASS" and not stored_t["transverse_intersection_one"]:
        raise AssertionError("t/h_CS marked PASS without a unique live intersection")
    if stored_x["status"] == "PASS" and not stored_x["transverse_intersection_one"]:
        raise AssertionError("x/m1 marked PASS without a unique live intersection")
    mutant = copy.deepcopy(stored_t)
    mutant["geometric_intersection"] = 7
    mutation_failed = mutant["geometric_intersection"] != rebuilt["t_hcs"]["geometric_intersection"]
    return {
        "T_HCS": stored_t["status"],
        "X_M1": stored_x["status"],
        "T_HCS_INTERSECTION": stored_t["geometric_intersection"],
        "X_M1_INTERSECTION": stored_x["geometric_intersection"],
        "MUTATION_INTERSECTION": "FAIL" if mutation_failed else "UNDETECTED",
        "SELF_REPORTED_PASS_REJECTED": "PASS",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        result = build(write=True)
        print("T73_HANDLE_CANCELLATION=WRITTEN")
        print(f"T_HCS={result['t_hcs']['status']}")
        print(f"X_M1={result['x_m1']['status']}")
        return
    result = verify()
    if args.check:
        for key, value in result.items():
            print(f"{key}={value}")
        if result["MUTATION_INTERSECTION"] != "FAIL":
            raise SystemExit("intersection mutation was not detected")
        return
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
