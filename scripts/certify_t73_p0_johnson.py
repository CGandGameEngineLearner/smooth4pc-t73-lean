#!/usr/bin/env python3
"""Final strict P0 certificate for the explicit Johnson replacement presentation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "audit" / "t73_p0_johnson_certificate.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def generate(run_geometric_braid: bool = True):
    factor = load("factor_t73_matrix_johnson").generate()
    bridge = load("certify_t73_johnson_ar_bridge").generate()
    side = load("search_t73_johnson_alpha_sides").generate()["known_candidate"]
    square_movie = load("generate_t73_johnson_alpha_movie").generate()
    relative = load("straighten_t73_johnson_relative_ball").generate()
    cancellation = load("certify_t73_johnson_cancellations").generate()
    collar = load("generate_t73_johnson_ribbon_collar").generate()
    sweeps = load("derive_t73_johnson_six_sweeps").generate(collar)
    recon = load("build_t73_p0_reconstruction_input").generate() if run_geometric_braid else None
    recon_pass = recon is not None and recon.get("reconstruction_verdict") == "PASS"
    checks = {
        "johnson_ar_affine_bridge": bridge["p0a_status"] == "PASS" and bridge["heegaard_handlebody_complex"] == "PASS",
        "matrix_factorization": factor["matrix_product_status"] == "PASS",
        "gap_free_basis": side["gap_is_bijective"],
        "exact_compact_m2": side["exact_compact_match"],
        "forty_four_channels": side["total_y_channels"] == 44,
        "zero_relative_ryz_coefficient": side["net_r_yz_coefficient"] == 0,
        "johnson_square_movie": square_movie["spine_pl_movie_status"] == "PASS",
        "relative_fixed_ball": relative["chosen_alpha_representative_local_identity_status"] == "PASS",
        "two_cancellations": cancellation["cancellation_status"] == "PASS",
        "embedded_framed_collar": recon_pass,
        "ar_passage_binding": recon_pass,
        "six_sweep_word": sweeps["verdict"] == "PASS",
        "geometric_braid": recon_pass,
        "noncircular_source_order": recon_pass,
    }
    passed = all(checks.values())
    result = {
        "schema": "t73_p0_johnson_certificate/v1",
        "verdict": "PASS" if passed else "OPEN",
        "P0_status": "PROVED_FOR_EXPLICIT_JOHNSON_REPLACEMENT_PRESENTATION" if passed else "OPEN",
        "historical_pd_claim": "NONE",
        "checks": checks,
        "hashes": {
            "johnson_ar_bridge": bridge["bridge_sha256"],
            "factorization": factor["witness_sha256"],
            "side_candidate": canonical_sha(side),
            "square_movie": square_movie["movie_sha256"],
            "relative_movie": relative["movie_sha256"],
            "cancellations": cancellation["certificate_sha256"],
            "collar": collar["collar_sha256"],
            "six_sweeps": sweeps["witness_sha256"],
            "geometric_braid": None if recon is None else recon["B44_sha256"],
        },
        "mathematical_scope": "explicit Johnson alpha-side AR replacement; not byte identity with the unavailable historical PD",
    }
    result["certificate_sha256"] = canonical_sha(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--skip-geometric-braid", action="store_true")
    args = parser.parse_args()
    if args.write and args.skip_geometric_braid:
        raise SystemExit("refusing to write a P0 certificate without the geometric braid")
    result = generate(not args.skip_geometric_braid)
    if args.write:
        COMMITTED.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"WROTE={COMMITTED}")
        print("T73_P0_JOHNSON_CERTIFICATE=PASS" if result["verdict"] == "PASS" else "T73_P0_JOHNSON_CERTIFICATE=OPEN")
        print(f"P0_STATUS={result['P0_status']}")
        print(f"CERTIFICATE_SHA256={result['certificate_sha256']}")
        print(f"B44_SHA256={result['hashes']['geometric_braid']}")
    if args.check:
        if not args.skip_geometric_braid:
            committed = json.loads(COMMITTED.read_text(encoding="utf-8"))
            if committed != result:
                raise AssertionError("committed Johnson P0 certificate differs from regeneration")
        print("T73_P0_JOHNSON_CERTIFICATE=PASS" if result["verdict"] == "PASS" else "T73_P0_JOHNSON_CERTIFICATE=OPEN")
        print(f"P0_STATUS={result['P0_status']}")
        print(f"CHECKS={result['checks']}")
        print(f"CERTIFICATE_SHA256={result['certificate_sha256']}")
        if result["verdict"] != "PASS":
            raise SystemExit(2)
        return
    if not args.write:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
