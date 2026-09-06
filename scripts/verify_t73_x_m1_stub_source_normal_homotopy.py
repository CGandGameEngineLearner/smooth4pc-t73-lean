#!/usr/bin/env python3
"""Verify the uniform nonvanishing source-to-R3 stub normal homotopy."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_stub_source_normal_homotopy.json"
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
TARGET = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def verify():
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("stub normal-homotopy payload SHA mismatch")
    product = json.loads(PRODUCT.read_text())
    target = json.loads(TARGET.read_text())
    if data["x_m1_collar_product_extension_sha256"] != product["sha256"]:
        raise AssertionError("stub normal-homotopy source binding changed")
    if data["target_stub_r3_push_paths_receipt_sha256"] != target["sha256"]:
        raise AssertionError("stub normal-homotopy target binding changed")
    source = [Fraction(value) for value in data["source_normal_q4"]]
    target_lift = [Fraction(value) for value in data["target_normal_q4_lift"]]
    if source != [Fraction(value) for value in product["exteriorized_uniform_push_vector"]]:
        raise AssertionError("stub source normal changed")
    if target_lift[:3] != [Fraction(value) for value in target["push_displacement"]] or target_lift[3] != 0:
        raise AssertionError("stub target normal lift changed")
    for numerator in range(1001):
        parameter = Fraction(numerator, 1000)
        vector = [
            (1 - parameter) * source[index] + parameter * target_lift[index]
            for index in range(4)
        ]
        if not any(vector):
            raise AssertionError("stub normal homotopy vanished on verifier grid")
        if 0 < parameter < 1 and not (vector[0] > 0 and vector[3] > 0):
            raise AssertionError("stub normal homotopy left its positive cone")
    if data["source_relative_twist"] != 0 or not data["normal_homotopy_applies_uniformly"]:
        raise AssertionError("stub normal homotopy has nonzero twist or incomplete scope")
    return {
        "verdict": "PASS_X_M1_STUB_SOURCE_NORMAL_HOMOTOPY",
        "stub_push_paths": data["stub_push_path_count"],
        "stub_segments": data["stub_segment_count"],
        "exact_parameter_checks": 1001,
        "relative_twist": 0,
        "uniform_nonvanishing_homotopy": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
