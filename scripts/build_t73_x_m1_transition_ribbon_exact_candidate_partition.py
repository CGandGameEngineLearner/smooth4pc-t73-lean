#!/usr/bin/env python3
"""Partition/deduplicate transition-ribbon candidates by normal type."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_AUDIT = ROOT / "audit/t73_x_m1_transition_ribbon_transition_candidates.json"
OUTPUT_AUDIT = ROOT / "audit/t73_x_m1_transition_ribbon_exact_candidate_partition.json"
DEFAULT_CONSTANT = Path.home() / ".cache/t73_x_m1_transition_constant_rectangle_candidates.csv.gz"
DEFAULT_VARIABLE = Path.home() / ".cache/t73_x_m1_transition_variable_triangle_candidates.csv.gz"


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


def variable_triangle(index):
    record, local = divmod(index, 12)
    return local >= 10 if record % 2 == 0 else local < 2


def build(constant_path, variable_path):
    source_audit = json.loads(SOURCE_AUDIT.read_text())
    source_path = resolve(source_audit["candidate_path"])
    if file_sha(source_path) != source_audit["candidate_sha256"]:
        raise AssertionError("transition triangle candidate stream changed")
    constant_pairs = set()
    variable_pairs = []
    triangle_pairs = adjacent_rectangle_incidences = 0
    with gzip.open(source_path, "rt", encoding="utf-8") as source:
        header = json.loads(source.readline())
        if header != {"comparison": "transition", "record": "header"}:
            raise AssertionError("transition candidate header changed")
        for line in source:
            first, second = (int(value) for value in line.split(","))
            triangle_pairs += 1
            first_variable = variable_triangle(first)
            second_variable = variable_triangle(second)
            first_rectangle, second_rectangle = first // 2, second // 2
            if first_rectangle // 6 == second_rectangle // 6 and abs(first_rectangle - second_rectangle) == 1:
                adjacent_rectangle_incidences += 1
                continue
            if first_variable or second_variable:
                variable_pairs.append((first, second))
            else:
                low, high = sorted((first_rectangle, second_rectangle))
                constant_pairs.add((low << 32) | high)
    if triangle_pairs != source_audit["exact_triangle_checks"]:
        raise AssertionError("transition candidate pair count changed")
    constant_path.parent.mkdir(parents=True, exist_ok=True)
    with constant_path.open("wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", compresslevel=6, mtime=0) as output:
            output.write(b"constant_rectangle_pairs/v1\n")
            for packed in sorted(constant_pairs):
                output.write(f"{packed >> 32},{packed & 0xFFFFFFFF}\n".encode())
    with variable_path.open("wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", compresslevel=6, mtime=0) as output:
            output.write(b"variable_triangle_pairs/v1\n")
            for first, second in variable_pairs:
                output.write(f"{first},{second}\n".encode())
    result = {
        "schema": "t73_x_m1_transition_ribbon_exact_candidate_partition/v1",
        "source_candidate_audit_sha256": source_audit["candidate_sha256"],
        "source_triangle_pair_count": triangle_pairs,
        "constant_constant_triangle_pair_count": triangle_pairs - len(variable_pairs) - adjacent_rectangle_incidences,
        "adjacent_rectangle_triangle_incidences_removed": adjacent_rectangle_incidences,
        "constant_rectangle_pair_count": len(constant_pairs),
        "variable_triangle_pair_count": len(variable_pairs),
        "variable_variable_triangle_pair_count": sum(variable_triangle(a) and variable_triangle(b) for a, b in variable_pairs),
        "constant_candidate_path": str(constant_path),
        "constant_candidate_size": constant_path.stat().st_size,
        "constant_candidate_sha256": file_sha(constant_path),
        "variable_candidate_path": str(variable_path),
        "variable_candidate_size": variable_path.stat().st_size,
        "variable_candidate_sha256": file_sha(variable_path),
        "status": "CANDIDATES_ONLY_NO_CLEARANCE_CLAIM",
    }
    result["sha256"] = canonical_sha(result)
    OUTPUT_AUDIT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--constant-output", type=Path, default=DEFAULT_CONSTANT)
    parser.add_argument("--variable-output", type=Path, default=DEFAULT_VARIABLE)
    args = parser.parse_args()
    result = build(args.constant_output, args.variable_output)
    print(json.dumps({
        "constant_rectangles": result["constant_rectangle_pair_count"],
        "variable_triangles": result["variable_triangle_pair_count"],
        "variable_variable": result["variable_variable_triangle_pair_count"],
        "status": result["status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
