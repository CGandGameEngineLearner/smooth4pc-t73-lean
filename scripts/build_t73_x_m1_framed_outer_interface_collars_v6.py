#!/usr/bin/env python3
"""Separate paired dual collars into opposite exterior x half-spaces."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path

from build_t73_x_m1_framed_outer_interface_collars import (
    add,
    affine_vector_hits_zero,
    canonical,
    canonical_sha,
    cross,
    encode,
    file_sha,
    point,
    subtract,
)

ROOT = Path(__file__).resolve().parents[1]
V5 = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v5_receipt.json"
OBSTRUCTION = ROOT / "audit/t73_x_m1_outer_collar_v5_ribbon_clearance.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v6_receipt.json"
DEFAULT_OUTPUT = (
    Path.home() / ".cache/t73_x_m1_framed_outer_interface_collars_v6.jsonl.gz"
)
SLOPE = 1_000_033
FUNCTIONAL_Z = 2
DENOMINATOR = 499_900
POSITIVE_LIFT = (Fraction(1, DENOMINATOR), Fraction(233, DENOMINATOR), Fraction(1))
END_OFFSET = Fraction(1, 2)


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def functional(value):
    return value[1] - SLOPE * value[0] + FUNCTIONAL_Z * value[2]


def ribbon_triangles(size):
    return [
        triangle
        for index in range(size - 1)
        for triangle in (
            [index, index + 1, size + index + 1],
            [index, size + index + 1, size + index],
        )
    ]


def build(output_path):
    v5 = json.loads(V5.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    if obstruction["verdict"] != "REFUTED_X_M1_OUTER_COLLAR_V5_RIBBON_CLEARANCE":
        raise AssertionError("v6 requires the exact v5 nonincident ribbon obstruction")
    if functional(POSITIVE_LIFT) != 0:
        raise AssertionError("v6 dual lift does not preserve F")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_framed_outer_interface_collars/v6",
        "refuted_v5_receipt_sha256": v5["sha256"],
        "v5_ribbon_obstruction_sha256": obstruction["sha256"],
        "dual_lift": [str(value) for value in POSITIVE_LIFT],
        "before_exterior_x_half_space": "positive",
        "after_exterior_x_half_space": "negative",
        "end_exterior_height_offset": str(END_OFFSET),
        "routing_functional": [str(-SLOPE), "1", str(FUNCTIONAL_Z)],
        "construction_classification": "CANDIDATE_UNVERIFIED_UNTIL_ALL_GLOBAL_AND_AMBIENT_CHECKS",
    }
    records = changed = unchanged = segments = triangles = transversality = 0
    with (
        gzip.open(resolve(v5["cache_path"]), "rt", encoding="utf-8") as source,
        output_path.open("wb") as raw,
        gzip.GzipFile(
            filename="", fileobj=raw, mode="wb", compresslevel=6, mtime=0
        ) as output,
    ):
        source.readline()
        encoded = (canonical(header) + "\n").encode()
        output.write(encoded)
        digest.update(encoded)
        for line in source:
            old = json.loads(line)
            core = [point(value) for value in old["final_core_vertices"]]
            normals = [point(value) for value in old["final_normal_field"]]
            is_changed = (
                old["neighbor_kind"] != "actual_johnson_central_connector"
                and old["side"] == "after"
            )
            if is_changed:
                height = Fraction(old["routing_base_height"])
                core[3] = (-abs(core[3][0]), core[3][1], core[3][2])
                core[3] = (
                    core[3][0],
                    functional(core[1]) + SLOPE * core[3][0] - FUNCTIONAL_Z * height,
                    height,
                )
                end_height = height + END_OFFSET
                core[4] = (-abs(core[4][0]), core[4][1], core[4][2])
                core[4] = (
                    core[4][0],
                    functional(core[6])
                    + SLOPE * core[4][0]
                    - FUNCTIONAL_Z * end_height,
                    end_height,
                )
                changed += 1
            else:
                unchanged += 1
            push = [add(vertex, normal) for vertex, normal in zip(core, normals)]
            for index in range(len(core) - 1):
                tangent = subtract(core[index + 1], core[index])
                if affine_vector_hits_zero(
                    cross(tangent, normals[index]), cross(tangent, normals[index + 1])
                ):
                    raise AssertionError(
                        f"v6 route normal becomes tangent: {old['interface_index']}/{index}"
                    )
                transversality += 1
            record = {
                **{
                    key: value
                    for key, value in old.items()
                    if key
                    not in {
                        "record",
                        "final_core_vertices",
                        "final_push_vertices",
                        "final_ribbon_triangles",
                        "classification",
                        "global_core_push_ribbon_clearance_status",
                    }
                },
                "record": "framed_outer_interface_collar_v6",
                "source_v5_record_sha256": canonical_sha(old),
                "opposite_exterior_half_space_changed": is_changed,
                "assigned_dual_lift": (
                    [str(value) for value in POSITIVE_LIFT]
                    if old["neighbor_kind"] != "actual_johnson_central_connector"
                    else None
                ),
                "final_core_vertices": [encode(value) for value in core],
                "final_push_vertices": [encode(value) for value in push],
                "final_ribbon_triangles": ribbon_triangles(len(core)),
                "global_core_push_ribbon_clearance_status": "OPEN",
                "classification": "CANDIDATE_UNVERIFIED",
            }
            encoded = (canonical(record) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            records += 1
            segments += len(core) - 1
            triangles += len(record["final_ribbon_triangles"])
    if (changed, unchanged) != (4, 3022):
        raise AssertionError("v6 changed-collar inventory is not minimal")
    receipt = {
        "schema": "t73_x_m1_framed_outer_interface_collars_v6_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha(Path(__file__)),
        "refuted_v5_receipt_sha256": v5["sha256"],
        "v5_ribbon_obstruction_sha256": obstruction["sha256"],
        "dual_lift": [str(value) for value in POSITIVE_LIFT],
        "before_exterior_x_half_space": "positive",
        "after_exterior_x_half_space": "negative",
        "end_exterior_height_offset": str(END_OFFSET),
        "changed_after_dual_collar_count": changed,
        "unchanged_collar_count": unchanged,
        "collar_count": records,
        "final_core_segment_count": segments,
        "final_push_segment_count": segments,
        "final_ribbon_triangle_count": triangles,
        "normal_transversality_check_count": transversality,
        "relative_twist_sum": 0,
        "classification": "CANDIDATE_UNVERIFIED",
        "global_clearance_status": "OPEN",
        "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_ISOTOPY_EXTENSION",
        "completion_status": "FOUR_AFTER_DUAL_COLLARS_USE_NEGATIVE_EXTERIOR_X_HALF_SPACE",
        "verdict": "PASS_X_M1_FRAMED_OUTER_INTERFACE_COLLARS_V6_LOCAL_CANDIDATE",
    }
    receipt["sha256"] = canonical_sha(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build(
        args.output
        or Path(os.environ.get("T73_X_M1_OUTER_COLLAR_V6_CACHE", DEFAULT_OUTPUT))
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "changed_after_dual": result["changed_after_dual_collar_count"],
                "unchanged": result["unchanged_collar_count"],
                "segments": result["final_core_segment_count"],
                "triangles": result["final_ribbon_triangle_count"],
                "classification": result["classification"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
