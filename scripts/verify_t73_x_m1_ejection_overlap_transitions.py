#!/usr/bin/env python3
"""Verify all framed local/global overlap mapping-cylinder transitions."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "audit/t73_x_m1_ejection_overlap_transitions_receipt.json"
BUILDER = ROOT / "scripts/build_t73_x_m1_ejection_overlap_transitions.py"
PRODUCT = ROOT / "geometry/t73_x_m1_collar_product_extension.json"
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
EJECTION = ROOT / "geometry/t73_m1_parallel_annulus_ambient_ejection.json"
EJECTION_RECEIPT = ROOT / "audit/t73_m1_parallel_annulus_ambient_ejection_receipt.json"
STUB_RECEIPT = ROOT / "audit/t73_x_m1_ejected_splice_stubs_receipt.json"
MIDDLE_RECEIPT = ROOT / "audit/t73_x_m1_ejected_middle_complements_receipt.json"


def canonical_sha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()
def point(values): return tuple(Fraction(value) for value in values)
def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""): digest.update(block)
    return digest.hexdigest().upper()
def resolve(value):
    path = Path(value)
    if path.exists() or len(value) < 3 or value[1:3] not in (":\\", ":/"): return path
    return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")


def check_receipt():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8")); product = json.loads(PRODUCT.read_text(encoding="utf-8")); foliation = json.loads(FOLIATION.read_text(encoding="utf-8")); ejection = json.loads(EJECTION.read_text(encoding="utf-8")); er = json.loads(EJECTION_RECEIPT.read_text(encoding="utf-8")); sr = json.loads(STUB_RECEIPT.read_text(encoding="utf-8")); mr = json.loads(MIDDLE_RECEIPT.read_text(encoding="utf-8"))
    checks = {"payload": receipt["sha256"] == canonical_sha({key: value for key, value in receipt.items() if key != "sha256"}), "builder": receipt["builder_sha256"] == file_sha(BUILDER), "sources": receipt["product_extension_sha256"] == product["sha256"] and receipt["foliation_sha256"] == foliation["sha256"] and receipt["ambient_ejection_sha256"] == ejection["sha256"] and receipt["ambient_ejection_receipt_sha256"] == er["sha256"] and receipt["stub_receipt_sha256"] == sr["sha256"] and receipt["middle_receipt_sha256"] == mr["sha256"], "counts": receipt["interface_count"] == 3026 and receipt["core_transition_count"] == 3026 and receipt["push_transition_count"] == 3026 and receipt["total_mapping_cylinder_tetrahedra"] == 18156, "verdict": receipt["verdict"] == "PASS_X_M1_FRAMED_OVERLAP_TRANSITION_CELLS_CONSTRUCTED"}
    if not all(checks.values()): raise AssertionError(f"overlap-transition receipt failed: {checks}")
    return receipt, checks


def endpoint(pieces, last):
    piece = pieces[-1] if last else pieces[0]; vertex = piece["target_vertices"][-1] if last else piece["target_vertices"][0]; return point(vertex)


def verify_full(stub_cache=None, middle_cache=None, check_cache_sha=False):
    receipt, checks = check_receipt(); sr = json.loads(STUB_RECEIPT.read_text(encoding="utf-8")); mr = json.loads(MIDDLE_RECEIPT.read_text(encoding="utf-8")); cache = resolve(receipt["cache_path"]); stub_cache = stub_cache or resolve(sr["cache_path"]); middle_cache = middle_cache or resolve(mr["cache_path"])
    if check_cache_sha and file_sha(cache) != receipt["cache_sha256"]: raise AssertionError("overlap-transition cache SHA changed")
    interface_count = core_matches = push_matches = support_checks = 0; previous_high = None
    with gzip.open(cache, "rt", encoding="utf-8") as tf, gzip.open(stub_cache, "rt", encoding="utf-8") as sf, gzip.open(middle_cache, "rt", encoding="utf-8") as mf:
        header = json.loads(next(tf)); next(sf); next(mf)
        if header["schema"] != "t73_x_m1_ejection_overlap_transitions/v1" or len(header["mapping_cylinder_tetrahedra"]) != 6: raise AssertionError("overlap transition header/template changed")
        for band in range(1513):
            stub = json.loads(next(sf)); middle = json.loads(next(mf)); first = json.loads(next(tf)); last = json.loads(next(tf))
            if (first["band_index"], first["side"], last["band_index"], last["side"]) != (band, "first", band, "last"): raise AssertionError("overlap interface order changed")
            low, high = map(Fraction, first["support_level_interval"])
            if previous_high is not None and low <= previous_high: raise AssertionError("parallel-level transition supports overlap")
            previous_high = high; support_checks += 1
            expected_local = {
                "first": (endpoint(stub["stubs"]["target_complement_first"]["core_segment_image"], True), endpoint(stub["stubs"]["target_complement_first"]["outward_push_segment_image"], True)),
                "last": (endpoint(stub["stubs"]["target_complement_last"]["core_segment_image"], False), endpoint(stub["stubs"]["target_complement_last"]["outward_push_segment_image"], False)),
            }
            expected_global = {"first": (point(middle["target_core_vertices"][0]), point(middle["target_push_vertices"][0])), "last": (point(middle["target_core_vertices"][-1]), point(middle["target_push_vertices"][-1]))}
            for record in (first, last):
                side = record["side"]
                if point(record["local_cubical_boundary"]["center_core"]) != expected_local[side][0] or point(record["global_annulus_boundary"]["center_core"]) != expected_global[side][0]: raise AssertionError("core overlap boundary misses source image cache")
                if point(record["local_cubical_boundary"]["center_push"]) != expected_local[side][1] or point(record["global_annulus_boundary"]["center_push"]) != expected_global[side][1]: raise AssertionError("push overlap boundary misses source image cache")
                if expected_local[side][0] == expected_local[side][1] or expected_global[side][0] == expected_global[side][1]: raise AssertionError("overlap framing interval collapsed")
                core_matches += 1; push_matches += 1; interface_count += 1
        if next(tf, None) is not None or next(sf, None) is not None or next(mf, None) is not None: raise AssertionError("overlap/source cache lengths differ")
    if (interface_count, core_matches, push_matches) != (3026, 3026, 3026): raise AssertionError("overlap full totals changed")
    return {"verdict": "PASS_X_M1_FRAMED_OVERLAP_TRANSITIONS_FULL", "fast_checks": checks, "interfaces": interface_count, "core_boundary_matches": core_matches, "push_boundary_matches": push_matches, "disjoint_level_support_checks": support_checks, "mapping_cylinder_tetrahedra": 18156, "cache_sha_checked": check_cache_sha, "charted_cycle_continuity": True, "single_affine_s3_chart_status": "OPEN"}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--full", action="store_true"); parser.add_argument("--stub-cache", type=Path); parser.add_argument("--middle-cache", type=Path); parser.add_argument("--check-cache-sha", action="store_true"); args = parser.parse_args()
    result = verify_full(args.stub_cache, args.middle_cache, args.check_cache_sha) if args.full else {"verdict": "PASS_X_M1_OVERLAP_TRANSITIONS_RECEIPT", "checks": check_receipt()[1], "interfaces": 3026}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__": main()
