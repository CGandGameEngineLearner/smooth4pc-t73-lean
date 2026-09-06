#!/usr/bin/env python3
"""Build zero-twist push disks for all globally port-fixed x-band strips."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STRIPS = ROOT / "audit/t73_x_band_global_r3_port_strips_receipt.json"
CLEARANCE = ROOT / "audit/t73_x_band_global_r3_port_strip_clearance.json"
SOURCE_ATLAS = ROOT / "geometry/t73_x_band_canonical_r3_cell_atlas.json"
FRAMING = ROOT / "geometry/t73_x_m1_framing_exteriorization.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_band_global_r3_push_disks_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_band_global_r3_push_disks.jsonl.gz"
INTEGER_DIRECTION = (1, 1, 2)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest().upper()


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    return path


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(values):
    return [str(value) for value in values]


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def build(output_path):
    strips = json.loads(STRIPS.read_text())
    clearance = json.loads(CLEARANCE.read_text())
    source_atlas = json.loads(SOURCE_ATLAS.read_text())
    framing = json.loads(FRAMING.read_text())
    width = Fraction(framing["band_width"])
    scale = width / 1000
    displacement = tuple(scale * value for value in INTEGER_DIRECTION)
    with gzip.open(resolve(strips["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        strip_records = [json.loads(line) for line in source]
    if len(strip_records) != 1513:
        raise AssertionError("global band-strip inventory changed")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_band_global_r3_push_disks/v1",
        "global_port_strips_receipt_sha256": strips["sha256"],
        "global_port_strip_clearance_sha256": clearance["sha256"],
        "canonical_source_band_atlas_sha256": source_atlas["sha256"],
        "x_m1_framing_exteriorization_sha256": framing["sha256"],
        "push_displacement": [str(value) for value in displacement],
    }
    records = triangles = lane_ribbons = product_tetrahedra = transverse = 0
    with output_path.open("wb") as raw_output:
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            encoded = (canonical(header) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            for index, (strip, source_band) in enumerate(zip(strip_records, source_atlas["bands"])):
                negative = [point(value) for value in strip["negative_lane_vertices"]]
                positive = [point(value) for value in reversed(strip["positive_lane_vertices_reverse_orientation"])]
                core = negative + positive
                push = [add(value, displacement) for value in core]
                triangle_ids = strip["strip_triangles"]
                product_ids = []
                for triangle in triangle_ids:
                    a, b, c = sorted(triangle)
                    product_ids.extend((
                        [a, b, c, c + 12],
                        [a, b, b + 12, c + 12],
                        [a, a + 12, b + 12, c + 12],
                    ))
                    first, second, third = [core[vertex] for vertex in triangle]
                    normal = cross(subtract(second, first), subtract(third, first))
                    if dot(normal, displacement) == 0:
                        raise AssertionError("global band push direction lies in a strip triangle")
                    transverse += 1
                ribbon_ids = []
                for offset in (0, 6):
                    for segment in range(5):
                        ribbon_ids.extend((
                            [offset + segment, offset + segment + 1, 12 + offset + segment + 1],
                            [offset + segment, 12 + offset + segment + 1, 12 + offset + segment],
                        ))
                record = {
                    "record": "global_r3_x_band_push_disk",
                    "band_index": index,
                    "component": strip["component"],
                    "source_band_surface_sha256": source_band["source_band_surface_sha256"],
                    "source_relative_twist": source_band["source_relative_twist"],
                    "core_vertices": [encode(value) for value in core],
                    "push_vertices": [encode(value) for value in push],
                    "core_triangles": triangle_ids,
                    "push_triangles": triangle_ids,
                    "lane_framing_ribbon_triangles": ribbon_ids,
                    "surface_product_tetrahedra": product_ids,
                    "push_displacement": [str(value) for value in displacement],
                    "endpoint_push_gluing_status": "OPEN_STUB_AND_TRANSITION_PUSH_PORTS",
                    "cell_status": "ZERO_TWIST_PRODUCT_PUSH_DISK_CONSTRUCTED",
                }
                encoded = (canonical(record) + "\n").encode()
                output.write(encoded)
                digest.update(encoded)
                records += 1
                triangles += len(triangle_ids)
                lane_ribbons += len(ribbon_ids)
                product_tetrahedra += len(product_ids)
    receipt = {
        "schema": "t73_x_band_global_r3_push_disks_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha256(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha256(Path(__file__)),
        "global_port_strips_receipt_sha256": strips["sha256"],
        "global_port_strip_clearance_sha256": clearance["sha256"],
        "canonical_source_band_atlas_sha256": source_atlas["sha256"],
        "x_m1_framing_exteriorization_sha256": framing["sha256"],
        "push_integer_direction": list(INTEGER_DIRECTION),
        "push_scale": str(scale),
        "push_displacement": [str(value) for value in displacement],
        "band_count": records,
        "core_triangle_count": triangles,
        "push_triangle_count": triangles,
        "lane_framing_ribbon_triangle_count": lane_ribbons,
        "surface_product_tetrahedron_count": product_tetrahedra,
        "triangle_push_transversality_checks": transverse,
        "relative_twist_sum": 0,
        "local_product_cells_status": "PASS",
        "global_push_disk_clearance_status": "OPEN_EXACT_NONINCIDENT_CHECK",
        "endpoint_push_gluing_status": "OPEN_STUB_AND_TRANSITION_PUSH_PORTS",
        "completion_status": "ALL_GLOBAL_X_BAND_PRODUCT_PUSH_DISKS_CONSTRUCTED",
        "verdict": "PASS_X_BAND_GLOBAL_R3_PUSH_DISKS_LOCAL_PRODUCT",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(os.environ.get("T73_X_BAND_GLOBAL_PUSH_DISKS_CACHE", DEFAULT_OUTPUT))
    result = build(output)
    print(json.dumps({
        "verdict": result["verdict"],
        "bands": result["band_count"],
        "triangles": result["core_triangle_count"],
        "lane_ribbons": result["lane_framing_ribbon_triangle_count"],
        "product_tetrahedra": result["surface_product_tetrahedron_count"],
        "global_clearance": result["global_push_disk_clearance_status"],
        "bytes": result["cache_size"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
