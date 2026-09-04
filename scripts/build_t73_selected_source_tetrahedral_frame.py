#!/usr/bin/env python3
"""Tetrahedralise the saved selected-source coefficient exterior.

This is deliberately a *source-frame* constructor, not an ambient-isotopy
constructor.  It turns every saved centreline and positive push-off into edge
constraints and every ruled framing strip into four triangular PLC facets.
TetGen is then required to recover those constraints without subdividing them.
The resulting JSON is accepted only after the repository's independent
five-boundary-component/frame verifier has replayed the full complex.

The optional packages are intentionally not repository dependencies.  Run in
the audited topology-tools environment, for example

  /tmp/t73-topology-tools/bin/python \
      scripts/build_t73_selected_source_tetrahedral_frame.py --limit 1

Remove ``--limit`` and add ``--write`` only for the complete 630-ribbon frame.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "geometry" / "t73_selected_source_exterior.json"
OUTPUT = ROOT / "geometry" / "t73_selected_source_tetrahedral_frame.json"


class MeshError(ValueError):
    """A fail-closed PLC construction or tetrahedralisation error."""


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def qpoint(raw: Iterable[Any]) -> tuple[Fraction, Fraction, Fraction]:
    point = tuple(Fraction(value) for value in raw)
    if len(point) != 3:
        raise MeshError("a point does not have three rational coordinates")
    return point  # type: ignore[return-value]


def encode(point: Iterable[Fraction]) -> list[str]:
    return [str(Fraction(value)) for value in point]


def simplex_faces(simplex: Iterable[int]) -> list[tuple[int, ...]]:
    values = tuple(simplex)
    return [tuple(sorted(values[:index] + values[index + 1 :])) for index in range(len(values))]


class Plc:
    """An exact-rational vertex registry plus triangular PLC facets."""

    def __init__(self) -> None:
        self.vertices: list[tuple[Fraction, Fraction, Fraction]] = []
        self.vertex_index: dict[tuple[Fraction, Fraction, Fraction], int] = {}
        self.facets: list[tuple[int, int, int]] = []
        self.boundary_facets: dict[str, list[tuple[int, int, int]]] = defaultdict(list)
        self.ribbon_facets: dict[str, list[tuple[int, int, int]]] = defaultdict(list)

    def vertex(self, point: Iterable[Any]) -> int:
        exact = qpoint(point)
        if exact not in self.vertex_index:
            self.vertex_index[exact] = len(self.vertices)
            self.vertices.append(exact)
        return self.vertex_index[exact]

    def triangle(self, points: Iterable[Iterable[Any]], *, boundary: str | None = None,
                 ribbon: str | None = None) -> tuple[int, int, int]:
        triangle = tuple(self.vertex(point) for point in points)
        if len(triangle) != 3 or len(set(triangle)) != 3:
            raise MeshError("a PLC triangle is degenerate at the vertex level")
        self.facets.append(triangle)  # orientation is immaterial to TetGen
        if boundary is not None:
            self.boundary_facets[boundary].append(triangle)
        if ribbon is not None:
            self.ribbon_facets[ribbon].append(triangle)
        return triangle


def rectangle_point(axis: int, value: Fraction, lower, upper, uv) -> tuple[Fraction, Fraction, Fraction]:
    free = [coordinate for coordinate in range(3) if coordinate != axis]
    point = [Fraction(0), Fraction(0), Fraction(0)]
    point[axis] = value
    point[free[0]], point[free[1]] = uv
    return tuple(point)  # type: ignore[return-value]


def triangulate_rectangle(
    plc: Plc,
    *,
    axis: int,
    value: Fraction,
    lower: tuple[Fraction, Fraction, Fraction],
    upper: tuple[Fraction, Fraction, Fraction],
    boundary_name: str,
    constrained_pairs: list[
        tuple[tuple[Fraction, Fraction, Fraction], tuple[Fraction, Fraction, Fraction]]
    ] | None = None,
) -> None:
    """Triangulate one box face, retaining each ribbon attachment as an edge."""

    try:
        triangle_module = importlib.import_module("triangle")
        numpy = importlib.import_module("numpy")
    except ImportError as error:  # pragma: no cover - optional executable path
        raise MeshError("install the optional 'numpy' and 'triangle' packages") from error

    free = [coordinate for coordinate in range(3) if coordinate != axis]
    corners_uv = [
        (lower[free[0]], lower[free[1]]),
        (upper[free[0]], lower[free[1]]),
        (upper[free[0]], upper[free[1]]),
        (lower[free[0]], upper[free[1]]),
    ]
    points = [rectangle_point(axis, value, lower, upper, uv) for uv in corners_uv]
    segments: list[tuple[int, int]] = [(0, 1), (1, 2), (2, 3), (3, 0)]
    for core, push in constrained_pairs or []:
        for point in (core, push):
            if point[axis] != value:
                raise MeshError("a ribbon attachment is not on its designated face")
            if any(point[item] < lower[item] or point[item] > upper[item] for item in free):
                raise MeshError("a ribbon attachment lies outside its designated face")
        start = len(points)
        points.extend((core, push))
        segments.append((start, start + 1))

    planar = numpy.asarray(
        [[float(point[free[0]]), float(point[free[1]])] for point in points],
        dtype=float,
    )
    result = triangle_module.triangulate(
        {"vertices": planar, "segments": numpy.asarray(segments, dtype=numpy.int32)},
        "pQ",
    )
    if "triangles" not in result:
        raise MeshError(f"Triangle did not triangulate boundary face {boundary_name}")
    output_points = [
        rectangle_point(
            axis,
            value,
            lower,
            upper,
            (Fraction(float(uv[0])), Fraction(float(uv[1]))),
        )
        for uv in result["vertices"]
    ]
    # No Steiner points were requested.  Recover the exact input rationals
    # rather than serialising their binary floating-point approximations.
    float_to_exact = {
        (float(point[free[0]]), float(point[free[1]])): point for point in points
    }
    recovered = []
    for point, uv in zip(output_points, result["vertices"]):
        key = (float(uv[0]), float(uv[1]))
        if key not in float_to_exact:
            raise MeshError(f"Triangle inserted an untracked point on {boundary_name}")
        recovered.append(float_to_exact[key])
    for raw_triangle in result["triangles"]:
        plc.triangle(
            [recovered[int(vertex)] for vertex in raw_triangle], boundary=boundary_name
        )

    present_edges = {
        edge
        for raw_triangle in result["triangles"]
        for edge in simplex_faces(tuple(int(vertex) for vertex in raw_triangle))
    }
    for segment in segments:
        if tuple(sorted(segment)) not in present_edges:
            raise MeshError(f"Triangle lost a required attachment segment on {boundary_name}")


def build_plc(source: dict[str, Any], limit: int | None = None) -> tuple[Plc, list[dict[str, Any]]]:
    routes = source["exterior_intervals"]
    if limit is not None:
        if limit < 1 or limit > len(routes):
            raise MeshError("--limit must lie between 1 and the saved route count")
        routes = routes[:limit]

    plc = Plc()
    outer = source["ambient"]["outer_ball"]
    outer_lower, outer_upper = qpoint(outer["lower"]), qpoint(outer["upper"])
    for axis in range(3):
        for value in (outer_lower[axis], outer_upper[axis]):
            triangulate_rectangle(
                plc,
                axis=axis,
                value=value,
                lower=outer_lower,
                upper=outer_upper,
                boundary_name="outer",
            )

    endpoint_data = {
        endpoint["endpoint_id"]: (
            sphere["name"],
            qpoint(endpoint["point"]),
            qpoint(endpoint["positive_push_off_point"]),
        )
        for sphere in source["insertion_spheres"]
        for endpoint in sphere["endpoints"]
    }
    attachments: dict[
        str,
        list[tuple[tuple[Fraction, Fraction, Fraction], tuple[Fraction, Fraction, Fraction]]],
    ] = defaultdict(list)
    used_endpoint_ids: set[str] = set()
    for route in routes:
        for endpoint_id in (route["from_endpoint_id"], route["to_endpoint_id"]):
            if endpoint_id in used_endpoint_ids:
                raise MeshError("selected source routes reuse an endpoint")
            used_endpoint_ids.add(endpoint_id)
            sphere_name, core, push = endpoint_data[endpoint_id]
            attachments[sphere_name].append((core, push))

    boundary_name = {
        "Y_minus": "y_left",
        "Y_plus": "y_right",
        "Z_minus": "z_left",
        "Z_plus": "z_right",
    }
    for sphere in source["insertion_spheres"]:
        name = sphere["name"]
        lower, upper = qpoint(sphere["box_lower"]), qpoint(sphere["box_upper"])
        designated_axis = {"x": 0, "y": 1, "z": 2}[sphere["designated_face_axis"]]
        designated_value = Fraction(sphere["designated_face_value"])
        for axis in range(3):
            for value in (lower[axis], upper[axis]):
                pairs = (
                    attachments[name]
                    if axis == designated_axis and value == designated_value
                    else None
                )
                triangulate_rectangle(
                    plc,
                    axis=axis,
                    value=value,
                    lower=lower,
                    upper=upper,
                    boundary_name=boundary_name[name],
                    constrained_pairs=pairs,
                )

    enriched_routes = []
    endpoint_index = Counter()
    for route in routes:
        name = f"source_arc:{route['route_index']}"
        core = [qpoint(point) for point in route["vertices"]]
        push = [qpoint(point) for point in route["positive_push_off_vertices"]]
        if len(core) != 3 or len(push) != 3:
            raise MeshError("v1 expects three-vertex core and push-off polylines")
        saved_ribbon_triangles = route.get("ruled_ribbon_triangles")
        if not isinstance(saved_ribbon_triangles, list) or len(saved_ribbon_triangles) != 4:
            raise MeshError(f"{name} does not save exactly four ruled-ribbon triangles")
        ribbon_triangles = [
            plc.triangle(
                [qpoint(point) for point in triangle],
                ribbon=name,
            )
            for triangle in saved_ribbon_triangles
        ]
        if {
            plc.vertices[vertex] for triangle in ribbon_triangles for vertex in triangle
        } != set(core + push):
            raise MeshError(f"saved ruled-ribbon facets have the wrong vertices for {name}")
        side = {"negative": "left", "positive": "right"}[route["copy_sign"]]
        index_on_side = endpoint_index[side]
        endpoint_index[side] += 1
        enriched_routes.append(
            {
                "name": name,
                "source_interval_id": route["interval_id"],
                "endpoint_ids": [route["from_endpoint_id"], route["to_endpoint_id"]],
                "core_input_path": [plc.vertex(point) for point in core],
                "push_input_path": [plc.vertex(point) for point in push],
                "ribbon_input_triangles": ribbon_triangles,
                "start_sphere": endpoint_data[route["from_endpoint_id"]][0],
                "end_sphere": endpoint_data[route["to_endpoint_id"]][0],
                "owner": route["owner"],
                "closure_side": side,
                "endpoint_index": index_on_side,
                "source_id": f"{route['from_source_id']}->{route['to_source_id']}",
            }
        )
    return plc, enriched_routes


def determinant6(points: list[tuple[Fraction, Fraction, Fraction]]) -> Fraction:
    base = points[0]
    columns = [tuple(points[index][axis] - base[axis] for axis in range(3)) for index in (1, 2, 3)]
    return (
        columns[0][0] * (columns[1][1] * columns[2][2] - columns[1][2] * columns[2][1])
        - columns[1][0] * (columns[0][1] * columns[2][2] - columns[0][2] * columns[2][1])
        + columns[2][0] * (columns[0][1] * columns[1][2] - columns[0][2] * columns[1][1])
    )


def nearest_grid(value: Fraction, step: Fraction) -> Fraction:
    """Round a rational to the nearest multiple of a positive dyadic step."""
    scaled = value / step
    quotient, remainder = divmod(scaled.numerator, scaled.denominator)
    if 2 * remainder >= scaled.denominator:
        quotient += 1
    return quotient * step


def dyadic_mesh_embedding(
    plc: Plc, routes: list[dict[str, Any]], source: dict[str, Any]
) -> tuple[list[tuple[Fraction, Fraction, Fraction]], dict[str, str]]:
    """Make exact source translation relations representable in binary64.

    Directly converting ``p`` and ``p+n`` to floats rounds the two values
    independently.  TetGen can then see two mathematically parallel translated
    edges as a non-coplanar quadruple and create a tetrahedron that is exactly
    flat when the authoritative rationals are restored.  A common dyadic grid
    preserves all repeated normal translations before TetGen is called.
    """

    normal_unit = Fraction(1, 2**20)
    source_normal = qpoint(source["normal"])
    nonzero_units = {abs(value) for value in source_normal if value != 0}
    if len(nonzero_units) != 1:
        raise MeshError("source normal does not define one rational base unit")
    source_unit = nonzero_units.pop()
    embedded = [
        tuple(Fraction.from_float(float(value)) for value in point)
        for point in plc.vertices
    ]
    assigned_pushes: dict[int, tuple[Fraction, Fraction, Fraction]] = {}
    for route in routes:
        for core_index, push_index in zip(
            route["core_input_path"], route["push_input_path"]
        ):
            difference = tuple(
                plc.vertices[push_index][axis] - plc.vertices[core_index][axis]
                for axis in range(3)
            )
            coefficients = []
            for value in difference:
                coefficient = value / source_unit
                if coefficient.denominator != 1:
                    raise MeshError("a framing normal is not integral in the saved normal unit")
                coefficients.append(coefficient.numerator)
            candidate = tuple(
                embedded[core_index][axis] + coefficients[axis] * normal_unit
                for axis in range(3)
            )
            previous = assigned_pushes.get(push_index)
            if previous is not None and previous != candidate:
                raise MeshError("one push-off vertex receives inconsistent dyadic embeddings")
            assigned_pushes[push_index] = candidate
            embedded[push_index] = candidate
    if len(set(embedded)) != len(embedded):
        raise MeshError("dyadic TetGen embedding collapses distinct PLC vertices")
    return embedded, {
        "mode": "common_dyadic_grid_with_exact_repeated_normal_translations",
        "core_coordinate_rule": "nearest_binary64_then_exact_dyadic_value",
        "normal_unit": str(normal_unit),
        "authoritative_coordinates_restored_after_meshing": True,
    }


def facet_edge_chains(
    subfaces: list[tuple[int, int, int]],
    corners: tuple[int, int, int],
) -> dict[tuple[int, int], list[int]]:
    """Recover the three subdivided boundary chains of one input triangle."""

    counts = Counter(edge for triangle in subfaces for edge in simplex_faces(triangle))
    boundary_edges = {edge for edge, count in counts.items() if count == 1}
    adjacency: dict[int, set[int]] = defaultdict(set)
    for first, second in boundary_edges:
        adjacency[first].add(second)
        adjacency[second].add(first)
    if not adjacency or set(len(neighbours) for neighbours in adjacency.values()) != {2}:
        raise MeshError("a marked TetGen facet is not a subdivided triangular disk")

    result: dict[tuple[int, int], list[int]] = {}
    for start, end, excluded in (
        (corners[0], corners[1], corners[2]),
        (corners[1], corners[2], corners[0]),
        (corners[2], corners[0], corners[1]),
    ):
        if start not in adjacency or end not in adjacency or excluded not in adjacency:
            raise MeshError("a marked TetGen facet lost an input corner")
        queue = [start]
        parent: dict[int, int | None] = {start: None}
        while queue and end not in parent:
            current = queue.pop(0)
            for neighbour in adjacency[current]:
                if neighbour == excluded or neighbour in parent:
                    continue
                parent[neighbour] = current
                queue.append(neighbour)
        if end not in parent:
            raise MeshError("cannot recover an input-facet boundary edge chain")
        path = []
        current: int | None = end
        while current is not None:
            path.append(current)
            current = parent[current]
        path.reverse()
        result[(start, end)] = path
        result[(end, start)] = list(reversed(path))
    return result


def affine_edge_point(
    raw_point: tuple[Fraction, Fraction, Fraction],
    mesh_start: tuple[Fraction, Fraction, Fraction],
    mesh_end: tuple[Fraction, Fraction, Fraction],
    exact_start: tuple[Fraction, Fraction, Fraction],
    exact_end: tuple[Fraction, Fraction, Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    axis = max(range(3), key=lambda item: abs(mesh_end[item] - mesh_start[item]))
    denominator = mesh_end[axis] - mesh_start[axis]
    if denominator == 0:
        raise MeshError("cannot parameterise a zero-length input edge")
    parameter = (raw_point[axis] - mesh_start[axis]) / denominator
    tolerance = Fraction(1, 10**8)
    if not -tolerance <= parameter <= 1 + tolerance:
        raise MeshError("a TetGen edge subdivision point lies outside its input edge")
    parameter = min(Fraction(1), max(Fraction(0), parameter))
    return tuple(
        exact_start[item] + parameter * (exact_end[item] - exact_start[item])
        for item in range(3)
    )  # type: ignore[return-value]


def affine_triangle_point(
    raw_point: tuple[Fraction, Fraction, Fraction],
    mesh_triangle: list[tuple[Fraction, Fraction, Fraction]],
    exact_triangle: list[tuple[Fraction, Fraction, Fraction]],
) -> tuple[Fraction, Fraction, Fraction]:
    first, second, third = mesh_triangle
    first_edge = tuple(second[item] - first[item] for item in range(3))
    second_edge = tuple(third[item] - first[item] for item in range(3))
    offset = tuple(raw_point[item] - first[item] for item in range(3))
    choices = []
    for one, two in ((0, 1), (0, 2), (1, 2)):
        determinant = first_edge[one] * second_edge[two] - first_edge[two] * second_edge[one]
        choices.append((abs(determinant), determinant, one, two))
    _size, determinant, one, two = max(choices)
    if determinant == 0:
        raise MeshError("an input PLC facet is exactly degenerate in the meshing embedding")
    first_weight = (offset[one] * second_edge[two] - offset[two] * second_edge[one]) / determinant
    second_weight = (first_edge[one] * offset[two] - first_edge[two] * offset[one]) / determinant
    tolerance = Fraction(1, 10**8)
    if (
        first_weight < -tolerance
        or second_weight < -tolerance
        or first_weight + second_weight > 1 + tolerance
    ):
        raise MeshError("a TetGen facet point lies outside its marked input triangle")
    # Clamp only binary64 noise at a boundary.  True boundary nodes have
    # already been assigned from their exact edge chain.
    first_weight = min(Fraction(1), max(Fraction(0), first_weight))
    second_weight = min(Fraction(1) - first_weight, max(Fraction(0), second_weight))
    return tuple(
        exact_triangle[0][item]
        + first_weight * (exact_triangle[1][item] - exact_triangle[0][item])
        + second_weight * (exact_triangle[2][item] - exact_triangle[0][item])
        for item in range(3)
    )  # type: ignore[return-value]


def tetrahedralise(
    source: dict[str, Any], *, limit: int | None = None, allow_large: bool = False
) -> dict[str, Any]:
    requested = 630 if limit is None else limit
    if requested > 10 and not allow_large:
        raise MeshError(
            "monolithic TetGen runs above 10 ribbons are resource-disabled: "
            "prefix 20 exceeded 14.6 GB RSS and prefix 50 exceeded six minutes; "
            "use a partitioned/glued constructor, or pass allow_large only for an audited resource probe"
        )
    try:
        numpy = importlib.import_module("numpy")
        tetgen = importlib.import_module("tetgen")
    except ImportError as error:  # pragma: no cover - optional executable path
        raise MeshError("install the optional 'numpy' and 'tetgen' packages") from error

    plc, routes = build_plc(source, limit)
    mesh_embedding, mesh_embedding_metadata = dyadic_mesh_embedding(plc, routes, source)
    points = numpy.asarray([[float(value) for value in point] for point in mesh_embedding])
    facets = numpy.asarray(plc.facets, dtype=numpy.int32)
    facet_markers = numpy.arange(1, len(plc.facets) + 1, dtype=numpy.int32)
    generator = tetgen.TetGen(points, facets, facet_markers)
    for sphere in source["insertion_spheres"]:
        lower, upper = qpoint(sphere["box_lower"]), qpoint(sphere["box_upper"])
        generator.add_hole([float((lower[axis] + upper[axis]) / 2) for axis in range(3)])
    nodes, tetrahedra, _attributes, output_face_markers = generator.tetrahedralize(
        plc=True,
        quality=False,
        nobisect=False,
        nomergevertex=True,
        nomergefacet=True,
        noexact=False,
        # The ribbon aspect ratio is intentionally extreme.  All input
        # coordinates are dyadic and TetGen's exact predicates remain enabled;
        # a loose geometric epsilon would nevertheless misclassify a narrow
        # attachment triangle as a pair of crossing collinear segments.
        epsilon=1e-20,
        facet_separate_ang_tol=180.0,
        collinear_ang_tol=180.0,
        facet_small_ang_tol=0.0,
        facesout=True,
        edgesout=True,
        quiet=True,
    )
    float_input = {tuple(float(value) for value in point): index for index, point in enumerate(mesh_embedding)}
    if len(float_input) != len(mesh_embedding):
        raise MeshError("two exact PLC vertices collapse to one binary64 coordinate")
    output_to_input: list[int | None] = []
    exact_nodes: list[tuple[Fraction, Fraction, Fraction]] = []
    for node in nodes:
        key = tuple(float(value) for value in node)
        input_index = float_input.get(key)
        output_to_input.append(input_index)
        if input_index is None:
            # TetGen may add mandatory *interior* Steiner points even under
            # nobisect.  A binary64 is an exact dyadic rational, so retain its
            # mathematical value rather than a rounded decimal surrogate.
            exact_nodes.append(tuple(Fraction.from_float(value) for value in key))
        else:
            # Restore the authoritative source rational at every input PLC
            # vertex; the exact determinant/volume checks below detect any
            # connectivity invalidated by this restoration.
            exact_nodes.append(plc.vertices[input_index])
    recovered_inputs = [value for value in output_to_input if value is not None]
    if len(recovered_inputs) != len(plc.vertices) or len(set(recovered_inputs)) != len(plc.vertices):
        raise MeshError("TetGen did not retain every input PLC vertex exactly once")
    input_to_output = {
        input_index: output
        for output, input_index in enumerate(output_to_input)
        if input_index is not None
    }

    # A PLC segment/facet can acquire mandatory Steiner vertices even under
    # -Y.  Unique input markers let us recover the exact subdivision of every
    # saved triangle instead of pretending the original three edges survived.
    marked_subfaces: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for triangle, marker in zip(generator.trifaces, output_face_markers):
        marker = int(marker)
        if marker == 0:
            continue
        if marker < 1 or marker > len(plc.facets):
            raise MeshError(f"TetGen emitted unknown PLC facet marker {marker}")
        marked_subfaces[marker - 1].append(tuple(int(vertex) for vertex in triangle))
    if set(marked_subfaces) != set(range(len(plc.facets))):
        raise MeshError("TetGen did not recover every uniquely marked PLC facet")

    facet_chains: dict[int, dict[tuple[int, int], list[int]]] = {}
    input_edge_candidates: dict[tuple[int, int], list[list[int]]] = defaultdict(list)
    for facet_index, input_triangle in enumerate(plc.facets):
        output_corners = tuple(input_to_output[vertex] for vertex in input_triangle)
        chains = facet_edge_chains(marked_subfaces[facet_index], output_corners)
        facet_chains[facet_index] = chains
        for first, second in simplex_faces(input_triangle):
            output_first, output_second = input_to_output[first], input_to_output[second]
            input_edge_candidates[(first, second)].append(chains[(output_first, output_second)])

    input_edge_chains: dict[tuple[int, int], list[int]] = {}
    for input_edge, candidates in input_edge_candidates.items():
        canonical = candidates[0]
        if any(candidate != canonical for candidate in candidates[1:]):
            raise MeshError("adjacent marked facets disagree on a shared edge subdivision")
        input_edge_chains[input_edge] = canonical
        input_edge_chains[(input_edge[1], input_edge[0])] = list(reversed(canonical))

    raw_output_points = [tuple(Fraction.from_float(float(value)) for value in node) for node in nodes]
    assigned_exact = {
        output: plc.vertices[input_index]
        for input_index, output in input_to_output.items()
    }

    def assign_exact(vertex: int, value, where: str) -> None:
        previous = assigned_exact.get(vertex)
        if previous is not None and previous != value:
            raise MeshError(f"inconsistent rational restoration at {where} vertex {vertex}")
        assigned_exact[vertex] = value

    # First restore every marked-facet boundary chain.  This guarantees that
    # core/push paths reduce exactly to the saved rational polylines.
    for (first, second), chain in input_edge_chains.items():
        if first > second:
            continue
        mesh_first, mesh_second = mesh_embedding[first], mesh_embedding[second]
        exact_first, exact_second = plc.vertices[first], plc.vertices[second]
        for vertex in chain:
            assign_exact(
                vertex,
                affine_edge_point(
                    raw_output_points[vertex],
                    mesh_first,
                    mesh_second,
                    exact_first,
                    exact_second,
                ),
                f"input edge {first}-{second}",
            )

    # Then restore any Steiner vertex in a facet interior by the affine map
    # from its dyadic input triangle to the authoritative rational triangle.
    for facet_index, subfaces in marked_subfaces.items():
        input_triangle = plc.facets[facet_index]
        mesh_triangle = [mesh_embedding[vertex] for vertex in input_triangle]
        exact_triangle = [plc.vertices[vertex] for vertex in input_triangle]
        for vertex in {item for triangle in subfaces for item in triangle}:
            if vertex in assigned_exact:
                continue
            assign_exact(
                vertex,
                affine_triangle_point(
                    raw_output_points[vertex], mesh_triangle, exact_triangle
                ),
                f"input facet {facet_index}",
            )
    exact_nodes = [assigned_exact.get(index, raw_output_points[index]) for index in range(len(nodes))]
    tets = [tuple(int(vertex) for vertex in tetrahedron) for tetrahedron in tetrahedra]
    if not tets:
        raise MeshError("TetGen emitted no tetrahedra")
    degenerate = [
        (index, tet)
        for index, tet in enumerate(tets)
        if determinant6([exact_nodes[vertex] for vertex in tet]) == 0
    ]
    if degenerate:
        preview = "; ".join(
            f"{index}:{tet}:{[encode(exact_nodes[vertex]) for vertex in tet]}"
            for index, tet in degenerate[:3]
        )
        raise MeshError(
            f"TetGen emitted {len(degenerate)} exactly degenerate tetrahedra "
            f"(first {preview})"
        )

    face_counts = Counter(face for tet in tets for face in simplex_faces(tet))
    if set(face_counts.values()) - {1, 2}:
        raise MeshError("TetGen output has nonmanifold triangle incidence")
    all_faces = set(face_counts)
    all_edges = {
        tuple(sorted((tet[first], tet[second])))
        for tet in tets
        for first in range(4)
        for second in range(first + 1, 4)
    }
    facet_lookup = {
        tuple(sorted(triangle)): index for index, triangle in enumerate(plc.facets)
    }
    if len(facet_lookup) != len(plc.facets):
        raise MeshError("the input PLC contains duplicate triangular facets")

    def subdivisions(input_triangles: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
        output = []
        for triangle in input_triangles:
            facet_index = facet_lookup.get(tuple(sorted(triangle)))
            if facet_index is None:
                raise MeshError("cannot locate an input triangle's unique facet marker")
            output.extend(marked_subfaces[facet_index])
        return output

    mapped_boundaries = {
        name: subdivisions(triangles)
        for name, triangles in plc.boundary_facets.items()
    }
    claimed_boundary = {
        tuple(sorted(triangle))
        for triangles in mapped_boundaries.values()
        for triangle in triangles
    }
    actual_boundary = {face for face, count in face_counts.items() if count == 1}
    if actual_boundary != claimed_boundary:
        raise MeshError("TetGen boundary is not exactly the five named input surfaces")

    arcs, ribbons, source_bindings = [], [], []
    for route in routes:
        def combined_path(input_path: list[int]) -> list[int]:
            output = []
            for first, second in zip(input_path, input_path[1:]):
                if (first, second) not in input_edge_chains:
                    raise MeshError(f"TetGen lost input edge {first}-{second}")
                chain = input_edge_chains[(first, second)]
                output.extend(chain if not output else chain[1:])
            if len(set(output)) != len(output):
                raise MeshError("a recovered coefficient path is not embedded")
            return output

        core = combined_path(route["core_input_path"])
        push = combined_path(route["push_input_path"])
        start_connector = combined_path(
            [route["core_input_path"][0], route["push_input_path"][0]]
        )
        end_connector = combined_path(
            [route["core_input_path"][-1], route["push_input_path"][-1]]
        )
        triangles = subdivisions(route["ribbon_input_triangles"])
        if any(tuple(sorted(edge)) not in all_edges for edge in zip(core, core[1:])):
            raise MeshError(f"TetGen lost a core subedge of {route['name']}")
        if any(tuple(sorted(edge)) not in all_edges for edge in zip(push, push[1:])):
            raise MeshError(f"TetGen lost a push-off subedge of {route['name']}")
        if any(face_counts.get(tuple(sorted(triangle))) != 2 for triangle in triangles):
            raise MeshError(f"TetGen lost a ribbon triangle of {route['name']}")
        sphere_to_boundary = {
            "Y_minus": "y_left",
            "Y_plus": "y_right",
            "Z_minus": "z_left",
            "Z_plus": "z_right",
        }
        arcs.append(
            {
                "name": route["name"],
                "edge_path": core,
                "start_boundary": sphere_to_boundary[route["start_sphere"]],
                "end_boundary": sphere_to_boundary[route["end_sphere"]],
                "owner": route["owner"],
                "closure_side": route["closure_side"],
                "endpoint_index": route["endpoint_index"],
                "source_id": route["source_id"],
            }
        )
        ribbons.append(
            {
                "name": f"ribbon:{route['name']}",
                "core_arc": route["name"],
                "push_off_path": push,
                "start_connector_path": start_connector,
                "end_connector_path": end_connector,
                "triangles": [list(triangle) for triangle in triangles],
            }
        )
        source_bindings.append(
            {
                "source_interval_id": route["source_interval_id"],
                "arc_name": route["name"],
                "endpoint_ids": route["endpoint_ids"],
                "endpoint_vertices": [core[0], core[-1]],
            }
        )

    frame = {
        "complex": {
            "vertices": [encode(point) for point in exact_nodes],
            "tetrahedra": [list(tet) for tet in tets],
        },
        "boundary_components": {
            name: [list(triangle) for triangle in triangles]
            for name, triangles in mapped_boundaries.items()
        },
        "arcs": arcs,
        "ribbons": ribbons,
    }
    return {
        "schema": "t73_selected_source_tetrahedral_frame/v1",
        "source_exterior_sha256": source["sha256"],
        "scope": "complete" if limit is None else f"prefix:{limit}",
        "actual_ar_relative_isotopy_proved": False,
        "tetgen": {"python_wrapper_version": getattr(tetgen, "__version__", "unknown")},
        "tetgen_input_embedding": mesh_embedding_metadata,
        "plc_counts": {"vertices": len(plc.vertices), "facets": len(plc.facets)},
        "additional_tetgen_vertex_count": len(nodes) - len(plc.vertices),
        "frame": frame,
        "initial_source_binding": source_bindings,
    }


def load_frame_verifier():
    path = ROOT / "scripts" / "verify_t73_coefficient_exterior.py"
    spec = importlib.util.spec_from_file_location("t73_coefficient_exterior", path)
    if spec is None or spec.loader is None:
        raise MeshError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_result(result: dict[str, Any], expected_routes: int) -> dict[str, Any]:
    verifier = load_frame_verifier()
    if expected_routes == 630:
        # This invokes the full repository gate, including the 630 typed arcs,
        # 630 pairwise-disjoint ribbon disks and the exact 88/88/542/542
        # insertion-boundary incidence.
        frame = verifier.validate_frame(result["frame"], expected_components=5)
    else:
        # Prefix mode is only a TetGen smoke test.  The full verifier quite
        # properly rejects it for not having all 630 records, so here we run
        # its ambient-manifold check and rely on tetrahedralise()'s explicit
        # edge/facet recovery checks for the selected prefix.
        complex_data = verifier.validate_manifold_with_boundary(
            result["frame"]["complex"], "prefix frame.complex"
        )
        if len(complex_data["boundary_components"]) != 5:
            raise MeshError("the prefix frame does not have five S2 boundaries")
        frame = {
            "complex": complex_data,
            "boundary_components": result["frame"]["boundary_components"],
            "arcs": {
                item["name"]: item["edge_path"] for item in result["frame"]["arcs"]
            },
            "ribbons": {
                item["name"]: item for item in result["frame"]["ribbons"]
            },
        }
    exact_nodes = [qpoint(point) for point in result["frame"]["complex"]["vertices"]]
    signed_determinants = [
        determinant6([exact_nodes[vertex] for vertex in tet])
        # validate_frame canonicalises each simplex by sorting its vertices,
        # which intentionally forgets orientation.  Use the raw TetGen order
        # for this geometric orientation check.
        for tet in result["frame"]["complex"]["tetrahedra"]
    ]
    signs = {1 if value > 0 else -1 if value < 0 else 0 for value in signed_determinants}
    if signs not in ({1}, {-1}):
        raise MeshError("exact rational tetrahedron orientations are zero or inconsistent")
    absolute_volume6 = sum(abs(value) for value in signed_determinants)
    expected_volume6 = Fraction(6) * (Fraction(40) ** 3 - 4 * Fraction(2) ** 3)
    if absolute_volume6 != expected_volume6:
        raise MeshError(
            f"exact tetrahedron volume {absolute_volume6}/6 does not equal exterior volume "
            f"{expected_volume6}/6"
        )
    if len(result["frame"]["arcs"]) != expected_routes:
        raise MeshError("the frame does not contain the requested route count")
    if expected_routes == 630 and len(result["frame"]["ribbons"]) != 630:
        raise MeshError("the complete frame does not contain 630 ribbons")
    return {
        "verdict": "PASS",
        "vertices": len(exact_nodes),
        "tetrahedra": len(result["frame"]["complex"]["tetrahedra"]),
        "boundary_components": len(frame["boundary_components"]),
        "arcs": len(frame["arcs"]),
        "ribbons": len(frame["ribbons"]),
        "exact_exterior_volume": str(absolute_volume6 / 6),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--unsafe-monolithic", action="store_true")
    args = parser.parse_args()
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    result = tetrahedralise(
        source, limit=args.limit, allow_large=args.unsafe_monolithic
    )
    expected_routes = args.limit if args.limit is not None else 630
    verification = verify_result(result, expected_routes)
    result["verification"] = verification
    result["sha256"] = canonical_sha(result)
    if args.write:
        if args.limit is not None and args.output == OUTPUT:
            raise MeshError("refusing to overwrite the complete-frame path with a prefix probe")
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"WROTE={args.output}")
    print(json.dumps(verification, indent=2, sort_keys=True))
    print(f"SHA256={result['sha256']}")


if __name__ == "__main__":
    main()
