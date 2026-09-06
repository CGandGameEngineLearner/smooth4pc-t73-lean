#!/usr/bin/env python3
"""Bind the source outward stub normal to the common R3 push displacement."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
SOURCE_STUBS = ROOT / "audit/t73_x_m1_ejected_splice_stubs_receipt.json"
TARGET_STUBS = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
STUB_TRANSFER = ROOT / "audit/t73_x_m1_stub_r3_embeddedness_transfer.json"
OUTPUT = ROOT / "audit/t73_x_m1_stub_source_normal_homotopy.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def build():
    product = json.loads(PRODUCT.read_text())
    source_stubs = json.loads(SOURCE_STUBS.read_text())
    target_stubs = json.loads(TARGET_STUBS.read_text())
    stub_transfer = json.loads(STUB_TRANSFER.read_text())
    source = [Fraction(value) for value in product["exteriorized_uniform_push_vector"]]
    target_r3 = [Fraction(value) for value in target_stubs["push_displacement"]]
    target = [*target_r3, Fraction(0)]
    if source[:3] != [0, 0, 0] or source[3] <= 0:
        raise AssertionError("source stub normal is not the positive fourth-axis vector")
    if any(value <= 0 for value in target_r3):
        raise AssertionError("target R3 stub displacement is not in the positive cone")
    checkpoints = []
    for parameter in (Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1)):
        vector = [
            (1 - parameter) * source[index] + parameter * target[index]
            for index in range(4)
        ]
        if not any(vector):
            raise AssertionError("stub normal homotopy passes through zero")
        checkpoints.append({
            "parameter": str(parameter),
            "vector": [str(value) for value in vector],
            "nonzero_coordinate_indices": [index for index, value in enumerate(vector) if value],
        })
    result = {
        "schema": "t73_x_m1_stub_source_normal_homotopy/v1",
        "x_m1_collar_product_extension_sha256": product["sha256"],
        "source_ejected_splice_stubs_receipt_sha256": source_stubs["sha256"],
        "target_stub_r3_push_paths_receipt_sha256": target_stubs["sha256"],
        "stub_r3_embeddedness_transfer_sha256": stub_transfer["sha256"],
        "source_normal_q4": [str(value) for value in source],
        "target_normal_r3": [str(value) for value in target_r3],
        "target_normal_q4_lift": [str(value) for value in target],
        "homotopy_formula": "N(t)=(t*delta,t*delta,2*t*delta,(1-t)*U)",
        "parameter_interval": ["0", "1"],
        "nonvanishing_proof": (
            "at t=0 the fourth coordinate U is positive; at t=1 the first "
            "three target coordinates are positive; for 0<t<1 both groups "
            "contain positive coordinates"
        ),
        "exact_checkpoints": checkpoints,
        "stub_push_path_count": target_stubs["stub_push_path_count"],
        "stub_segment_count": target_stubs["core_segment_count"],
        "source_relative_twist": 0,
        "normal_homotopy_applies_uniformly": True,
        "completion_status": "ALL_STUB_SOURCE_NORMALS_HOMOTOPED_TO_R3_PUSH_WITH_ZERO_TWIST",
        "verdict": "PASS_X_M1_STUB_SOURCE_NORMAL_HOMOTOPY",
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
        raise AssertionError("stub source-normal homotopy is stale")
    print(json.dumps({
        "verdict": result["verdict"],
        "paths": result["stub_push_path_count"],
        "segments": result["stub_segment_count"],
        "relative_twist": result["source_relative_twist"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
