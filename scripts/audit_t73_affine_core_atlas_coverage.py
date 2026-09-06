#!/usr/bin/env python3
"""Audit whether the affine core realizes every framed-atlas segment."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AFFINE = ROOT / "geometry/t73_affine_s3_core_realization.json"
ATLAS = ROOT / "geometry/t73_complete_framed_dotted_atlas.json"
POST_X = ROOT / "geometry/t73_post_x_framed_cycle_assembly.json"
POST_X_RECEIPT = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
PRIOR_GAP = ROOT / "audit/t73_source_pd_post_x_coverage_gap.json"
HOMOLOGY_MODEL = ROOT / "geometry/t73_homology_admissible_affine_framed_model.json"
OUTPUT = ROOT / "audit/t73_affine_core_atlas_coverage_gap.json"


def canonical_sha256(value: dict) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def build() -> dict:
    affine = json.loads(AFFINE.read_text())
    atlas = json.loads(ATLAS.read_text())
    post_x = json.loads(POST_X.read_text())
    post_x_receipt = json.loads(POST_X_RECEIPT.read_text())
    prior_gap = json.loads(PRIOR_GAP.read_text())
    homology_model = json.loads(HOMOLOGY_MODEL.read_text())

    role_counts = Counter(
        role["kind"]
        for component in affine["framed_core_components"]
        for role in component["segment_roles"]
    )
    replacement_blocks = [
        block
        for component in post_x["components"]
        for block in component["blocks"]
        if block["kind"] == "post_x_framed_replacement_path"
    ]
    replacement_by_component = Counter()
    for component in post_x["components"]:
        replacement_by_component[component["component"]] += sum(
            block["core_segment_count"]
            for block in component["blocks"]
            if block["kind"] == "post_x_framed_replacement_path"
        )

    result = {
        "schema": "t73_affine_core_atlas_coverage_gap/v1",
        "affine_core_realization_sha256": affine["sha256"],
        "complete_framed_dotted_atlas_sha256": atlas["sha256"],
        "post_x_framed_cycle_assembly_sha256": post_x["sha256"],
        "post_x_replacement_cells_receipt_sha256": post_x_receipt["sha256"],
        "prior_source_pd_coverage_gap_sha256": prior_gap["sha256"],
        "homology_admissible_affine_model_sha256": homology_model["sha256"],
        "complete_atlas_core_segments": atlas["framed_core_segment_count"],
        "complete_atlas_push_segments": atlas["framed_push_segment_count"],
        "affine_core_segments": affine["framed_core_segment_count"],
        "affine_segment_role_counts": dict(sorted(role_counts.items())),
        "post_x_replacement_block_count": len(replacement_blocks),
        "post_x_replacement_core_segments": sum(
            block["core_segment_count"] for block in replacement_blocks
        ),
        "post_x_replacement_push_segments": sum(
            block["push_segment_count"] for block in replacement_blocks
        ),
        "post_x_replacement_core_segments_by_component": dict(
            sorted(replacement_by_component.items())
        ),
        "affine_post_x_replacement_roles": role_counts.get(
            "post_x_framed_replacement_path", 0
        ),
        "coverage_fraction_is_not_defined": (
            "affine corridors are substitute edges, not images of omitted "
            "atlas cells, so raw segment-count division would be misleading"
        ),
        "affine_model_scope": (
            "Johnson central-connector plus dotted-passage skeleton with "
            "new arbitrary closure corridors"
        ),
        "homology_model_actual_t73_status": "REFUTED_BY_ATLAS_COVERAGE_GAP",
        "required_repair": (
            "stream all 1513 explicit post-x framed replacement cells into "
            "one common dotted-S3 realization, retain their splice/collar "
            "crossings, and rebuild the complete core/push PD"
        ),
        "completion_status": "AFFINE_CORE_ATLAS_COVERAGE_GAP_CONFIRMED",
    }
    result["sha256"] = canonical_sha256(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("affine atlas coverage audit is stale")
    print(json.dumps({
        "status": result["completion_status"],
        "atlas_core": result["complete_atlas_core_segments"],
        "affine_core": result["affine_core_segments"],
        "omitted_post_x": result["post_x_replacement_core_segments"],
        "affine_post_x_roles": result["affine_post_x_replacement_roles"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
