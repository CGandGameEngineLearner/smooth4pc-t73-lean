#!/usr/bin/env python3
"""Run the exact Rust cross-system checker and persist its first obstruction."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSEMBLY = ROOT / "audit/t73_x_m1_complete_global_r3_replacement_cores_receipt.json"
BANDS = ROOT / "audit/t73_x_band_global_r3_port_strips_receipt.json"
TRANSITIONS = ROOT / "audit/t73_x_m1_global_r3_middle_transition_cores_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
MANIFEST = ROOT / "rust/t73_exact_cross_clearance/Cargo.toml"
LOCK = ROOT / "rust/t73_exact_cross_clearance/Cargo.lock"
SOURCE = ROOT / "rust/t73_exact_cross_clearance/src/main.rs"
OUTPUT = ROOT / "audit/t73_x_m1_cross_system_core_clearance_obstruction.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def wsl_path(path):
    absolute = path.resolve()
    drive = absolute.drive[0].lower()
    rest = absolute.as_posix()[3:]
    return f"/mnt/{drive}/{rest}"


def main():
    assembly = json.loads(ASSEMBLY.read_text())
    bands = json.loads(BANDS.read_text())
    transitions = json.loads(TRANSITIONS.read_text())
    stubs = json.loads(STUBS.read_text())
    if os.name == "nt":
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
                "/mnt/c/Users/Administrator/.cache/t73_x_m1_global_r3_middle_transition_cores.jsonl.gz",
            )),
        ]
    else:
        command = [
            str(ROOT / "rust/t73_exact_cross_clearance/target/release/t73_exact_cross_clearance"),
            str(Path(assembly["cache_path"])),
            str(Path(bands["cache_path"])),
            str(Path(transitions["cache_path"])),
        ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    rust_result = json.loads(lines[-1])
    collision = rust_result["stub_transition_lifts"]["first_extra_intersection"]
    expected_collision = {
        "transition": 0,
        "transition_band": 0,
        "transition_side": "first",
        "stub_band": 1,
        "stub_piece": "target_complement_first",
        "stub_segment": 1,
    }
    if rust_result["verdict"] != "FAIL_EXACT_STUB_TRANSITION_CROSS_SYSTEM_COLLISION":
        raise AssertionError("Rust checker did not fail closed on the known collision")
    if collision != expected_collision:
        raise AssertionError(f"first exact collision changed: {collision}")
    if rust_result["stub_band_columns"]["extra_intersections"] != 0:
        raise AssertionError("stub/band port columns unexpectedly intersect")
    result = {
        "schema": "t73_x_m1_cross_system_core_clearance_obstruction/v1",
        "complete_global_r3_replacement_cores_receipt_sha256": assembly["sha256"],
        "global_band_port_strips_receipt_sha256": bands["sha256"],
        "global_middle_transition_cores_receipt_sha256": transitions["sha256"],
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "rust_manifest_sha256": file_sha256(MANIFEST),
        "rust_lock_sha256": file_sha256(LOCK),
        "rust_source_sha256": file_sha256(SOURCE),
        "rust_toolchain": "rustc 1.98.1",
        "rust_result": rust_result,
        "stub_band_clearance_status": "PASS_EXACT",
        "stub_transition_clearance_status": "REFUTED_BY_EXACT_INTERSECTION",
        "complete_replacement_core_embedding_status": "OPEN_REPAIR_TRANSITION_SHELL_ESCAPE_GERMS",
        "preserved_results": [
            "all 89258 R3 core coordinates and 12104 cross-piece endpoint matches",
            "internal band-strip clearance",
            "internal middle-transition-family centerline clearance",
            "stub-to-band expected endpoint incidences with no extras",
        ],
        "required_repair": (
            "replace the common skew shell lift by port-local escape germs "
            "that are exactly clear of every nonincident stub segment, then "
            "rerun this cross-system verifier"
        ),
        "completion_status": "FIRST_EXACT_STUB_TRANSITION_COLLISION_PERSISTED",
        "verdict": "PASS_EXACT_CROSS_SYSTEM_COLLISION_OBSTRUCTION",
    }
    result["sha256"] = canonical_sha256(result)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "verdict": result["verdict"],
        "stub_band_extra": rust_result["stub_band_columns"]["extra_intersections"],
        "stub_transition_extra_at_least": rust_result["stub_transition_lifts"]["extra_intersections_at_least"],
        "first_collision": collision,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
