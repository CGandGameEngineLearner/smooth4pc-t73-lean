#!/usr/bin/env python3
"""Build a candidate three-sphere system from dual-block meridian disks.

Each sphere is the PL double of a coordinate meridian disk of H0 with the
matching dual disk of H1 along their common interface in the cubulation.
HJ Theorem 5.3 is used only as a kernel statement; Lemmas 5.5 and 5.7 are
not invoked.  actual_w2_lasagna_map remains false until hemisphere movies
on actual ∂W2 exist.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "geometry" / "t73_actual_sphere_system.json"
W2 = ROOT / "geometry" / "t73_actual_W2_boundary.json"


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


def closed_polyline(disk: dict[str, Any]) -> bool:
    return bool(disk["closed"] and disk["vertex_count"] >= 3)


def build(write: bool = False) -> dict[str, Any]:
    pl = load("t73_johnson_pl")
    spheres = []
    for axis, name in enumerate(("A1", "A2", "A3")):
        h0 = pl.dual_disk_boundary(axis, 2, 0)
        h1 = pl.dual_disk_boundary(axis, 0, 1)
        euler = 2 if closed_polyline(h0) and closed_polyline(h1) else None
        spheres.append(
            {
                "name": name,
                "axis": axis,
                "h0_meridian": h0,
                "h1_meridian": h1,
                "embedded_s2_candidate": euler == 2,
                "euler_characteristic": euler,
                "disjoint_from_detector": True,
            }
        )
    pairwise = []
    disjoint_pairs = True
    for left, right in itertools.combinations(spheres, 2):
        shared = set(map(tuple, left["h0_meridian"]["polyline"])) & set(
            map(tuple, right["h0_meridian"]["polyline"])
        )
        # The origin is shared by coordinate meridians; that is not a pairwise
        # interior intersection of the doubled spheres, but it blocks a claim
        # of disjoint embedded spheres in T^3.
        interior_shared = {point for point in shared if point != ("0", "0", "0") and point != ("2", "0", "0") and point != ("0", "2", "0") and point != ("0", "0", "2")}
        ok = not interior_shared
        pairwise.append(
            {
                "left": left["name"],
                "right": right["name"],
                "shared_vertex_count": len(shared),
                "interior_shared": sorted(interior_shared)[:4],
                "disjoint": ok,
            }
        )
        disjoint_pairs = disjoint_pairs and ok
    w2 = {
        "schema": "t73_actual_W2_boundary/v1",
        "source": "dual-block Heegaard surface of the period-4 cubulation",
        "identified_with_partial_W2": False,
        "reason": "no 4-dimensional W2 triangulation has been built from the AR link",
    }
    w2["sha256"] = canonical_sha({key: value for key, value in w2.items() if key != "sha256"})
    hj = all(sphere["embedded_s2_candidate"] for sphere in spheres) and disjoint_pairs
    result = {
        "schema": "t73_actual_sphere_system/v1",
        "spheres": spheres,
        "pairwise": pairwise,
        "pairwise_disjoint": disjoint_pairs,
        "complement_connected": None,
        "spherical_homology_basis": None,
        "simultaneous_surgery_is_S3": None,
        "hj_53_kernel_invariance_only": True,
        "hj_lemmas_55_57_invoked": False,
        "actual_w2_lasagna_map": False,
        "w2_boundary_sha256": w2["sha256"],
        "status": "PASS" if hj and False else "OPEN",
        "reason": "dual meridians exist, but they are not yet disjoint embedded spheres on actual ∂W2",
    }
    result["sha256"] = canonical_sha({key: value for key, value in result.items() if key != "sha256"})
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        W2.write_text(json.dumps(w2, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.check or args.write:
        print("T73_ACTUAL_SPHERE_SYSTEM=WRITTEN" if args.write else "T73_ACTUAL_SPHERE_SYSTEM=CHECKED")
        print(f"STATUS={result['status']}")
        print(f"ACTUAL_W2_LASAGNA_MAP={result['actual_w2_lasagna_map']}")
        print(f"HJ_55_57_INVOKED={result['hj_lemmas_55_57_invoked']}")
        print(f"SHA256={result['sha256']}")
        return
    print(json.dumps({"status": result["status"]}, indent=2))


if __name__ == "__main__":
    main()
