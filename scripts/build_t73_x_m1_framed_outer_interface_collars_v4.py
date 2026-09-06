#!/usr/bin/env python3
"""Stagger v3 end-exterior heights to repair the exact mutual collision."""

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
V3 = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v3_receipt.json"
OBSTRUCTION = ROOT / "audit/t73_x_m1_outer_collar_v3_core_push_clearance.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v4_receipt.json"
DEFAULT_OUTPUT = (
    Path.home() / ".cache/t73_x_m1_framed_outer_interface_collars_v4.jsonl.gz"
)
SLOPE = 1_000_033
FUNCTIONAL_Z = 2
END_EXTERIOR_HEIGHT_OFFSET = Fraction(1, 2)


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
    v3 = json.loads(V3.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    if obstruction["verdict"] != "REFUTED_X_M1_OUTER_COLLAR_V3_CORE_PUSH_CLEARANCE":
        raise AssertionError("v4 requires the saved exact v3 mutual obstruction")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_m1_framed_outer_interface_collars/v4",
        "refuted_v3_receipt_sha256": v3["sha256"],
        "v3_mutual_obstruction_sha256": obstruction["sha256"],
        "end_exterior_height_offset": str(END_EXTERIOR_HEIGHT_OFFSET),
        "routing_functional": [str(-SLOPE), "1", str(FUNCTIONAL_Z)],
        "construction_classification": "CANDIDATE_UNVERIFIED_UNTIL_ALL_GLOBAL_AND_AMBIENT_CHECKS",
    }
    records = segments = triangles = transversality = changed_vertices = 0
    with (
        gzip.open(resolve(v3["cache_path"]), "rt", encoding="utf-8") as source,
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
            old_end_exterior = core[4]
            target_functional = functional(core[-1])
            new_height = old_end_exterior[2] + END_EXTERIOR_HEIGHT_OFFSET
            core[4] = (
                old_end_exterior[0],
                target_functional
                + SLOPE * old_end_exterior[0]
                - FUNCTIONAL_Z * new_height,
                new_height,
            )
            push = [add(vertex, normal) for vertex, normal in zip(core, normals)]
            if (
                functional(core[4]) != target_functional
                or functional(core[5]) != target_functional
            ):
                raise AssertionError("v4 staggered last ray changes target functional")
            if (
                core[4][2] - core[3][2] != END_EXTERIOR_HEIGHT_OFFSET
                or core[4][2] - core[5][2] != END_EXTERIOR_HEIGHT_OFFSET
            ):
                raise AssertionError("v4 end-exterior half-layer changed")
            for index in range(len(core) - 1):
                tangent = subtract(core[index + 1], core[index])
                if affine_vector_hits_zero(
                    cross(tangent, normals[index]), cross(tangent, normals[index + 1])
                ):
                    raise AssertionError("v4 staggered route normal becomes tangent")
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
                        "routing_height",
                        "classification",
                        "global_core_push_ribbon_clearance_status",
                    }
                },
                "record": "framed_outer_interface_collar_v4",
                "source_v3_record_sha256": canonical_sha(old),
                "routing_base_height": old["routing_height"],
                "end_exterior_height": str(new_height),
                "end_exterior_height_offset": str(END_EXTERIOR_HEIGHT_OFFSET),
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
            changed_vertices += 1
    receipt = {
        "schema": "t73_x_m1_framed_outer_interface_collars_v4_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha(Path(__file__)),
        "refuted_v3_receipt_sha256": v3["sha256"],
        "v3_mutual_obstruction_sha256": obstruction["sha256"],
        "end_exterior_height_offset": str(END_EXTERIOR_HEIGHT_OFFSET),
        "changed_end_exterior_vertex_count": changed_vertices,
        "collar_count": records,
        "final_core_segment_count": segments,
        "final_push_segment_count": segments,
        "final_ribbon_triangle_count": triangles,
        "normal_transversality_check_count": transversality,
        "relative_twist_sum": 0,
        "classification": "CANDIDATE_UNVERIFIED",
        "global_clearance_status": "OPEN",
        "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_ISOTOPY_EXTENSION",
        "completion_status": "ALL_V4_END_EXTERIOR_HEIGHTS_STAGGERED_BY_ONE_HALF",
        "verdict": "PASS_X_M1_FRAMED_OUTER_INTERFACE_COLLARS_V4_LOCAL_CANDIDATE",
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
        or Path(os.environ.get("T73_X_M1_OUTER_COLLAR_V4_CACHE", DEFAULT_OUTPUT))
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "collars": result["collar_count"],
                "changed_vertices": result["changed_end_exterior_vertex_count"],
                "segments": result["final_core_segment_count"],
                "triangles": result["final_ribbon_triangle_count"],
                "classification": result["classification"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
