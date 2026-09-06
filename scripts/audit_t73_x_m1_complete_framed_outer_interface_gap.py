#!/usr/bin/env python3
"""Record every unmapped Johnson/dual-to-complete-R3 x-cycle interface."""

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
CYCLES = ROOT / "geometry/t73_post_x_framed_cycle_assembly.json"
SPINE = ROOT / "geometry/t73_johnson_spine_embedding.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
DUAL = ROOT / "geometry/t73_actual_dual_product_ribbons.json"
FRAMED = (
    ROOT / "audit/t73_x_m1_complete_global_r3_framed_replacement_cycles_receipt.json"
)
OUTPUT = ROOT / "audit/t73_x_m1_complete_framed_outer_interface_gap.json"


def canonical_sha(value):
    return (
        hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        )
        .hexdigest()
        .upper()
    )


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value[:3])


def encode(value):
    return [str(coordinate) for coordinate in value]


def add(first, second):
    return tuple(a + b for a, b in zip(first, second))


def subtract(first, second):
    return tuple(a - b for a, b in zip(first, second))


def framed_records(receipt):
    with gzip.open(resolve(receipt["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        return [json.loads(line) for line in source]


def build():
    cycles = json.loads(CYCLES.read_text())
    spine = json.loads(SPINE.read_text())
    ar_link = json.loads(AR_LINK.read_text())
    dual = json.loads(DUAL.read_text())
    framed_receipt = json.loads(FRAMED.read_text())
    framed = framed_records(framed_receipt)
    connectors = {
        item["connector_id"]: [point(vertex) for vertex in item["polyline"]]
        for item in spine["central_connectors"]
    }
    width = Fraction(ar_link["framing"]["spine_ribbon_transport"]["width"])
    connector_normal = (width, width, width)
    dual_normals = {
        item["name"]: point(item["product_normal"]) for item in dual["components"]
    }
    ar_paths = {
        name: [point(vertex) for vertex in ar_link["components"][name]["polyline"]]
        for name in ("r_xy", "r_yz", "r_zx")
    }

    def neighbor_port(component, block, before):
        if block["kind"] == "actual_johnson_central_connector":
            path = connectors[block["connector_id"]]
            return (
                (path[-1], path[-2], connector_normal)
                if before
                else (path[0], path[1], connector_normal)
            )
        low, high = block["source_segment_range"]
        path = ar_paths[component]
        return (
            (path[high + 1], path[high], dual_normals[component])
            if before
            else (path[low], path[low + 1], dual_normals[component])
        )

    interfaces = []
    kinds = Counter()
    for component in cycles["components"]:
        blocks = component["blocks"]
        for block_index, block in enumerate(blocks):
            if block["kind"] != "post_x_framed_replacement_path":
                continue
            band = block["band_index"]
            target = framed[band]
            for side, neighbor, target_index in (
                ("before", blocks[block_index - 1], 0),
                ("after", blocks[(block_index + 1) % len(blocks)], -1),
            ):
                source_core, source_inner, source_normal = neighbor_port(
                    component["component"], neighbor, side == "before"
                )
                source_push = add(source_core, source_normal)
                source_inner_push = add(source_inner, source_normal)
                target_core = point(target["core_vertices"][target_index])
                target_push = point(target["push_vertices"][target_index])
                neighbor_id = neighbor.get("connector_id", neighbor.get("passage_id"))
                interfaces.append(
                    {
                        "interface_index": len(interfaces),
                        "band_index": band,
                        "component": component["component"],
                        "side": side,
                        "neighbor_kind": neighbor["kind"],
                        "neighbor_id": neighbor_id,
                        "source_core_port": encode(source_core),
                        "source_push_port": encode(source_push),
                        "source_inner_core": encode(source_inner),
                        "source_inner_push": encode(source_inner_push),
                        "target_core_port": encode(target_core),
                        "target_push_port": encode(target_push),
                        "core_displacement": encode(subtract(target_core, source_core)),
                        "push_displacement": encode(subtract(target_push, source_push)),
                        "core_port_match": source_core == target_core,
                        "push_port_match": source_push == target_push,
                        "relative_extension_status": "OPEN_CONSTRUCT_AMBIENT_COLLAR_EXTENSION",
                    }
                )
                kinds[neighbor["kind"]] += 1
    if len(interfaces) != 3026:
        raise AssertionError("outer framed interface inventory changed")
    result = {
        "schema": "t73_x_m1_complete_framed_outer_interface_gap/v1",
        "post_x_framed_cycle_assembly_sha256": cycles["sha256"],
        "johnson_spine_embedding_sha256": spine["sha256"],
        "actual_ar_link_sha256": ar_link["sha256"],
        "actual_dual_product_ribbons_sha256": dual["sha256"],
        "complete_r3_framed_replacement_cycles_sha256": framed_receipt["sha256"],
        "interface_count": len(interfaces),
        "neighbor_kind_counts": dict(sorted(kinds.items())),
        "core_port_match_count": sum(item["core_port_match"] for item in interfaces),
        "push_port_match_count": sum(item["push_port_match"] for item in interfaces),
        "distinct_core_displacement_count": len(
            {tuple(item["core_displacement"]) for item in interfaces}
        ),
        "distinct_push_displacement_count": len(
            {tuple(item["push_displacement"]) for item in interfaces}
        ),
        "interfaces": interfaces,
        "integration_status": "OPEN_3026_RELATIVE_FRAMED_COLLAR_EXTENSIONS",
        "verdict": "CONFIRMED_COMPLETE_R3_FRAMED_OUTER_INTERFACE_GAP",
    }
    result["sha256"] = canonical_sha(result)
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
        raise AssertionError("complete framed outer interface audit is stale")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "interfaces": result["interface_count"],
                "core_matches": result["core_port_match_count"],
                "push_matches": result["push_port_match_count"],
                "distinct_core_displacements": result[
                    "distinct_core_displacement_count"
                ],
                "status": result["integration_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
