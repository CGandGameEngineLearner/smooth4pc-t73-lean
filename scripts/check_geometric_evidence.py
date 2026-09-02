from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPOSITORY / "audit" / "geometric_evidence_manifest.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest().upper()


def resolve(candidate: str) -> Path:
    path = Path(candidate)
    return path if path.is_absolute() else REPOSITORY / path


def audit(manifest_path: Path) -> list[dict[str, object]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    for item in manifest["items"]:
        expected = item["sha256"].upper()
        existing = [resolve(value) for value in item["paths"] if resolve(value).is_file()]
        if not existing:
            rows.append({**item, "status": "MISSING", "found": None})
            continue
        matches = []
        mismatches = []
        for path in existing:
            actual = digest(path)
            record = {"path": str(path), "sha256": actual, "bytes": path.stat().st_size}
            (matches if actual == expected else mismatches).append(record)
        status = "PASS" if matches else "HASH_MISMATCH"
        rows.append(
            {
                **item,
                "status": status,
                "found": matches[0] if matches else mismatches[0],
                "other_candidates": matches[1:] + mismatches[1:],
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check availability and hashes of candidate-specific geometric witnesses."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="report missing evidence without returning a failing exit status",
    )
    args = parser.parse_args()

    rows = audit(args.manifest.resolve())
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for row in rows:
            found = row["found"]
            location = found["path"] if isinstance(found, dict) else "-"
            print(f'{row["priority"]:>2}  {row["status"]:<13}  {row["id"]:<24}  {location}')
        passed = sum(row["status"] == "PASS" for row in rows)
        print(f"SUMMARY={passed}/{len(rows)} geometric witness artifacts available and hash-matched")

    failed = any(row["status"] != "PASS" for row in rows)
    if failed and not args.allow_missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
