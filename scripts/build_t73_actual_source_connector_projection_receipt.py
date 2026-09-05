#!/usr/bin/env python3
"""Stream the large source-connector projection into a compact Git receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import ijson

ROOT = Path(__file__).resolve().parents[1]
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
PROVENANCE = ROOT / "geometry/t73_reduced_source_connector_provenance.json"
FULL_BUILDER = ROOT / "scripts/build_t73_actual_source_connector_projection.py"
OUTPUT = ROOT / "audit/t73_actual_source_connector_projection_receipt.json"
DEFAULT_FULL = Path.home() / ".cache/t73_actual_source_connector_projection.full.json"


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_sha(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def root_scalars(path):
    with path.open("rb") as source:
        head = source.read(16384).decode("utf-8")
        source.seek(max(0, path.stat().st_size - 16384))
        tail = source.read().decode("utf-8")
    scalar_text = head + tail
    values = {}
    for key in (
        "broad_phase_candidates",
        "crossing_count",
        "segment_count",
    ):
        match = re.search(rf'"{key}":\s*(\d+)', scalar_text)
        if not match:
            raise AssertionError(f"full projection header lacks {key}")
        values[key] = int(match.group(1))
    status = re.search(r'"completion_status":\s*"([^"]+)"', scalar_text)
    if not status:
        raise AssertionError("full projection header lacks completion_status")
    values["completion_status"] = status.group(1)
    return values


def crossing_summary(path):
    digest = hashlib.sha256()
    digest.update(b"[")
    count = 0
    pair_counts = Counter()
    pair_signed_sums = Counter()
    first_crossing = None
    last_crossing = None
    with path.open("rb") as source:
        for crossing in ijson.items(source, "crossings.item"):
            if count:
                digest.update(b",")
            digest.update(
                json.dumps(
                    crossing, sort_keys=True, separators=(",", ":")
                ).encode()
            )
            pair = "/".join(
                sorted((crossing["over_owner"], crossing["under_owner"]))
            )
            pair_counts[pair] += 1
            pair_signed_sums[pair] += crossing["sign"]
            if first_crossing is None:
                first_crossing = crossing
            last_crossing = crossing
            count += 1
    digest.update(b"]")
    return {
        "crossing_count": count,
        "crossings_canonical_sha256": digest.hexdigest().upper(),
        "owner_pair_crossing_counts": dict(sorted(pair_counts.items())),
        "owner_pair_signed_sums": dict(sorted(pair_signed_sums.items())),
        "first_crossing": first_crossing,
        "last_crossing": last_crossing,
    }


def build(full_path):
    if not full_path.is_file():
        raise FileNotFoundError(full_path)
    scalars = root_scalars(full_path)
    summary = crossing_summary(full_path)
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    if scalars.get("completion_status") != "ACTUAL_SOURCE_CONNECTOR_PROJECTION_CONSTRUCTED":
        raise AssertionError("full source connector projection is not complete")
    if scalars.get("crossing_count") != summary["crossing_count"]:
        raise AssertionError("streamed crossing count differs from the full root field")
    if summary["crossing_count"] != 1758060 or scalars.get("segment_count") != 7116:
        raise AssertionError("source connector projection fixed counts changed")
    result = {
        "schema": "t73_actual_source_connector_projection_receipt/v1",
        "full_cache_path": str(full_path),
        "full_file_size": full_path.stat().st_size,
        "full_file_sha256": file_sha(full_path),
        "full_builder_path": "scripts/build_t73_actual_source_connector_projection.py",
        "full_builder_sha256": file_sha(FULL_BUILDER),
        "johnson_spine_embedding_sha256": spine["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "reduced_source_connector_provenance_sha256": provenance["sha256"],
        "segment_count": scalars["segment_count"],
        "broad_phase_candidates": scalars["broad_phase_candidates"],
        "projection_basis": scalars["projection_basis"]
        if "projection_basis" in scalars
        else [["1", "0", "1/1000003"], ["0", "1", "1/1000006000009"]],
        "near_xy_projection_denominator": 1000003,
        **summary,
        "verdict": "PASS_ACTUAL_SOURCE_CONNECTOR_PROJECTION_FULL_CACHE",
    }
    result["sha256"] = canonical_sha(result)
    return result


def check_receipt(check_full=False):
    receipt = json.loads(OUTPUT.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    checks = {
        "builder": receipt["full_builder_sha256"] == file_sha(FULL_BUILDER),
        "spine": receipt["johnson_spine_embedding_sha256"] == spine["sha256"],
        "ar_link": receipt["actual_ar_link_sha256"] == ar_link["sha256"],
        "provenance": receipt["reduced_source_connector_provenance_sha256"]
        == provenance["sha256"],
        "counts": receipt["segment_count"] == 7116
        and receipt["crossing_count"] == 1758060,
        "verdict": receipt["verdict"]
        == "PASS_ACTUAL_SOURCE_CONNECTOR_PROJECTION_FULL_CACHE",
    }
    if check_full:
        full_path = Path(receipt["full_cache_path"])
        checks["full_file"] = full_path.is_file() and receipt[
            "full_file_sha256"
        ] == file_sha(full_path)
    if not all(checks.values()):
        raise AssertionError(f"source connector projection receipt failed: {checks}")
    return {
        "verdict": "PASS_SOURCE_CONNECTOR_PROJECTION_RECEIPT",
        "checks": checks,
        "full_crossings": receipt["crossing_count"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", type=Path, default=DEFAULT_FULL)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--check-full", action="store_true")
    args = parser.parse_args()
    if args.write:
        OUTPUT.write_text(
            json.dumps(build(args.full), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.check or args.check_full:
        print(json.dumps(check_receipt(args.check_full), sort_keys=True))


if __name__ == "__main__":
    main()
