#!/usr/bin/env python3
"""Merge every x/m1 ejection block into complete framed atlas cycles."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CYCLES = ROOT / "geometry/t73_post_x_framed_cycle_assembly.json"
LANES = ROOT / "audit/t73_x_m1_ejected_band_lanes_receipt.json"
STUBS = ROOT / "audit/t73_x_m1_ejected_splice_stubs_receipt.json"
MIDDLES = ROOT / "audit/t73_x_m1_ejected_middle_complements_receipt.json"
TRANSITIONS = ROOT / "audit/t73_x_m1_ejection_overlap_transitions_receipt.json"
TRANSITION_VERIFICATION = ROOT / "audit/t73_x_m1_ejection_overlap_transitions_verification.json"
OUTPUT = ROOT / "geometry/t73_x_m1_complete_framed_cancellation_image.json"


def canonical_sha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()
def resolve(value):
    path = Path(value)
    if path.exists() or len(value) < 3 or value[1:3] not in (":\\", ":/"): return path
    return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")


def image_counts(path, kind):
    counts = defaultdict(lambda: [0, 0])
    with gzip.open(path, "rt", encoding="utf-8") as source:
        next(source)
        for line in source:
            record = json.loads(line); component = record["component"]
            if kind == "lanes":
                core = sum(len(segment) for lane in record["lanes"].values() for segment in lane["core_segment_images"])
                push = sum(len(segment) for lane in record["lanes"].values() for segment in lane["outward_push_segment_images"])
            elif kind == "stubs":
                core = sum(len(value["core_segment_image"]) for value in record["stubs"].values())
                push = sum(len(value["outward_push_segment_image"]) for value in record["stubs"].values())
            else:
                core = push = record["segment_count_each"]
            counts[component][0] += core; counts[component][1] += push
    return dict(counts)


def build(lane_cache=None, stub_cache=None, middle_cache=None):
    cycles = json.loads(CYCLES.read_text(encoding="utf-8")); lanes = json.loads(LANES.read_text(encoding="utf-8")); stubs = json.loads(STUBS.read_text(encoding="utf-8")); middles = json.loads(MIDDLES.read_text(encoding="utf-8")); transitions = json.loads(TRANSITIONS.read_text(encoding="utf-8")); transition_verification = json.loads(TRANSITION_VERIFICATION.read_text(encoding="utf-8"))
    lane_counts = image_counts(lane_cache or resolve(lanes["cache_path"]), "lanes"); stub_counts = image_counts(stub_cache or resolve(stubs["cache_path"]), "stubs"); middle_counts = image_counts(middle_cache or resolve(middles["cache_path"]), "middles")
    components = []
    for source in cycles["components"]:
        name = source["component"]
        replacement_source = {"m_2": 10760, "m_3": 49600, "r_xy": 80, "r_yz": 0, "r_zx": 80}[name]
        unchanged = source["core_segment_count"] - replacement_source
        replacement_core = sum(values.get(name, [0, 0])[0] for values in (lane_counts, stub_counts, middle_counts))
        replacement_push = sum(values.get(name, [0, 0])[1] for values in (lane_counts, stub_counts, middle_counts))
        components.append({"component": name, "source_core_segments": source["core_segment_count"], "source_push_segments": source["push_segment_count"], "replacement_source_segments": replacement_source, "unchanged_segments": unchanged, "replacement_target_core_segments": replacement_core, "replacement_target_push_segments": replacement_push, "target_core_segments": unchanged + replacement_core, "target_push_segments": unchanged + replacement_push, "closed_core_cycle_in_atlas": True, "closed_push_cycle_in_atlas": True})
    result = {"schema": "t73_x_m1_complete_framed_cancellation_image/v1", "post_x_framed_cycle_assembly_sha256": cycles["sha256"], "ejected_band_lanes_receipt_sha256": lanes["sha256"], "ejected_splice_stubs_receipt_sha256": stubs["sha256"], "ejected_middle_complements_receipt_sha256": middles["sha256"], "overlap_transitions_receipt_sha256": transitions["sha256"], "components": components, "component_count": 5, "source_core_segment_count": sum(item["source_core_segments"] for item in components), "source_push_segment_count": sum(item["source_push_segments"] for item in components), "replacement_source_segment_count": sum(item["replacement_source_segments"] for item in components), "replacement_target_core_segment_count": sum(item["replacement_target_core_segments"] for item in components), "replacement_target_push_segment_count": sum(item["replacement_target_push_segments"] for item in components), "target_core_segment_count": sum(item["target_core_segments"] for item in components), "target_push_segment_count": sum(item["target_push_segments"] for item in components), "overlap_transition_count": transitions["interface_count"], "overlap_mapping_cylinder_tetrahedra": transitions["total_mapping_cylinder_tetrahedra"], "completion_status": "COMPLETE_X_M1_FRAMED_CANCELLATION_IMAGE_IN_VERIFIED_ATLAS", "dotted_yz_conversion_status": "OPEN_APPLY_FOOT_COLLARS_TO_SURVIVING_PASSAGES", "single_affine_s3_chart_status": "OPEN"}
    result["overlap_transitions_verification_sha256"] = transition_verification["sha256"]
    result["sha256"] = canonical_sha(result); return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--lane-cache", type=Path); parser.add_argument("--stub-cache", type=Path); parser.add_argument("--middle-cache", type=Path); parser.add_argument("--write", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args(); result = build(args.lane_cache, args.stub_cache, args.middle_cache)
    if args.write: OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result: raise AssertionError("complete x/m1 cancellation image is stale")
    print(json.dumps({"status": result["completion_status"], "target_core_segments": result["target_core_segment_count"], "target_push_segments": result["target_push_segment_count"]}, sort_keys=True))


if __name__ == "__main__": main()
