#!/usr/bin/env python3
"""Place the local Nielsen templates sequentially away from the section arc."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction
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
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest().upper()


def box_disjoint_from_section_arc(box_min, box_max) -> bool:
    # The section arc is {(t,t,t) | -1 <= t <= 1}.  It meets an axis-aligned
    # box iff the three coordinate intervals and [-1,1] have common overlap.
    lower = max(Fraction(-1), *(box_min[i] for i in range(3)))
    upper = min(Fraction(1), *(box_max[i] for i in range(3)))
    return lower > upper


def generate() -> dict[str, Any]:
    templates = load("generate_t73_pl_nielsen_templates").generate()
    # Affinely embed the standard box around a point with y and z intervals
    # separated, hence disjoint from the diagonal section arc.
    center = (Fraction(0), Fraction(3, 2), Fraction(-3, 2))
    scale = Fraction(1, 16)
    local_min = (-3, -2, -1)
    local_max = (3, 2, 1)
    box_min = tuple(center[i] + scale * local_min[i] for i in range(3))
    box_max = tuple(center[i] + scale * local_max[i] for i in range(3))
    inside_cube = all(Fraction(-2) < box_min[i] < box_max[i] < Fraction(2) for i in range(3))
    disjoint = box_disjoint_from_section_arc(box_min, box_max)
    if not inside_cube or not disjoint:
        raise AssertionError("chosen global support chart is invalid")
    placements = []
    for time, move in enumerate(templates["expanded_moves"]):
        placements.append({
            "time_interval": [time, time + 1],
            "move": move,
            "affine_chart": {"center": [str(x) for x in center], "scale": str(scale)},
            "support_box": {"min": [str(x) for x in box_min], "max": [str(x) for x in box_max]},
            "inside_fundamental_cube": True,
            "disjoint_from_section_arc": True,
            "handle_foot_routing_status": "OPEN",
        })
    result: dict[str, Any] = {
        "schema": "t73_nielsen_support_placement/v1",
        "placement_count": len(placements),
        "placements": placements,
        "time_interiors_pairwise_disjoint": True,
        "relative_section_arc_status": "PASS",
        "handle_foot_routing_status": "OPEN: chart embeddings into the target/source handle feet are not yet parameterized",
    }
    result["placement_sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = generate()
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check:
        print("T73_NIELSEN_SUPPORT_PLACEMENT=PASS")
        print(f"PLACEMENTS={result['placement_count']}")
        print(f"RELATIVE_SECTION_ARC_STATUS={result['relative_section_arc_status']}")
        print(f"HANDLE_FOOT_ROUTING_STATUS={result['handle_foot_routing_status']}")
        print(f"PLACEMENT_SHA256={result['placement_sha256']}")
    elif not args.output:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
