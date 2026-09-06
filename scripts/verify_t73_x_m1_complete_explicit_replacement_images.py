#!/usr/bin/env python3
"""Independently replay the complete explicit post-x replacement stream."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_complete_explicit_replacement_images_receipt.json"
LANES = ROOT / "audit/t73_x_m1_ejected_band_lanes_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_ejected_splice_stubs_receipt.json"
MIDDLES = ROOT / "audit/t73_x_m1_ejected_middle_complements_receipt.json"
TRANSITIONS = ROOT / "audit/t73_x_m1_ejection_overlap_transitions_receipt.json"
TRANSITIONS_VERIFICATION = ROOT / "audit/t73_x_m1_ejection_overlap_transitions_verification.json"


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


def leaf_pieces(value):
    if isinstance(value, dict):
        yield value
    else:
        for item in value:
            yield from leaf_pieces(item)


def target_vertices(images):
    result = []
    for piece in leaf_pieces(images):
        start, end = piece["target_vertices"]
        if result and result[-1] != start:
            raise AssertionError("source piece images are discontinuous")
        if not result:
            result.append(start)
        result.append(end)
    return result


def append_checked(result, values, label, ranges):
    if result and result[-1] != values[0]:
        raise AssertionError(f"independent reconstruction breaks before {label}")
    start = len(result) - 1 if result else 0
    result.extend(values if not result else values[1:])
    ranges.append({
        "piece": label,
        "segment_range": [start, len(result) - 1],
        "segment_count": len(values) - 1,
    })


def reconstruct(lane, stub, middle, first, last, kind):
    core = kind == "core"
    lane_key = "core_segment_images" if core else "outward_push_segment_images"
    stub_key = "core_segment_image" if core else "outward_push_segment_image"
    middle_key = "target_core_vertices" if core else "target_push_vertices"
    center_key = "center_core" if core else "center_push"
    pieces = (
        ("source_stub_before", target_vertices(stub["stubs"]["source_stub_before"][stub_key])),
        ("negative_band_lane", target_vertices(lane["lanes"]["negative_band_lane"][lane_key])),
        ("target_complement_first", target_vertices(stub["stubs"]["target_complement_first"][stub_key])),
        ("transition_first", [first["local_cubical_boundary"][center_key], first["global_annulus_boundary"][center_key]]),
        ("oriented_m1_parallel_middle", middle[middle_key]),
        ("transition_last", [last["global_annulus_boundary"][center_key], last["local_cubical_boundary"][center_key]]),
        ("target_complement_last", target_vertices(stub["stubs"]["target_complement_last"][stub_key])),
        ("positive_band_lane", target_vertices(lane["lanes"]["positive_band_lane"][lane_key])),
        ("source_stub_after", target_vertices(stub["stubs"]["source_stub_after"][stub_key])),
    )
    result = []
    ranges = []
    for label, values in pieces:
        append_checked(result, values, label, ranges)
    return result, ranges


def check_receipt() -> tuple[dict, dict, dict]:
    data = json.loads(DATA.read_text())
    sources = {
        "lanes": json.loads(LANES.read_text()),
        "stubs": json.loads(STUBS.read_text()),
        "middles": json.loads(MIDDLES.read_text()),
        "transitions": json.loads(TRANSITIONS.read_text()),
    }
    transition_verification = json.loads(TRANSITIONS_VERIFICATION.read_text())
    checks = {
        "payload_sha": data["sha256"] == canonical_sha256(data),
        "source_receipts": data["source_receipt_sha256s"] == {
            name: source["sha256"] for name, source in sources.items()
        },
        "transition_verification": (
            data["transition_verification_sha256"] == transition_verification["sha256"]
        ),
        "counts": (
            data["replacement_block_count"] == 1513
            and data["transition_center_track_count"] == 6052
            and data["exact_piece_boundary_matches"] == 24208
        ),
        "scope": (
            data["ambient_coordinate_dimension"] == 4
            and data["common_three_manifold_chart_status"] == "OPEN"
        ),
        "verdict": (
            data["verdict"]
            == "PASS_COMPLETE_EXPLICIT_POST_X_REPLACEMENT_IMAGE_STREAM_4D_ATLAS"
        ),
    }
    if not all(checks.values()):
        raise AssertionError(f"explicit replacement receipt failed: {checks}")
    return data, sources, checks


def verify_full(check_cache_sha: bool = False) -> dict:
    data, sources, _ = check_receipt()
    cache = resolve_cache_path(data["cache_path"])
    if not cache.is_file() or cache.stat().st_size != data["cache_size"]:
        raise AssertionError("complete explicit replacement cache missing or resized")
    if check_cache_sha and file_sha256(cache) != data["cache_sha256"]:
        raise AssertionError("complete explicit replacement cache SHA mismatch")

    paths = {
        name: resolve_cache_path(source["cache_path"])
        for name, source in sources.items()
    }
    counts = Counter()
    core_segments = push_segments = records = boundary_checks = 0
    digest = hashlib.sha256()
    with (
        gzip.open(cache, "rt", encoding="utf-8") as output,
        gzip.open(paths["lanes"], "rt", encoding="utf-8") as lane_source,
        gzip.open(paths["stubs"], "rt", encoding="utf-8") as stub_source,
        gzip.open(paths["middles"], "rt", encoding="utf-8") as middle_source,
        gzip.open(paths["transitions"], "rt", encoding="utf-8") as transition_source,
    ):
        output_header_line = output.readline()
        output_header = json.loads(output_header_line)
        digest.update(output_header_line.encode())
        for source in (lane_source, stub_source, middle_source, transition_source):
            header = json.loads(source.readline())
            if header.get("record") != "header":
                raise AssertionError("source stream header missing")
        expected_header = {
            "record": "header",
            "schema": "t73_x_m1_complete_explicit_replacement_images/v1",
            "source_receipt_sha256s": data["source_receipt_sha256s"],
            "transition_verification_sha256": data["transition_verification_sha256"],
        }
        if output_header != expected_header:
            raise AssertionError("complete explicit output header changed")

        for lane_line, stub_line, middle_line in zip(
            lane_source, stub_source, middle_source, strict=True
        ):
            output_line = output.readline()
            if not output_line:
                raise AssertionError("complete explicit output ended early")
            record = json.loads(output_line)
            digest.update(output_line.encode())
            lane = json.loads(lane_line)
            stub = json.loads(stub_line)
            middle = json.loads(middle_line)
            first = json.loads(transition_source.readline())
            last = json.loads(transition_source.readline())
            identity = (lane["band_index"], lane["component"])
            if any(
                (source["band_index"], source["component"]) != identity
                for source in (stub, middle, first, last)
            ):
                raise AssertionError("source stream identity mismatch")
            if (first["side"], last["side"]) != ("first", "last"):
                raise AssertionError("transition source order changed")

            core, core_ranges = reconstruct(lane, stub, middle, first, last, "core")
            push, push_ranges = reconstruct(lane, stub, middle, first, last, "push")
            expected = {
                "record": "complete_explicit_replacement_image",
                "band_index": identity[0],
                "component": identity[1],
                "ambient_coordinate_dimension": 4,
                "core_vertices": core,
                "push_vertices": push,
                "core_piece_ranges": core_ranges,
                "push_piece_ranges": push_ranges,
                "core_segment_count": len(core) - 1,
                "push_segment_count": len(push) - 1,
                "transition_center_tracks": {
                    "core": [core_ranges[3]["segment_range"], core_ranges[5]["segment_range"]],
                    "push": [push_ranges[3]["segment_range"], push_ranges[5]["segment_range"]],
                },
                "source_relative_status": "BOUND_TO_VERIFIED_EJECTION_CELLS",
            }
            if record != expected:
                raise AssertionError(f"explicit replacement record {identity[0]} changed")
            records += 1
            counts[identity[1]] += 1
            core_segments += len(core) - 1
            push_segments += len(push) - 1
            boundary_checks += 16
        if output.readline() or transition_source.readline():
            raise AssertionError("unused output or transition records remain")

    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("complete explicit decompressed stream SHA mismatch")
    expected_counts = {"m_2": 269, "m_3": 1240, "r_xy": 2, "r_zx": 2}
    totals = (records, core_segments, push_segments, boundary_checks)
    if dict(sorted(counts.items())) != expected_counts or totals != (1513, 77182, 81558, 24208):
        raise AssertionError(f"complete explicit replay totals changed: {totals}")
    if (data["explicit_core_segment_count"], data["explicit_push_segment_count"]) != (
        core_segments, push_segments
    ):
        raise AssertionError("receipt explicit segment counts changed")

    return {
        "verdict": "PASS_COMPLETE_EXPLICIT_POST_X_REPLACEMENT_IMAGES_FULL",
        "records_reconstructed": records,
        "core_segments_reconstructed": core_segments,
        "push_segments_reconstructed": push_segments,
        "piece_boundary_matches_replayed": boundary_checks,
        "transition_center_tracks_replayed": 6052,
        "record_stream_sha_checked": True,
        "cache_sha_checked": check_cache_sha,
        "common_three_manifold_chart": "OPEN",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--check-cache-sha", action="store_true")
    args = parser.parse_args()
    if args.full:
        result = verify_full(args.check_cache_sha)
    else:
        _, _, checks = check_receipt()
        result = {"verdict": "PASS_COMPLETE_EXPLICIT_POST_X_REPLACEMENT_RECEIPT", "checks": checks}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
