#!/usr/bin/env python3
"""Independently verify every connector-to-replacement framing mismatch."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_post_x_connector_stub_framing_gap.json"
ASSEMBLY = ROOT / "geometry/t73_post_x_framed_cycle_assembly.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
DUAL = ROOT / "geometry/t73_actual_dual_product_ribbons.json"
RECEIPT = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"


def point(values):
    return tuple(Fraction(value) for value in values)


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/home/") and os.name == "nt":
        return Path("//wsl.localhost/Ubuntu") / value[1:]
    return path


def same_quotient_endpoint(raw, expected):
    value = point(raw)
    return (
        len(value) in (3, 4)
        and (len(value) == 3 or value[3] == 1)
        and all((value[axis] - expected[axis]) % 4 == 0 for axis in range(3))
    )


def verify():
    saved = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in saved.items() if key != "sha256"}
    if saved["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("connector-stub gap payload SHA mismatch")
    assembly = json.loads(ASSEMBLY.read_text())
    spine = json.loads(SPINE.read_text())
    ar_link = json.loads(AR_LINK.read_text())
    dual = json.loads(DUAL.read_text())
    receipt = json.loads(RECEIPT.read_text())
    bindings = {
        "post_x_framed_cycle_assembly_sha256": assembly["sha256"],
        "johnson_spine_embedding_sha256": spine["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "actual_dual_product_ribbons_sha256": dual["sha256"],
        "post_x_replacement_cells_receipt_sha256": receipt["sha256"],
    }
    if any(saved[key] != value for key, value in bindings.items()):
        raise AssertionError("connector-stub gap source binding changed")

    connectors = {
        item["connector_id"]: item["polyline"] for item in spine["central_connectors"]
    }
    dual_normals = {
        item["name"]: point(item["product_normal"]) for item in dual["components"]
    }
    width = Fraction(ar_link["framing"]["spine_ribbon_transport"]["width"])
    neighbors = {}
    for component in assembly["components"]:
        blocks = component["blocks"]
        for index, block in enumerate(blocks):
            if block["kind"] == "post_x_framed_replacement_path":
                neighbors[block["band_index"]] = (
                    component["component"],
                    blocks[index - 1],
                    blocks[(index + 1) % len(blocks)],
                )

    def expected_core(component, block, before):
        if block["kind"] == "actual_johnson_central_connector":
            vertices = connectors[block["connector_id"]]
            return point(vertices[-1] if before else vertices[0])
        low, high = block["source_segment_range"]
        index = high + 1 if before else low
        return point(ar_link["components"][component]["polyline"][index])

    core_matches = push_matches = endpoints = 0
    mismatch_counts = Counter()
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        if json.loads(source.readline()).get("record") != "header":
            raise AssertionError("replacement cache header missing")
        for line in source:
            cell = json.loads(line)
            component, previous, following = neighbors[cell["band_index"]]
            for before, key, endpoint_index, neighbor in (
                (True, "source_stub_before", 0, previous),
                (False, "source_stub_after", -1, following),
            ):
                expected = expected_core(component, neighbor, before)
                core_raw = cell[key]["vertices"][endpoint_index]
                push_raw = cell[key]["push_vertices"][endpoint_index]
                if same_quotient_endpoint(core_raw, expected):
                    core_matches += 1
                core_point = point(core_raw)
                push_point = point(push_raw)
                source_normal = tuple(
                    push_point[axis] - core_point[axis] for axis in range(3)
                )
                target_normal = (
                    (width, width, width)
                    if neighbor["kind"] == "actual_johnson_central_connector"
                    else dual_normals[component]
                )
                if source_normal == target_normal:
                    push_matches += 1
                else:
                    mismatch_counts[(
                        component, neighbor["kind"], source_normal, target_normal
                    )] += 1
                endpoints += 1

    replayed_counts = sorted(mismatch_counts.values(), reverse=True)
    if endpoints != 3026 or core_matches != 3026 or push_matches != 0:
        raise AssertionError("connector-stub endpoint replay totals changed")
    if replayed_counts != [2480, 538, 4, 4]:
        raise AssertionError("connector-stub mismatch classes changed")
    saved_counts = sorted(
        (record["endpoint_count"] for record in saved["mismatch_types"]),
        reverse=True,
    )
    if saved_counts != replayed_counts:
        raise AssertionError("saved mismatch-class counts disagree with replay")
    return {
        "verdict": "PASS_POST_X_CONNECTOR_STUB_FRAMING_GAP",
        "core_endpoint_matches": core_matches,
        "push_endpoint_matches": push_matches,
        "missing_normal_homotopies": endpoints - push_matches,
        "mismatch_types": len(mismatch_counts),
        "actual_complete_push_cycles": False,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
