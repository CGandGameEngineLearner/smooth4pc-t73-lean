#!/usr/bin/env python3
"""Persist an independent verification result for a Gmsh prefix frame."""

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
VERIFIER = "scripts/verify_t73_selected_source_tetrahedral_frame.py"
DEFAULT_EXPECTED = {
    "prefix": 10,
    "vertices": 2664,
    "tetrahedra": 14599,
    "arcs": 10,
    "ribbons": 10,
    "boundary_components": 5,
    "exact_exterior_volume": "63968",
}


def canonical_sha(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_verifier():
    path = ROOT / VERIFIER
    spec = importlib.util.spec_from_file_location("gmsh_frame_receipt_verifier", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expected_counts(
    *,
    prefix,
    vertices,
    tetrahedra,
    arcs,
    ribbons,
    boundary_components,
    exact_exterior_volume,
):
    return {
        "prefix": prefix,
        "vertices": vertices,
        "tetrahedra": tetrahedra,
        "arcs": arcs,
        "ribbons": ribbons,
        "boundary_components": boundary_components,
        "exact_exterior_volume": str(exact_exterior_volume),
    }


def build_full(frame_path=FRAME, expected=DEFAULT_EXPECTED):
    """Run the full independent verifier and construct a receipt in memory."""
    verifier = load_verifier()
    result = verifier.inspect(frame_path)
    if result.get("verdict") != "PASS_PREFIX_ONLY":
        raise AssertionError(f"Gmsh prefix frame did not pass: {result}")
    frame = json.loads(frame_path.read_text(encoding="utf-8"))
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    _check_expected(frame, result, expected)
    receipt = {
        "schema": "t73_gmsh_frame_verification_receipt/v1",
        "frame_path": frame_path.relative_to(ROOT).as_posix(),
        "frame_content_sha256": file_sha(frame_path),
        "frame_payload_sha256": frame["sha256"],
        "source_exterior_sha256": source["sha256"],
        "verifier": VERIFIER,
        "result": result,
        "status": "PASS_PREFIX_ONLY",
    }
    receipt["sha256"] = canonical_sha(receipt)
    return receipt


def _check_expected(frame, result, expected):
    if frame.get("scope") != f"prefix:{expected['prefix']}":
        raise AssertionError("Gmsh frame prefix scope changed")
    required_result = {
        "verdict": "PASS_PREFIX_ONLY",
        "vertices": expected["vertices"],
        "tetrahedra": expected["tetrahedra"],
        "boundary_components": expected["boundary_components"],
        "arcs": expected["arcs"],
        "ribbons": expected["ribbons"],
        "exact_exterior_volume": expected["exact_exterior_volume"],
        "sha256": frame.get("sha256"),
        "source_exterior_sha256": frame.get("source_exterior_sha256"),
    }
    if any(result.get(key) != value for key, value in required_result.items()):
        raise AssertionError("Gmsh verification receipt counts/status changed")


def check_files(receipt, frame_path=FRAME, expected=DEFAULT_EXPECTED):
    """Check saved bindings without rerunning the expensive frame verifier."""
    payload = {key: value for key, value in receipt.items() if key != "sha256"}
    if receipt.get("sha256") != canonical_sha(payload):
        raise AssertionError("Gmsh frame receipt hash is stale")
    if receipt.get("frame_path") != frame_path.relative_to(ROOT).as_posix():
        raise AssertionError("Gmsh verification receipt frame path changed")
    if receipt.get("verifier") != VERIFIER:
        raise AssertionError("Gmsh verification receipt verifier path changed")
    if receipt.get("status") != "PASS_PREFIX_ONLY":
        raise AssertionError("Gmsh verification receipt status changed")
    frame = json.loads(frame_path.read_text(encoding="utf-8"))
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if receipt.get("frame_content_sha256") != file_sha(frame_path):
        raise AssertionError("Gmsh frame bytes changed after verification")
    if receipt.get("frame_payload_sha256") != frame.get("sha256"):
        raise AssertionError("Gmsh frame payload changed after verification")
    if receipt.get("source_exterior_sha256") != source.get("sha256"):
        raise AssertionError("Gmsh verification receipt is stale relative to source")
    if frame.get("source_exterior_sha256") != source.get("sha256"):
        raise AssertionError("Gmsh frame is stale relative to source")
    _check_expected(frame, receipt.get("result", {}), expected)
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check-files", action="store_true")
    parser.add_argument("--frame", type=Path, default=FRAME)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument(
        "--expected-prefix", type=int, default=DEFAULT_EXPECTED["prefix"]
    )
    parser.add_argument(
        "--expected-vertices", type=int, default=DEFAULT_EXPECTED["vertices"]
    )
    parser.add_argument(
        "--expected-tetrahedra", type=int, default=DEFAULT_EXPECTED["tetrahedra"]
    )
    parser.add_argument("--expected-arcs", type=int, default=DEFAULT_EXPECTED["arcs"])
    parser.add_argument(
        "--expected-ribbons", type=int, default=DEFAULT_EXPECTED["ribbons"]
    )
    parser.add_argument(
        "--expected-boundary-components",
        type=int,
        default=DEFAULT_EXPECTED["boundary_components"],
    )
    parser.add_argument(
        "--expected-exact-volume",
        default=DEFAULT_EXPECTED["exact_exterior_volume"],
    )
    args = parser.parse_args()
    frame_path = args.frame if args.frame.is_absolute() else ROOT / args.frame
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    expected = expected_counts(
        prefix=args.expected_prefix,
        vertices=args.expected_vertices,
        tetrahedra=args.expected_tetrahedra,
        arcs=args.expected_arcs,
        ribbons=args.expected_ribbons,
        boundary_components=args.expected_boundary_components,
        exact_exterior_volume=args.expected_exact_volume,
    )
    if args.write:
        receipt = build_full(frame_path, expected)
        output_path.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    else:
        receipt = json.loads(output_path.read_text(encoding="utf-8"))
    check_files(receipt, frame_path, expected)
    print(f"T73_GMSH_PREFIX{expected['prefix']}_FRAME_RECEIPT=PASS_PREFIX_ONLY")
    print(f"SHA256={receipt['sha256']}")


if __name__ == "__main__":
    main()
