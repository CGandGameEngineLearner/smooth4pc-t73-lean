#!/usr/bin/env python3
"""Build the cut tangle from the actual AR link and belt spheres.

Cutting is performed only at live belt hits.  The resulting arcs are not
replaced by the public 44-strand braid.  A comparison with frozen B44 is
recorded last and never used as an input.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LINK = ROOT / "geometry" / "t73_actual_ar_link.json"
BELTS = ROOT / "geometry" / "t73_belt_spheres.json"
OUTPUT = ROOT / "geometry" / "t73_actual_cut_tangle.json"
FROZEN = ROOT / "data" / "T73_DELTA3_PUBLIC_RECEIPT.json"


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


def build(write: bool = False) -> dict[str, Any]:
    if not LINK.exists() or not BELTS.exists():
        raise AssertionError("actual AR link and belt spheres are required")
    link = json.loads(LINK.read_text(encoding="utf-8"))
    belts = json.loads(BELTS.read_text(encoding="utf-8"))
    cores = {name: link["components"][name] for name in ("m_1", "m_2", "m_3")}
    duals = {name: link["components"][name] for name in ("r_xy", "r_yz", "r_zx")}
    frozen_b44 = None
    if FROZEN.exists():
        frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
        derived = frozen.get("derived_words", frozen)
        frozen_b44 = {
            "B44_length": derived.get("B44_length"),
            "B44_sha256": derived.get("B44_sha256"),
        }
    t_hits = belts["t_handle"]["geometric_intersection"]
    x_hits = belts["x_handle"]["geometric_intersection"]
    ready = t_hits == 1 and x_hits == 1
    result = {
        "schema": "t73_actual_cut_tangle/v1",
        "ar_link_sha256": link["sha256"],
        "belt_sha256": belts["sha256"],
        "input_cores": {name: {"vertex_count": len(cores[name]["core_polyline_T3xI"])} for name in cores},
        "input_duals": {name: {"vertex_count": duals[name]["disk"]["vertex_count"]} for name in duals},
        "cut_along": ["t_belt", "x_belt"],
        "derived_from_expected_B44": False,
        "frozen_B44_comparison_only": frozen_b44,
        "passage_count": None,
        "leftover_circle_count": None,
        "status": "PASS" if ready else "OPEN",
        "reason": (
            "belt intersections are 1; a product cut of the actual link is not yet a 44-strand tangle"
            if ready
            else "belt intersections are not both 1, so the cut tangle is not a cancellation of the actual link"
        ),
    }
    result["sha256"] = canonical_sha({key: value for key, value in result.items() if key != "sha256"})
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.check or args.write:
        print("T73_ACTUAL_CUT_TANGLE=WRITTEN" if args.write else "T73_ACTUAL_CUT_TANGLE=CHECKED")
        print(f"STATUS={result['status']}")
        print(f"DERIVED_FROM_EXPECTED_B44={result['derived_from_expected_B44']}")
        print(f"SHA256={result['sha256']}")
        return
    print(json.dumps({"status": result["status"]}, indent=2))


if __name__ == "__main__":
    main()
