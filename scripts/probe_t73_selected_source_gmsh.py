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
import importlib.util
import json
from collections import Counter, defaultdict
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


def encoded(values):
    return [str(Fraction(value)) for value in values]


def element_rows(gmsh, dimension, entity, nodes_per_element):
    rows = []
    element_types, _element_tags, node_tags = gmsh.model.mesh.getElements(
        dimension, entity
    )
    for element_type, flat in zip(element_types, node_tags):
        properties = gmsh.model.mesh.getElementProperties(element_type)
        if int(properties[1]) != dimension or int(properties[3]) != nodes_per_element:
            raise RuntimeError(
                f"unexpected element type {element_type} on dimension {dimension}"
            )
        raw = [int(value) for value in flat]
        rows.extend(
            raw[index : index + nodes_per_element]
            for index in range(0, len(raw), nodes_per_element)
        )
    return rows


def ordered_curve_path(gmsh, line_tags, node_index, exact_nodes, start_point):
    edges = []
    for tag in line_tags:
        edges.extend(
            [node_index[first], node_index[second]]
            for first, second in element_rows(gmsh, 1, tag, 2)
        )
    adjacency = defaultdict(set)
    for first, second in edges:
        adjacency[first].add(second)
        adjacency[second].add(first)
    endpoints = [vertex for vertex, neighbours in adjacency.items() if len(neighbours) == 1]
    if len(endpoints) != 2 or any(len(value) not in (1, 2) for value in adjacency.values()):
        raise RuntimeError("Gmsh curve subdivision is not one simple path")
    expected = tuple(Fraction(value) for value in start_point)
    starts = [vertex for vertex in endpoints if exact_nodes[vertex] == expected]
    if len(starts) != 1:
        raise RuntimeError("Gmsh curve path lost its specified initial endpoint")
    path, previous, current = [starts[0]], None, starts[0]
    while True:
        following = adjacency[current] - ({previous} if previous is not None else set())
        if not following:
            break
        if len(following) != 1:
            raise RuntimeError("Gmsh curve path branches")
        next_vertex = next(iter(following))
        path.append(next_vertex)
        previous, current = current, next_vertex
    if len(path) != len(adjacency):
        raise RuntimeError("Gmsh curve path is disconnected or cyclic")
    return path


def load_frame_verifier():
    path = ROOT / "scripts" / "verify_t73_selected_source_tetrahedral_frame.py"
    spec = importlib.util.spec_from_file_location("gmsh_frame_verifier", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_frame(
    gmsh,
    source,
    route_entities,
    boundary_surfaces,
    volume,
    algorithm,
    line_exact_endpoints,
    surface_exact_triangles,
    perform_independent_verify=True,
):
    node_tags, coordinates, _ = gmsh.model.mesh.getNodes()
    node_tags = [int(value) for value in node_tags]
    node_index = {tag: index for index, tag in enumerate(node_tags)}
    float_to_exact = {}
    for item in route_entities:
        route = item["route"]
        for raw in route["vertices"] + route["positive_push_off_vertices"]:
            exact = tuple(Fraction(value) for value in raw)
            float_to_exact[tuple(float(value) for value in exact)] = exact
    for lower, upper in [
        (
            tuple(Fraction(value) for value in source["ambient"]["outer_ball"]["lower"]),
            tuple(Fraction(value) for value in source["ambient"]["outer_ball"]["upper"]),
        ),
        *[
            (
                tuple(Fraction(value) for value in sphere["box_lower"]),
                tuple(Fraction(value) for value in sphere["box_upper"]),
            )
            for sphere in source["insertion_spheres"]
        ],
    ]:
        for mask in range(8):
            exact = tuple(
                upper[axis] if mask & (1 << axis) else lower[axis]
                for axis in range(3)
            )
            float_to_exact[tuple(float(value) for value in exact)] = exact
    exact_nodes = []
    raw_node_coordinates = {}
    for index in range(len(node_tags)):
        raw = tuple(float(coordinates[3 * index + axis]) for axis in range(3))
        raw_node_coordinates[node_tags[index]] = raw
        exact_nodes.append(
            float_to_exact.get(raw, tuple(Fraction(value) for value in raw))
        )

    fixed_values = {
        Fraction(-20), Fraction(20),
        *(
            Fraction(value)
            for sphere in source["insertion_spheres"]
            for value in sphere["box_lower"] + sphere["box_upper"]
        ),
    }
    for surface in boundary_surfaces:
        bounds = gmsh.model.getBoundingBox(2, surface)
        fixed_axes = [
            axis for axis in range(3) if abs(bounds[axis + 3] - bounds[axis]) < 1e-6
        ]
        if len(fixed_axes) != 1:
            raise RuntimeError("an OCC boundary surface is not axis aligned")
        axis = fixed_axes[0]
        approximate = (bounds[axis] + bounds[axis + 3]) / 2
        candidates = [value for value in fixed_values if abs(float(value) - approximate) < 1e-5]
        if len(candidates) != 1:
            raise RuntimeError("cannot restore an exact OCC boundary plane")
        fixed = candidates[0]
        tags = gmsh.model.mesh.getNodes(2, surface, True, False)[0]
        for raw_tag in tags:
            index = node_index[int(raw_tag)]
            value = list(exact_nodes[index])
            value[axis] = fixed
            exact_nodes[index] = tuple(value)

    for surface, triangle in surface_exact_triangles.items():
        direction1 = tuple(float(triangle[1][axis] - triangle[0][axis]) for axis in range(3))
        direction2 = tuple(float(triangle[2][axis] - triangle[0][axis]) for axis in range(3))
        axes = next(
            pair
            for pair in ((0, 1), (0, 2), (1, 2))
            if abs(direction1[pair[0]] * direction2[pair[1]] - direction1[pair[1]] * direction2[pair[0]]) > 1e-30
        )
        determinant = direction1[axes[0]] * direction2[axes[1]] - direction1[axes[1]] * direction2[axes[0]]
        tags = gmsh.model.mesh.getNodes(2, surface, True, False)[0]
        for raw_tag in tags:
            tag = int(raw_tag)
            raw = raw_node_coordinates[tag]
            relative = tuple(raw[axis] - float(triangle[0][axis]) for axis in range(3))
            first = (relative[axes[0]] * direction2[axes[1]] - relative[axes[1]] * direction2[axes[0]]) / determinant
            second = (direction1[axes[0]] * relative[axes[1]] - direction1[axes[1]] * relative[axes[0]]) / determinant
            first_q, second_q = Fraction(first), Fraction(second)
            index = node_index[tag]
            exact_nodes[index] = tuple(
                triangle[0][axis]
                + first_q * (triangle[1][axis] - triangle[0][axis])
                + second_q * (triangle[2][axis] - triangle[0][axis])
                for axis in range(3)
            )

    for line, (first, second) in line_exact_endpoints.items():
        direction = tuple(float(second[axis] - first[axis]) for axis in range(3))
        denominator = sum(value * value for value in direction)
        tags = gmsh.model.mesh.getNodes(1, line, True, False)[0]
        for raw_tag in tags:
            tag = int(raw_tag)
            raw = raw_node_coordinates[tag]
            parameter = sum(
                (raw[axis] - float(first[axis])) * direction[axis]
                for axis in range(3)
            ) / denominator
            if abs(parameter) < 1e-12:
                parameter_q = Fraction(0)
            elif abs(parameter - 1) < 1e-12:
                parameter_q = Fraction(1)
            else:
                parameter_q = Fraction(parameter)
            index = node_index[tag]
            exact_nodes[index] = tuple(
                first[axis] + parameter_q * (second[axis] - first[axis])
                for axis in range(3)
            )

    tetrahedra = [
        [node_index[tag] for tag in row]
        for row in element_rows(gmsh, 3, volume, 4)
    ]
    verifier = load_frame_verifier()
    determinants = [
        verifier.determinant6([exact_nodes[index] for index in tetrahedron])
        for tetrahedron in tetrahedra
    ]
    signs = {1 if value > 0 else -1 if value < 0 else 0 for value in determinants}
    if signs not in ({1}, {-1}):
        raise RuntimeError("Gmsh tetrahedra are degenerate or inconsistently oriented over Q")
    volume_value = sum(abs(value) for value in determinants) / 6

    sphere_bounds = {
        sphere["name"]: (
            tuple(float(Fraction(value)) for value in sphere["box_lower"]),
            tuple(float(Fraction(value)) for value in sphere["box_upper"]),
        )
        for sphere in source["insertion_spheres"]
    }
    boundary_name = {
        "Y_minus": "y_left",
        "Y_plus": "y_right",
        "Z_minus": "z_left",
        "Z_plus": "z_right",
    }
    named_boundaries = {name: [] for name in ["outer", *boundary_name.values()]}
    for surface in boundary_surfaces:
        bounds = gmsh.model.getBoundingBox(2, surface)
        candidates = [
            name
            for name, (lower, upper) in sphere_bounds.items()
            if all(bounds[axis] >= lower[axis] - 1e-6 for axis in range(3))
            and all(bounds[axis + 3] <= upper[axis] + 1e-6 for axis in range(3))
        ]
        if len(candidates) > 1:
            raise RuntimeError("a Gmsh boundary surface belongs to two insertion boxes")
        name = boundary_name[candidates[0]] if candidates else "outer"
        named_boundaries[name].extend(
            [node_index[tag] for tag in row]
            for row in element_rows(gmsh, 2, surface, 3)
        )
    if any(not triangles for triangles in named_boundaries.values()):
        raise RuntimeError("Gmsh mesh lost a named boundary surface")

    arcs, ribbons, bindings = [], [], []
    side_index = Counter()
    for item in route_entities:
        route = item["route"]
        arc_name = f"source_arc:{route['route_index']}"
        core = ordered_curve_path(
            gmsh,
            item["core_lines"],
            node_index,
            exact_nodes,
            route["vertices"][0],
        )
        push = ordered_curve_path(
            gmsh,
            item["push_lines"],
            node_index,
            exact_nodes,
            route["positive_push_off_vertices"][0],
        )
        connectors = [
            ordered_curve_path(
                gmsh,
                [tag],
                node_index,
                exact_nodes,
                start,
            )
            for tag, start in zip(
                item["connectors"],
                (route["vertices"][0], route["vertices"][-1]),
            )
        ]
        triangles = []
        for surface in item["surfaces"]:
            triangles.extend(
                [node_index[tag] for tag in row]
                for row in element_rows(gmsh, 2, surface, 3)
            )
        side = {"negative": "left", "positive": "right"}[route["copy_sign"]]
        index = side_index[side]
        side_index[side] += 1
        endpoint_sphere = {
            endpoint["endpoint_id"]: sphere["name"]
            for sphere in source["insertion_spheres"]
            for endpoint in sphere["endpoints"]
        }
        arcs.append(
            {
                "name": arc_name,
                "edge_path": core,
                "start_boundary": boundary_name[endpoint_sphere[route["from_endpoint_id"]]],
                "end_boundary": boundary_name[endpoint_sphere[route["to_endpoint_id"]]],
                "owner": route["owner"],
                "closure_side": side,
                "endpoint_index": index,
                "source_id": f"{route['from_source_id']}->{route['to_source_id']}",
            }
        )
        ribbons.append(
            {
                "name": f"ribbon:{arc_name}",
                "core_arc": arc_name,
                "push_off_path": push,
                "start_connector_path": connectors[0],
                "end_connector_path": connectors[1],
                "triangles": triangles,
            }
        )
        bindings.append(
            {
                "source_interval_id": route["interval_id"],
                "arc_name": arc_name,
                "endpoint_ids": [route["from_endpoint_id"], route["to_endpoint_id"]],
                "endpoint_vertices": [core[0], core[-1]],
            }
        )
    frame = {
        "complex": {
            "vertices": [encoded(value) for value in exact_nodes],
            "tetrahedra": tetrahedra,
        },
        "boundary_components": named_boundaries,
        "arcs": arcs,
        "ribbons": ribbons,
    }
    payload = {
        "schema": "t73_selected_source_tetrahedral_frame/v1",
        "source_exterior_sha256": source["sha256"],
        "scope": f"prefix:{len(route_entities)}",
        "actual_ar_relative_isotopy_proved": False,
        "gmsh": {"version": gmsh.option.getString("General.Version"), "algorithm_3d": algorithm},
        "frame": frame,
        "initial_source_binding": bindings,
        "verification": {
            "verdict": "PASS",
            "vertices": len(exact_nodes),
            "tetrahedra": len(tetrahedra),
            "boundary_components": 5,
            "arcs": len(arcs),
            "ribbons": len(ribbons),
            "exact_exterior_volume": str(volume_value),
        },
    }
    payload["sha256"] = canonical_sha(payload)
    if perform_independent_verify:
        checked = verifier.verify(payload, source)
        if checked["verdict"] != "PASS_PREFIX_ONLY":
            raise RuntimeError("independent verifier did not accept Gmsh prefix")
    return payload


def run(
    limit: int,
    algorithm: int = 10,
    include_frame: bool = False,
    perform_independent_verify: bool = True,
) -> dict:
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
        line_exact_endpoints = {}
        surface_exact_triangles = {}
        ribbon_surfaces = []
        ribbon_curves = set()
        route_entities = []

        def add_point(raw):
            coordinate = point(raw)
            if coordinate not in points:
                points[coordinate] = occ.addPoint(*coordinate, 1.0)
            return points[coordinate]

        def add_line(first, second):
            first_exact = tuple(Fraction(value) for value in first)
            second_exact = tuple(Fraction(value) for value in second)
            first_coordinate, second_coordinate = point(first), point(second)
            first_tag, second_tag = add_point(first), add_point(second)
            key = tuple(sorted((first_tag, second_tag)))
            if key not in lines:
                lines[key] = occ.addLine(first_tag, second_tag)
                line_endpoints[lines[key]] = (
                    first_coordinate,
                    second_coordinate,
                )
                line_exact_endpoints[lines[key]] = (first_exact, second_exact)
            tag = lines[key]
            return tag if (first_tag, second_tag) == key else -tag

        connector_tags = []
        for route in routes:
            surfaces_for_route = []
            for triangle in route["ruled_ribbon_triangles"]:
                edges = [
                    add_line(triangle[index], triangle[(index + 1) % 3])
                    for index in range(3)
                ]
                loop = occ.addCurveLoop(edges)
                surface = occ.addPlaneSurface([loop])
                surface_exact_triangles[surface] = tuple(
                    tuple(Fraction(value) for value in vertex)
                    for vertex in triangle
                )
                ribbon_surfaces.append(surface)
                surfaces_for_route.append(surface)
                ribbon_curves.update(abs(edge) for edge in edges)
            core_lines = [
                abs(add_line(route["vertices"][index], route["vertices"][index + 1]))
                for index in range(2)
            ]
            push_lines = [
                abs(
                    add_line(
                        route["positive_push_off_vertices"][index],
                        route["positive_push_off_vertices"][index + 1],
                    )
                )
                for index in range(2)
            ]
            connectors_for_route = []
            for key in ("initial_transverse_edge", "terminal_transverse_edge"):
                connector = abs(add_line(*route["ruled_ribbon_boundary"][key]))
                connector_tags.append(connector)
                connectors_for_route.append(connector)
            route_entities.append(
                {
                    "route": route,
                    "surfaces": surfaces_for_route,
                    "core_lines": core_lines,
                    "push_lines": push_lines,
                    "connectors": connectors_for_route,
                }
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
        if include_frame:
            result["frame_payload"] = extract_frame(
                gmsh,
                source,
                route_entities,
                boundary_surfaces,
                volume,
                algorithm,
                line_exact_endpoints,
                surface_exact_triangles,
                perform_independent_verify,
            )
        return result
    finally:
        gmsh.finalize()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--algorithm", type=int, default=10)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--frame-output", type=Path)
    parser.add_argument("--defer-independent-verify", action="store_true")
    args = parser.parse_args()
    result = run(
        args.limit,
        args.algorithm,
        include_frame=args.frame_output is not None,
        perform_independent_verify=not args.defer_independent_verify,
    )
    frame_payload = result.pop("frame_payload", None)
    if args.frame_output:
        args.frame_output.write_text(
            json.dumps(frame_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.output:
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
