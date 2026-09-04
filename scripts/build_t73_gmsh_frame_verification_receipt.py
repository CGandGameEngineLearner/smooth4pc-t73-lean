#!/usr/bin/env python3
"""Persist the independent verification result for the Gmsh prefix-10 frame."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRAME = ROOT / "geometry/examples/t73_selected_source_gmsh_prefix10_frame.json"
SOURCE = ROOT / "geometry/t73_selected_source_exterior.json"
OUTPUT = ROOT / "audit/t73_selected_source_gmsh_prefix10_frame_verification.json"


def canonical_sha(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_verifier():
    path = ROOT / "scripts/verify_t73_selected_source_tetrahedral_frame.py"
    spec = importlib.util.spec_from_file_location("gmsh_frame_receipt_verifier", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_full():
    verifier = load_verifier()
    result = verifier.inspect(FRAME)
    if result.get("verdict") != "PASS_PREFIX_ONLY":
        raise AssertionError(f"Gmsh prefix-10 frame did not pass: {result}")
    frame = json.loads(FRAME.read_text(encoding="utf-8"))
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    receipt = {
        "schema": "t73_gmsh_frame_verification_receipt/v1",
        "frame_path": str(FRAME.relative_to(ROOT)),
        "frame_content_sha256": file_sha(FRAME),
        "frame_payload_sha256": frame["sha256"],
        "source_exterior_sha256": source["sha256"],
        "verifier": "scripts/verify_t73_selected_source_tetrahedral_frame.py",
        "result": result,
        "status": "PASS_PREFIX_ONLY",
    }
    receipt["sha256"] = canonical_sha(receipt)
    return receipt


def check_files(receipt):
    payload = {key: value for key, value in receipt.items() if key != "sha256"}
    if receipt.get("sha256") != canonical_sha(payload):
        raise AssertionError("Gmsh frame receipt hash is stale")
    frame = json.loads(FRAME.read_text(encoding="utf-8"))
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if receipt.get("frame_content_sha256") != file_sha(FRAME):
        raise AssertionError("Gmsh frame bytes changed after verification")
    if receipt.get("frame_payload_sha256") != frame.get("sha256"):
        raise AssertionError("Gmsh frame payload changed after verification")
    if receipt.get("source_exterior_sha256") != source.get("sha256"):
        raise AssertionError("Gmsh verification receipt is stale relative to source")
    result = receipt.get("result", {})
    expected = {
        "verdict": "PASS_PREFIX_ONLY",
        "vertices": 2664,
        "tetrahedra": 14599,
        "boundary_components": 5,
        "arcs": 10,
        "ribbons": 10,
        "exact_exterior_volume": "63968",
    }
    if any(result.get(key) != value for key, value in expected.items()):
        raise AssertionError("Gmsh verification receipt counts/status changed")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check-files", action="store_true")
    args = parser.parse_args()
    if args.write:
        receipt = build_full()
        OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        receipt = json.loads(OUTPUT.read_text(encoding="utf-8"))
    check_files(receipt)
    print("T73_GMSH_PREFIX10_FRAME_RECEIPT=PASS_PREFIX_ONLY")
    print(f"SHA256={receipt['sha256']}")


if __name__ == "__main__":
    main()
