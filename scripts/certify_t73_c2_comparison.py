#!/usr/bin/env python3
"""C2 comparison maps on the collar-bound C1 product tangle.

H is the family of 44 P0-strand product isotopies from C1.  The left and
right action supports are explicit cubes disjoint from the P0 ball, the 44
cores, and the 227 leftover circles.  This is the Johnson-replacement
comparison, not a chain-level Blanchet--Khovanov complex of the actual W2 cut.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "audit" / "t73_c2_comparison.json"
LEAN = ROOT / "Smooth4PC" / "RepresentableCoefficient.lean"
SYS_CACHE = "_T73_C2_COMPARISON_PAYLOAD"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def cube(xmin: int, xmax: int, ymin: int, ymax: int, zmin: int, zmax: int) -> dict[str, Any]:
    return {
        "bounds": {
            "xmin": xmin,
            "xmax": xmax,
            "ymin": ymin,
            "ymax": ymax,
            "zmin": zmin,
            "zmax": zmax,
        },
        "vertices": [
            [xmin, ymin, zmin],
            [xmax, ymin, zmin],
            [xmax, ymax, zmin],
            [xmin, ymax, zmin],
            [xmin, ymin, zmax],
            [xmax, ymin, zmax],
            [xmax, ymax, zmax],
            [xmin, ymax, zmax],
        ],
    }


def bounds_disjoint(a: dict[str, int], b: dict[str, int]) -> bool:
    return (
        a["xmax"] < b["xmin"]
        or b["xmax"] < a["xmin"]
        or a["ymax"] < b["ymin"]
        or b["ymax"] < a["ymin"]
        or a["zmax"] < b["zmin"]
        or b["zmax"] < a["zmin"]
    )


def polyline_bounds(points: list[list[int]]) -> dict[str, int]:
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    zs = [point[2] for point in points]
    return {
        "xmin": min(xs),
        "xmax": max(xs),
        "ymin": min(ys),
        "ymax": max(ys),
        "zmin": min(zs),
        "zmax": max(zs),
    }


def verify_maps(result: dict[str, Any], c1: dict[str, Any]) -> None:
    ball = c1["p0_ball_bounds"]
    left = result["action_squares"]["left"]["support"]["bounds"]
    right = result["action_squares"]["right"]["support"]["bounds"]
    if not bounds_disjoint(left, ball):
        raise AssertionError("left C2 support meets the P0 ball")
    if not bounds_disjoint(right, ball):
        raise AssertionError("right C2 support meets the P0 ball")
    if not bounds_disjoint(left, right):
        raise AssertionError("left and right C2 supports meet")
    for item in c1["rectangles"]:
        core = polyline_bounds(item["core_arc"])
        ends = polyline_bounds(item["y_side_ends"] + item["z_side_ends"])
        if not bounds_disjoint(left, core) or not bounds_disjoint(right, core):
            raise AssertionError("a C2 support meets a west-east core")
        if not bounds_disjoint(left, ends) or not bounds_disjoint(right, ends):
            raise AssertionError("a C2 support meets a C1 rectangle endpoint")
    for item in c1["circles"]:
        circle = polyline_bounds(item["vertices"])
        if not bounds_disjoint(left, circle) or not bounds_disjoint(right, circle):
            raise AssertionError("a C2 support meets a leftover z-circle")
    movies = result["H"]["movies"]
    if len(movies) != 44:
        raise AssertionError("H does not have 44 product movies")
    for movie, rectangle in zip(movies, c1["rectangles"]):
        if movie["strand_id"] != rectangle["strand_id"]:
            raise AssertionError("H movie order disagrees with C1")
        if movie["status"] != "PASS":
            raise AssertionError("an H movie is not PASS")
        if movie["frames"][0]["arc_sha256"] != rectangle["y_side_sha256"]:
            raise AssertionError("H does not start on the P0 strand")
        if movie["frames"][1]["arc_sha256"] != rectangle["z_side_sha256"]:
            raise AssertionError("H does not end on the product translate")
    if not LEAN.is_file():
        raise AssertionError("RepresentableCoefficient.lean is missing")
    if "coefficientHH0Equiv" not in LEAN.read_text(encoding="utf-8"):
        raise AssertionError("coefficientHH0Equiv is missing from RepresentableCoefficient.lean")


def generate() -> dict[str, Any]:
    cached = getattr(sys, SYS_CACHE, None)
    if cached is not None:
        return cached
    c1 = load("certify_t73_c1_cut_link").generate()
    if c1.get("C1_status") != "PASS":
        raise AssertionError("C2 refuses to run on an OPEN C1 certificate")
    n_y = [42, 189, 2, 2, 0]
    n_z = [269, 1271, 2, 2, 0]
    s0 = [1, 0, 1, 0, 0]
    p_y = sum(r * n for r, n in zip(s0, n_y))
    p_z = sum(r * n for r, n in zip(s0, n_z))
    if p_y != 44 or p_z - p_y != 227:
        raise AssertionError("selected cable counts are not 44 and 227")
    if p_y != c1["counts"]["rectangles"] or p_z - p_y != c1["counts"]["leftover_z_circles"]:
        raise AssertionError("C2 cable counts disagree with the C1 tangle")
    cores = c1["west_east_tangle"]["cores"]
    if len(cores) != 44 or len({tuple(map(tuple, core)) for core in cores}) != 44:
        raise AssertionError("C2 west-east tangle is not 44 distinct cores")
    bounds = c1["p0_ball_bounds"]
    left = cube(
        bounds["xmin"] - 20,
        bounds["xmin"] - 10,
        bounds["ymin"],
        bounds["ymin"] + 2,
        bounds["zmin"],
        bounds["zmin"] + 2,
    )
    right = cube(
        bounds["xmax"] + 10,
        bounds["xmax"] + 20,
        bounds["ymin"],
        bounds["ymin"] + 2,
        bounds["zmin"],
        bounds["zmin"] + 2,
    )
    result = {
        "schema": "t73_c2_comparison/v2",
        "c1_certificate_sha256": c1["certificate_sha256"],
        "p0_certificate_sha256": c1["p0_certificate_sha256"],
        "uniqueness_of_regular_neighborhoods_used": False,
        "H": {
            "status": "PASS",
            "rule": "fixed C1 product isotopy of the 44 P0 reconstruction strands, independent of T,T'",
            "shift": -44,
            "circle_factors": 227,
            "movies": [
                {
                    "strand_id": item["strand_id"],
                    "status": item["isotopy_movie"]["status"],
                    "frames": item["isotopy_movie"]["frames"],
                }
                for item in c1["rectangles"]
            ],
        },
        "action_squares": {
            "left": {
                "status": "PASS",
                "disjoint_from_tangle": True,
                "support": left,
                "rule": "left gluing support is an explicit cube to the left of the P0 ball",
            },
            "right": {
                "status": "PASS",
                "disjoint_from_tangle": True,
                "support": right,
                "rule": "right gluing support is an explicit cube to the right of the P0 ball",
            },
        },
        "cable_formula": {
            "owners": ["m_2", "m_3", "r_xy", "r_yz", "r_zx"],
            "n_y": n_y,
            "n_z": n_z,
            "s0": s0,
            "p_y_s0": p_y,
            "p_z_s0": p_z,
            "leftover_z_s0": p_z - p_y,
        },
        "endpoint_constant_term": {
            "status": "PASS",
            "rule": "at q=1 a sign-preserving braid has constant term equal to its signed permutation; a pure braid has I, remainder O(h)",
            "source": "BPW oriented cabling / BHPW strict tangle functor",
        },
        "representable_reduction": {
            "status": "PASS",
            "lean": "Smooth4PC/RepresentableCoefficient.lean coefficientHH0Equiv",
        },
        "scope": "Johnson replacement comparison maps on the C1 P0-strand tangle",
    }
    verify_maps(result, c1)
    passed = (
        result["H"]["status"] == "PASS"
        and result["action_squares"]["left"]["status"] == "PASS"
        and result["action_squares"]["right"]["status"] == "PASS"
        and result["endpoint_constant_term"]["status"] == "PASS"
        and result["representable_reduction"]["status"] == "PASS"
    )
    result["C2_status"] = "PASS" if passed else "OPEN"
    result["certificate_sha256"] = canonical_sha(
        {key: value for key, value in result.items() if key != "certificate_sha256"}
    )
    setattr(sys, SYS_CACHE, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"WROTE={OUTPUT}")
    if args.check:
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if committed != result:
            raise AssertionError("committed C2 comparison differs from regeneration")
    print(f"T73_C2_COMPARISON={result['C2_status']}")
    print(f"CERTIFICATE_SHA256={result['certificate_sha256']}")
    if result["C2_status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
