from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def checked_relative_path(root: Path, raw: str) -> Path:
    posix = PurePosixPath(raw)
    if posix.is_absolute() or ".." in posix.parts or not posix.parts:
        raise ValueError(f"unsafe receipt path: {raw}")
    resolved = (root / Path(*posix.parts)).resolve()
    resolved.relative_to(root)
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the frozen Task4 source/dump receipt.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    try:
        root = args.root.resolve()
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        if receipt.get("schema") != "smooth4pc_t73_task4_remote_receipt/v1":
            raise ValueError("unexpected receipt schema")
        if receipt.get("epistemic_status") != "INTERFACE_SURFACE_FROZEN_ONLY":
            raise ValueError("receipt overstates the epistemic status")
        files = receipt["files"]
        if not isinstance(files, dict) or not files:
            raise ValueError("receipt files must be a nonempty object")
        for raw_path, expected in files.items():
            path = checked_relative_path(root, raw_path)
            if not path.is_file():
                raise ValueError(f"missing receipt file: {raw_path}")
            actual_bytes = path.stat().st_size
            actual_sha = sha256(path)
            if actual_bytes != expected["bytes"]:
                raise ValueError(
                    f"byte-count mismatch for {raw_path}: "
                    f"expected={expected['bytes']} actual={actual_bytes}"
                )
            if actual_sha != expected["sha256"].upper():
                raise ValueError(
                    f"SHA-256 mismatch for {raw_path}: "
                    f"expected={expected['sha256'].upper()} actual={actual_sha}"
                )
        remote_files = receipt["remote_verified_files"]
        for raw_path, remote in remote_files.items():
            if raw_path not in files:
                raise ValueError(f"remote-only unbound file: {raw_path}")
            local = files[raw_path]
            if remote["sha256"].upper() != local["sha256"].upper():
                raise ValueError(f"remote/local SHA mismatch for {raw_path}")
            if remote["bytes"] != local["bytes"]:
                raise ValueError(f"remote/local byte-count mismatch for {raw_path}")
        manifest_path = checked_relative_path(root, "audit/interface_manifest.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        dump_entry = files["audit/lean_type_dump.txt"]
        if manifest["lean_dump_sha256"].upper() != dump_entry["sha256"].upper():
            raise ValueError("manifest/dump SHA mismatch")
        runs = receipt["remote_runs"]
        if runs.get("interfaces_exit") != 0 or runs.get("audit_type_exit") != 0:
            raise ValueError("remote Lean run was not successful")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print("task4 receipt gate: FAIL", file=sys.stderr)
        print(error, file=sys.stderr)
        return 1

    print("task4 receipt gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
