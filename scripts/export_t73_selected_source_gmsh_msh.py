#!/usr/bin/env python3
"""Restore and export a rational frame from a saved Gmsh mesh/entity map."""

from __future__ import annotations

import argparse
import importlib.util
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "geometry/t73_selected_source_exterior.json"


def load_probe():
    path = ROOT / "scripts/probe_t73_selected_source_gmsh.py"
    spec = importlib.util.spec_from_file_location("gmsh_probe_export", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def export(msh_path, entity_map_path, output, perform_independent_verify=True):
    import gmsh

    probe = load_probe()
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    entity_map = json.loads(entity_map_path.read_text(encoding="utf-8"))
    recorded = entity_map.get("sha256")
    payload = {key: value for key, value in entity_map.items() if key != "sha256"}
    if recorded != probe.canonical_sha(payload):
        raise AssertionError("Gmsh entity map hash is stale")
    if entity_map.get("source_exterior_sha256") != source["sha256"]:
        raise AssertionError("Gmsh entity map is stale relative to source")
    routes_by_index = {
        item["route_index"]: item for item in source["exterior_intervals"]
    }
    route_entities = []
    for item in entity_map["routes"]:
        index = item["route_index"]
        if index not in routes_by_index:
            raise AssertionError("Gmsh entity map names an unknown source route")
        route_entities.append({**item, "route": routes_by_index[index]})
    line_exact = {
        int(tag): tuple(
            tuple(Fraction(value) for value in endpoint) for endpoint in endpoints
        )
        for tag, endpoints in entity_map["line_exact_endpoints"].items()
    }
    surface_exact = {
        int(tag): tuple(
            tuple(Fraction(value) for value in vertex) for vertex in triangle
        )
        for tag, triangle in entity_map["surface_exact_triangles"].items()
    }
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.open(str(msh_path))
        frame = probe.extract_frame(
            gmsh,
            source,
            route_entities,
            entity_map["boundary_surfaces"],
            entity_map["volume"],
            entity_map["gmsh_algorithm_3d"],
            line_exact,
            surface_exact,
            perform_independent_verify,
        )
    finally:
        gmsh.finalize()
    output.write_text(json.dumps(frame, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return frame


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("msh", type=Path)
    parser.add_argument("entity_map", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--defer-independent-verify", action="store_true")
    args = parser.parse_args()
    result = export(
        args.msh,
        args.entity_map,
        args.output,
        not args.defer_independent_verify,
    )
    print("T73_GMSH_MSH_EXPORT=PASS_PREFIX_ONLY")
    print(f"SCOPE={result['scope']}")
    print(f"SHA256={result['sha256']}")


if __name__ == "__main__":
    main()
