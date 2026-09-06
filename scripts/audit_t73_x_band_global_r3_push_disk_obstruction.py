#!/usr/bin/env python3
"""Persist the first exact collision in the constant-translation push disks."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
from fractions import Fraction
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from verify_t73_affine_s3_product_ribbon_clearance import triangles_intersect


ROOT = Path(__file__).resolve().parents[1]
PUSH = ROOT / "audit/t73_x_band_global_r3_push_disks_receipt.json"
OUTPUT = ROOT / "audit/t73_x_band_global_r3_push_disk_obstruction.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    return path


def point(values):
    return tuple(Fraction(value) for value in values)


def build():
    push = json.loads(PUSH.read_text())
    first_collision = None
    pair_checks = 0
    with gzip.open(resolve(push["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            core_vertices = [point(value) for value in record["core_vertices"]]
            push_vertices = [point(value) for value in record["push_vertices"]]
            core_triangles = [tuple(core_vertices[index] for index in ids) for ids in record["core_triangles"]]
            push_triangles = [tuple(push_vertices[index] for index in ids) for ids in record["push_triangles"]]
            for core_index, core_triangle in enumerate(core_triangles):
                for push_index, push_triangle in enumerate(push_triangles):
                    pair_checks += 1
                    if triangles_intersect(core_triangle, push_triangle):
                        first_collision = {
                            "band_index": record["band_index"],
                            "core_triangle_index": core_index,
                            "push_triangle_index": push_index,
                        }
                        break
                if first_collision:
                    break
            if first_collision:
                break
    expected = {"band_index": 0, "core_triangle_index": 0, "push_triangle_index": 2}
    if first_collision != expected:
        raise AssertionError(f"first global band push-disk collision changed: {first_collision}")
    result = {
        "schema": "t73_x_band_global_r3_push_disk_obstruction/v1",
        "global_band_push_disks_receipt_sha256": push["sha256"],
        "push_cache_sha256": push["cache_sha256"],
        "tested_construction": "constant translation by band_width/1000 times (1,1,2)",
        "exact_triangle_pairs_before_first_collision": pair_checks,
        "first_exact_collision": first_collision,
        "global_push_disk_status": "REFUTED",
        "preserved_scope": (
            "all stored vertices, lane ribbons and product tetrahedra remain "
            "valid local cells; the union of translated push disks is not "
            "disjoint from the core disk union"
        ),
        "repair_direction": (
            "construct only the required attaching-lane push paths and ruled "
            "framing ribbons; do not require a parallel copy of the entire "
            "nonconvex routed band disk"
        ),
        "verdict": "PASS_X_BAND_GLOBAL_PUSH_DISK_COLLISION_OBSTRUCTION",
    }
    result["sha256"] = canonical_sha256(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("band push-disk obstruction is stale")
    print(json.dumps({
        "verdict": result["verdict"],
        "pairs": result["exact_triangle_pairs_before_first_collision"],
        "collision": result["first_exact_collision"],
        "status": result["global_push_disk_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
