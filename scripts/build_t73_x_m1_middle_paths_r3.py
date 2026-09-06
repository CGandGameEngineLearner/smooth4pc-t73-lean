#!/usr/bin/env python3
"""Map every ejected m1-parallel middle path into the canonical R3 chart."""

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
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
CHART = ROOT / "geometry/t73_x_m1_canonical_r3_annulus_chart.json"
MIDDLE_RECEIPT = ROOT / "audit/t73_x_m1_ejected_middle_complements_receipt.json"
COMPLETE_RECEIPT = ROOT / "audit/t73_x_m1_complete_explicit_replacement_images_receipt.json"
COMPLETE_VERIFICATION = ROOT / "audit/t73_x_m1_complete_explicit_replacement_images_verification.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_middle_paths_r3_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_m1_middle_paths_r3.jsonl.gz"
ANGLE_COUNT = 34


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest().upper()


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


def encode(values):
    return [str(value) for value in values]


def quotient_normalize(value):
    return tuple(
        value[axis] - 4 * (value[axis] // 4) for axis in range(3)
    ) + (value[3],)


def add_scaled(base, normal, level):
    return tuple(base[axis] + level * normal[axis] for axis in range(4))


def index_table(base, normals, level):
    table = {}
    for source_index, (vertex, normal) in enumerate(zip(base, normals)):
        key = quotient_normalize(add_scaled(vertex, normal, level))
        table.setdefault(key, set()).add(source_index % ANGLE_COUNT)
    if any(len(indices) != 1 for indices in table.values()):
        raise AssertionError("foliation quotient has an ambiguous angular index")
    return {key: next(iter(indices)) for key, indices in table.items()}


def match_indices(values, table):
    indices = []
    deck_shifts = []
    for raw in values:
        value = point(raw)
        key = quotient_normalize(value)
        if key not in table:
            raise AssertionError("middle vertex is not on its declared foliation level")
        index = table[key]
        indices.append(index)
        deck_shifts.append([
            int((value[axis] - key[axis]) / 4) for axis in range(3)
        ])
    return indices, deck_shifts


def canonical_r3_vertex(index, level, maximum_level):
    outer = (Fraction(index), Fraction(index * index))
    center = (Fraction(33, 2), Fraction(737, 2))
    alpha = Fraction(level, 2 * (maximum_level + 1))
    return (
        (1 - alpha) * outer[0] + alpha * center[0],
        (1 - alpha) * outer[1] + alpha * center[1],
        Fraction(0),
    )


def build(output_path: Path) -> dict:
    foliation = json.loads(FOLIATION.read_text())
    chart = json.loads(CHART.read_text())
    middle_receipt = json.loads(MIDDLE_RECEIPT.read_text())
    complete_receipt = json.loads(COMPLETE_RECEIPT.read_text())
    complete_verification = json.loads(COMPLETE_VERIFICATION.read_text())
    source_path = resolve_cache_path(middle_receipt["cache_path"])
    base = [point(value) for value in foliation["base_vertices"]]
    normals = [point(value) for value in foliation["unit_normal_field"]]
    maximum_level = max(foliation["parallel_levels"])

    counts = Counter()
    orientation_counts = Counter()
    records = core_segments = push_segments = ribbon_triangles = 0
    source_point_matches = deck_shifted_points = radial_clearance_checks = 0
    previous_push_level = None
    stream_digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_middle_paths_r3/v1",
        "canonical_r3_annulus_chart_sha256": chart["sha256"],
        "middle_complements_receipt_sha256": middle_receipt["sha256"],
        "complete_explicit_replacement_receipt_sha256": complete_receipt["sha256"],
        "complete_explicit_replacement_verification_sha256": complete_verification["sha256"],
        "maximum_parallel_level": maximum_level,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(source_path, "rt", encoding="utf-8") as source, output_path.open("wb") as raw_output:
        source_header = json.loads(source.readline())
        if source_header.get("schema") != "t73_x_m1_ejected_middle_complements/v1":
            raise AssertionError("unexpected middle-complement source stream")
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            encoded = (canonical(header) + "\n").encode()
            output.write(encoded)
            stream_digest.update(encoded)
            for line in source:
                middle = json.loads(line)
                core_level = middle["parallel_level"]
                push_level = core_level + 1
                core_table = index_table(base, normals, core_level)
                push_table = index_table(base, normals, push_level)
                core_indices, core_decks = match_indices(
                    middle["source_core_vertices"], core_table
                )
                push_indices, push_decks = match_indices(
                    middle["source_push_vertices"], push_table
                )
                if core_indices != push_indices:
                    raise AssertionError("core and push angular indices differ")
                steps = {(right - left) % ANGLE_COUNT for left, right in zip(core_indices, core_indices[1:])}
                if steps not in ({1}, {ANGLE_COUNT - 1}):
                    raise AssertionError("middle path is not monotone in the quotient angle")
                orientation_step = next(iter(steps))
                if previous_push_level is not None:
                    if core_level <= previous_push_level:
                        raise AssertionError("successive framing strips overlap radially")
                    radial_clearance_checks += 1
                previous_push_level = push_level

                core_r3 = [
                    encode(canonical_r3_vertex(index, core_level, maximum_level))
                    for index in core_indices
                ]
                push_r3 = [
                    encode(canonical_r3_vertex(index, push_level, maximum_level))
                    for index in push_indices
                ]
                segment_count = len(core_indices) - 1
                record = {
                    "record": "middle_path_r3",
                    "band_index": middle["band_index"],
                    "component": middle["component"],
                    "core_level": core_level,
                    "push_level": push_level,
                    "angular_indices": core_indices,
                    "orientation_step_mod_34": orientation_step,
                    "source_core_deck_shifts": core_decks,
                    "source_push_deck_shifts": push_decks,
                    "core_vertices_r3": core_r3,
                    "push_vertices_r3": push_r3,
                    "segment_count_each": segment_count,
                    "ribbon_triangle_count": 2 * segment_count,
                    "ribbon_triangle_rule": (
                        "for segment i: (core_i,core_i+1,push_i+1) and "
                        "(core_i,push_i+1,push_i)"
                    ),
                    "relative_map_status": "EXACT_FOLIATION_QUOTIENT_COORDINATES",
                }
                encoded = (canonical(record) + "\n").encode()
                output.write(encoded)
                stream_digest.update(encoded)
                records += 1
                counts[middle["component"]] += 1
                orientation_counts[str(orientation_step)] += 1
                core_segments += segment_count
                push_segments += segment_count
                ribbon_triangles += 2 * segment_count
                source_point_matches += 2 * len(core_indices)
                deck_shifted_points += sum(any(shift) for shift in core_decks + push_decks)

    receipt = {
        "schema": "t73_x_m1_middle_paths_r3_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha256(output_path),
        "record_stream_sha256": stream_digest.hexdigest().upper(),
        "builder_sha256": file_sha256(Path(__file__)),
        "canonical_r3_annulus_chart_sha256": chart["sha256"],
        "middle_complements_receipt_sha256": middle_receipt["sha256"],
        "complete_explicit_replacement_receipt_sha256": complete_receipt["sha256"],
        "complete_explicit_replacement_verification_sha256": complete_verification["sha256"],
        "record_count": records,
        "component_counts": dict(sorted(counts.items())),
        "orientation_step_counts": dict(sorted(orientation_counts.items())),
        "core_segment_count": core_segments,
        "push_segment_count": push_segments,
        "ribbon_triangle_count": ribbon_triangles,
        "source_q4_point_matches": source_point_matches,
        "deck_shifted_point_count": deck_shifted_points,
        "radial_strip_clearance_checks": radial_clearance_checks,
        "pairwise_disjoint_middle_ribbons": True,
        "remaining_piece_types": [
            "source/target splice stubs",
            "positive/negative band lanes",
            "overlap transition tracks",
        ],
        "completion_status": "ALL_POST_X_MIDDLE_PATHS_MAPPED_TO_CANONICAL_R3",
        "verdict": "PASS_X_M1_ALL_MIDDLE_PATHS_CANONICAL_R3",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(os.environ.get("T73_X_M1_MIDDLE_R3_CACHE", DEFAULT_OUTPUT))
    receipt = build(output)
    print(json.dumps({
        "verdict": receipt["verdict"],
        "records": receipt["record_count"],
        "core_segments": receipt["core_segment_count"],
        "ribbon_triangles": receipt["ribbon_triangle_count"],
        "bytes": receipt["cache_size"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
