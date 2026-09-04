#!/usr/bin/env python3
"""Build the C-H1 co-Yoneda certificate only after a coordinate movie passes."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MOVIE = ROOT / "geometry" / "t73_c_h1_relative_isotopy.json"
OUTPUT = ROOT / "audit" / "t73_c_h1_coend_certificate.json"


def load_verifier():
    path = ROOT / "scripts" / "verify_t73_c_h1_relative_isotopy.py"
    spec = importlib.util.spec_from_file_location("c_h1_movie_verifier", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build() -> dict:
    verifier = load_verifier()
    report = verifier.generate_report()
    if report["status"] != "PASS_COORDINATE_MOVIE":
        mismatch = report.get("boundary_endpoint_mismatch")
        mismatch_text = (
            "; source/target boundary totals "
            + str(mismatch.get("source_total"))
            + "/"
            + str(mismatch.get("target_total"))
            if mismatch
            else ""
        )
        raise RuntimeError(
            "C-H1 co-Yoneda certificate requires PASS_COORDINATE_MOVIE; status="
            + report["status"]
            + mismatch_text
            + "; "
            + "; ".join(report.get("missing", []))
        )
    movie = json.loads(MOVIE.read_text(encoding="utf-8"))
    p_y, p_z, ell = 44, 271, 227
    return {
        "schema": "t73_c_h1_coend_certificate/v1",
        "relative_isotopy_sha256": verifier.canonical_sha(movie),
        "coefficient_category": "C_44 tensor C_271",
        "representable_shift_normalized": p_y - p_z,
        "co_yoneda_shift": -ell,
        "split_circle_kunneth_shift": ell,
        "reduced_normalized_shift": 0,
        "circle_factors": ell,
        "all_X_degree": ell,
        "cabled_shift": -4,
        "final_degree": ell - 4,
        "statewise_shadow_target": "End(E_88)",
        "cup_position": "external E_86 -> E_88",
        "status": "PASS_FROM_COORDINATE_MOVIE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
