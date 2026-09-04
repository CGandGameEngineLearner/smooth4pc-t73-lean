#!/usr/bin/env python3
"""Shared PL cells for Johnson unit transvections and dual 2-cells.

Each unit alpha is the composition Phi o A_ij of the global affine transvection
A_ij with a relative square-fan isotopy Phi supported on a prism that misses
the protected ball.  Phi is isotopic to the identity, so (Phi o A_ij)_* = A_ij.
Setwise preservation of the dual-block Heegaard pair is checked live and is
not assumed.
"""

from __future__ import annotations

import itertools
from collections import Counter, defaultdict
from fractions import Fraction
from typing import Any, Iterable

PERIOD = 4
AXES = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
PROTECTED_RADIUS = Fraction(1, 196104)
INNER = Fraction(1, 4)
OUTER = Fraction(3, 4)
INSET = Fraction(1, 16)
Vertex = tuple[int, int, int]


def identity3() -> list[list[int]]:
    return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def matvec(matrix: list[list[int]], vector: Iterable[int | Fraction]) -> list[Fraction]:
    vec = [Fraction(value) for value in vector]
    return [sum(Fraction(matrix[i][j]) * vec[j] for j in range(3)) for i in range(3)]


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [[sum(left[i][k] * right[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def det3(matrix: list[list[int | Fraction]]) -> Fraction:
    a = [[Fraction(matrix[i][j]) for j in range(3)] for i in range(3)]
    return (
        a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
    )


def transvection_matrix(source: int, prefix: int, power: int) -> list[list[int]]:
    matrix = identity3()
    matrix[prefix][source] = power
    return matrix


def add(a: Iterable[Fraction], b: Iterable[Fraction]) -> list[Fraction]:
    aa, bb = list(a), list(b)
    return [aa[i] + bb[i] for i in range(3)]


def sub(a: Iterable[Fraction], b: Iterable[Fraction]) -> list[Fraction]:
    aa, bb = list(a), list(b)
    return [aa[i] - bb[i] for i in range(3)]


def scale(coeff: Fraction, vector: Iterable[Fraction]) -> list[Fraction]:
    return [coeff * Fraction(value) for value in vector]


def cross(a: Iterable[int | Fraction], b: Iterable[int | Fraction]) -> list[Fraction]:
    aa = [Fraction(value) for value in a]
    bb = [Fraction(value) for value in b]
    return [
        aa[1] * bb[2] - aa[2] * bb[1],
        aa[2] * bb[0] - aa[0] * bb[2],
        aa[0] * bb[1] - aa[1] * bb[0],
    ]


def inf_norm(vector: Iterable[int | Fraction]) -> Fraction:
    return max(abs(Fraction(value)) for value in vector)


def encode(point: Iterable[Fraction]) -> list[str]:
    return [str(Fraction(value)) for value in point]


def decode(point: Iterable[str | int | float]) -> list[Fraction]:
    return [Fraction(value) for value in point]


def wrap_delta(value: float, period: int = PERIOD) -> float:
    residue = float(value) % period
    if residue > period / 2:
        residue -= period
    return residue


def torus_inf(point: Iterable[Fraction], period: int = PERIOD) -> Fraction:
    best = None
    for lift in itertools.product((-period, 0, period), repeat=3):
        dist = inf_norm(sub(point, lift))
        if best is None or dist < best:
            best = dist
    assert best is not None
    return best


def affine_from_tets(
    source: list[list[Fraction]], image: list[list[Fraction]]
) -> tuple[list[list[Fraction]], list[Fraction], Fraction]:
    """Unique affine map sending source tetrahedron vertices to image vertices."""

    s0, i0 = source[0], image[0]
    s_cols = [[source[j][i] - s0[i] for j in range(1, 4)] for i in range(3)]
    i_cols = [[image[j][i] - i0[i] for j in range(1, 4)] for i in range(3)]
    det_s = det3(s_cols)
    if det_s == 0:
        raise AssertionError("source tetrahedron is degenerate")
    # linear = I_cols * S_cols^{-1}
    inv_s = invert3(s_cols)
    linear = matmul_frac(i_cols, inv_s)
    translation = sub(i0, matvec_frac(linear, s0))
    return linear, translation, det3(linear)


def invert3(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    det = det3(matrix)
    if det == 0:
        raise AssertionError("singular 3x3 matrix")
    a = matrix
    cof = [
        [
            a[1][1] * a[2][2] - a[1][2] * a[2][1],
            -(a[1][0] * a[2][2] - a[1][2] * a[2][0]),
            a[1][0] * a[2][1] - a[1][1] * a[2][0],
        ],
        [
            -(a[0][1] * a[2][2] - a[0][2] * a[2][1]),
            a[0][0] * a[2][2] - a[0][2] * a[2][0],
            -(a[0][0] * a[2][1] - a[0][1] * a[2][0]),
        ],
        [
            a[0][1] * a[1][2] - a[0][2] * a[1][1],
            -(a[0][0] * a[1][2] - a[0][2] * a[1][0]),
            a[0][0] * a[1][1] - a[0][1] * a[1][0],
        ],
    ]
    return [[cof[j][i] / det for j in range(3)] for i in range(3)]


def matmul_frac(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum(left[i][k] * right[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def matvec_frac(matrix: list[list[Fraction]], vector: Iterable[Fraction]) -> list[Fraction]:
    vec = list(vector)
    return [sum(matrix[i][j] * vec[j] for j in range(3)) for i in range(3)]


def apply_affine(
    linear: list[list[Fraction]], translation: list[Fraction], point: Iterable[Fraction]
) -> list[Fraction]:
    return add(matvec_frac(linear, point), translation)


def tet_volume(vertices: list[list[Fraction]]) -> Fraction:
    cols = [[vertices[j][i] - vertices[0][i] for j in range(1, 4)] for i in range(3)]
    return det3(cols) / 6


def barycentric(tet: list[list[Fraction]], point: Iterable[Fraction]) -> list[Fraction] | None:
    if tet_volume(tet) == 0:
        return None
    coeffs = []
    for omitted in range(4):
        replaced = [point if index == omitted else tet[index] for index in range(4)]
        replaced = [list(vertex) for vertex in replaced]
        vol = tet_volume(replaced)
        coeffs.append(vol)
    total = sum(coeffs)
    if total == 0:
        return None
    return [coeff / total for coeff in coeffs]


def point_in_tet(tet: list[list[Fraction]], point: Iterable[Fraction], tol: Fraction = Fraction(1, 10**9)) -> bool:
    coords = barycentric(tet, point)
    if coords is None:
        return False
    return all(coord >= -tol for coord in coords)


def prism_tets(
    bottom: tuple[list[Fraction], list[Fraction], list[Fraction]],
    top: tuple[list[Fraction], list[Fraction], list[Fraction]],
) -> list[list[list[Fraction]]]:
    a, b, c = bottom
    d, e, f = top
    candidates = [
        [a, b, c, d],
        [b, c, d, e],
        [c, d, e, f],
    ]
    # Prefer a partition with strictly positive volumes; fall back to the
    # opposite diagonal split if the first convention inverts.
    if all(tet_volume(tet) > 0 for tet in candidates):
        return candidates
    alt = [
        [a, b, c, f],
        [a, b, e, f],
        [a, d, e, f],
    ]
    if all(tet_volume(tet) > 0 for tet in alt):
        return alt
    oriented = []
    for tet in candidates:
        if tet_volume(tet) < 0:
            tet = [tet[0], tet[2], tet[1], tet[3]]
        if tet_volume(tet) <= 0:
            raise AssertionError("could not orient prism tetrahedron")
        oriented.append(tet)
    return oriented


def _orient_tet(vertices: list[list[Fraction]]) -> list[list[Fraction]]:
    if tet_volume(vertices) < 0:
        return [vertices[0], vertices[2], vertices[1], vertices[3]]
    if tet_volume(vertices) <= 0:
        raise AssertionError("straightening tetrahedron is degenerate")
    return vertices


def square_fan_cells(
    target: list[int],
    prefix: list[int],
    side: str,
) -> dict[str, Any]:
    """PL homeomorphism of a prism, identity on the entire boundary.

    The inner parallelogram is a cube in (a, b, normal) coordinates.  The unique
    interior vertex is the center; it is sent toward the bent-path midpoint and
    every boundary vertex stays.  Affine extension on the six face-pyramids is
    therefore a homeomorphism of the prism that glues by the identity to the
    complementary transvection.
    """

    tvec = [Fraction(value) for value in target]
    pvec = [Fraction(value) for value in prefix]
    normal = cross(tvec, pvec)
    if normal == [0, 0, 0]:
        raise AssertionError("degenerate Johnson square")
    denom = 10000 * inf_norm(normal)
    offset = scale(Fraction(1, denom), normal)
    sw = add(scale(INNER, tvec), scale(INNER, pvec))
    se = add(scale(OUTER, tvec), scale(INNER, pvec))
    ne = add(scale(OUTER, tvec), scale(OUTER, pvec))
    nw = add(scale(INNER, tvec), scale(OUTER, pvec))
    center = add(scale(Fraction(1, 2), tvec), scale(Fraction(1, 2), pvec))
    if side == "prefix-first":
        moved = add(scale(INNER + INSET, tvec), scale(OUTER - INSET, pvec))
    elif side == "target-first":
        moved = add(scale(OUTER - INSET, tvec), scale(INNER + INSET, pvec))
    else:
        raise AssertionError(f"unknown Johnson side {side}")
    bottom = [sub(vertex, offset) for vertex in (sw, se, ne, nw)]
    top = [add(vertex, offset) for vertex in (sw, se, ne, nw)]
    faces = [
        (bottom[0], bottom[1], bottom[2], bottom[3]),
        (top[0], top[3], top[2], top[1]),
        (bottom[0], bottom[3], top[3], top[0]),
        (bottom[1], bottom[0], top[0], top[1]),
        (bottom[2], bottom[1], top[1], top[2]),
        (bottom[3], bottom[2], top[2], top[3]),
    ]
    cells = []
    inverse_cells = []
    min_det = None
    for face in faces:
        triangles = [(face[0], face[1], face[2]), (face[0], face[2], face[3])]
        for triangle in triangles:
            source_tet = [*triangle, center]
            image_tet = [*triangle, moved]
            if tet_volume(source_tet) < 0:
                source_tet = [triangle[0], triangle[2], triangle[1], center]
                image_tet = [triangle[0], triangle[2], triangle[1], moved]
            if tet_volume(source_tet) <= 0 or tet_volume(image_tet) <= 0:
                raise AssertionError("straightening tetrahedron is degenerate")
            linear, translation, jacobian = affine_from_tets(source_tet, image_tet)
            if jacobian <= 0:
                raise AssertionError(f"straightening cell has Jacobian {jacobian}")
            inv_linear, inv_translation, inv_jac = affine_from_tets(image_tet, source_tet)
            if inv_jac <= 0:
                raise AssertionError(f"inverse straightening cell has Jacobian {inv_jac}")
            min_det = jacobian if min_det is None else min(min_det, jacobian)
            cells.append(
                {
                    "source": [encode(vertex) for vertex in source_tet],
                    "image": [encode(vertex) for vertex in image_tet],
                    "linear": [[str(entry) for entry in row] for row in linear],
                    "translation": encode(translation),
                    "jacobian_det": str(jacobian),
                    "inverse_linear": [[str(entry) for entry in row] for row in inv_linear],
                    "inverse_translation": encode(inv_translation),
                }
            )
            inverse_cells.append(
                {
                    "source": [encode(vertex) for vertex in image_tet],
                    "image": [encode(vertex) for vertex in source_tet],
                    "linear": [[str(entry) for entry in row] for row in inv_linear],
                    "translation": encode(inv_translation),
                    "jacobian_det": str(inv_jac),
                }
            )
    prism_vertices = list(bottom) + list(top) + [center, moved]
    nearest = min(torus_inf(vertex) for vertex in prism_vertices)
    if nearest <= PROTECTED_RADIUS:
        raise AssertionError("straightening prism meets the protected ball")
    return {
        "cells": cells,
        "inverse_cells": inverse_cells,
        "jacobian_det_min": str(min_det),
        "offset": encode(offset),
        "inner_corners": [encode(vertex) for vertex in (sw, se, ne, nw)],
        "center": encode(center),
        "moved_center": encode(moved),
        "boundary_identity": True,
        "protected_clearance": str(nearest),
        "cell_count": len(cells),
    }


def apply_cells(cells: list[dict[str, Any]], point: Iterable[Fraction]) -> list[Fraction]:
    pt = [Fraction(value) for value in point]
    for cell in cells:
        source = [decode(vertex) for vertex in cell["source"]]
        if point_in_tet(source, pt):
            linear = [[Fraction(entry) for entry in row] for row in cell["linear"]]
            translation = decode(cell["translation"])
            return apply_affine(linear, translation, pt)
    return pt


def apply_alpha(generator: dict[str, Any], point: Iterable[Fraction]) -> list[Fraction]:
    linear = generator["transvection"]["linear"]
    after_a = matvec(linear, point)
    return apply_cells(generator["straightening"]["cells"], after_a)


def coarse_spine_vertices(base: Vertex) -> tuple[Vertex, ...]:
    origin = tuple(base)
    arms = [origin]
    for axis in range(3):
        vertex = list(origin)
        vertex[axis] = origin[axis] + 2
        arms.append(tuple(vertex))  # type: ignore[arg-type]
    return tuple(arms)  # type: ignore[return-value]


def inf_dist_to_set(point: tuple[float, float, float], family: Iterable[Vertex]) -> float:
    best: float | None = None
    for vertex in family:
        dist = max(abs(wrap_delta(point[i] - vertex[i])) for i in range(3))
        if best is None or dist < best:
            best = dist
    if best is None:
        raise AssertionError("empty dual-block family")
    return best


def cube_owner(origin: Vertex, family_a: tuple[Vertex, ...], family_b: tuple[Vertex, ...]) -> int:
    center = (origin[0] + 0.5, origin[1] + 0.5, origin[2] + 0.5)
    dist_a = inf_dist_to_set(center, family_a)
    dist_b = inf_dist_to_set(center, family_b)
    if dist_a == dist_b:
        raise AssertionError(f"unit cube {origin} is not in a unique dual 3-block")
    return 0 if dist_a < dist_b else 1


def johnson_owners() -> dict[Vertex, int]:
    family_0 = coarse_spine_vertices((0, 0, 0))
    family_1 = coarse_spine_vertices((2, 2, 2))
    return {
        origin: cube_owner(origin, family_0, family_1)
        for origin in itertools.product(range(PERIOD), repeat=3)
    }


def point_owner(point: Iterable[Fraction], owners: dict[Vertex, int] | None = None) -> int:
    if owners is None:
        owners = johnson_owners()
    coords = [float(Fraction(value)) % PERIOD for value in point]
    origin = tuple(int(value) % PERIOD for value in coords)  # type: ignore[assignment]
    return owners[origin]  # type: ignore[index]


def heegaard_preservation(generator: dict[str, Any]) -> dict[str, Any]:
    owners = johnson_owners()
    h0 = [origin for origin, owner in owners.items() if owner == 0]
    stayed = 0
    left = 0
    for origin in h0:
        center = [Fraction(origin[i]) + Fraction(1, 2) for i in range(3)]
        image = apply_alpha(generator, center)
        if point_owner(image, owners) == 0:
            stayed += 1
        else:
            left += 1
    return {
        "h0_cube_centers": len(h0),
        "stayed_in_h0": stayed,
        "left_h0": left,
        "preserved": left == 0,
    }


def section_ball_identity(generator: dict[str, Any], samples: int = 8) -> dict[str, Any]:
    radius = PROTECTED_RADIUS * Fraction(1, 2)
    directions = (
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
        (1, 1, 0),
        (1, 0, 1),
        (0, 1, 1),
        (1, 1, 1),
        (-1, 1, 0),
    )
    failures = []
    count = 0
    for direction in directions:
        for index in range(1, samples + 1):
            coeff = radius * Fraction(index, samples) / max(abs(component) for component in direction)
            point = [coeff * direction[i] for i in range(3)]
            image = apply_alpha(generator, point)
            count += 1
            delta = inf_norm(sub(image, point))
            if delta != 0:
                failures.append({"point": encode(point), "image": encode(image), "delta": str(delta)})
    return {
        "samples": count,
        "identity": not failures,
        "failures": failures[:4],
        "failure_count": len(failures),
    }


def dual_disk_boundary(plane_axis: int, plane_value: int, owner: int) -> dict[str, Any]:
    """Boundary of the coordinate-plane slice of one dual-block handlebody."""

    owners = johnson_owners()
    squares: list[tuple[int, int]] = []
    other = [axis for axis in range(3) if axis != plane_axis]
    for origin, cube in owners.items():
        if cube != owner:
            continue
        if origin[plane_axis] == plane_value or (origin[plane_axis] + 1) % PERIOD == plane_value:
            squares.append((origin[other[0]], origin[other[1]]))
    unique = sorted(set(squares))
    edges: Counter[tuple[tuple[int, int], tuple[int, int]]] = Counter()
    for x, y in unique:
        corners = [(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)]
        for start, end in zip(corners, corners[1:] + corners[:1]):
            edge = tuple(sorted((start, end)))
            edges[edge] += 1  # type: ignore[index]
    boundary = [edge for edge, count in edges.items() if count == 1]
    adj: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for start, end in boundary:
        adj[start].append(end)
        adj[end].append(start)
    if not boundary:
        raise AssertionError("coordinate slice has empty boundary")
    start = min(adj)
    loop = [start]
    prev = None
    while True:
        options = [vertex for vertex in adj[loop[-1]] if vertex != prev]
        if not options:
            raise AssertionError("coordinate slice boundary is not a cycle")
        nxt = min(options)
        if nxt == start:
            break
        loop.append(nxt)
        prev = loop[-2]
        if len(loop) > 32:
            raise AssertionError("coordinate slice boundary did not close")
    polyline = []
    for x, y in loop + [loop[0]]:
        point = [Fraction(0), Fraction(0), Fraction(0)]
        point[other[0]] = Fraction(x)
        point[other[1]] = Fraction(y)
        point[plane_axis] = Fraction(plane_value)
        polyline.append(encode(point))
    return {
        "plane_axis": plane_axis,
        "plane_value": plane_value,
        "owner": owner,
        "square_count": len(unique),
        "boundary_edge_count": len(boundary),
        "polyline": polyline,
        "closed": polyline[0] == polyline[-1],
        "vertex_count": len(loop),
    }


def spine_circle(axis: int, samples: int = 32) -> list[list[str]]:
    points = []
    for index in range(samples):
        point = [Fraction(0), Fraction(0), Fraction(0)]
        point[axis] = Fraction(index, samples)
        points.append(encode(point))
    points.append(points[0])
    return points


def framing_annulus(polyline: list[list[str]], offset: Iterable[Fraction]) -> dict[str, Any]:
    shift = [Fraction(value) for value in offset]
    inner = [decode(point) for point in polyline]
    outer = [add(point, shift) for point in inner]
    return {
        "inner": [encode(point) for point in inner],
        "outer": [encode(point) for point in outer],
        "offset": encode(shift),
    }
