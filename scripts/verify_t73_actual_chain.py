#!/usr/bin/env python3
"""Replay the current actual-geometry certificate chain in dependency order."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CORE_COMMANDS = [
    ["scripts/verify_t73_actual_ar_link.py", "--check"],
    ["scripts/verify_t73_handle_cancellation.py", "--check"],
    ["scripts/verify_t73_actual_cut_tangle.py", "--check"],
    ["scripts/verify_t73_actual_product_rectangles.py", "--check"],
    ["scripts/verify_t73_actual_leftover_z_circles.py", "--check"],
    ["scripts/verify_t73_actual_geometric_braid.py", "--check"],
    ["scripts/verify_t73_endpoint_transport.py", "--check"],
    ["scripts/recompute_t73_delta3.py", "--check"],
    ["scripts/verify_t73_product_ribbon_isotopy.py", "--check"],
    ["scripts/generate_t73_c_comparison_witness.py", "--check"],
    ["scripts/verify_t73_johnson_dual_disk_movie.py", "--check"],
    ["scripts/verify_t73_three_handle_surface_transport.py", "--check"],
    ["scripts/verify_t73_actual_sphere_system.py", "--check"],
    ["scripts/verify_t73_hemisphere_movies.py", "--check"],
    ["scripts/certify_t73_s_relative_moves.py", "--check"],
    ["scripts/certify_t73_p3_four_handle.py", "--check"],
    ["scripts/certify_t73_e12_s4.py", "--check"],
    ["scripts/certify_t73_e13_close.py", "--check"],
    ["scripts/certify_t73_e13_identification.py", "--check"],
    ["scripts/audit_t73_premises.py", "--check"],
    ["scripts/check_t73_claim_boundary.py", "--check"],
]

FULL_PREFIX = [
    ["scripts/verify_t73_pl_homeomorphism.py", "--check"],
    ["scripts/verify_t73_johnson_spine_binding.py", "--check"],
    ["scripts/certify_t73_p0_johnson.py", "--check"],
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        action="store_true",
        help="also replay the expensive 93-factor PL and aggregate P0 checks",
    )
    args = parser.parse_args()
    commands = (FULL_PREFIX if args.full else []) + CORE_COMMANDS
    for index, command in enumerate(commands, start=1):
        rendered = " ".join([sys.executable, *command])
        print(f"[{index}/{len(commands)}] {rendered}", flush=True)
        subprocess.run([sys.executable, *command], cwd=ROOT, check=True)
    print("T73_ACTUAL_CHAIN=PASS")
    print("T73_FORMAL_STATUS=CONDITIONAL_EXTERNAL_GEOMETRY")


if __name__ == "__main__":
    main()
