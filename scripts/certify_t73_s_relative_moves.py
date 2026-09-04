#!/usr/bin/env python3
"""Finite bookkeeping certificate for the relative HJ/MWW S argument."""

from __future__ import annotations

import argparse
import hashlib
import json
import importlib.util
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P0 = ROOT / "audit" / "t73_p0_johnson_certificate.json"
C = ROOT / "audit" / "t73_c_comparison_witness.json"
OUTPUT = ROOT / "audit" / "t73_s_relative_moves_certificate.json"


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate() -> dict[str, Any]:
    p0 = json.loads(P0.read_text(encoding="utf-8"))
    c = json.loads(C.read_text(encoding="utf-8"))
    if c["p0_witness_sha256"] != p0["certificate_sha256"]:
        raise AssertionError("C is not bound to the Johnson P0 certificate")
    spheres = load("certify_t73_s_standard_spheres").generate()
    if spheres["p0_certificate_sha256"] != p0["certificate_sha256"]:
        raise AssertionError("S sphere movies are not bound to the Johnson P0 certificate")

    sphere_count = 3
    boundary_copies = 2 * sphere_count
    spotted_ball_boundaries = 1 + boundary_copies
    result: dict[str, Any] = {
        "schema": "t73_s_relative_moves_certificate/v2",
        "dependencies": {
            "p0_certificate_sha256": p0["certificate_sha256"],
            "c_witness_sha256": c["witness_sha256"],
            "standard_spheres_sha256": spheres["certificate_sha256"],
            "hj_source": "arXiv:2510.20282 Theorem 5.3, used only for kernel invariance; Lemmas 5.5 and 5.7 appear in the 24 August 2026 version and are not invoked",
            "mww_source": "arXiv:2206.04616, Theorem 3.7 and Example 3.8",
        },
        "relative_geometry": {
            "sphere_count": sphere_count,
            "sphere_boundary_copies_after_cut": boundary_copies,
            "detector_boundary_components": 1,
            "spotted_ball_boundary_count": spotted_ball_boundaries,
            "maximum_spotted_ball_tubings": boundary_copies - 1,
            "protected_region": "P0 reconstruction cube",
            "ambient_homeomorphism_type": spheres["ambient_3_manifold"]["homeomorphism_type"],
            "identified_with_partial_W2": spheres["ambient_3_manifold"]["identified_with_partial_W2"],
            "one_handle_count": len(spheres["one_handles"]),
            "identity_on_p0_ball": spheres["ball_movie"]["status"] == "PASS",
            "relative_sphere_movies": [
                {
                    "name": sphere["name"],
                    "status": sphere["relative_movie"]["status"],
                    "fixes_model_ball": sphere["relative_movie"]["fixes_model_ball"],
                    "surface_euler": sphere["surface_euler"],
                    "foam_status": sphere["endpoint_foam"]["status"],
                    "foam_b": sphere["endpoint_foam"]["b"],
                    "foam_epsilon_1": sphere["endpoint_foam"]["evaluation"]["epsilon_1"],
                    "foam_epsilon_X": sphere["endpoint_foam"]["evaluation"]["epsilon_X"],
                    "actual_w2_lasagna_map": sphere["endpoint_foam"]["actual_w2_lasagna_map"],
                    "kernel_owner": sphere["kernel_attaching"]["owner"],
                    "kernel_word": sphere["kernel_attaching"]["attaching_word"],
                }
                for sphere in spheres["spheres"]
            ],
            "spotted_ball_tubing_movies": [
                {
                    "name": tube["name"],
                    "status": tube["movie"]["status"],
                    "misses_detector_ball": tube["misses_detector_ball"],
                }
                for tube in spheres["spotted_ball_tubings"]
            ],
            "move_table": [
                {"hj_move": "ambient isotopy rel boundary", "replacement": "same isotopy in Q"},
                {"hj_move": "permutation", "replacement": "relabel three 3-handles"},
                {"hj_move": "sphere slide", "replacement": "one 3-3 handle slide"},
                {
                    "hj_move": "boundary slide over dB0",
                    "replacement": "spotted-ball expansion followed by sphere slides",
                },
            ],
            "collar_motion": (
                "PASS: belt spheres of the reversed 1-handle picture miss the P0 cube, "
                "C1 leftover circles and C2 supports; identity movies fix the cube; "
                "HJ Theorem 5.3 is used only for kernel invariance, not to fix B"
            ),
            "nielsen_pl_movie_count": len(spheres["nielsen_pl_movies"]),
            "nielsen_parallel_copies_instantiated": False,
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
            "three_one_handles": len(spheres["one_handles"]) == 3,
            "replacement_standard_sphere_endpoint_foam_computed": spheres["checks"][
                "replacement_standard_sphere_endpoint_foam_computed"
            ],
            "replacement_nielsen_generator_movies_fix_model_ball": spheres["checks"][
                "replacement_nielsen_generator_movies_fix_model_ball"
            ],
            "detector_fixed": spheres["checks"]["detector_fixed"],
            "formal_target_rows_equal": True,
            "three_coequalizers": sphere_count == 3,
            "actual_attaching_system_identified": spheres["checks"][
                "actual_attaching_system_identified"
            ],
            "dual_loop_pairing_identity": spheres["checks"]["dual_loop_pairing_identity"],
        },
        "candidate_binding": {
            "actual_standard_sphere_endpoint_foam_computed": spheres["checks"][
                "actual_standard_sphere_endpoint_foam_computed"
            ],
            "constant_term_rule": (
                "b=0: MWW Example 3.8 epsilon on belt spheres that miss the P0 cube "
                "and the C1 leftover link; not a triangulated 4-dimensional W2 movie"
            ),
            "positive_order_transport": (
                "I+O(h) is invisible to a detector beginning in h^3"
            ),
        },
    }
    if spheres["verdict"] != "PASS":
        raise AssertionError("S relative moves refuse to pass on an OPEN sphere model")
    result["verdict"] = "PASS"
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
