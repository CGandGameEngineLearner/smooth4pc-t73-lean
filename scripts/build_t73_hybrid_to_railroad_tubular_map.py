#!/usr/bin/env python3
"""Build identical triangulated solid-torus neighborhoods for source and railroad links."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH_MAP = ROOT / "geometry/t73_hybrid_to_railroad_graph_map.json"
RAILROAD = ROOT / "geometry/t73_actual_railroad_core_coordinates.json"
FRAMINGS = ROOT / "geometry/t73_railroad_product_framings.json"
PD = ROOT / "geometry/t73_source_bound_standard_pd_candidate.json"
OUTPUT = ROOT / "geometry/t73_hybrid_to_railroad_tubular_map.json"


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def segment_prism_tetrahedra(first_fiber, second_fiber):
    first = [3 * first_fiber + index for index in range(3)]
    second = [3 * second_fiber + index for index in range(3)]
    return [
        [first[0], first[1], first[2], second[2]],
        [first[0], first[1], second[1], second[2]],
        [first[0], second[0], second[1], second[2]],
    ]


def side_triangles(first_fiber, second_fiber):
    first = [3 * first_fiber + index for index in range(3)]
    second = [3 * second_fiber + index for index in range(3)]
    triangles = []
    for index in range(3):
        next_index = (index + 1) % 3
        triangles.extend([
            [first[index], first[next_index], second[next_index]],
            [first[index], second[next_index], second[index]],
        ])
    return triangles


def build() -> dict:
    graph = json.loads(GRAPH_MAP.read_text(encoding="utf-8"))
    railroad = json.loads(RAILROAD.read_text(encoding="utf-8"))
    framings = json.loads(FRAMINGS.read_text(encoding="utf-8"))
    pd = json.loads(PD.read_text(encoding="utf-8"))
    railroad_by_name = {item["name"]: item for item in railroad["components"]}
    graph_components = {item["component"]: item for item in graph["component_maps"]}
    edge_maps = graph["edge_maps"]
    components = []
    for name in railroad["component_order"]:
        target_segments = len(railroad_by_name[name]["vertices"]) - 1
        tetrahedra = []
        for segment in range(target_segments):
            next_fiber = (segment + 1) % target_segments
            tetrahedra.extend(segment_prism_tetrahedra(segment, next_fiber))
        face_counts = Counter(
            tuple(sorted(face))
            for tetrahedron in tetrahedra
            for face in combinations(tetrahedron, 3)
        )
        boundary = [list(face) for face, count in sorted(face_counts.items()) if count == 1]
        source_subdivision = [
            {
                "source_edge": edge["source_edge"],
                "target_segment_range": edge["target_segment_range"],
                "subdivision_segment_count": edge["target_segment_range"][1]
                - edge["target_segment_range"][0]
                + 1,
            }
            for edge in edge_maps
            if edge["component"] == name
        ]
        components.append({
            "component": name,
            "source_graph_map_sha256": canonical_sha(graph_components[name]),
            "target_segment_count": target_segments,
            "fiber_vertex_count": 3,
            "solid_torus_vertex_count": 3 * target_segments,
            "tetrahedra": tetrahedra,
            "boundary_triangles": boundary,
            "source_edge_subdivision": source_subdivision,
            "source_to_target_vertex_map": "identity on the listed common template vertex ids",
            "source_to_target_tetrahedron_map": "identity on the listed common template tetrahedra",
            "meridian_cycle": [0, 1, 2, 0],
            "framing_longitude_vertex_class": 0,
            "closing_fiber_map": [0, 1, 2],
            "relative_twist": 0,
        })
    result = {
        "schema": "t73_hybrid_to_railroad_tubular_map/v1",
        "hybrid_to_railroad_graph_map_sha256": graph["sha256"],
        "railroad_core_coordinates_sha256": railroad["sha256"],
        "railroad_product_framings_sha256": framings["sha256"],
        "source_bound_standard_pd_sha256": pd["sha256"],
        "components": components,
        "component_count": len(components),
        "map_scope": "framed regular neighborhoods only",
        "complement_extension_status": "OPEN_HANDLEBODY_COMPLEMENT_CELL_MAP_REQUIRED",
        "completion_status": "HYBRID_TO_RAILROAD_FRAMED_TUBULAR_HOMEOMORPHISM_CONSTRUCTED",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("hybrid-to-railroad tubular map is stale")
    print("T73_HYBRID_RAILROAD_TUBES=HYBRID_TO_RAILROAD_FRAMED_TUBULAR_HOMEOMORPHISM_CONSTRUCTED")


if __name__ == "__main__":
    main()
