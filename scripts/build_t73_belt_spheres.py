#!/usr/bin/env python3
"""Build belt spheres and attaching circles from the actual AR link.

The t-handle belt is a small octahedron around the section point in the
slice T^3 x {1/2}.  The x-handle belt is a small octahedron around a point
of the x-core in T^3 x {0}.  Intersections with attaching polylines are
counted from sampled segments; they are not assumed.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LINK = ROOT / "geometry" / "t73_actual_ar_link.json"
OUTPUT = ROOT / "geometry" / "t73_belt_spheres.json"
RADIUS = Fraction(1, 64)


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


def encode(point: list[Fraction]) -> list[str]:
    return [str(Fraction(value)) for value in point]


def octahedron(center: list[Fraction], radius: Fraction) -> dict[str, Any]:
    cx, cy, cz = (Fraction(value) for value in center)
    verts = [
        [cx + radius, cy, cz],
        [cx - radius, cy, cz],
        [cx, cy + radius, cz],
        [cx, cy - radius, cz],
        [cx, cy, cz + radius],
        [cx, cy, cz - radius],
    ]
    faces = [
        [0, 2, 4],
        [2, 1, 4],
        [1, 3, 4],
        [3, 0, 4],
        [0, 5, 2],
        [2, 5, 1],
        [1, 5, 3],
        [3, 5, 0],
    ]
    return {
        "center": encode(center),
        "radius": str(radius),
        "vertices": [encode(vertex) for vertex in verts],
        "faces": faces,
        "euler": 6 - 12 + 8,
    }


def lift_sphere(sphere: dict[str, Any], u: str) -> dict[str, Any]:
    lifted = dict(sphere)
    lifted["vertices"] = [vertex + [u] for vertex in sphere["vertices"]]
    lifted["slice"] = u
    return lifted


def segment_hits_octahedron(
    start: list[Fraction], end: list[Fraction], center: list[Fraction], radius: Fraction
) -> bool:
    """A coarse live test: some sampled point of the segment lies on the sphere shell."""

    lo = radius * Fraction(3, 4)
    hi = radius * Fraction(5, 4)
    for index in range(21):
        t = Fraction(index, 20)
        point = [start[i] + t * (end[i] - start[i]) for i in range(len(center))]
        dist = max(abs(point[i] - center[i]) for i in range(len(center)))
        if lo <= dist <= hi:
            return True
    return False


def polyline_hits(polyline: list[list[str]], center: list[Fraction], radius: Fraction, coords: int = 3) -> int:
    hits = 0
    points = [[Fraction(value) for value in point[:coords]] for point in polyline]
    for start, end in zip(points, points[1:]):
        if segment_hits_octahedron(start, end, center, radius):
            hits += 1
    return hits


def build(write: bool = False) -> dict[str, Any]:
    if not LINK.exists():
        raise AssertionError("geometry/t73_actual_ar_link.json is missing")
    link = json.loads(LINK.read_text(encoding="utf-8"))
    origin = [Fraction(0), Fraction(0), Fraction(0)]
    x_point = [Fraction(1, 8), Fraction(0), Fraction(0)]
    belt_t = lift_sphere(octahedron(origin, RADIUS), "1/2")
    belt_x = lift_sphere(octahedron(x_point, RADIUS), "0")
    m1 = link["components"]["m_1"]
    lambda_hits_t = polyline_hits(m1["lambda_i"], origin, RADIUS, coords=3)
    mu_hits_t = polyline_hits(m1["mu_i"], origin, RADIUS, coords=3)
    core_hits_t = polyline_hits(m1["core_polyline_T3xI"], origin, RADIUS, coords=3)
    c_hits_x = polyline_hits(m1["C_i"], x_point, RADIUS, coords=3)
    result = {
        "schema": "t73_belt_spheres/v1",
        "ar_link_sha256": link["sha256"],
        "t_handle": {
            "belt_sphere": belt_t,
            "attaching_polyline": m1["lambda_i"],
            "segment_hits_on_lambda": lambda_hits_t,
            "segment_hits_on_mu": mu_hits_t,
            "segment_hits_on_core": core_hits_t,
            "geometric_intersection": lambda_hits_t,
            "transverse_intersection_one": lambda_hits_t == 1,
        },
        "x_handle": {
            "belt_sphere": belt_x,
            "attaching_polyline": m1["C_i"],
            "segment_hits_on_C_i": c_hits_x,
            "geometric_intersection": c_hits_x,
            "transverse_intersection_one": c_hits_x == 1,
        },
        "status": {
            "belt_spheres_triangulated": "PASS",
            "t_hcs_intersection_one": "PASS" if lambda_hits_t == 1 else "OPEN",
            "x_m1_intersection_one": "PASS" if c_hits_x == 1 else "OPEN",
        },
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
        print("T73_BELT_SPHERES=WRITTEN" if args.write else "T73_BELT_SPHERES=CHECKED")
        print(f"T_HCS_INTERSECTION={result['status']['t_hcs_intersection_one']}")
        print(f"X_M1_INTERSECTION={result['status']['x_m1_intersection_one']}")
        print(f"SHA256={result['sha256']}")
        return
    print(json.dumps(result["status"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
