#!/usr/bin/env python3
"""Verify the actual partial-W2 boundary and its three attaching spheres."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPHERES = ROOT / "geometry" / "t73_actual_sphere_system.json"
W2 = ROOT / "geometry" / "t73_actual_W2_boundary.json"
DUAL_DISKS = ROOT / "geometry" / "t73_johnson_dual_disk_movie.json"
SURFACE_TRANSPORT = ROOT / "geometry" / "t73_three_handle_surface_transport.json"


def load(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(data, w2):
    if not w2["identified_with_partial_W2"] or w2["handle_counts_at_W2"] != [1, 2, 5, 0, 0]:
        raise AssertionError("sphere system is not bound to the actual W2 boundary")
    if len(data["spheres"]) != 3 or not data["pairwise_disjoint"] or not data["complement_connected"]:
        raise AssertionError("actual three-handle sphere system is incomplete")
    if not data["simultaneous_surgery_is_S3"] or not data["simultaneous_surgery_in_reversed_model_is_S3"]:
        raise AssertionError("actual sphere surgery does not reach S3")
    expected_b = [12578, 1824, 409]
    for sphere, b_count in zip(data["spheres"], expected_b):
        if sphere["surface_euler"] != 2 or not sphere["embedded_s2_in_reversed_model"] or not sphere["embedded_s2_on_actual_W2"]:
            raise AssertionError("actual attaching surface is not an embedded S2")
        profile_count = sum(item["copy_count"] for item in sphere["core_disk_boundary_profile"])
        if sphere["core_disk_intersection_count_b"] != profile_count or profile_count != b_count:
            raise AssertionError("actual sphere/core-disk intersection profile changed")
        if not sphere["disjoint_from_detector"]:
            raise AssertionError("actual attaching sphere meets the detector ball")
    if data["spherical_homology_basis"]["dual_loop_pairing_matrix"] != [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
        raise AssertionError("sphere/dual-loop pairing is not the identity")
    if data["hj_lemmas_55_57_invoked"]:
        raise AssertionError("forbidden HJ Lemma 5.5/5.7 route was invoked")


def verify():
    builder = load("build_t73_actual_sphere_system")
    stored = json.loads(SPHERES.read_text(encoding="utf-8"))
    w2 = json.loads(W2.read_text(encoding="utf-8"))
    dual_disks = json.loads(DUAL_DISKS.read_text(encoding="utf-8"))
    surface_transport = json.loads(SURFACE_TRANSPORT.read_text(encoding="utf-8"))
    rebuilt = builder.build(write=False)
    if stored != rebuilt:
        raise AssertionError("stored actual sphere system does not match a live rebuild")
    validate(stored, w2)
    if stored["johnson_dual_disk_movie_sha256"] != dual_disks["sha256"]:
        raise AssertionError("sphere profile is not bound to the actual H1 disk movie")
    if stored["three_handle_surface_transport_sha256"] != surface_transport["sha256"]:
        raise AssertionError("sphere system is not bound to the Kirby surface transport")
    mutant = copy.deepcopy(stored)
    mutant["spheres"][0]["core_disk_boundary_profile"][0]["copy_count"] += 1
    failed = False
    try:
        validate(mutant, w2)
    except AssertionError:
        failed = True
    if not failed:
        raise AssertionError("sphere boundary-copy mutation was not detected")
    return {
        "REVERSED_SPHERE_MODEL": "PASS",
        "ACTUAL_W2_BOUNDARY": "PASS",
        "ACTUAL_SPHERE_SYSTEM": "PASS",
        "CORE_DISK_COUNTS": [12578, 1824, 409],
        "SIMULTANEOUS_SURGERY": "S3",
        "HJ_55_57_INVOKED": False,
        "MUTATION_BOUNDARY_COPY": "FAIL",
        "SHA256": stored["sha256"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.check:
        for key, value in result.items():
            print(f"{key}={value}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
