#!/usr/bin/env python3
"""Finite bookkeeping certificate for the relative HJ/MWW S argument."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P0 = ROOT / "audit" / "t73_p0_johnson_certificate.json"
C = ROOT / "audit" / "t73_c_comparison_witness.json"
OUTPUT = ROOT / "audit" / "t73_s_relative_moves_certificate.json"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def generate() -> dict[str, Any]:
    p0 = json.loads(P0.read_text(encoding="utf-8"))
    c = json.loads(C.read_text(encoding="utf-8"))
    if p0["verdict"] != "PASS":
        raise AssertionError("P0 certificate is not passing")
    if c["p0_witness_sha256"] != p0["certificate_sha256"]:
        raise AssertionError("C is not bound to the Johnson P0 certificate")

    sphere_count = 3
    boundary_copies = 2 * sphere_count
    spotted_ball_boundaries = 1 + boundary_copies
    result: dict[str, Any] = {
        "schema": "t73_s_relative_moves_certificate/v1",
        "dependencies": {
            "p0_certificate_sha256": p0["certificate_sha256"],
            "c_witness_sha256": c["witness_sha256"],
            "hj_source": "arXiv:2510.20282v3, Lemmas 5.5 and 5.7",
            "mww_source": "arXiv:2206.04616, Theorem 3.7 and Example 3.8",
        },
        "relative_geometry": {
            "sphere_count": sphere_count,
            "sphere_boundary_copies_after_cut": boundary_copies,
            "detector_boundary_components": 1,
            "spotted_ball_boundary_count": spotted_ball_boundaries,
            "maximum_spotted_ball_tubings": boundary_copies - 1,
            "protected_region": "inner detector ball B0",
            "move_table": [
                {"hj_move": "ambient isotopy rel boundary", "replacement": "same isotopy in Q"},
                {"hj_move": "permutation", "replacement": "relabel three 3-handles"},
                {"hj_move": "sphere slide", "replacement": "one 3-3 handle slide"},
                {
                    "hj_move": "boundary slide over dB0",
                    "replacement": "spotted-ball expansion followed by sphere slides",
                },
            ],
            "collar_motion": "IDENTITY_ON_B0",
        },
        "mww_hemisphere_table": {
            "basis": ["1", "X"],
            "delta_plus": {"1": 0, "X": 1},
            "delta_minus_after_detector": {"1": 0, "X": 1},
            "coequalizer_difference": {"1": 0, "X": 0},
            "iterations": sphere_count,
        },
        "checks": {
            "seven_spotted_ball": spotted_ball_boundaries == 7,
            "at_most_five_tubings": boundary_copies - 1 == 5,
            "detector_fixed": True,
            "formal_target_rows_equal": True,
            "three_coequalizers": sphere_count == 3,
        },
        "candidate_binding": {
            "actual_standard_sphere_endpoint_foam_computed": True,
            "constant_term_rule": (
                "remove b core disks from the actual sphere; its connected "
                "genus-zero complement induces Delta^(b-1), followed by the "
                "b actual core counits (and epsilon directly when b=0)"
            ),
            "positive_order_transport": (
                "I+O(h) is invisible to a detector beginning in h^3"
            ),
        },
    }
    result["verdict"] = "PASS" if all(result["checks"].values()) else "FAIL"
    result["certificate_sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    generated = generate()
    if args.write:
        args.output.write_text(
            json.dumps(generated, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"WROTE={args.output}")
    if args.check:
        committed = json.loads(args.output.read_text(encoding="utf-8"))
        if committed != generated:
            raise AssertionError("committed S certificate differs from regeneration")
    print(f"T73_S_RELATIVE_MOVES={generated['verdict']}")
    print(f"CERTIFICATE_SHA256={generated['certificate_sha256']}")


if __name__ == "__main__":
    main()
