#!/usr/bin/env python3
"""Build a compactly supported PL ejection of the full m1 parallel annulus."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAME = ROOT / "geometry/t73_m1_parallel_annulus_tubular_frame.json"
CLEARANCE = ROOT / "audit/t73_m1_parallel_annulus_tubular_clearance_receipt.json"
OUTPUT = ROOT / "geometry/t73_m1_parallel_annulus_ambient_ejection.json"


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def build():
    frame = json.loads(FRAME.read_text(encoding="utf-8")); clearance = json.loads(CLEARANCE.read_text(encoding="utf-8"))
    annulus = [point(value) for value in frame["source_annulus_vertices"]]; displacement = point(frame["outward_displacement"])
    source_levels, target_levels = (Fraction(-1), Fraction(0), Fraction(2)), (Fraction(-1), Fraction(1), Fraction(2))
    source_vertices = [tuple(value[axis] + level * displacement[axis] for axis in range(4)) for level in source_levels for value in annulus]
    target_vertices = [tuple(value[axis] + level * displacement[axis] for axis in range(4)) for level in target_levels for value in annulus]
    layer_size = len(annulus); tetrahedra = []
    for layer in range(2):
        lower = layer * layer_size; upper = (layer + 1) * layer_size
        for triangle in frame["annulus_triangles"]:
            a, b, c = sorted(triangle)
            tetrahedra.extend(((lower + a, lower + b, lower + c, upper + c),
                               (lower + a, lower + b, upper + b, upper + c),
                               (lower + a, upper + a, upper + b, upper + c)))
    result = {
        "schema": "t73_m1_parallel_annulus_ambient_ejection/v1",
        "m1_parallel_annulus_tubular_frame_sha256": frame["sha256"],
        "m1_parallel_annulus_tubular_clearance_receipt_sha256": clearance["sha256"],
        "source_b_levels": [str(value) for value in source_levels],
        "target_b_images": [str(value) for value in target_levels],
        "outward_displacement": frame["outward_displacement"],
        "source_vertices": [encode(value) for value in source_vertices],
        "target_vertex_images": [encode(value) for value in target_vertices],
        "tetrahedra": [list(value) for value in tetrahedra],
        "vertex_count": len(source_vertices),
        "tetrahedron_count": len(tetrahedra),
        "support_boundary_rule": "b=-1 and b=2 fixed pointwise",
        "annulus_image_rule": "b=0 maps to b=1",
        "interval_map": "linear on [-1,0] and [0,2], with slopes 2 and 1/2",
        "completion_status": "M1_PARALLEL_ANNULUS_AMBIENT_EJECTION_LOCAL_CELLS_CONSTRUCTED",
        "support_clearance_status": "OPEN_EXTENDED_MINUS1_TO2_TUBE_CLEARANCE",
    }
    result["sha256"] = canonical_sha(result); return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args(); result = build()
    if args.write: OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result: raise AssertionError("m1 ambient ejection is stale")
    print(f"T73_M1_AMBIENT_EJECTION={result['completion_status']}")


if __name__ == "__main__": main()
