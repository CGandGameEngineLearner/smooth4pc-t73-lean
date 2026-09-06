#!/usr/bin/env python3
"""Glue every canonical x-band disk to its four fixed shell ports in R3."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUBS = ROOT / "audit/t73_x_m1_splice_stub_cores_r3_receipt.json"
BANDS = ROOT / "geometry/t73_x_band_canonical_r3_cell_atlas.json"
FRAMING = ROOT / "geometry/t73_x_m1_framing_exteriorization.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_x_band_global_r3_port_strips_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_x_band_global_r3_port_strips.jsonl.gz"
SLOPE = 1_000_003


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


def scale(factor, value):
    return tuple(factor * coordinate for coordinate in value)


def midpoint(first, second):
    return tuple((a + b) / 2 for a, b in zip(first, second))


def functional(value):
    return value[1] - SLOPE * value[0]


def build(output_path):
    stubs = json.loads(STUBS.read_text())
    bands = json.loads(BANDS.read_text())
    framing = json.loads(FRAMING.read_text())
    width = Fraction(framing["band_width"])
    stub_records = []
    with gzip.open(resolve(stubs["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        stub_records.extend(json.loads(line) for line in source)
    if len(stub_records) != len(bands["bands"]) != 1513:
        raise AssertionError("band/stub record inventory changed")

    endpoint_centers = []
    port_data = []
    for stub in stub_records:
        values = stub["stubs"]
        v0 = point(values["source_stub_before"]["end_r3"])
        v1 = point(values["source_stub_after"]["start_r3"])
        v4 = point(values["target_complement_first"]["start_r3"])
        v5 = point(values["target_complement_last"]["end_r3"])
        start = midpoint(v0, v1)
        end = midpoint(v4, v5)
        endpoint_centers.extend((start, end))
        port_data.append((v0, v1, v4, v5, start, end))
    if len(set(endpoint_centers)) != 3026:
        raise AssertionError("band attachment center endpoints are not distinct")
    functional_values = sorted(functional(value) for value in endpoint_centers)
    if len(set(functional_values)) != 3026:
        raise AssertionError("routing functional is not injective on endpoint columns")
    minimum_functional_separation = min(
        right - left for left, right in zip(functional_values, functional_values[1:])
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_x_band_global_r3_port_strips/v1",
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "x_band_canonical_r3_cell_atlas_sha256": bands["sha256"],
        "x_m1_framing_exteriorization_sha256": framing["sha256"],
        "routing_functional": [str(-SLOPE), "1", "0"],
    }
    records = strip_triangles = transversality_checks = port_matches = 0
    maximum_functional_halfwidth = Fraction(0)
    maximum_z_halfwidth = Fraction(0)
    generic_width = (width, 2 * width, 3 * width)
    with output_path.open("wb") as raw_output:
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            encoded = (canonical(header) + "\n").encode()
            output.write(encoded)
            digest.update(encoded)
            for index, (stub, band, ports) in enumerate(zip(stub_records, bands["bands"], port_data)):
                v0, v1, v4, v5, start, end = ports
                if (stub["band_index"], band["band_index"]) != (index, index):
                    raise AssertionError("band/stub order mismatch")
                height = Fraction(100 + index)
                exterior_x = Fraction(10_000 + 2 * index)
                start_high = (start[0], start[1], height)
                start_exterior = (
                    exterior_x,
                    start[1] + SLOPE * (exterior_x - start[0]),
                    height,
                )
                end_exterior_x = exterior_x + 1
                end_exterior = (
                    end_exterior_x,
                    end[1] + SLOPE * (end_exterior_x - end[0]),
                    height,
                )
                end_high = (end[0], end[1], height)
                centerline = [start, start_high, start_exterior, end_exterior, end_high, end]
                start_width = subtract(v1, v0)
                end_width = subtract(v5, v4)
                widths = [start_width, generic_width, generic_width, generic_width, generic_width, end_width]
                negative = [add(center, scale(Fraction(-1, 2), vector)) for center, vector in zip(centerline, widths)]
                positive = [add(center, scale(Fraction(1, 2), vector)) for center, vector in zip(centerline, widths)]
                if (negative[0], positive[0], negative[-1], positive[-1]) != (v0, v1, v4, v5):
                    raise AssertionError("global band strip misses a fixed shell port")
                port_matches += 4
                triangles = []
                for segment in range(5):
                    triangles.extend((
                        [segment, segment + 1, 6 + segment + 1],
                        [segment, 6 + segment + 1, 6 + segment],
                    ))
                    tangent = subtract(centerline[segment + 1], centerline[segment])
                    for vector in widths[segment:segment + 2]:
                        cross = (
                            tangent[1] * vector[2] - tangent[2] * vector[1],
                            tangent[2] * vector[0] - tangent[0] * vector[2],
                            tangent[0] * vector[1] - tangent[1] * vector[0],
                        )
                        if cross == (0, 0, 0):
                            raise AssertionError("global band-strip width becomes tangent")
                        transversality_checks += 1
                for vector in widths:
                    maximum_functional_halfwidth = max(
                        maximum_functional_halfwidth,
                        abs(vector[1] - SLOPE * vector[0]) / 2,
                    )
                    maximum_z_halfwidth = max(maximum_z_halfwidth, abs(vector[2]) / 2)
                record = {
                    "record": "global_r3_band_port_strip",
                    "band_index": index,
                    "component": band["component"],
                    "source_band_surface_sha256": band["source_band_surface_sha256"],
                    "centerline_vertices": [encode(value) for value in centerline],
                    "strip_width_field": [encode(value) for value in widths],
                    "negative_lane_vertices": [encode(value) for value in negative],
                    "positive_lane_vertices_reverse_orientation": [encode(value) for value in reversed(positive)],
                    "strip_triangles": triangles,
                    "fixed_shell_ports": {
                        "source_negative": encode(v0),
                        "source_positive": encode(v1),
                        "target_negative": encode(v4),
                        "target_positive": encode(v5),
                    },
                    "routing_height": str(height),
                    "exterior_x_interval": [str(exterior_x), str(end_exterior_x)],
                    "relative_cell_map_status": "SOURCE_BAND_DISK_SUBDIVIDED_TO_PORT_FIXED_STRIP",
                }
                encoded = (canonical(record) + "\n").encode()
                output.write(encoded)
                digest.update(encoded)
                records += 1
                strip_triangles += len(triangles)

    if 2 * maximum_functional_halfwidth >= minimum_functional_separation:
        raise AssertionError("strip width exhausts endpoint functional separation")
    if 2 * maximum_z_halfwidth >= 1:
        raise AssertionError("strip width exhausts routing-height separation")
    receipt = {
        "schema": "t73_x_band_global_r3_port_strips_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha256(output_path),
        "record_stream_sha256": digest.hexdigest().upper(),
        "builder_sha256": file_sha256(Path(__file__)),
        "splice_stub_cores_r3_receipt_sha256": stubs["sha256"],
        "x_band_canonical_r3_cell_atlas_sha256": bands["sha256"],
        "x_m1_framing_exteriorization_sha256": framing["sha256"],
        "band_count": records,
        "fixed_shell_port_count": port_matches,
        "strip_triangle_count": strip_triangles,
        "width_transversality_check_count": transversality_checks,
        "routing_functional": [str(-SLOPE), "1", "0"],
        "endpoint_functional_value_count": len(functional_values),
        "minimum_endpoint_functional_separation": str(minimum_functional_separation),
        "maximum_strip_functional_halfwidth": str(maximum_functional_halfwidth),
        "minimum_routing_height_separation": "1",
        "maximum_strip_z_halfwidth": str(maximum_z_halfwidth),
        "centerline_global_disjointness": "PASS_BY_FUNCTIONAL_AND_HEIGHT_SEPARATION",
        "strip_global_clearance_status": "OPEN_EXACT_TRIANGLE_CHECK",
        "push_framing_status": "OPEN",
        "completion_status": "ALL_X_BAND_DISKS_GLUED_TO_FIXED_SHELL_PORTS_IN_R3",
        "verdict": "PASS_X_BAND_GLOBAL_R3_PORT_STRIPS_CONSTRUCTED",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(os.environ.get("T73_X_BAND_GLOBAL_PORT_STRIPS_CACHE", DEFAULT_OUTPUT))
    receipt = build(output)
    print(json.dumps({
        "verdict": receipt["verdict"],
        "bands": receipt["band_count"],
        "ports": receipt["fixed_shell_port_count"],
        "triangles": receipt["strip_triangle_count"],
        "centerlines": receipt["centerline_global_disjointness"],
        "strip_clearance": receipt["strip_global_clearance_status"],
        "bytes": receipt["cache_size"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
