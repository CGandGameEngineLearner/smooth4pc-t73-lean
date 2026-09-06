#!/usr/bin/env python3
"""Persist the exact Rust clearance of repaired transition shell germs."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUBS = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
BANDS = ROOT / "audit/t73_x_band_global_r3_port_strips_receipt.json"
REPAIRED = ROOT / "audit/t73_x_m1_repaired_global_r3_middle_transition_cores_receipt.json"
OBSTRUCTION = ROOT / "audit/t73_x_m1_cross_system_core_clearance_obstruction.json"
MANIFEST = ROOT / "rust/t73_exact_cross_clearance/Cargo.toml"
LOCK = ROOT / "rust/t73_exact_cross_clearance/Cargo.lock"
SOURCE = ROOT / "rust/t73_exact_cross_clearance/src/main.rs"
OUTPUT = ROOT / "audit/t73_x_m1_repaired_stub_cross_clearance.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def wsl_path(path):
    absolute = path.resolve()
    return f"/mnt/{absolute.drive[0].lower()}/{absolute.as_posix()[3:]}"


def main():
    stubs = json.loads(STUBS.read_text())
    bands = json.loads(BANDS.read_text())
    repaired = json.loads(REPAIRED.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    if os.name != "nt":
        raise RuntimeError("run this receipt builder from the Windows host")
    root = wsl_path(ROOT)
    command = [
        "wsl.exe", "bash", "-lc",
        " && ".join((
            f"cd {root}/rust/t73_exact_cross_clearance",
            "source /home/lifesize/.cargo/env",
            "cargo build --release",
            f"cd {root}",
            "rust/t73_exact_cross_clearance/target/release/t73_exact_cross_clearance "
            "/mnt/c/Users/Administrator/.cache/t73_x_m1_complete_global_r3_replacement_cores.jsonl.gz "
            "/mnt/c/Users/Administrator/.cache/t73_x_band_global_r3_port_strips.jsonl.gz "
            "/mnt/c/Users/Administrator/.cache/t73_x_m1_repaired_global_r3_middle_transition_cores.jsonl.gz",
        )),
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    result = json.loads([line for line in completed.stdout.splitlines() if line.strip()][-1])
    band = result["stub_band_columns"]
    escapes = result["stub_transition_escape_germs"]
    lifts = result["stub_transition_lifts"]
    if result["verdict"] != "PASS_EXACT_STUB_CROSS_SYSTEM_CORE_CLEARANCE":
        raise AssertionError("repaired Rust cross-system clearance failed")
    if (band["expected_endpoint_incidences"], band["extra_intersections"]) != (6052, 0):
        raise AssertionError("repaired stub/band clearance changed")
    if (escapes["escape_germs"], escapes["expected_endpoint_incidences"], escapes["extra_intersections"]) != (3026, 3026, 0):
        raise AssertionError("repaired escape-germ clearance changed")
    if lifts["modular_pairs"] != 32021132 or lifts["modular_survivors"] != 0:
        raise AssertionError("repaired skew-lift modular clearance changed")
    receipt = {
        "schema": "t73_x_m1_repaired_stub_cross_clearance/v1",
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "global_band_port_strips_receipt_sha256": bands["sha256"],
        "repaired_middle_transition_cores_receipt_sha256": repaired["sha256"],
        "prior_collision_obstruction_sha256": obstruction["sha256"],
        "rust_manifest_sha256": file_sha256(MANIFEST),
        "rust_lock_sha256": file_sha256(LOCK),
        "rust_source_sha256": file_sha256(SOURCE),
        "rust_toolchain": "rustc 1.98.1",
        "rust_result": result,
        "old_collision_repaired": True,
        "stub_band_clearance": "PASS_EXACT",
        "stub_escape_germ_clearance": "PASS_EXACT",
        "stub_skew_lift_clearance": "PASS_THREE_PRIME_FILTER_WITH_ZERO_SURVIVORS",
        "remaining_cross_system_checks": [
            "band strips versus repaired transition non-shell segments",
            "translated middle cores versus repaired transitions",
            "stub subsystem inherited embeddedness transfer",
        ],
        "verdict": "PASS_X_M1_REPAIRED_STUB_CROSS_CLEARANCE",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "verdict": receipt["verdict"],
        "band_extra": band["extra_intersections"],
        "escape_extra": escapes["extra_intersections"],
        "skew_modular_survivors": lifts["modular_survivors"],
        "old_collision_repaired": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
