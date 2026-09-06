#!/usr/bin/env python3
"""Recompute and verify the Regina boundary-recognition receipt."""

from __future__ import annotations

import json

from build_t73_x_m1_regina_boundary_recognition import OUTPUT, build


def verify():
    saved = json.loads(OUTPUT.read_text())
    replayed = build()
    if saved != replayed:
        raise AssertionError("Regina boundary recognition receipt is stale")
    if not saved["support_prime_isomorphic_to_reference_s2xs1"]:
        raise AssertionError("support prime is not Regina's S2xS1")
    if not saved["standard_boundary"]["is_sphere"]:
        raise AssertionError("Regina does not recognize the standard boundary as S3")
    if not saved["standard_simplification_matches_reference_s3"]:
        raise AssertionError("standard simplification does not match Regina's S3")
    return {
        "verdict": "PASS_X_M1_REGINA_BOUNDARY_RECOGNITION_FULL",
        "regina_version": saved["regina_version"],
        "support_type": "S2 x S1",
        "support_prime_iso_sig": saved["support_prime_summands"][0]["iso_sig"],
        "standard_type": "S3",
        "standard_simplified_iso_sig": saved["standard_boundary"]["simplified_iso_sig"],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
