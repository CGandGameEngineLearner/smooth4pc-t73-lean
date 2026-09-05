#!/usr/bin/env python3
"""Exactly cut every selected-source ruled triangle by the plane z=0.

This is a preparatory datum for a conforming two-block mesh, not a
tetrahedral-frame certificate.  All clipping is rational and both blocks use
the same explicitly saved interface segments.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "geometry/t73_selected_source_exterior.json"
OUTPUT = ROOT / "geometry/t73_selected_source_partition_z0.json"


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def point(raw):
    return tuple(Fraction(value) for value in raw)


def encode(value):
    return [str(item) for item in value]


def intersection(first, second):
    if first[2] == second[2]:
        raise AssertionError("parallel edge cannot define a unique z=0 cut")
    factor = -first[2] / (second[2] - first[2])
    return tuple(first[index] + factor * (second[index] - first[index]) for index in range(3))


def clip(polygon, keep_nonnegative):
    result = []
    for first, second in zip(polygon, polygon[1:] + polygon[:1]):
        first_in = first[2] >= 0 if keep_nonnegative else first[2] <= 0
        second_in = second[2] >= 0 if keep_nonnegative else second[2] <= 0
        if first_in:
            result.append(first)
        if first_in != second_in:
            result.append(intersection(first, second))
    deduped = []
    for item in result:
        if not deduped or item != deduped[-1]:
            deduped.append(item)
    return deduped[:-1] if len(deduped) > 1 and deduped[0] == deduped[-1] else deduped


def triangles(polygon):
    return [[polygon[0], polygon[index], polygon[index + 1]] for index in range(1, len(polygon) - 1)]


def split_segment(first, second):
    cut = intersection(first, second) if first[2] * second[2] < 0 else None
    pieces = ((first, cut), (cut, second)) if cut is not None else ((first, second),)
    return [("z_nonpositive" if (left[2] + right[2]) / 2 <= 0 else "z_nonnegative", left, right) for left, right in pieces]


def build():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    lower, upper, interface, paths = [], [], [], []
    for route_index, route in enumerate(source["exterior_intervals"]):
        for triangle_index, raw in enumerate(route["ruled_ribbon_triangles"]):
            original = [point(vertex) for vertex in raw]
            below, above = clip(original, False), clip(original, True)
            key = {"route_index": route_index, "triangle_index": triangle_index}
            for side, polygon, collection in (("z_nonpositive", below, lower), ("z_nonnegative", above, upper)):
                if len(polygon) >= 3:
                    collection.append({**key, "side": side, "triangles": [[encode(vertex) for vertex in item] for item in triangles(polygon)]})
            cut = sorted({vertex for vertex in below + above if vertex[2] == 0})
            if len(cut) == 2:
                interface.append({**key, "segment": [encode(vertex) for vertex in cut]})
            elif len(cut) not in (0, 1, 3):
                raise AssertionError("unexpected z=0 interface cardinality")
        for kind, vertices in (("core", route["vertices"]), ("push", route["positive_push_off_vertices"])):
            raw_vertices = [point(vertex) for vertex in vertices]
            for segment_index, (first, second) in enumerate(zip(raw_vertices, raw_vertices[1:])):
                for side, left, right in split_segment(first, second):
                    paths.append({"route_index": route_index, "kind": kind, "segment_index": segment_index, "side": side, "segment": [encode(left), encode(right)]})
    result = {"schema": "t73_selected_source_partition_z0/v1", "source_exterior_sha256": source["sha256"], "plane": ["0", "0", "1", "0"], "blocks": {"z_nonpositive": lower, "z_nonnegative": upper}, "interface_segments": interface, "path_fragments": paths, "original_triangle_count": 2520}
    result["sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("saved z=0 partition is stale")
    print(f"T73_Z0_PARTITION=PASS fragments={len(value['blocks']['z_nonpositive']) + len(value['blocks']['z_nonnegative'])} interface={len(value['interface_segments'])}")


if __name__ == "__main__":
    main()
