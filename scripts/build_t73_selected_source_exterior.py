#!/usr/bin/env python3
"""Build the complete selected source endpoint incidence and a rational representative."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PRIMITIVES = ROOT / "geometry" / "t73_all_owner_product_primitives.json"
OUTPUT = ROOT / "geometry" / "t73_selected_source_exterior.json"
OWNERS = ("m_2", "r_xy")
COPY_SIGNS = ("negative", "positive")
NORMAL_DENOMINATOR = 2**20
NORMAL = (Fraction(0), Fraction(1, NORMAL_DENOMINATOR), Fraction(0))
MIN_ROUTE_CLEARANCE = Fraction(1, 1000)
BOXES = {
    "Y_minus": ((Fraction(-7), Fraction(-7), Fraction(-1)), (Fraction(-5), Fraction(-5), Fraction(1)), Fraction(-5)),
    "Y_plus": ((Fraction(-7), Fraction(5), Fraction(-1)), (Fraction(-5), Fraction(7), Fraction(1)), Fraction(-5)),
    "Z_minus": ((Fraction(5), Fraction(-7), Fraction(-1)), (Fraction(7), Fraction(-5), Fraction(1)), Fraction(5)),
    "Z_plus": ((Fraction(5), Fraction(5), Fraction(-1)), (Fraction(7), Fraction(7), Fraction(1)), Fraction(5)),
}


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def encode(point) -> list[str]:
    return [str(Fraction(value)) for value in point]


def add(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def sub(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def clamp01(value: Fraction) -> Fraction:
    return max(Fraction(0), min(Fraction(1), value))


def segment_distance_squared(first, second) -> Fraction:
    """Exact squared Euclidean distance between two closed Q^3 segments."""
    p1, q1 = first
    p2, q2 = second
    d1, d2, relative = sub(q1, p1), sub(q2, p2), sub(p1, p2)
    a, e = dot(d1, d1), dot(d2, d2)
    if a == 0 or e == 0:
        raise AssertionError("zero-length centre segment in clearance audit")
    b, c, f = dot(d1, d2), dot(d1, relative), dot(d2, relative)
    denominator = a * e - b * b
    first_parameter = (
        clamp01((b * f - c * e) / denominator)
        if denominator != 0
        else Fraction(0)
    )
    second_parameter = (b * first_parameter + f) / e
    if second_parameter < 0:
        second_parameter = Fraction(0)
        first_parameter = clamp01(-c / a)
    elif second_parameter > 1:
        second_parameter = Fraction(1)
        first_parameter = clamp01((b - c) / a)
    difference = sub(
        add(p1, tuple(first_parameter * value for value in d1)),
        add(p2, tuple(second_parameter * value for value in d2)),
    )
    return dot(difference, difference)


def ribbon_clearance(routes) -> dict[str, Any]:
    """Certify different ruled ribbons disjoint by an exact width bound."""
    centre_segments = []
    maximum_l1_width = Fraction(0)
    for route in routes:
        vertices = [tuple(Fraction(value) for value in point) for point in route["vertices"]]
        pushed = [
            tuple(Fraction(value) for value in point)
            for point in route["positive_push_off_vertices"]
        ]
        for centre, push in zip(vertices, pushed):
            maximum_l1_width = max(
                maximum_l1_width,
                sum(abs(value) for value in sub(push, centre)),
            )
        centre_segments.extend(
            (route["route_index"], segment_index, segment)
            for segment_index, segment in enumerate(zip(vertices, vertices[1:]))
        )
    minimum = None
    minimum_pair = None
    for first_index, (first_route, first_segment, first) in enumerate(centre_segments):
        for second_route, second_segment, second in centre_segments[first_index + 1 :]:
            if first_route == second_route:
                continue
            distance_squared = segment_distance_squared(first, second)
            if minimum is None or distance_squared < minimum:
                minimum = distance_squared
                minimum_pair = {
                    "first_route_index": first_route,
                    "first_segment_index": first_segment,
                    "second_route_index": second_route,
                    "second_segment_index": second_segment,
                }
    if minimum is None or minimum_pair is None:
        raise AssertionError("no distinct route pair for ribbon clearance")
    threshold = (2 * maximum_l1_width) ** 2
    if minimum <= MIN_ROUTE_CLEARANCE**2:
        raise AssertionError("stored route set violates its construction clearance")
    if minimum <= threshold:
        raise AssertionError("framing width is not below half the centre-route clearance")
    return {
        "method": "exact centre-segment distance and L1 tubular-width bound",
        "minimum_centre_segment_distance_squared": str(minimum),
        "attaining_segment_pair": minimum_pair,
        "maximum_vertex_l1_push_width": str(maximum_l1_width),
        "twice_width_squared": str(threshold),
        "strict_clearance": True,
        "conclusion": "ruled ribbons belonging to distinct exterior intervals are disjoint",
    }


def segment_intersects(first, second) -> bool:
    p, p2 = first
    q, q2 = second
    r, s = sub(p2, p), sub(q2, q)
    for a, b in ((0, 1), (0, 2), (1, 2)):
        determinant = r[b] * s[a] - r[a] * s[b]
        if determinant == 0:
            continue
        rhs = sub(q, p)
        t = (rhs[b] * s[a] - rhs[a] * s[b]) / determinant
        u = (r[a] * rhs[b] - r[b] * rhs[a]) / determinant
        if 0 <= t <= 1 and 0 <= u <= 1:
            left = add(p, tuple(t * value for value in r))
            right = add(q, tuple(u * value for value in s))
            return left == right
        return False
    # Parallel segments: generic construction forbids collinearity.
    return cross(sub(q, p), r) == (0, 0, 0)


def segment_meets_box_interior(segment, bounds) -> bool:
    start, end = segment
    lower, upper = bounds
    direction = sub(end, start)
    low, high = Fraction(0), Fraction(1)
    for axis in range(3):
        if direction[axis] == 0:
            if not lower[axis] < start[axis] < upper[axis]:
                return False
            continue
        a = (lower[axis] - start[axis]) / direction[axis]
        b = (upper[axis] - start[axis]) / direction[axis]
        if a > b:
            a, b = b, a
        low = max(low, a)
        high = min(high, b)
    return max(low, Fraction(0, 10**12)) < min(high, Fraction(1) - Fraction(1, 10**12))


def endpoint_grid(count: int, lower, upper, face_x):
    columns = math.isqrt(count)
    if columns * columns < count:
        columns += 1
    rows = (count + columns - 1) // columns
    result = []
    for index in range(count):
        column, row = index % columns, index // columns
        y = lower[1] + (upper[1] - lower[1]) * Fraction(column + 1, columns + 1)
        z = lower[2] + (upper[2] - lower[2]) * Fraction(row + 1, rows + 1)
        result.append((face_x, y, z))
    return result


def build_cycles(all_owner):
    cycles = []
    endpoints_by_sphere = {name: [] for name in BOXES}
    for owner in OWNERS:
        base = all_owner["primitive_geometry"][owner]["reduced_events"]
        for copy_sign in COPY_SIGNS:
            order = list(range(len(base))) if copy_sign == "positive" else list(reversed(range(len(base))))
            cycle_id = f"{owner}:{copy_sign}"
            occurrences = []
            for traversal_index, base_index in enumerate(order):
                event = base[base_index]
                multiplier = 1 if copy_sign == "positive" else -1
                orientation = multiplier * int(event["orientation"])
                handle = event["label"].upper()
                entry_suffix, exit_suffix = (
                    ("minus", "plus") if orientation > 0 else ("plus", "minus")
                )
                entry_sphere = f"{handle}_{entry_suffix}"
                exit_sphere = f"{handle}_{exit_suffix}"
                occurrence_id = f"{cycle_id}:event:{traversal_index}"
                record = {
                    "occurrence_id": occurrence_id,
                    "cycle_id": cycle_id,
                    "owner": owner,
                    "copy_sign": copy_sign,
                    "traversal_index": traversal_index,
                    "base_event_index": base_index,
                    "source_id": event["source_id"],
                    "handle": handle,
                    "base_orientation": int(event["orientation"]),
                    "effective_orientation": orientation,
                    "entry_sphere": entry_sphere,
                    "exit_sphere": exit_sphere,
                    "entry_endpoint_id": f"{occurrence_id}:entry",
                    "exit_endpoint_id": f"{occurrence_id}:exit",
                }
                occurrences.append(record)
                endpoints_by_sphere[entry_sphere].append(
                    {
                        "endpoint_id": record["entry_endpoint_id"],
                        "occurrence_id": occurrence_id,
                        "role": "entry",
                    }
                )
                endpoints_by_sphere[exit_sphere].append(
                    {
                        "endpoint_id": record["exit_endpoint_id"],
                        "occurrence_id": occurrence_id,
                        "role": "exit",
                    }
                )
            cycles.append(
                {
                    "cycle_id": cycle_id,
                    "owner": owner,
                    "copy_sign": copy_sign,
                    "event_count": len(occurrences),
                    "occurrences": occurrences,
                }
            )
    return cycles, endpoints_by_sphere


def route_candidate(index: int, attempt: int):
    modulus = 10007
    a = (97 * (index + 1) + 193 * (attempt + 1)) % modulus
    b = (211 * (index + 1) + 389 * (attempt + 1)) % modulus
    c = (431 * (index + 1) + 769 * (attempt + 1)) % modulus
    return (
        Fraction(-4) + Fraction(8 * (a + 1), modulus + 1),
        Fraction(-4) + Fraction(8 * (b + 1), modulus + 1),
        Fraction(-12) + Fraction(24 * (c + 1), modulus + 1),
    )


def build_routes(interval_specs, endpoint_lookup):
    routes = []
    segments = []
    box_bounds = [(value[0], value[1]) for value in BOXES.values()]
    for index, spec in enumerate(interval_specs):
        start = endpoint_lookup[spec["from_endpoint_id"]]
        end = endpoint_lookup[spec["to_endpoint_id"]]
        accepted = None
        for attempt in range(20000):
            bend = route_candidate(index, attempt)
            candidate = [(start, bend), (bend, end)]
            if any(segment_meets_box_interior(segment, bounds) for segment in candidate for bounds in box_bounds):
                continue
            if segment_intersects(candidate[0], candidate[1]):
                # The two segments meet at their common bend and are otherwise
                # generic; collinearity is the only rejected case here.
                if cross(sub(bend, start), sub(end, bend)) == (0, 0, 0):
                    continue
            if any(segment_intersects(new, old) for new in candidate for old in segments):
                continue
            if any(
                segment_distance_squared(new, old) <= MIN_ROUTE_CLEARANCE**2
                for new in candidate
                for old in segments
            ):
                continue
            accepted = bend
            break
        if accepted is None:
            raise AssertionError(f"no disjoint rational route for interval {index}")
        centerline = [start, accepted, end]
        routes.append(
            {
                **spec,
                "route_index": index,
                "vertices": [encode(point) for point in centerline],
                "relative_twist": 0,
            }
        )
        segments.extend(zip(centerline, centerline[1:]))
    push_segments = []
    for route in routes:
        vertices = [tuple(Fraction(value) for value in point) for point in route["vertices"]]
        start_push, end_push = add(vertices[0], NORMAL), add(vertices[2], NORMAL)
        accepted_push = None
        accepted_normal = None
        for attempt in range(1, 20000):
            # Endpoint normals stay equal to the insertion-face product
            # normal.  The interior normal is allowed to turn inside the
            # framed tubular neighborhood.
            interior_normal = (
                Fraction((17 * attempt) % 101 + 1, NORMAL_DENOMINATOR),
                Fraction((29 * attempt) % 103 + 1, NORMAL_DENOMINATOR),
                Fraction((43 * attempt) % 107 + 1, NORMAL_DENOMINATOR),
            )
            bend_push = add(vertices[1], interior_normal)
            candidate = [(start_push, bend_push), (bend_push, end_push)]
            if any(segment_meets_box_interior(segment, bounds) for segment in candidate for bounds in box_bounds):
                continue
            if any(segment_intersects(new, old) for new in candidate for old in segments):
                continue
            if any(segment_intersects(new, old) for new in candidate for old in push_segments):
                continue
            accepted_push = [start_push, bend_push, end_push]
            accepted_normal = [NORMAL, interior_normal, NORMAL]
            break
        if accepted_push is None or accepted_normal is None:
            raise AssertionError(f"no disjoint framing push-off for route {route['route_index']}")
        route["boundary_product_normal"] = encode(NORMAL)
        route["framing_normal_vertices"] = [encode(value) for value in accepted_normal]
        route["positive_push_off_vertices"] = [encode(value) for value in accepted_push]
        route["ruled_ribbon_triangles"] = [
            [encode(vertices[index]), encode(vertices[index + 1]), encode(accepted_push[index + 1])]
            for index in range(2)
        ] + [
            [encode(vertices[index]), encode(accepted_push[index + 1]), encode(accepted_push[index])]
            for index in range(2)
        ]
        route["ruled_ribbon_boundary"] = {
            "core_vertices": route["vertices"],
            "push_off_vertices": route["positive_push_off_vertices"],
            "initial_transverse_edge": [route["vertices"][0], route["positive_push_off_vertices"][0]],
            "terminal_transverse_edge": [route["vertices"][-1], route["positive_push_off_vertices"][-1]],
        }
        push_segments.extend(zip(accepted_push, accepted_push[1:]))
    return routes


def build():
    all_owner = json.loads(PRIMITIVES.read_text(encoding="utf-8"))
    cycles, endpoints_by_sphere = build_cycles(all_owner)
    endpoint_lookup = {}
    sphere_records = []
    for sphere_name, records in endpoints_by_sphere.items():
        lower, upper, face_x = BOXES[sphere_name]
        coordinates = endpoint_grid(len(records), lower, upper, face_x)
        enriched = []
        for index, (record, coordinate) in enumerate(zip(records, coordinates)):
            item = {
                **record,
                "sphere_index": index,
                "point": encode(coordinate),
                "positive_push_off_point": encode(add(coordinate, NORMAL)),
            }
            enriched.append(item)
            endpoint_lookup[item["endpoint_id"]] = coordinate
        sphere_records.append(
            {
                "name": sphere_name,
                "box_lower": encode(lower),
                "box_upper": encode(upper),
                "designated_face_axis": "x",
                "designated_face_value": str(face_x),
                "endpoint_count": len(enriched),
                "endpoints": enriched,
            }
        )

    interval_specs = []
    for cycle in cycles:
        occurrences = cycle["occurrences"]
        for index, occurrence in enumerate(occurrences):
            following = occurrences[(index + 1) % len(occurrences)]
            interval_specs.append(
                {
                    "interval_id": f"{cycle['cycle_id']}:interval:{index}",
                    "cycle_id": cycle["cycle_id"],
                    "owner": cycle["owner"],
                    "copy_sign": cycle["copy_sign"],
                    "from_occurrence_id": occurrence["occurrence_id"],
                    "to_occurrence_id": following["occurrence_id"],
                    "from_endpoint_id": occurrence["exit_endpoint_id"],
                    "to_endpoint_id": following["entry_endpoint_id"],
                    "cyclic_seam": index == len(occurrences) - 1,
                    "from_source_id": occurrence["source_id"],
                    "to_source_id": following["source_id"],
                    "interval_type": (
                        "active_y_z"
                        if occurrence["handle"] != following["handle"]
                        else "residual_z_z"
                    ),
                }
            )
    routes = build_routes(interval_specs, endpoint_lookup)
    interval_counts_by_copy = {
        copy_sign: {
            "active_y_z": sum(
                route["copy_sign"] == copy_sign
                and route["interval_type"] == "active_y_z"
                for route in routes
            ),
            "residual_z_z": sum(
                route["copy_sign"] == copy_sign
                and route["interval_type"] == "residual_z_z"
                for route in routes
            ),
        }
        for copy_sign in COPY_SIGNS
    }
    result = {
        "schema": "t73_selected_source_exterior/v1",
        "all_owner_primitives_sha256": all_owner["sha256"],
        "ambient": {
            "outer_ball": {
                "model": "cube",
                "lower": ["-20", "-20", "-20"],
                "upper": ["20", "20", "20"],
            },
            "inner_insertion_balls": [record["name"] for record in sphere_records],
        },
        "cycles": cycles,
        "insertion_spheres": sphere_records,
        "endpoint_counts_per_sphere": {
            record["name"]: record["endpoint_count"] for record in sphere_records
        },
        "base_passage_counts": {"y": 44, "z": 271},
        "cabled_passage_counts": {"y": 88, "z": 542},
        "total_boundary_endpoint_count": sum(
            record["endpoint_count"] for record in sphere_records
        ),
        "exterior_interval_count": len(routes),
        "exterior_intervals": routes,
        "interval_counts_by_copy": interval_counts_by_copy,
        "cyclic_seam_count": sum(route["cyclic_seam"] for route in routes),
        "normal": encode(NORMAL),
        "ribbon_clearance": ribbon_clearance(routes),
        "canonical_representative_only": True,
        "actual_ar_relative_isotopy_proved": False,
        "contains_braid_word": False,
    }
    result["sha256"] = canonical_sha(
        {key: value for key, value in result.items() if key != "sha256"}
    )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        temporary = OUTPUT.with_name(OUTPUT.name + ".tmp")
        temporary.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(OUTPUT)
        print(f"WROTE={OUTPUT}")
    print("T73_SELECTED_SOURCE_EXTERIOR=BUILT")
    print(f"SPHERE_ENDPOINTS={result['endpoint_counts_per_sphere']}")
    print(f"INTERVALS={result['exterior_interval_count']}")
    print(f"CYCLIC_SEAMS={result['cyclic_seam_count']}")
    print(f"SHA256={result['sha256']}")


if __name__ == "__main__":
    main()
