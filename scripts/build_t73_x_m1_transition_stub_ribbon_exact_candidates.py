#!/usr/bin/env python3
"""Deduplicate transition/stub triangle candidates to rectangle pairs."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "audit/t73_x_m1_transition_ribbon_stub_candidates.json"
STUBS = ROOT / "audit/t73_x_m1_stub_r3_push_paths_receipt.json"
OUTPUT = ROOT / "audit/t73_x_m1_transition_stub_ribbon_exact_candidates.json"
DEFAULT_CACHE = Path.home() / ".cache/t73_x_m1_transition_stub_rectangle_candidates.csv.gz"


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def stub_rectangle_metadata(receipt):
    answer = []
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            for name, stub in record["stubs"].items():
                for segment in range(stub["segment_count"]):
                    answer.append((record["band_index"], name, segment, stub["segment_count"]))
    return answer


def permitted(transition_rectangle, stub_info):
    transition_record, segment = divmod(transition_rectangle, 6)
    band, side = divmod(transition_record, 2)
    stub_band, name, stub_segment, stub_count = stub_info
    if band != stub_band:
        return False
    if side == 0:
        return segment == 0 and name == "target_complement_first" and stub_segment == stub_count - 1
    return segment == 5 and name == "target_complement_last" and stub_segment == 0


def build(cache_path=DEFAULT_CACHE):
    source_audit = json.loads(SOURCE.read_text())
    stubs = json.loads(STUBS.read_text())
    metadata = stub_rectangle_metadata(stubs)
    source_path = resolve(source_audit["candidate_path"])
    if file_sha(source_path) != source_audit["candidate_sha256"]:
        raise AssertionError("transition/stub triangle candidate stream changed")
    pairs = set()
    triangle_pairs = permitted_triangle_pairs = 0
    with gzip.open(source_path, "rt", encoding="utf-8") as source:
        header = json.loads(source.readline())
        if header != {"comparison": "stub", "record": "header"}:
            raise AssertionError("transition/stub candidate schema changed")
        for line in source:
            transition_triangle, stub_triangle = (int(value) for value in line.split(","))
            triangle_pairs += 1
            transition_rectangle, stub_rectangle = transition_triangle // 2, stub_triangle // 2
            if permitted(transition_rectangle, metadata[stub_rectangle]):
                permitted_triangle_pairs += 1
                continue
            pairs.add((transition_rectangle << 32) | stub_rectangle)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", compresslevel=6, mtime=0) as output:
            output.write(b"transition_stub_rectangle_pairs/v1\n")
            for packed in sorted(pairs):
                output.write(f"{packed >> 32},{packed & 0xFFFFFFFF}\n".encode())
    result = {
        "schema": "t73_x_m1_transition_stub_ribbon_exact_candidates/v1",
        "source_candidate_stream_sha256": source_audit["candidate_sha256"],
        "source_triangle_pair_count": triangle_pairs,
        "permitted_port_triangle_pair_count": permitted_triangle_pairs,
        "stub_rectangle_count": len(metadata),
        "exact_rectangle_pair_count": len(pairs),
        "candidate_path": str(cache_path),
        "candidate_size": cache_path.stat().st_size,
        "candidate_sha256": file_sha(cache_path),
        "status": "CANDIDATES_ONLY_NO_CLEARANCE_CLAIM",
    }
    result["sha256"] = canonical_sha(result)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    result = build()
    print(json.dumps({"rectangles": result["exact_rectangle_pair_count"], "permitted": result["permitted_port_triangle_pair_count"], "status": result["status"]}, sort_keys=True))
