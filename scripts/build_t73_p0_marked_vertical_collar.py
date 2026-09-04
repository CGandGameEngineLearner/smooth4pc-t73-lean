#!/usr/bin/env python3
"""Build the retyped P0 collar: 44 static framed vertical arcs, no braid."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CUT = ROOT / "geometry" / "t73_actual_cut_tangle.json"
OUTPUT = ROOT / "geometry" / "t73_p0_marked_vertical_collar.json"
DELTA = Fraction(1, 1000)


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def encode(point) -> list[str]:
    return [str(Fraction(value)) for value in point]


def standard_point(wicket: int) -> tuple[Fraction, Fraction]:
    """Place wickets on an 11 by 4 rational grid strictly inside the unit disk."""

    index = wicket - 1
    column, row = index % 11, index // 11
    return Fraction(column - 5, 12), Fraction(2 * row - 3, 16)


def build() -> dict[str, Any]:
    cut = json.loads(CUT.read_text(encoding="utf-8"))
    passages = sorted(cut["passages"], key=lambda item: item["wicket"])
    if [item["wicket"] for item in passages] != list(range(1, 45)):
        raise AssertionError("actual cut does not supply wickets 1 through 44")
    arcs = []
    by_wicket = {}
    for passage in passages:
        wicket = int(passage["wicket"])
        x, y = standard_point(wicket)
        center_bottom = (x, y, Fraction(-1))
        center_top = (x, y, Fraction(1))
        push_bottom = (x, y + DELTA, Fraction(-1))
        push_top = (x, y + DELTA, Fraction(1))
        record = {
            "wicket": wicket,
            "owner": passage["owner"],
            "orientation": int(passage["orientation"]),
            "source_id": passage["source_id"],
            "paired_z_source_id": passage["paired_z_source_id"],
            "actual_word_event_index": int(passage["word_event_index"]),
            "standard_point": [str(x), str(y)],
            "center_arc": [encode(center_bottom), encode(center_top)],
            "product_normal": ["0", str(DELTA), "0"],
            "positive_push_off_arc": [encode(push_bottom), encode(push_top)],
            "framing_rectangle": {
                "vertices": [
                    encode(center_bottom),
                    encode(center_top),
                    encode(push_top),
                    encode(push_bottom),
                ],
                "triangles": [[0, 1, 2], [0, 2, 3]],
            },
        }
        arcs.append(record)
        by_wicket[wicket] = record

    boundary_wicket_order = [1, 2] + list(reversed(range(3, 45)))
    endpoints = []
    for wicket in boundary_wicket_order:
        arc = by_wicket[wicket]
        x, y = (Fraction(value) for value in arc["standard_point"])
        for side, coefficient, source_key in (
            ("neg", -1, "paired_z_source_id"),
            ("pos", 1, "source_id"),
        ):
            endpoints.append(
                {
                    "index": len(endpoints),
                    "wicket": wicket,
                    "side": side,
                    "owner": arc["owner"],
                    "orientation": arc["orientation"],
                    "source_id": arc[source_key],
                    "point": [str(x), str(y + coefficient * DELTA), "0"],
                    "normal_coefficient": coefficient,
                }
            )
    result = {
        "schema": "t73_p0_marked_vertical_collar/v1",
        "actual_cut_tangle_sha256": cut["sha256"],
        "model": {
            "ambient": "D2 x [-1,1]",
            "disk": "x^2+y^2<1",
            "height_coordinate": "z",
            "bottom_disk": "z=-1",
            "top_disk": "z=1",
            "mid_disk": "z=0",
        },
        "arc_count": len(arcs),
        "arcs": arcs,
        "owner_counts": {
            "m_2": sum(arc["owner"] == "m_2" for arc in arcs),
            "r_xy": sum(arc["owner"] == "r_xy" for arc in arcs),
        },
        "orientation_counts": {
            "positive": sum(arc["orientation"] == 1 for arc in arcs),
            "negative": sum(arc["orientation"] == -1 for arc in arcs),
        },
        "normal_delta": str(DELTA),
        "doubled_endpoint_count": len(endpoints),
        "doubled_endpoint_order": endpoints,
        "endpoint_order_rule": (
            "r_xy wickets 1,2 forward; m_2 wickets 44,...,3 reverse; "
            "within each wicket neg then pos"
        ),
        "contains_braid_word": False,
        "scope": (
            "P0 static marked product collar only; the six-sweep braid is "
            "auxiliary C detector data"
        ),
    }
    result["sha256"] = canonical_sha(
        {key: value for key, value in result.items() if key != "sha256"}
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"WROTE={OUTPUT}")
    print("T73_P0_MARKED_VERTICAL_COLLAR=BUILT")
    print(f"ARCS={result['arc_count']}")
    print(f"ENDPOINTS={result['doubled_endpoint_count']}")
    print(f"OWNER_COUNTS={result['owner_counts']}")
    print(f"CONTAINS_BRAID_WORD={result['contains_braid_word']}")
    print(f"SHA256={result['sha256']}")


if __name__ == "__main__":
    main()
