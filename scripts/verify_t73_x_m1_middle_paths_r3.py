#!/usr/bin/env python3
"""Independently replay all intrinsic-Q4 to canonical-R3 middle-path maps."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
CHART = ROOT / "geometry/t73_x_m1_canonical_r3_annulus_chart.json"
MIDDLE = ROOT / "audit/t73_x_m1_ejected_middle_complements_receipt.json"
ANGLE_COUNT = 34


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: dict) -> str:
    unsigned = {key: item for key, item in value.items() if key != "sha256"}
    return hashlib.sha256(canonical(unsigned).encode()).hexdigest().upper()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def resolve_cache_path(value: str) -> Path:
    path = Path(value)
    if path.exists():
        return path
    if len(value) >= 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    return path


def point(values):
    return tuple(Fraction(value) for value in values)


def quotient_key(value):
    return tuple(value[axis] - 4 * (value[axis] // 4) for axis in range(3)) + (value[3],)


def level_point(base, normal, level):
    return tuple(base[axis] + level * normal[axis] for axis in range(4))


def make_lookup(base, normals, level):
    lookup = {}
    for source_index, (vertex, normal) in enumerate(zip(base, normals)):
        key = quotient_key(level_point(vertex, normal, level))
        lookup.setdefault(key, set()).add(source_index % ANGLE_COUNT)
    if any(len(values) != 1 for values in lookup.values()):
        raise AssertionError("independent quotient lookup is ambiguous")
    return {key: next(iter(values)) for key, values in lookup.items()}


def recover(values, lookup):
    indices = []
    shifts = []
    for raw in values:
        value = point(raw)
        key = quotient_key(value)
        if key not in lookup:
            raise AssertionError("source Q4 point misses its foliation level")
        indices.append(lookup[key])
        shifts.append([int((value[axis] - key[axis]) / 4) for axis in range(3)])
    return indices, shifts


def r3(index, level, maximum):
    outer = (Fraction(index), Fraction(index * index))
    center = (Fraction(33, 2), Fraction(737, 2))
    alpha = Fraction(level, 2 * (maximum + 1))
    return [
        str((1 - alpha) * outer[0] + alpha * center[0]),
        str((1 - alpha) * outer[1] + alpha * center[1]),
        "0",
    ]


def check_receipt():
    data = json.loads(DATA.read_text())
    foliation = json.loads(FOLIATION.read_text())
    chart = json.loads(CHART.read_text())
    middle = json.loads(MIDDLE.read_text())
    checks = {
        "payload_sha": data["sha256"] == canonical_sha256(data),
        "foliation": max(foliation["parallel_levels"]) == 30260,
        "chart": data["canonical_r3_annulus_chart_sha256"] == chart["sha256"],
        "middle": data["middle_complements_receipt_sha256"] == middle["sha256"],
        "counts": (
            data["record_count"] == 1513
            and data["core_segment_count"] == 48416
            and data["push_segment_count"] == 48416
            and data["ribbon_triangle_count"] == 96832
            and data["source_q4_point_matches"] == 99858
        ),
        "scope": len(data["remaining_piece_types"]) == 3,
        "verdict": data["verdict"] == "PASS_X_M1_ALL_MIDDLE_PATHS_CANONICAL_R3",
    }
    if not all(checks.values()):
        raise AssertionError(f"middle R3 receipt failed: {checks}")
    return data, foliation, middle, checks


def verify_full(check_cache_sha=False):
    data, foliation, middle, _ = check_receipt()
    output_path = resolve_cache_path(data["cache_path"])
    source_path = resolve_cache_path(middle["cache_path"])
    if not output_path.is_file() or output_path.stat().st_size != data["cache_size"]:
        raise AssertionError("middle R3 cache missing or resized")
    if check_cache_sha and file_sha256(output_path) != data["cache_sha256"]:
        raise AssertionError("middle R3 cache SHA mismatch")
    base = [point(value) for value in foliation["base_vertices"]]
    normals = [point(value) for value in foliation["unit_normal_field"]]
    maximum = max(foliation["parallel_levels"])
    digest = hashlib.sha256()
    counts = Counter()
    orientations = Counter()
    records = segments = points = deck_shifted = radial_checks = 0
    previous_push = None
    with gzip.open(output_path, "rt", encoding="utf-8") as output, gzip.open(source_path, "rt", encoding="utf-8") as source:
        header_line = output.readline()
        header = json.loads(header_line)
        digest.update(header_line.encode())
        if json.loads(source.readline()).get("record") != "header":
            raise AssertionError("middle source header missing")
        if header["schema"] != "t73_x_m1_middle_paths_r3/v1":
            raise AssertionError("middle R3 output header changed")
        for source_line in source:
            output_line = output.readline()
            if not output_line:
                raise AssertionError("middle R3 output ended early")
            source_record = json.loads(source_line)
            record = json.loads(output_line)
            digest.update(output_line.encode())
            core_level = source_record["parallel_level"]
            push_level = core_level + 1
            core_indices, core_shifts = recover(
                source_record["source_core_vertices"],
                make_lookup(base, normals, core_level),
            )
            push_indices, push_shifts = recover(
                source_record["source_push_vertices"],
                make_lookup(base, normals, push_level),
            )
            if core_indices != push_indices:
                raise AssertionError("independent core/push quotient indices differ")
            steps = {(right - left) % ANGLE_COUNT for left, right in zip(core_indices, core_indices[1:])}
            if steps not in ({1}, {33}):
                raise AssertionError("independent angular path is not monotone")
            step = next(iter(steps))
            if previous_push is not None:
                if core_level <= previous_push:
                    raise AssertionError("independent radial ribbon intervals overlap")
                radial_checks += 1
            previous_push = push_level
            expected = {
                "record": "middle_path_r3",
                "band_index": source_record["band_index"],
                "component": source_record["component"],
                "core_level": core_level,
                "push_level": push_level,
                "angular_indices": core_indices,
                "orientation_step_mod_34": step,
                "source_core_deck_shifts": core_shifts,
                "source_push_deck_shifts": push_shifts,
                "core_vertices_r3": [r3(index, core_level, maximum) for index in core_indices],
                "push_vertices_r3": [r3(index, push_level, maximum) for index in push_indices],
                "segment_count_each": len(core_indices) - 1,
                "ribbon_triangle_count": 2 * (len(core_indices) - 1),
                "ribbon_triangle_rule": (
                    "for segment i: (core_i,core_i+1,push_i+1) and "
                    "(core_i,push_i+1,push_i)"
                ),
                "relative_map_status": "EXACT_FOLIATION_QUOTIENT_COORDINATES",
            }
            if record != expected:
                raise AssertionError(f"middle R3 record {source_record['band_index']} changed")
            records += 1
            segments += len(core_indices) - 1
            points += 2 * len(core_indices)
            deck_shifted += sum(any(shift) for shift in core_shifts + push_shifts)
            counts[source_record["component"]] += 1
            orientations[str(step)] += 1
        if output.readline():
            raise AssertionError("unused middle R3 output records remain")
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("middle R3 decompressed stream SHA mismatch")
    if (records, segments, points, radial_checks) != (1513, 48416, 99858, 1512):
        raise AssertionError("middle R3 independent totals changed")
    if dict(sorted(orientations.items())) != {"1": 1511, "33": 2}:
        raise AssertionError("middle R3 orientation inventory changed")
    if deck_shifted != data["deck_shifted_point_count"]:
        raise AssertionError("middle R3 deck-shift inventory changed")
    return {
        "verdict": "PASS_X_M1_ALL_MIDDLE_PATHS_CANONICAL_R3_FULL",
        "records_reconstructed": records,
        "core_segments_reconstructed": segments,
        "push_segments_reconstructed": segments,
        "source_q4_points_reconstructed": points,
        "radial_strip_clearance_checks": radial_checks,
        "orientation_step_counts": dict(sorted(orientations.items())),
        "pairwise_disjoint_middle_ribbons": True,
        "cache_sha_checked": check_cache_sha,
        "remaining_piece_types": data["remaining_piece_types"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--check-cache-sha", action="store_true")
    args = parser.parse_args()
    if args.full:
        result = verify_full(args.check_cache_sha)
    else:
        _, _, _, checks = check_receipt()
        result = {"verdict": "PASS_X_M1_MIDDLE_PATHS_R3_RECEIPT", "checks": checks}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
