#!/usr/bin/env python3
"""Verify the saved Gmsh resource receipt without treating it as a mesh."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "geometry" / "t73_selected_source_exterior.json"
RECEIPT = ROOT / "audit" / "t73_selected_source_gmsh_prefix20.json"


def canonical_sha(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def verify(receipt):
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if receipt.get("schema") != "t73_selected_source_gmsh_probe/v1":
        raise AssertionError("unexpected Gmsh probe schema")
    recorded = receipt.get("sha256")
    payload = {key: value for key, value in receipt.items() if key != "sha256"}
    if recorded != canonical_sha(payload):
        raise AssertionError("Gmsh probe receipt hash is stale")
    if receipt.get("source_exterior_sha256") != source["sha256"]:
        raise AssertionError("Gmsh probe is stale relative to source exterior")
    expected = {
        "route_prefix": 20,
        "ribbon_surfaces": 80,
        "endpoint_connectors": 40,
        "boundary_surfaces": 30,
        "gmsh_algorithm_3d": 10,
        "mesh_nodes": 4134,
        "tetrahedra": 23725,
        "status": "PASS_PROBE_ONLY",
    }
    for key, value in expected.items():
        if receipt.get(key) != value:
            raise AssertionError(f"Gmsh probe field {key} changed")
    if "frame" in receipt or "tetrahedron_vertices" in receipt:
        raise AssertionError("probe receipt improperly claims to contain a mesh artifact")
    return {
        "verdict": "PASS_RECEIPT_ONLY",
        **expected,
        "full_630_frame": "OPEN",
        "sha256": recorded,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = verify(json.loads(RECEIPT.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
