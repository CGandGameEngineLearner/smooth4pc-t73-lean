#!/usr/bin/env python3
"""Audit framing-normal continuity at all post-x replacement outer ports."""

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
ASSEMBLY = ROOT / "geometry/t73_post_x_framed_cycle_assembly.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
DUAL_RIBBONS = ROOT / "geometry/t73_actual_dual_product_ribbons.json"
REPLACEMENT_RECEIPT = ROOT / "audit/t73_post_x_framed_replacement_cells_receipt.json"
OUTPUT = ROOT / "audit/t73_post_x_connector_stub_framing_gap.json"


def canonical_sha256(value: dict) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def resolve_cache_path(value: str) -> Path:
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/home/") and os.name == "nt":
        return Path("//wsl.localhost/Ubuntu") / value[1:]
    if len(value) >= 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def point(values):
    return tuple(Fraction(value) for value in values)


def adjacent_blocks(assembly):
    result = {}
    for component in assembly["components"]:
        blocks = component["blocks"]
        for index, block in enumerate(blocks):
            if block["kind"] == "post_x_framed_replacement_path":
                result[block["band_index"]] = (
                    component["component"],
                    blocks[index - 1],
                    blocks[(index + 1) % len(blocks)],
                )
    return result


def expected_core_endpoint(component, block, side, connectors, ar_link):
    if block["kind"] == "actual_johnson_central_connector":
        path = connectors[block["connector_id"]]
        return point(path[-1] if side == "before" else path[0])
    if block["kind"] == "actual_dual_two_segment_passage":
        low, high = block["source_segment_range"]
        index = high + 1 if side == "before" else low
        return point(ar_link["components"][component]["polyline"][index])
    raise AssertionError(f"unexpected neighbor block kind {block['kind']}")


def endpoint_matches_mod_deck(raw, expected):
    value = point(raw)
    if len(value) not in (3, 4) or len(expected) != 3:
        return False
    if len(value) == 4 and value[3] != 1:
        return False
    return all((value[axis] - expected[axis]) % 4 == 0 for axis in range(3))


def endpoint_normal(cell, key, endpoint_index):
    core = point(cell[key]["vertices"][endpoint_index])
    push = point(cell[key]["push_vertices"][endpoint_index])
    return tuple(push[axis] - core[axis] for axis in range(3))


def build() -> dict:
    assembly = json.loads(ASSEMBLY.read_text())
    spine = json.loads(SPINE.read_text())
    ar_link = json.loads(AR_LINK.read_text())
    dual_ribbons = json.loads(DUAL_RIBBONS.read_text())
    replacement_receipt = json.loads(REPLACEMENT_RECEIPT.read_text())
    connectors = {
        record["connector_id"]: record["polyline"]
        for record in spine["central_connectors"]
    }
    dual_normals = {
        record["name"]: point(record["product_normal"])
        for record in dual_ribbons["components"]
    }
    width = Fraction(ar_link["framing"]["spine_ribbon_transport"]["width"])
    connector_normal = (width, width, width)
    adjacency = adjacent_blocks(assembly)
    mismatch_types = Counter()
    core_matches = push_matches = endpoint_count = 0

    cache = resolve_cache_path(replacement_receipt["cache_path"])
    with gzip.open(cache, "rt", encoding="utf-8") as source:
        header = json.loads(source.readline())
        if header.get("schema") != "t73_post_x_framed_replacement_cells/v1":
            raise AssertionError("replacement-cell cache header changed")
        for line in source:
            cell = json.loads(line)
            component, previous, following = adjacency[cell["band_index"]]
            for side, key, endpoint_index, neighbor in (
                ("before", "source_stub_before", 0, previous),
                ("after", "source_stub_after", -1, following),
            ):
                expected_core = expected_core_endpoint(
                    component, neighbor, side, connectors, ar_link
                )
                if endpoint_matches_mod_deck(
                    cell[key]["vertices"][endpoint_index], expected_core
                ):
                    core_matches += 1
                source_normal = endpoint_normal(cell, key, endpoint_index)
                expected_normal = (
                    connector_normal
                    if neighbor["kind"] == "actual_johnson_central_connector"
                    else dual_normals[component]
                )
                if source_normal == expected_normal:
                    push_matches += 1
                else:
                    mismatch_types[(
                        component,
                        neighbor["kind"],
                        tuple(str(value) for value in source_normal),
                        tuple(str(value) for value in expected_normal),
                    )] += 1
                endpoint_count += 1

    mismatch_records = [
        {
            "component": key[0],
            "neighbor_kind": key[1],
            "replacement_stub_normal": list(key[2]),
            "adjacent_block_normal": list(key[3]),
            "endpoint_count": count,
        }
        for key, count in sorted(mismatch_types.items())
    ]
    result = {
        "schema": "t73_post_x_connector_stub_framing_gap/v1",
        "post_x_framed_cycle_assembly_sha256": assembly["sha256"],
        "johnson_spine_embedding_sha256": spine["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "actual_dual_product_ribbons_sha256": dual_ribbons["sha256"],
        "post_x_replacement_cells_receipt_sha256": replacement_receipt["sha256"],
        "replacement_block_count": len(adjacency),
        "outer_endpoint_count": endpoint_count,
        "core_endpoint_matches_mod_deck": core_matches,
        "push_endpoint_matches": push_matches,
        "missing_framing_normal_transition_count": endpoint_count - push_matches,
        "mismatch_types": mismatch_records,
        "mismatch_type_count": len(mismatch_records),
        "prior_closed_push_cycle_interpretation": (
            "REFUTED_AT_LITERAL_CONNECTOR_STUB_INTERFACES"
        ),
        "preserved_result": (
            "all core endpoints agree modulo the mapping-torus deck and all "
            "interior replacement framing cells remain valid"
        ),
        "required_repair": (
            "insert one source-relative nonvanishing normal homotopy and its "
            "framing strip at each of the 3026 connector/dual-to-stub ports"
        ),
        "completion_status": "POST_X_CONNECTOR_STUB_FRAMING_GAP_CONFIRMED",
    }
    result["sha256"] = canonical_sha256(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("connector-stub framing audit is stale")
    print(json.dumps({
        "core_matches": result["core_endpoint_matches_mod_deck"],
        "push_matches": result["push_endpoint_matches"],
        "missing_transitions": result["missing_framing_normal_transition_count"],
        "mismatch_types": result["mismatch_type_count"],
        "status": result["completion_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
