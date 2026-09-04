#!/usr/bin/env python3
"""Resource/geometry probe for a Gmsh-conformal selected-source frame.

This probe does not write a proof artifact.  It tests whether Gmsh can mesh
the holed outer cube while conforming to saved ribbon surfaces.  In contrast
to the first failed experiment, every ribbon endpoint connector is embedded
in its unique insertion-ball boundary surface before the ribbon is embedded
in the volume.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "geometry" / "t73_selected_source_exterior.json"


def point(raw):
    return tuple(float(Fraction(value)) for value in raw)


def canonical_sha(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def run(limit: int, algorithm: int = 10) -> dict:
    if limit < 1 or limit > 630:
        raise ValueError("limit must lie in 1..630")
    import gmsh

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    routes = source["exterior_intervals"][:limit]
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add(f"t73-selected-source-prefix-{limit}")
        occ = gmsh.model.occ
        outer = occ.addBox(-20, -20, -20, 40, 40, 40)
        holes = []
        for sphere in source["insertion_spheres"]:
            lower = point(sphere["box_lower"])
            upper = point(sphere["box_upper"])
            holes.append(
                occ.addBox(
                    *lower, *(upper[axis] - lower[axis] for axis in range(3))
                )
            )
        cut, _ = occ.cut(
            [(3, outer)],
            [(3, hole) for hole in holes],
            removeObject=True,
            removeTool=True,
        )
        occ.synchronize()
        if len(cut) != 1 or cut[0][0] != 3:
            raise RuntimeError("OCC cut did not produce one holed volume")
        volume = cut[0][1]
        boundary_surfaces = [
            tag
            for dimension, tag in gmsh.model.getBoundary(
                [(3, volume)], oriented=False
            )
            if dimension == 2
        ]

        points = {}
        lines = {}
        line_endpoints = {}
        ribbon_surfaces = []
        ribbon_curves = set()

        def add_point(raw):
            coordinate = point(raw)
            if coordinate not in points:
                points[coordinate] = occ.addPoint(*coordinate, 1.0)
            return points[coordinate]

        def add_line(first, second):
            first_coordinate, second_coordinate = point(first), point(second)
            first_tag, second_tag = add_point(first), add_point(second)
            key = tuple(sorted((first_tag, second_tag)))
            if key not in lines:
                lines[key] = occ.addLine(first_tag, second_tag)
                line_endpoints[lines[key]] = (
                    first_coordinate,
                    second_coordinate,
                )
            tag = lines[key]
            return tag if (first_tag, second_tag) == key else -tag

        connector_tags = []
        for route in routes:
            for triangle in route["ruled_ribbon_triangles"]:
                edges = [
                    add_line(triangle[index], triangle[(index + 1) % 3])
                    for index in range(3)
                ]
                loop = occ.addCurveLoop(edges)
                ribbon_surfaces.append(occ.addPlaneSurface([loop]))
                ribbon_curves.update(abs(edge) for edge in edges)
            for key in ("initial_transverse_edge", "terminal_transverse_edge"):
                connector_tags.append(
                    abs(add_line(*route["ruled_ribbon_boundary"][key]))
                )
        occ.synchronize()

        def lies_in_bbox(value, bounds, tolerance=1e-7):
            return all(
                bounds[axis] - tolerance
                <= value[axis]
                <= bounds[axis + 3] + tolerance
                for axis in range(3)
            )

        connector_surface = {}
        for tag in connector_tags:
            first, second = line_endpoints[tag]
            candidates = [
                surface
                for surface in boundary_surfaces
                if lies_in_bbox(first, gmsh.model.getBoundingBox(2, surface))
                and lies_in_bbox(second, gmsh.model.getBoundingBox(2, surface))
            ]
            if len(candidates) != 1:
                raise RuntimeError(
                    f"connector {tag} belongs to {len(candidates)} boundary surfaces"
                )
            connector_surface[tag] = candidates[0]
            gmsh.model.mesh.embed(1, [tag], 2, candidates[0])
        gmsh.model.mesh.embed(2, ribbon_surfaces, 3, volume)
        gmsh.model.mesh.embed(1, sorted(ribbon_curves), 3, volume)
        gmsh.option.setNumber("Mesh.Algorithm3D", algorithm)
        gmsh.option.setNumber("Mesh.MeshSizeMax", 5)
        gmsh.option.setNumber("Mesh.MeshSizeMin", 1e-6)
        gmsh.model.mesh.generate(3)
        tetrahedra = sum(
            len(tags) for tags in gmsh.model.mesh.getElements(3, volume)[1]
        )
        result = {
            "schema": "t73_selected_source_gmsh_probe/v1",
            "source_exterior_sha256": source["sha256"],
            "route_prefix": limit,
            "ribbon_surfaces": len(ribbon_surfaces),
            "endpoint_connectors": len(connector_tags),
            "boundary_surfaces": len(boundary_surfaces),
            "gmsh_algorithm_3d": algorithm,
            "mesh_nodes": len(gmsh.model.mesh.getNodes()[0]),
            "tetrahedra": tetrahedra,
            "status": "PASS_PROBE_ONLY",
        }
        result["sha256"] = canonical_sha(result)
        return result
    finally:
        gmsh.finalize()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--algorithm", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.limit, args.algorithm)
    if args.output:
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
