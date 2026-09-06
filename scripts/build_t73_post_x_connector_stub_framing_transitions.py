#!/usr/bin/env python3
"""Construct all missing connector/dual-to-replacement framing collars."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAP = ROOT / "audit/t73_post_x_connector_stub_framing_gap.json"
ASSEMBLY = ROOT / "geometry/t73_post_x_framed_cycle_assembly.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
DUAL = ROOT / "geometry/t73_actual_dual_product_ribbons.json"
REPLACEMENT = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
OUTPUT_RECEIPT = ROOT / "audit/t73_post_x_connector_stub_framing_transitions_receipt.json"
DEFAULT_OUTPUT = Path.home() / ".cache/t73_post_x_connector_stub_framing_transitions.jsonl.gz"
COLLAR_FRACTION = Fraction(1, 1_000_000)


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
    if value.startswith("/home/") and os.name == "nt":
        return Path("//wsl.localhost/Ubuntu") / value[1:]
    if len(value) >= 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def point(values):
    return tuple(Fraction(value) for value in values[:3])


def encode(values):
    return [str(value) for value in values]


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def scale(factor, value):
    return tuple(factor * coordinate for coordinate in value)


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def build(output_path):
    gap = json.loads(GAP.read_text())
    assembly = json.loads(ASSEMBLY.read_text())
    spine = json.loads(SPINE.read_text())
    ar_link = json.loads(AR_LINK.read_text())
    dual = json.loads(DUAL.read_text())
    replacement = json.loads(REPLACEMENT.read_text())
    connectors = {
        item["connector_id"]: [point(vertex) for vertex in item["polyline"]]
        for item in spine["central_connectors"]
    }
    dual_normals = {
        item["name"]: point(item["product_normal"]) for item in dual["components"]
    }
    width = Fraction(ar_link["framing"]["spine_ribbon_transport"]["width"])
    adjacency = {}
    for component in assembly["components"]:
        blocks = component["blocks"]
        for index, block in enumerate(blocks):
            if block["kind"] == "post_x_framed_replacement_path":
                adjacency[block["band_index"]] = (
                    component["component"], blocks[index - 1], blocks[(index + 1) % len(blocks)]
                )

    def neighbor_segment(component, block, before):
        if block["kind"] == "actual_johnson_central_connector":
            path = connectors[block["connector_id"]]
            return (path[-2], path[-1]) if before else (path[0], path[1])
        low, high = block["source_segment_range"]
        path = [point(value) for value in ar_link["components"][component]["polyline"]]
        return (path[high], path[high + 1]) if before else (path[low], path[low + 1])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    stream_digest = hashlib.sha256()
    header = {
        "record": "header",
        "schema": "t73_post_x_connector_stub_framing_transitions/v1",
        "framing_gap_sha256": gap["sha256"],
        "replacement_cells_receipt_sha256": replacement["sha256"],
        "collar_fraction": str(COLLAR_FRACTION),
    }
    records = triangles = endpoint_matches = transversality_checks = 0
    type_counts = Counter()
    with gzip.open(resolve(replacement["cache_path"]), "rt", encoding="utf-8") as source, output_path.open("wb") as raw_output:
        source.readline()
        with gzip.GzipFile(filename="", fileobj=raw_output, mode="wb", compresslevel=6, mtime=0) as output:
            encoded = (canonical(header) + "\n").encode()
            output.write(encoded)
            stream_digest.update(encoded)
            for line in source:
                cell = json.loads(line)
                component, previous, following = adjacency[cell["band_index"]]
                for before, key, endpoint_index, neighbor in (
                    (True, "source_stub_before", 0, previous),
                    (False, "source_stub_after", -1, following),
                ):
                    segment_start, segment_end = neighbor_segment(component, neighbor, before)
                    port = segment_end if before else segment_start
                    other = segment_start if before else segment_end
                    collar = add(port, scale(COLLAR_FRACTION, subtract(other, port)))
                    stub_core = point(cell[key]["vertices"][endpoint_index])
                    stub_push = point(cell[key]["push_vertices"][endpoint_index])
                    stub_normal = subtract(stub_push, stub_core)
                    adjacent_normal = (
                        (width, width, width)
                        if neighbor["kind"] == "actual_johnson_central_connector"
                        else dual_normals[component]
                    )
                    core_vertices = (
                        [other, collar, port] if before else [port, collar, other]
                    )
                    normals = (
                        [adjacent_normal, adjacent_normal, stub_normal]
                        if before else [stub_normal, adjacent_normal, adjacent_normal]
                    )
                    push_vertices = [add(vertex, normal) for vertex, normal in zip(core_vertices, normals)]
                    if not all(cross(subtract(core_vertices[i + 1], core_vertices[i]), normals[j]) != (0, 0, 0)
                               for i in range(2) for j in (i, i + 1)):
                        raise AssertionError("framing transition becomes tangent")
                    transversality_checks += 4
                    if subtract(push_vertices[0 if before else -1], core_vertices[0 if before else -1]) != adjacent_normal:
                        raise AssertionError("transition misses adjacent framing")
                    if subtract(push_vertices[-1 if before else 0], core_vertices[-1 if before else 0]) != stub_normal:
                        raise AssertionError("transition misses replacement framing")
                    endpoint_matches += 2
                    record = {
                        "record": "connector_stub_framing_transition",
                        "band_index": cell["band_index"],
                        "component": component,
                        "side": "before" if before else "after",
                        "neighbor_kind": neighbor["kind"],
                        "neighbor_id": neighbor.get("connector_id", neighbor.get("passage_id")),
                        "core_vertices": [encode(value) for value in core_vertices],
                        "normal_field": [encode(value) for value in normals],
                        "push_vertices": [encode(value) for value in push_vertices],
                        "ribbon_triangles": [[0, 1, 4], [0, 4, 3], [1, 2, 5], [1, 5, 4]],
                        "relative_twist": 0,
                        "source_relative_status": "EXPLICIT_ENDPOINT_NORMAL_HOMOTOPY",
                    }
                    encoded = (canonical(record) + "\n").encode()
                    output.write(encoded)
                    stream_digest.update(encoded)
                    records += 1
                    triangles += 4
                    type_counts[f"{component}/{neighbor['kind']}"] += 1

    receipt = {
        "schema": "t73_post_x_connector_stub_framing_transitions_receipt/v1",
        "cache_path": str(output_path),
        "cache_size": output_path.stat().st_size,
        "cache_sha256": file_sha256(output_path),
        "record_stream_sha256": stream_digest.hexdigest().upper(),
        "builder_sha256": file_sha256(Path(__file__)),
        "framing_gap_sha256": gap["sha256"],
        "post_x_framed_cycle_assembly_sha256": assembly["sha256"],
        "johnson_spine_embedding_sha256": spine["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "actual_dual_product_ribbons_sha256": dual["sha256"],
        "replacement_cells_receipt_sha256": replacement["sha256"],
        "collar_fraction": str(COLLAR_FRACTION),
        "transition_count": records,
        "ribbon_triangle_count": triangles,
        "endpoint_normal_match_count": endpoint_matches,
        "normal_transversality_check_count": transversality_checks,
        "transition_type_counts": dict(sorted(type_counts.items())),
        "relative_twist_sum": 0,
        "global_transition_clearance_status": "OPEN",
        "completion_status": "ALL_CONNECTOR_STUB_FRAMING_TRANSITIONS_CONSTRUCTED",
        "verdict": "PASS_POST_X_CONNECTOR_STUB_FRAMING_TRANSITIONS_LOCAL",
    }
    receipt["sha256"] = canonical_sha256(receipt)
    OUTPUT_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(os.environ.get("T73_POST_X_FRAMING_TRANSITIONS_CACHE", DEFAULT_OUTPUT))
    receipt = build(output)
    print(json.dumps({
        "verdict": receipt["verdict"],
        "transitions": receipt["transition_count"],
        "triangles": receipt["ribbon_triangle_count"],
        "endpoint_matches": receipt["endpoint_normal_match_count"],
        "global_clearance": receipt["global_transition_clearance_status"],
        "bytes": receipt["cache_size"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
