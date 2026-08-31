from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def normalized(text: str) -> str:
    return " ".join(text.strip().split())


def parse_dump(path: Path) -> dict[str, str]:
    found: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        marker = raw_line.find("AUDIT_TYPE|")
        if marker < 0:
            continue
        raw_line = raw_line[marker:]
        _, declaration, type_text = raw_line.split("|", 2)
        if declaration in found:
            raise ValueError(f"duplicate declaration in dump: {declaration}")
        found[declaration] = normalized(type_text)
    return found


def parse_bodies(path: Path) -> dict[str, str]:
    found: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        marker = raw_line.find("AUDIT_BODY|")
        if marker < 0:
            continue
        raw_line = raw_line[marker:]
        _, declaration, body_text = raw_line.split("|", 2)
        if declaration in found:
            raise ValueError(f"duplicate declaration body in dump: {declaration}")
        found[declaration] = normalized(body_text)
    return found


def parse_fields(path: Path) -> dict[str, str]:
    found: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        marker = raw_line.find("AUDIT_FIELD|")
        if marker < 0:
            continue
        raw_line = raw_line[marker:]
        _, projection, type_text = raw_line.split("|", 2)
        if projection in found:
            raise ValueError(f"duplicate projection in dump: {projection}")
        found[projection] = normalized(type_text)
    return found


def produce_dump(root: Path, output: Path) -> None:
    result = subprocess.run(
        ["lake", "env", "lean", "AuditType.lean"], cwd=root,
        capture_output=True, text=True, check=False,
    )
    output.write_text(
        result.stdout + result.stderr,
        encoding="utf-8",
        newline="\n",
    )
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare a Lean Meta theorem-type dump to its frozen manifest.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dump", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        declarations = manifest["declarations"]
        expected = {entry["declaration"]: normalized(entry["normalized_type"]) for entry in declarations}
        dump = args.dump
        if dump is None:
            dump = args.root / ".lake" / "build" / "audit" / "lean_type_dump.current.txt"
            dump.parent.mkdir(parents=True, exist_ok=True)
            produce_dump(args.root, dump)
        expected_dump_sha = manifest.get("lean_dump_sha256")
        if expected_dump_sha:
            actual_dump_sha = hashlib.sha256(dump.read_bytes()).hexdigest().upper()
            if actual_dump_sha != expected_dump_sha.upper():
                raise ValueError(
                    f"dump SHA-256 mismatch; expected={expected_dump_sha.upper()}; "
                    f"actual={actual_dump_sha}"
                )
        actual = parse_dump(dump)
        if actual != expected:
            missing = sorted(set(expected) - set(actual))
            extra = sorted(set(actual) - set(expected))
            changed = sorted(name for name in set(actual) & set(expected) if actual[name] != expected[name])
            raise ValueError(f"type mismatch; missing={missing}; extra={extra}; changed={changed}")
        expected_bodies = {
            entry["declaration"]: normalized(entry["normalized_body"])
            for entry in declarations if "normalized_body" in entry
        }
        signature_bodies = {
            declaration: normalized(body)
            for declaration, body in manifest.get("signature_bodies", {}).items()
        }
        # `signature_bodies` is the separately reviewed, human-readable scope
        # summary.  `normalized_body` is the exact Lean Meta output.  Their
        # keys must agree, but the summary must not masquerade as byte-exact
        # elaborator output.
        if signature_bodies and set(signature_bodies) != set(expected_bodies):
            raise ValueError("signature_bodies keys do not match declaration bodies")
        if expected_bodies:
            actual_bodies = parse_bodies(dump)
            if actual_bodies != expected_bodies:
                raise ValueError("expanded definition body mismatch")
        interfaces = manifest.get("interfaces", {})
        expected_fields = {
            f"Smooth4PC.{interface_name}.{entry['name']}": normalized(entry["normalized_type"])
            for interface_name, entries in interfaces.items()
            for entry in entries
        }
        if expected_fields:
            actual_fields = parse_fields(dump)
            if actual_fields != expected_fields:
                missing = sorted(set(expected_fields) - set(actual_fields))
                extra = sorted(set(actual_fields) - set(expected_fields))
                changed = sorted(
                    name for name in set(actual_fields) & set(expected_fields)
                    if actual_fields[name] != expected_fields[name]
                )
                raise ValueError(
                    f"interface projection mismatch; missing={missing}; extra={extra}; changed={changed}"
                )
    except (OSError, ValueError, KeyError, json.JSONDecodeError, RuntimeError) as error:
        print("theorem-type gate: FAIL", file=sys.stderr)
        print(error, file=sys.stderr)
        return 1
    print("theorem-type gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
