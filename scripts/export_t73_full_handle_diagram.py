#!/usr/bin/env python3
"""Export a complete rational polygonal Kirby diagram to standard link data.

The input is deliberately stronger than a crossing ledger: every component
and every framing push-off is a closed polygonal curve in one oriented affine
Q^3 chart.  All projection intersections and their along-segment parameters
are recomputed with ``fractions.Fraction``.  Nongeneric or incomplete input is
rejected before a PD row is emitted.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_NAMES = [
    "m_2",
    "m_3",
    "r_xy",
    "r_yz",
    "r_zx",
    "dotted_y",
    "dotted_z",
]
TWO_HANDLE_NAMES = REQUIRED_NAMES[:5]


class DiagramError(ValueError):
    """The coordinate diagram is incomplete or fails exact genericity."""


def q(value: Any) -> Fraction:
    if isinstance(value, bool):
        raise DiagramError("booleans are not rational coordinates")
    try:
        return Fraction(value)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise DiagramError(f"invalid rational coordinate {value!r}") from exc


def enc(value: Fraction) -> str:
    return str(value)


def enc_point(point: Iterable[Fraction]) -> list[str]:
    return [enc(value) for value in point]


def vector(value: Any, label: str) -> tuple[Fraction, Fraction, Fraction]:
    if not isinstance(value, list) or len(value) != 3:
        raise DiagramError(f"{label} must be a three-entry rational vector")
    return tuple(q(entry) for entry in value)  # type: ignore[return-value]


def dot(a: Iterable[Fraction], b: Iterable[Fraction]) -> Fraction:
    return sum((x * y for x, y in zip(a, b)), Fraction(0))


def sub(a: Iterable[Fraction], b: Iterable[Fraction]) -> tuple[Fraction, ...]:
    return tuple(x - y for x, y in zip(a, b))


def add_scaled(
    a: Iterable[Fraction], direction: Iterable[Fraction], parameter: Fraction
) -> tuple[Fraction, ...]:
    return tuple(x + parameter * d for x, d in zip(a, direction))


def det2(a: tuple[Fraction, Fraction], b: tuple[Fraction, Fraction]) -> Fraction:
    return a[0] * b[1] - a[1] * b[0]


def det3(rows: list[tuple[Fraction, Fraction, Fraction]]) -> Fraction:
    a, b, c = rows
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def parse_closed_polyline(value: Any, label: str) -> list[tuple[Fraction, ...]]:
    if not isinstance(value, list) or len(value) < 4:
        raise DiagramError(f"{label} must have at least three segments")
    points = [vector(point, f"{label}[{index}]") for index, point in enumerate(value)]
    if points[0] != points[-1]:
        raise DiagramError(f"{label} is not explicitly closed")
    for index, (start, end) in enumerate(zip(points, points[1:])):
        if start == end:
            raise DiagramError(f"{label} has zero-length segment {index}")
    return points


def validate_successors(value: Any, count: int, label: str) -> None:
    expected = [(index + 1) % count for index in range(count)]
    if value != expected:
        raise DiagramError(
            f"{label} must be the explicit oriented cyclic order {expected}"
        )


def projection(point: Iterable[Fraction], basis: list[tuple[Fraction, ...]]) -> tuple[Fraction, Fraction]:
    return (dot(basis[0], point), dot(basis[1], point))


def projected_intersection(
    a0: tuple[Fraction, ...],
    a1: tuple[Fraction, ...],
    b0: tuple[Fraction, ...],
    b1: tuple[Fraction, ...],
    basis: list[tuple[Fraction, ...]],
    label: str,
) -> tuple[Fraction, Fraction, tuple[Fraction, Fraction]] | None:
    pa0, pa1 = projection(a0, basis), projection(a1, basis)
    pb0, pb1 = projection(b0, basis), projection(b1, basis)
    if (
        max(min(pa0[0], pa1[0]), min(pb0[0], pb1[0]))
        > min(max(pa0[0], pa1[0]), max(pb0[0], pb1[0]))
        or max(min(pa0[1], pa1[1]), min(pb0[1], pb1[1]))
        > min(max(pa0[1], pa1[1]), max(pb0[1], pb1[1]))
    ):
        return None
    da = sub(pa1, pa0)
    db = sub(pb1, pb0)
    if da == (0, 0) or db == (0, 0):
        raise DiagramError(f"{label}: a segment collapses under projection")
    denominator = det2(da, db)  # type: ignore[arg-type]
    delta = sub(pb0, pa0)
    if denominator == 0:
        if det2(delta, da) == 0:  # type: ignore[arg-type]
            coordinate = 0 if da[0] != 0 else 1
            first_parameter = (pb0[coordinate] - pa0[coordinate]) / da[coordinate]
            second_parameter = (pb1[coordinate] - pa0[coordinate]) / da[coordinate]
            overlap_left = max(Fraction(0), min(first_parameter, second_parameter))
            overlap_right = min(Fraction(1), max(first_parameter, second_parameter))
            if overlap_left <= overlap_right:
                raise DiagramError(f"{label}: overlapping projected collinear segments")
        return None
    ta = det2(delta, db) / denominator  # type: ignore[arg-type]
    tb = det2(delta, da) / denominator  # type: ignore[arg-type]
    if 0 < ta < 1 and 0 < tb < 1:
        point = add_scaled(pa0, da, ta)
        return ta, tb, (point[0], point[1])
    if 0 <= ta <= 1 and 0 <= tb <= 1:
        raise DiagramError(f"{label}: crossing occurs at a polygon vertex")
    return None


def adjacent_segments(first: int, second: int, count: int) -> bool:
    return first == second or (first - second) % count in (1, count - 1)


def curve_crossings(
    curves: list[dict[str, Any]],
    basis: list[tuple[Fraction, ...]],
    height: tuple[Fraction, ...],
    *,
    include_self: bool,
    require_unique_projection_points: bool,
) -> list[dict[str, Any]]:
    """Return all exact regular-diagram crossings for named polygonal curves."""

    crossings: list[dict[str, Any]] = []
    seen_points: dict[tuple[Fraction, Fraction], str] = {}
    for curve in curves:
        points = curve["points"]
        for segment, (start, end) in enumerate(zip(points, points[1:])):
            if projection(start, basis) == projection(end, basis):
                raise DiagramError(
                    f"{curve['name']}:{segment}: a segment collapses under projection"
                )
    for first_index, first in enumerate(curves):
        first_points = first["points"]
        for second_index in range(first_index, len(curves)):
            second = curves[second_index]
            if first_index == second_index and not include_self:
                continue
            second_points = second["points"]
            for first_segment in range(len(first_points) - 1):
                start_second_segment = first_segment + 1 if first_index == second_index else 0
                for second_segment in range(start_second_segment, len(second_points) - 1):
                    if first_index == second_index and adjacent_segments(
                        first_segment, second_segment, len(first_points) - 1
                    ):
                        continue
                    label = (
                        f"{first['name']}:{first_segment}/"
                        f"{second['name']}:{second_segment}"
                    )
                    hit = projected_intersection(
                        first_points[first_segment],
                        first_points[first_segment + 1],
                        second_points[second_segment],
                        second_points[second_segment + 1],
                        basis,
                        label,
                    )
                    if hit is None:
                        continue
                    first_parameter, second_parameter, point = hit
                    first_direction = sub(
                        first_points[first_segment + 1], first_points[first_segment]
                    )
                    second_direction = sub(
                        second_points[second_segment + 1], second_points[second_segment]
                    )
                    first_point = add_scaled(
                        first_points[first_segment], first_direction, first_parameter
                    )
                    second_point = add_scaled(
                        second_points[second_segment], second_direction, second_parameter
                    )
                    first_height = dot(height, first_point)
                    second_height = dot(height, second_point)
                    if first_height == second_height:
                        raise DiagramError(f"{label}: the polygonal curves meet in Q^3")
                    if require_unique_projection_points and point in seen_points:
                        raise DiagramError(
                            f"{label}: triple/repeated projected crossing at {enc_point(point)}; "
                            f"first used by {seen_points[point]}"
                        )
                    seen_points[point] = label
                    first_tangent = sub(
                        projection(first_points[first_segment + 1], basis),
                        projection(first_points[first_segment], basis),
                    )
                    second_tangent = sub(
                        projection(second_points[second_segment + 1], basis),
                        projection(second_points[second_segment], basis),
                    )
                    if first_height > second_height:
                        over_curve, under_curve = first, second
                        over_segment, under_segment = first_segment, second_segment
                        over_parameter, under_parameter = first_parameter, second_parameter
                        over_tangent, under_tangent = first_tangent, second_tangent
                    else:
                        over_curve, under_curve = second, first
                        over_segment, under_segment = second_segment, first_segment
                        over_parameter, under_parameter = second_parameter, first_parameter
                        over_tangent, under_tangent = second_tangent, first_tangent
                    determinant = det2(over_tangent, under_tangent)  # type: ignore[arg-type]
                    if determinant == 0:
                        raise DiagramError(f"{label}: nontransverse projected crossing")
                    crossings.append(
                        {
                            "id": f"X{len(crossings)}",
                            "projection_point": enc_point(point),
                            "over_owner": over_curve["name"],
                            "under_owner": under_curve["name"],
                            "over_segment": over_segment,
                            "under_segment": under_segment,
                            "over_parameter": enc(over_parameter),
                            "under_parameter": enc(under_parameter),
                            "over_height": enc(max(first_height, second_height)),
                            "under_height": enc(min(first_height, second_height)),
                            "sign": 1 if determinant > 0 else -1,
                        }
                    )
    crossings.sort(
        key=lambda crossing: (
            q(crossing["projection_point"][0]),
            q(crossing["projection_point"][1]),
            crossing["over_owner"],
            crossing["under_owner"],
        )
    )
    for index, crossing in enumerate(crossings):
        crossing["id"] = f"X{index}"
    return crossings


def occurrence(crossing: dict[str, Any], owner: str, role: str) -> dict[str, Any]:
    if role not in ("over", "under") or crossing[f"{role}_owner"] != owner:
        raise AssertionError("owner is not incident to crossing")
    return {
        "crossing": crossing["id"],
        "role": role,
        "sign": crossing["sign"],
        "segment": crossing[f"{role}_segment"],
        "parameter": crossing[f"{role}_parameter"],
    }


def pd_and_cycles(
    component_names: list[str], crossings: list[dict[str, Any]]
) -> tuple[list[list[int]], dict[str, list[dict[str, Any]]], list[str]]:
    ordered: dict[str, list[dict[str, Any]]] = {}
    crossingless = []
    next_label = 0
    occurrence_by_crossing: dict[tuple[str, str], dict[str, Any]] = {}
    for name in component_names:
        events = []
        for crossing in crossings:
            if crossing["over_owner"] == name:
                events.append(occurrence(crossing, name, "over"))
            if crossing["under_owner"] == name:
                events.append(occurrence(crossing, name, "under"))
        events.sort(key=lambda event: (event["segment"], q(event["parameter"]), event["role"]))
        if not events:
            crossingless.append(name)
            ordered[name] = []
            continue
        labels = list(range(next_label, next_label + len(events)))
        next_label += len(events)
        for index, event in enumerate(events):
            event["incoming_arc"] = labels[(index - 1) % len(events)]
            event["outgoing_arc"] = labels[index]
            event["successor_crossing"] = events[(index + 1) % len(events)]["crossing"]
            event["successor_role"] = events[(index + 1) % len(events)]["role"]
            key = (event["crossing"], event["role"])
            if key in occurrence_by_crossing:
                # A self-crossing uses one over and one under occurrence, so
                # role distinguishes the two visits.
                raise DiagramError(f"duplicate {key} occurrence")
            occurrence_by_crossing[key] = event
        ordered[name] = events

    pd = []
    for crossing in crossings:
        under = occurrence_by_crossing[(crossing["id"], "under")]
        over = occurrence_by_crossing[(crossing["id"], "over")]
        row: list[int | None] = [None, None, None, None]
        row[0] = under["incoming_arc"]
        row[2] = under["outgoing_arc"]
        if crossing["sign"] == 1:
            row[3] = over["incoming_arc"]
            row[1] = over["outgoing_arc"]
        else:
            row[1] = over["incoming_arc"]
            row[3] = over["outgoing_arc"]
        if any(value is None for value in row):
            raise AssertionError("incomplete PD row")
        pd.append([int(value) for value in row])  # type: ignore[arg-type]
    counts = Counter(label for row in pd for label in row)
    if counts and set(counts.values()) != {2}:
        raise AssertionError("internal PD arc-incidence failure")
    return pd, ordered, crossingless


def linking_number_between(
    first: dict[str, Any],
    second: dict[str, Any],
    basis: list[tuple[Fraction, ...]],
    height: tuple[Fraction, ...],
) -> tuple[int, list[dict[str, Any]]]:
    crossings = curve_crossings(
        [first, second],
        basis,
        height,
        include_self=False,
        require_unique_projection_points=True,
    )
    signed_sum = sum(crossing["sign"] for crossing in crossings)
    if signed_sum % 2:
        raise DiagramError(
            f"mixed crossing sum for {first['name']}/{second['name']} is odd"
        )
    return signed_sum // 2, crossings


def pairwise_linking_matrix(
    names: list[str], crossings: list[dict[str, Any]]
) -> list[list[int]]:
    matrix = [[0 for _ in names] for _ in names]
    for first_index, first in enumerate(names):
        for second_index in range(first_index + 1, len(names)):
            second = names[second_index]
            signed_sum = sum(
                crossing["sign"]
                for crossing in crossings
                if {crossing["over_owner"], crossing["under_owner"]}
                == {first, second}
            )
            if signed_sum % 2:
                raise DiagramError(f"mixed crossing sum for {first}/{second} is odd")
            matrix[first_index][second_index] = signed_sum // 2
            matrix[second_index][first_index] = signed_sum // 2
    return matrix


def parse(data: dict[str, Any]) -> tuple[list[dict[str, Any]], list[tuple[Fraction, ...]], tuple[Fraction, ...]]:
    if data.get("schema") != "t73_full_handle_diagram_input/v1":
        raise DiagramError("wrong full-handle input schema")
    ambient = data.get("ambient")
    if not isinstance(ambient, dict):
        raise DiagramError("ambient record is missing")
    if ambient.get("chart") != "oriented_affine_Q3":
        raise DiagramError("ambient chart must be oriented_affine_Q3")
    if ambient.get("ambient_orientation") != "standard_xyz":
        raise DiagramError("ambient orientation must be standard_xyz")
    direction = vector(ambient.get("projection_direction"), "projection_direction")
    height = vector(ambient.get("height_direction"), "height_direction")
    raw_basis = ambient.get("projection_basis")
    if not isinstance(raw_basis, list) or len(raw_basis) != 2:
        raise DiagramError("projection_basis must contain two rational covectors")
    basis = [vector(row, f"projection_basis[{index}]") for index, row in enumerate(raw_basis)]
    if direction == (0, 0, 0) or height == (0, 0, 0):
        raise DiagramError("projection and height directions must be nonzero")
    if any(dot(row, direction) != 0 for row in basis):
        raise DiagramError("projection_basis must annihilate projection_direction")
    orientation_determinant = det3([basis[0], basis[1], height])
    if dot(height, direction) == 0 or orientation_determinant == 0:
        raise DiagramError("projection/height coordinate system is singular")
    if orientation_determinant < 0:
        raise DiagramError("projection_basis followed by height reverses standard_xyz orientation")
    certificate = ambient.get("genericity_certificate")
    if certificate != {"method": "exact_fraction_recomputation", "claimed": "PASS"}:
        raise DiagramError("genericity_certificate must request exact recomputation")

    raw_components = data.get("components")
    if not isinstance(raw_components, list):
        raise DiagramError("components must be an ordered list")
    names = [component.get("name") for component in raw_components if isinstance(component, dict)]
    if names != REQUIRED_NAMES:
        raise DiagramError(f"component order/names must be {REQUIRED_NAMES}")
    components = []
    for component in raw_components:
        name = component["name"]
        expected_kind = "two_handle" if name in TWO_HANDLE_NAMES else "dotted_one_handle"
        if component.get("component_kind") != expected_kind:
            raise DiagramError(f"{name} has wrong component_kind")
        points = parse_closed_polyline(component.get("closed_core_polyline"), f"{name}.core")
        validate_successors(
            component.get("cyclic_segment_successor"), len(points) - 1, f"{name}.cyclic_segment_successor"
        )
        record = {"name": name, "kind": expected_kind, "points": points}
        if expected_kind == "two_handle":
            push_points = parse_closed_polyline(
                component.get("closed_push_off_polyline"), f"{name}.push_off"
            )
            validate_successors(
                component.get("push_off_cyclic_segment_successor"),
                len(push_points) - 1,
                f"{name}.push_off_cyclic_segment_successor",
            )
            record["push_points"] = push_points
        components.append(record)
    return components, basis, height


def export(data: dict[str, Any]) -> dict[str, Any]:
    components, basis, height = parse(data)
    all_curves = [
        {"name": component["name"], "points": component["points"]}
        for component in components
    ] + [
        {
            "name": f"{component['name']}__push_off",
            "points": component["push_points"],
        }
        for component in components
        if component["kind"] == "two_handle"
    ]
    # This includes every core and all five push-offs.  In particular it
    # rejects a claimed push-off that meets another component, another
    # push-off, or itself in Q^3.
    all_names = [curve["name"] for curve in all_curves]
    framed_crossings = curve_crossings(
        all_curves,
        basis,
        height,
        include_self=True,
        require_unique_projection_points=True,
    )
    framed_pd, framed_cycles, framed_crossingless = pd_and_cycles(
        all_names, framed_crossings
    )
    crossings = curve_crossings(
        components,
        basis,
        height,
        include_self=True,
        require_unique_projection_points=True,
    )
    pd, cycles, crossingless = pd_and_cycles(REQUIRED_NAMES, crossings)

    pairwise = pairwise_linking_matrix(REQUIRED_NAMES, crossings)
    framed_pairwise = pairwise_linking_matrix(all_names, framed_crossings)

    blackboard_writhe = {
        name: sum(
            crossing["sign"]
            for crossing in crossings
            if crossing["over_owner"] == crossing["under_owner"] == name
        )
        for name in REQUIRED_NAMES
    }
    integer_framings: dict[str, int] = {}
    framing_receipts = {}
    for component in components:
        if component["kind"] != "two_handle":
            continue
        core_name = component["name"]
        push_name = f"{core_name}__push_off"
        framing_crossings = [
            crossing
            for crossing in framed_crossings
            if {crossing["over_owner"], crossing["under_owner"]}
            == {core_name, push_name}
        ]
        signed_sum = sum(crossing["sign"] for crossing in framing_crossings)
        if signed_sum % 2:
            raise DiagramError(f"mixed crossing sum for {core_name}/{push_name} is odd")
        framing = signed_sum // 2
        integer_framings[component["name"]] = framing
        framing_receipts[component["name"]] = {
            "push_off_owner": push_name,
            "mixed_crossing_sign_sum": signed_sum,
            "crossings": framing_crossings,
        }

    surgery_matrix = []
    for first in TWO_HANDLE_NAMES:
        row = []
        for second in TWO_HANDLE_NAMES:
            if first == second:
                row.append(integer_framings[first])
            else:
                row.append(pairwise[REQUIRED_NAMES.index(first)][REQUIRED_NAMES.index(second)])
        surgery_matrix.append(row)

    result = {
        "schema": "t73_full_handle_diagram_export/v1",
        "input_sha256": canonical_sha(data),
        "ambient": data["ambient"],
        "crossing_sign_convention": (
            "sign(det(P(over_tangent),P(under_tangent))) in standard_xyz orientation"
        ),
        "component_order": REQUIRED_NAMES,
        "crossing_count": len(crossings),
        "crossings": crossings,
        "component_halfedge_cycles": cycles,
        "structured_gauss_code": cycles,
        "standard_pd_code": pd,
        "crossingless_components": crossingless,
        "pd_limitation": (
            "standard PD rows omit crossingless split unknot components; the explicit core polylines remain authoritative"
            if crossingless
            else None
        ),
        "blackboard_writhe": blackboard_writhe,
        "pairwise_linking_matrix": {
            "component_order": REQUIRED_NAMES,
            "matrix": pairwise,
        },
        "integer_surgery_framings": integer_framings,
        "framing_linking_receipts": framing_receipts,
        "framed_link": {
            "component_order": all_names,
            "crossing_count": len(framed_crossings),
            "crossings": framed_crossings,
            "component_halfedge_cycles": framed_cycles,
            "standard_pd_code": framed_pd,
            "crossingless_components": framed_crossingless,
            "pairwise_linking_matrix": framed_pairwise,
        },
        "two_handle_surgery_matrix": {
            "component_order": TWO_HANDLE_NAMES,
            "matrix": surgery_matrix,
        },
        "genericity": {
            "exact_rational_recomputation": "PASS",
            "no_vertex_crossings": "PASS",
            "no_projected_triple_points": "PASS",
            "no_equal_height_crossings": "PASS",
            "all_cores_and_push_offs_disjoint": "PASS",
        },
        "status": "PASS",
    }
    result["sha256"] = canonical_sha(result)
    return result


def validate_with_open_source(exported: dict[str, Any]) -> dict[str, Any]:
    """Cross-check the PD/exterior with Spherogram, SnapPy, and Regina."""

    if exported["crossingless_components"]:
        raise DiagramError(
            "open-source PD exterior check requires every component to occur at a crossing"
        )
    try:
        import regina
        import snappy
        import spherogram
    except ImportError as exc:
        raise DiagramError(f"topology engine unavailable: {exc}") from exc
    pd = [tuple(row) for row in exported["standard_pd_code"]]
    link = spherogram.Link(pd)
    signs = [crossing.sign for crossing in link.crossings]
    expected_signs = [crossing["sign"] for crossing in exported["crossings"]]
    if signs != expected_signs:
        raise DiagramError(f"Spherogram crossing signs disagree: {signs} != {expected_signs}")
    if len(link.link_components) != len(REQUIRED_NAMES):
        raise DiagramError("Spherogram did not recover seven components")
    spherogram_linking = link.linking_matrix()
    if spherogram_linking != exported["pairwise_linking_matrix"]["matrix"]:
        raise DiagramError("Spherogram pairwise linking matrix disagrees")
    spherogram_writhe = link.writhe()
    if spherogram_writhe != sum(exported["blackboard_writhe"].values()):
        raise DiagramError("Spherogram total writhe disagrees")
    framed = exported["framed_link"]
    framed_receipt: dict[str, Any]
    if framed["crossingless_components"]:
        framed_receipt = {
            "verdict": "OPEN",
            "reason": "ordinary PD omits at least one crossingless push-off/core",
            "crossingless_components": framed["crossingless_components"],
        }
    else:
        framed_link = spherogram.Link(
            [tuple(row) for row in framed["standard_pd_code"]]
        )
        framed_linking = framed_link.linking_matrix()
        if len(framed_link.link_components) != len(framed["component_order"]):
            raise DiagramError("Spherogram did not recover all framed-link components")
        if framed_linking != framed["pairwise_linking_matrix"]:
            raise DiagramError("Spherogram framed-link linking matrix disagrees")
        framed_receipt = {
            "verdict": "PASS",
            "components": len(framed_link.link_components),
            "crossings": len(framed_link.crossings),
            "pairwise_linking_matrix": framed_linking,
        }
    manifold = link.exterior()
    if manifold.num_cusps() != len(REQUIRED_NAMES):
        raise DiagramError("SnapPy exterior did not recover seven cusps")
    decorated_isosig = manifold.triangulation_isosig()
    # SnapPy appends peripheral-curve decoration after an underscore;
    # Regina's fromIsoSig accepts the underlying undecorated triangulation.
    isosig = decorated_isosig.split("_", 1)[0]
    triangulation = regina.Triangulation3.fromIsoSig(isosig)
    if triangulation.size() != manifold.num_tetrahedra():
        raise DiagramError("Regina/SnapPy tetrahedron counts disagree")
    if not triangulation.isValid() or not triangulation.isOrientable():
        raise DiagramError("Regina triangulation is invalid or nonorientable")
    if not triangulation.isConnected() or not triangulation.isIdeal():
        raise DiagramError("Regina triangulation is not a connected ideal triangulation")
    if triangulation.countBoundaryComponents() != len(REQUIRED_NAMES):
        raise DiagramError("Regina triangulation does not have seven ideal boundary components")
    receipt = {
        "schema": "t73_full_handle_open_source_receipt/v1",
        "export_sha256": exported["sha256"],
        "spherogram_version": getattr(spherogram, "__version__", "unknown"),
        "snappy_version": getattr(snappy, "__version__", "unknown"),
        "regina_version": regina.versionString(),
        "spherogram_components": len(link.link_components),
        "spherogram_crossings": len(link.crossings),
        "spherogram_crossing_signs": signs,
        "spherogram_pairwise_linking_matrix": spherogram_linking,
        "spherogram_total_writhe": spherogram_writhe,
        "spherogram_framed_link": framed_receipt,
        "snappy_cusps": manifold.num_cusps(),
        "snappy_tetrahedra": manifold.num_tetrahedra(),
        "snappy_decorated_triangulation_isosig": decorated_isosig,
        "regina_undecorated_triangulation_isosig": isosig,
        "regina_tetrahedra": triangulation.size(),
        "regina_valid": triangulation.isValid(),
        "regina_orientable": triangulation.isOrientable(),
        "regina_connected": triangulation.isConnected(),
        "regina_ideal": triangulation.isIdeal(),
        "regina_boundary_components": triangulation.countBoundaryComponents(),
        "verdict": "PASS",
    }
    receipt["sha256"] = canonical_sha(receipt)
    return receipt


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--engines-output", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = export(data)
        if args.output:
            write_json(args.output, result)
        if args.check:
            stored = json.loads(args.check.read_text(encoding="utf-8"))
            if stored != result:
                raise DiagramError(f"stored export differs from live rebuild: {args.check}")
        if args.engines_output:
            receipt = validate_with_open_source(result)
            write_json(args.engines_output, receipt)
        print("T73_FULL_HANDLE_EXPORT=PASS")
        print(f"COMPONENTS={len(result['component_order'])}")
        print(f"CROSSINGS={result['crossing_count']}")
        print(f"SHA256={result['sha256']}")
    except (OSError, json.JSONDecodeError, DiagramError) as exc:
        print("T73_FULL_HANDLE_EXPORT=OPEN")
        print(f"REASON={exc}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
