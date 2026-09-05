#!/usr/bin/env python3
"""Bind every surviving y/z source passage to its framed dotted-S3 cell."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CYCLES = ROOT / "geometry/t73_final_component_passage_cycles.json"
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
MIDDLE_RECEIPT = ROOT / "audit/t73_x_m1_ejected_middle_complements_receipt.json"
DOTTED = ROOT / "geometry/t73_actual_dotted_s3_passage_cells.json"
COLLARS = ROOT / "geometry/t73_dotted_s3_foot_collars.json"
AMBIENT = ROOT / "geometry/t73_dotted_disk_ambient_extensions.json"
X_IMAGE = ROOT / "geometry/t73_x_m1_complete_framed_cancellation_image.json"
OUTPUT = ROOT / "geometry/t73_yz_dotted_passage_replacement_map.json"


def canonical_sha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()
def point(values): return tuple(Fraction(value) for value in values)
def resolve(value):
    path = Path(value)
    if path.exists() or len(value) < 3 or value[1:3] not in (":\\", ":/"): return path
    return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
def quotient_equal(first, second):
    if first[3] != second[3]: return False
    return all((first[axis] - second[axis]) / 4 == int((first[axis] - second[axis]) / 4) for axis in range(3))


def middle_records(path):
    result = {}
    with gzip.open(path, "rt", encoding="utf-8") as source:
        next(source)
        for line in source:
            value = json.loads(line); result[value["band_index"]] = value
    return result


def build(middle_cache=None):
    cycles = json.loads(CYCLES.read_text(encoding="utf-8")); foliation = json.loads(FOLIATION.read_text(encoding="utf-8")); middle_receipt = json.loads(MIDDLE_RECEIPT.read_text(encoding="utf-8")); dotted = json.loads(DOTTED.read_text(encoding="utf-8")); collars = json.loads(COLLARS.read_text(encoding="utf-8")); ambient = json.loads(AMBIENT.read_text(encoding="utf-8")); x_image = json.loads(X_IMAGE.read_text(encoding="utf-8"))
    middles = middle_records(middle_cache or resolve(middle_receipt["cache_path"])); base = [point(value) for value in foliation["base_vertices"]]; normals = [point(value) for value in foliation["unit_normal_field"]]
    dotted_by_id = {item["passage_id"]: (chart["handle"], item) for chart in dotted["charts"] for item in chart["passages"]}; collar_ids = {item["passage_id"] for item in collars["endpoint_records"]}
    replacements = []; source_core_segments = source_push_segments = target_segments = 0
    for cycle in cycles["components"]:
        for passage in cycle["passages"]:
            passage_id = passage["passage_id"]; handle, target = dotted_by_id[passage_id]; source_kind = passage["source_kind"]
            record = {"passage_id": passage_id, "owner": cycle["component"], "handle": handle, "orientation": passage["orientation"], "slot_rank": target["slot_rank"], "dotted_passage_sha256": canonical_sha(target), "foot_collar_record_ref": passage_id, "ambient_disk_track_ref": passage_id, "target_core_segment_count": 1, "target_push_segment_count": 1}
            if source_kind == "x_slide_m1_parallel_z_lane":
                band_index = int(passage_id.split(":")[1]); middle = middles[band_index]; level = Fraction(middle["parallel_level"]); source_vertices = [point(value) for value in middle["source_core_vertices"]]
                expected_order = [18, 19, 20] if passage["orientation"] == 1 else [20, 19, 18]
                indices = []
                for base_index in expected_order:
                    expected = tuple(base[base_index][axis] + level * normals[base_index][axis] for axis in range(4))
                    matches = [index for index, value in enumerate(source_vertices) if quotient_equal(value, expected)]
                    if len(matches) != 1: raise AssertionError(f"{passage_id}: cannot locate unique m1 z-passage vertex {base_index}")
                    indices.append(matches[0])
                if indices != list(range(indices[0], indices[0] + 3)): raise AssertionError(f"{passage_id}: m1 z-passage vertices are not consecutive")
                record.update({"source_kind": "ejected_x_replacement_m1_z_subpath", "band_index": band_index, "middle_cache_record_index": band_index + 1, "source_middle_vertex_range": [indices[0], indices[-1]], "source_base_vertex_order": expected_order, "source_core_segment_count": 2, "source_push_segment_count": 2})
            elif source_kind == "johnson_base_arc":
                record.update({"source_kind": "actual_johnson_handle_arc", "source_arc_id": passage["arc_id"], "source_core_segment_count": 2, "source_push_segment_count": 2})
            elif source_kind == "bottom_coordinate_arc":
                record.update({"source_kind": "actual_bottom_cut_arc", "source_core_segment_count": 1, "source_push_segment_count": 1})
            elif source_kind == "dual_disk_boundary":
                edge = int(passage_id.rsplit(":", 1)[1]); record.update({"source_kind": "actual_dual_two_segment_passage", "source_segment_range": [edge, edge + 1], "source_core_segment_count": 2, "source_push_segment_count": 2})
            else: raise AssertionError(f"unknown passage kind {source_kind}")
            if passage_id not in collar_ids: raise AssertionError("passage has no foot-collar record")
            source_core_segments += record["source_core_segment_count"]; source_push_segments += record["source_push_segment_count"]; target_segments += 1; replacements.append(record)
    if len(replacements) != 1785 or len({item["passage_id"] for item in replacements}) != 1785: raise AssertionError("dotted replacement map is not exhaustive")
    result = {"schema": "t73_yz_dotted_passage_replacement_map/v1", "final_component_passage_cycles_sha256": cycles["sha256"], "m1_parallel_foliation_sha256": foliation["sha256"], "ejected_middle_complements_receipt_sha256": middle_receipt["sha256"], "actual_dotted_s3_passage_cells_sha256": dotted["sha256"], "dotted_s3_foot_collars_sha256": collars["sha256"], "dotted_disk_ambient_extensions_sha256": ambient["sha256"], "x_m1_complete_framed_cancellation_image_sha256": x_image["sha256"], "replacements": replacements, "replacement_count": len(replacements), "x_replacement_count": 1513, "non_x_replacement_count": 272, "source_core_segment_count": source_core_segments, "source_push_segment_count": source_push_segments, "target_core_segment_count": target_segments, "target_push_segment_count": target_segments, "post_conversion_core_segment_count": x_image["target_core_segment_count"] - source_core_segments + target_segments, "post_conversion_push_segment_count": x_image["target_push_segment_count"] - source_push_segments + target_segments, "completion_status": "ALL_SURVIVING_YZ_PASSAGES_BOUND_TO_FRAMED_DOTTED_S3_CELLS", "mapping_cylinder_status": "OPEN_BUILD_1785_FRAMED_PASSAGE_TRANSITIONS"}
    result["sha256"] = canonical_sha(result); return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--middle-cache", type=Path); parser.add_argument("--write", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args(); result = build(args.middle_cache)
    if args.write: OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result: raise AssertionError("dotted passage replacement map is stale")
    print(json.dumps({"status": result["completion_status"], "source_segments": result["source_core_segment_count"], "target_segments": result["target_core_segment_count"], "post_core": result["post_conversion_core_segment_count"], "post_push": result["post_conversion_push_segment_count"]}, sort_keys=True))


if __name__ == "__main__": main()
