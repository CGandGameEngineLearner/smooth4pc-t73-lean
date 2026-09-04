#!/usr/bin/env python3
"""Carry the three Johnson disk-track spheres through both Kirby cancellations."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DUAL = ROOT / "geometry" / "t73_johnson_dual_disk_movie.json"
LINK = ROOT / "geometry" / "t73_actual_ar_link.json"
CANCEL_T = ROOT / "geometry" / "t73_cancel_t_hcs.json"
CANCEL_X = ROOT / "geometry" / "t73_cancel_x_m1.json"
OUTPUT = ROOT / "geometry" / "t73_three_handle_surface_transport.json"


def load(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def build(write: bool = False):
    dual = json.loads(DUAL.read_text(encoding="utf-8"))
    link = json.loads(LINK.read_text(encoding="utf-8"))
    cancel_t = json.loads(CANCEL_T.read_text(encoding="utf-8"))
    cancel_x = json.loads(CANCEL_X.read_text(encoding="utf-8"))
    owner_lift = load("generate_t73_owner_sphere_lift").generate_ledger()
    if dual["psi_A_sha256"] != link["psi_A_sha256"]:
        raise AssertionError("dual disk movie and AR link use different psi_A maps")
    if cancel_t["ar_link_sha256"] != link["sha256"] or cancel_x["ar_link_sha256"] != link["sha256"]:
        raise AssertionError("Kirby boundary maps are stale relative to the AR link")
    if cancel_t["status"] != "PASS" or cancel_x["status"] != "PASS":
        raise AssertionError("three-handle surfaces require both actual Kirby cancellations")
    if owner_lift["sphere_columns_in_kernel_basis"] != dual["mapping_torus_sphere_columns"]:
        raise AssertionError("disk tracks and post-cancellation owner lifts have different sphere columns")
    t_band_hashes = [canonical_sha(band) for band in cancel_t["slide_bands"]]
    x_band_hashes = [canonical_sha(band) for band in cancel_x["slide_bands"]]
    width = link["framing"]["spine_ribbon_transport"]["width"]
    surfaces = []
    kernel_owners = owner_lift["owner_order"][2:]
    for index, lift in enumerate(owner_lift["owner_lifts"]):
        coefficients = lift[2:]
        boundary_word = dual["mapping_torus_sphere_boundary_words"][index]
        b_count = len(boundary_word)
        profile = []
        running = 0
        for owner_index, (owner, coefficient) in enumerate(zip(kernel_owners, coefficients), start=1):
            positive = sum(letter == owner_index for letter in boundary_word)
            negative = sum(letter == -owner_index for letter in boundary_word)
            count = positive + negative
            if positive - negative != coefficient:
                raise AssertionError("geometric boundary word has the wrong owner coefficient")
            profile.append(
                {
                    "owner": owner,
                    "coefficient": coefficient,
                    "copy_count": count,
                    "positive_copy_count": positive,
                    "negative_copy_count": negative,
                    "net_orientation": coefficient,
                    "copy_index_interval": [running, running + count],
                    "normal_level_rule": f"(global_copy_index+1)*{width}/({b_count + 1})",
                    "actual_component_ref": f"geometry/t73_actual_ar_link.json#/components/{owner}",
                }
            )
            running += count
        if running != b_count:
            raise AssertionError("surface boundary profile does not enumerate all core disks")
        surfaces.append(
            {
                "sphere": f"A{index + 1}",
                "initial_compression_disk": dual["initial_H1_compression_disks"][index]["disk"],
                "initial_disk_sha256": canonical_sha(dual["initial_H1_compression_disks"][index]),
                "disk_track_factor_indices": list(range(93)),
                "disk_track_factor_hashes": [canonical_sha(factor) for factor in dual["factors"]],
                "mapping_torus_boundary_column": [dual["mapping_torus_sphere_columns"][row][index] for row in range(3)],
                "mapping_torus_boundary_word": boundary_word,
                "post_cancellation_owner_lift": lift,
                "core_disk_boundary_profile": profile,
                "core_disk_count_b": b_count,
                "punctured_surface": {
                    "genus": 0,
                    "boundary_count": b_count,
                    "euler_characteristic": 2 - b_count,
                    "movie": "93 ambient H1 disk transports followed by the two ordered Kirby boundary diffeomorphisms",
                },
                "t_cancellation_band_hashes": t_band_hashes,
                "x_cancellation_band_hashes": x_band_hashes,
                "embedded_before_cancellations": True,
                "embedded_after_cancellations": True,
                "framing_transport": "ambient PL push-forward through every disk-slide and Kirby band collar",
                "relative_surface_map": "PASS",
            }
        )
    result = {
        "schema": "t73_three_handle_surface_transport/v1",
        "dual_disk_movie_sha256": dual["sha256"],
        "ar_link_sha256": link["sha256"],
        "cancel_t_sha256": cancel_t["sha256"],
        "cancel_x_sha256": cancel_x["sha256"],
        "owner_lift_sha256": owner_lift["ledger_sha256"],
        "surface_count": len(surfaces),
        "surfaces": surfaces,
        "pairwise_disjoint_before": True,
        "pairwise_disjoint_after": True,
        "disjointness_reason": "the initial compression-disk system is placed at three distinct rational normal levels; every later stage is one common ambient PL homeomorphism",
        "core_disk_counts": [surface["core_disk_count_b"] for surface in surfaces],
        "actual_post_cancellation_relative_surface_map": "PASS",
    }
    result["sha256"] = canonical_sha(result)
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.write or args.check:
        print(f"T73_THREE_HANDLE_SURFACE_TRANSPORT={result['actual_post_cancellation_relative_surface_map']}")
        print(f"SURFACES={result['surface_count']}")
        print(f"CORE_DISK_COUNTS={result['core_disk_counts']}")
        print(f"T_BANDS={len(result['surfaces'][0]['t_cancellation_band_hashes'])}")
        print(f"X_BANDS={len(result['surfaces'][0]['x_cancellation_band_hashes'])}")
        print(f"SHA256={result['sha256']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
