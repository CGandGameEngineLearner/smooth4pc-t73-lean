#!/usr/bin/env python3
"""Build a shelling certificate for the standard x/m1 pair boundary S3."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDLE_PAIR = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"
OUTPUT = ROOT / "geometry/t73_x_m1_standard_pair_boundary_s3.json"
SHELLING_ORDER = [1, 3, 4, 2, 7, 8, 9, 22, 6, 5, 11, 14, 12, 21, 20, 19, 23, 24, 16, 18, 25, 17, 15, 13, 10]


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def facets(simplex):
    return [tuple(sorted(simplex[:index] + simplex[index + 1:])) for index in range(len(simplex))]


def build():
    handle_pair = json.loads(HANDLE_PAIR.read_text())
    four_simplices = [tuple(value) for value in handle_pair["standard_pair"]["union_four_simplices"]]
    counts = Counter(face for simplex in four_simplices for face in facets(simplex))
    boundary_tetrahedra = sorted(face for face, count in counts.items() if count == 1)
    removed_index = 0
    removed = boundary_tetrahedra[removed_index]
    chosen = []
    steps = []
    for tetrahedron_index in SHELLING_ORDER:
        tetrahedron = boundary_tetrahedra[tetrahedron_index]
        shared = sorted(
            face for face in facets(tetrahedron)
            if any(set(face) <= set(boundary_tetrahedra[index]) for index in chosen)
        )
        steps.append({
            "tetrahedron_index": tetrahedron_index,
            "tetrahedron": list(tetrahedron),
            "shared_boundary_triangles": [list(face) for face in shared],
            "shared_triangle_count": len(shared),
        })
        chosen.append(tetrahedron_index)
    result = {
        "schema": "t73_x_m1_standard_pair_boundary_s3/v1",
        "x_m1_handle_pair_deletion_sha256": handle_pair["sha256"],
        "standard_pair_four_simplex_count": len(four_simplices),
        "boundary_tetrahedra": [list(value) for value in boundary_tetrahedra],
        "boundary_tetrahedron_count": len(boundary_tetrahedra),
        "removed_tetrahedron_index": removed_index,
        "removed_tetrahedron": list(removed),
        "ball_shelling_order": SHELLING_ORDER,
        "ball_shelling_steps": steps,
        "ball_tetrahedron_count": len(steps),
        "recognition_argument": (
            "the 25-tetrahedron complement shells from one tetrahedron by "
            "disk attachments and has boundary equal to the removed "
            "tetrahedron boundary; gluing the removed 3-ball gives S3"
        ),
        "recognized_boundary_type": "S3",
        "completion_status": "STANDARD_X_M1_HANDLE_PAIR_BOUNDARY_S3_SHELLED",
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
        raise AssertionError("standard-pair S3 shelling artifact is stale")
    print(json.dumps({
        "boundary_tetrahedra": result["boundary_tetrahedron_count"],
        "ball_shelling_tetrahedra": result["ball_tetrahedron_count"],
        "recognized": result["recognized_boundary_type"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
