#!/usr/bin/env python3
"""Build the three missing source AR dual-cell product framing ribbons."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
OUTPUT = ROOT / "geometry/t73_actual_dual_product_ribbons.json"
NAMES = ("r_xy", "r_yz", "r_zx")


def canonical_sha(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def build() -> dict:
    source = json.loads(AR_LINK.read_text(encoding="utf-8"))
    components = []
    for component_index, name in enumerate(NAMES):
        item = source["components"][name]
        disk = item["disk"]
        axis = disk["plane_axis"]
        plane = Fraction(disk["plane_value"])
        core_closed = [point(value) for value in item["polyline"]]
        if core_closed[0] != core_closed[-1]:
            raise AssertionError(f"{name} dual boundary is not closed")
        core = core_closed[:-1]
        epsilon = Fraction(component_index + 1, 1000)
        normal = tuple(epsilon if index == axis else Fraction(0) for index in range(3))
        if any(value[axis] != plane for value in core):
            raise AssertionError(f"{name} core left its dual-disk plane")
        push = [tuple(value[index] + normal[index] for index in range(3)) for value in core]
        vertices = core + push
        count = len(core)
        triangles = []
        for index in range(count):
            successor = (index + 1) % count
            triangles.extend(((index, successor, count + successor),
                              (index, count + successor, count + index)))
        components.append({
            "name": name,
            "source_pointer": f"geometry/t73_actual_ar_link.json#/components/{name}",
            "plane_axis": axis,
            "core_plane": str(plane),
            "push_plane": str(plane + epsilon),
            "product_normal": encode(normal),
            "core_vertices": [encode(value) for value in core],
            "push_vertices": [encode(value) for value in push],
            "ribbon_vertices": [encode(value) for value in vertices],
            "ribbon_triangles": [list(value) for value in triangles],
            "quadrilateral_count": count,
            "triangle_count": len(triangles),
            "relative_twist": 0,
            "self_linking": 0,
            "self_linking_rule": "push bounds the translated dual disk, which is disjoint from the core plane",
        })
    result = {
        "schema": "t73_actual_dual_product_ribbons/v1",
        "actual_ar_link_sha256": source["sha256"],
        "components": components,
        "component_count": len(components),
        "triangle_count": sum(item["triangle_count"] for item in components),
        "completion_status": "ACTUAL_PRE_CANCELLATION_DUAL_PRODUCT_RIBBONS_CONSTRUCTED",
        "post_cancellation_transport_status": "OPEN_X_SLIDE_RIBBON_TRANSPORT_TO_SOURCE_NATIVE_PD",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("actual dual product ribbons are stale")
    print(f"T73_ACTUAL_DUAL_RIBBONS={result['completion_status']}")


if __name__ == "__main__":
    main()
