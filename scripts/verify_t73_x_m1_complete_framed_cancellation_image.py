#!/usr/bin/env python3
"""Verify the merged five-component x/m1 framed cancellation image."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_complete_framed_cancellation_image.json"
SOURCES = {"post_x_framed_cycle_assembly_sha256": ROOT / "geometry/t73_post_x_framed_cycle_assembly.json", "ejected_band_lanes_receipt_sha256": ROOT / "audit/t73_x_m1_ejected_band_lanes_receipt.json", "ejected_splice_stubs_receipt_sha256": ROOT / "audit/t73_x_m1_ejected_splice_stubs_receipt.json", "ejected_middle_complements_receipt_sha256": ROOT / "audit/t73_x_m1_ejected_middle_complements_receipt.json", "overlap_transitions_receipt_sha256": ROOT / "audit/t73_x_m1_ejection_overlap_transitions_receipt.json", "overlap_transitions_verification_sha256": ROOT / "audit/t73_x_m1_ejection_overlap_transitions_verification.json"}
def canonical_sha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()
def verify():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    if data["sha256"] != canonical_sha({key: value for key, value in data.items() if key != "sha256"}): raise AssertionError("complete cancellation image payload SHA changed")
    for key, path in SOURCES.items():
        if data[key] != json.loads(path.read_text(encoding="utf-8"))["sha256"]: raise AssertionError(f"stale cancellation-image source: {key}")
    expected = {"m_2": (12098, 10760, 1338, 13428, 14044, 14766, 15382), "m_3": (55902, 49600, 6302, 60540, 64284, 66842, 70586), "r_xy": (84, 80, 4, 94, 102, 98, 106), "r_yz": (8, 0, 8, 0, 0, 8, 8), "r_zx": (84, 80, 4, 94, 102, 98, 106)}
    for item in data["components"]:
        values = (item["source_core_segments"], item["replacement_source_segments"], item["unchanged_segments"], item["replacement_target_core_segments"], item["replacement_target_push_segments"], item["target_core_segments"], item["target_push_segments"])
        if values != expected[item["component"]] or not item["closed_core_cycle_in_atlas"] or not item["closed_push_cycle_in_atlas"]: raise AssertionError("component cancellation-image counts/closure changed")
    totals = (data["source_core_segment_count"], data["replacement_source_segment_count"], data["replacement_target_core_segment_count"], data["replacement_target_push_segment_count"], data["target_core_segment_count"], data["target_push_segment_count"])
    if totals != (68176, 60520, 74156, 78532, 81812, 86188): raise AssertionError("complete cancellation-image totals changed")
    overlap = json.loads(SOURCES["overlap_transitions_verification_sha256"].read_text(encoding="utf-8"))
    if overlap["verdict"] != "PASS_X_M1_FRAMED_OVERLAP_TRANSITIONS_FULL" or not overlap["full_verifier_result"]["charted_cycle_continuity"]: raise AssertionError("overlap continuity did not verify")
    if data["completion_status"] != "COMPLETE_X_M1_FRAMED_CANCELLATION_IMAGE_IN_VERIFIED_ATLAS" or data["single_affine_s3_chart_status"] != "OPEN": raise AssertionError("complete cancellation-image scope changed")
    return {"verdict": "PASS_COMPLETE_X_M1_FRAMED_CANCELLATION_IMAGE_IN_ATLAS", "components": 5, "source_core_segments": 68176, "target_core_segments": 81812, "target_push_segments": 86188, "overlap_transitions": 3026, "single_affine_s3_chart_status": "OPEN"}
if __name__ == "__main__": print(json.dumps(verify(), sort_keys=True))
