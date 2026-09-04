#!/usr/bin/env python3
"""Verify the complete selected source endpoint incidence and rational routes."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "geometry" / "t73_selected_source_exterior.json"
PRIMITIVES = ROOT / "geometry" / "t73_all_owner_product_primitives.json"
MIN_ROUTE_CLEARANCE = Fraction(1, 1000)


def load_builder():
    path = ROOT / "scripts" / "build_t73_selected_source_exterior.py"
    spec = importlib.util.spec_from_file_location("source_exterior_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def point(raw):
    return tuple(Fraction(value) for value in raw)


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
    return sum(a[index] * b[index] for index in range(3))


def clamp01(value):
    return max(Fraction(0), min(Fraction(1), value))


def segment_distance_squared(first, second):
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


def clearance_certificate(intervals):
    segments = []
    maximum_width = Fraction(0)
    for interval in intervals:
        vertices = [point(value) for value in interval["vertices"]]
        pushed = [point(value) for value in interval["positive_push_off_vertices"]]
        maximum_width = max(
            maximum_width,
            *(sum(abs(value) for value in sub(push, centre)) for centre, push in zip(vertices, pushed)),
        )
        segments.extend(
            (interval["route_index"], segment_index, segment)
            for segment_index, segment in enumerate(zip(vertices, vertices[1:]))
        )
    minimum = None
    pair = None
    for first_index, (first_route, first_segment, first) in enumerate(segments):
        for second_route, second_segment, second in segments[first_index + 1 :]:
            if first_route == second_route:
                continue
            candidate = segment_distance_squared(first, second)
            if minimum is None or candidate < minimum:
                minimum = candidate
                pair = {
                    "first_route_index": first_route,
                    "first_segment_index": first_segment,
                    "second_route_index": second_route,
                    "second_segment_index": second_segment,
                }
    if minimum is None or pair is None:
        raise AssertionError("no distinct centre segments for clearance audit")
    threshold = (2 * maximum_width) ** 2
    if minimum <= MIN_ROUTE_CLEARANCE**2:
        raise AssertionError("centre routes violate the promised construction clearance")
    if minimum <= threshold:
        raise AssertionError("the ruled-ribbon width exceeds the route clearance")
    return {
        "method": "exact centre-segment distance and L1 tubular-width bound",
        "minimum_centre_segment_distance_squared": str(minimum),
        "attaining_segment_pair": pair,
        "maximum_vertex_l1_push_width": str(maximum_width),
        "twice_width_squared": str(threshold),
        "strict_clearance": True,
        "conclusion": "ruled ribbons belonging to distinct exterior intervals are disjoint",
    }


def segment_intersects(first, second):
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
            return add(p, tuple(t * value for value in r)) == add(
                q, tuple(u * value for value in s)
            )
        return False
    return cross(sub(q, p), r) == (0, 0, 0)


def inside_box(value, lower, upper, strict=False):
    if strict:
        return all(lower[i] < value[i] < upper[i] for i in range(3))
    return all(lower[i] <= value[i] <= upper[i] for i in range(3))


def segment_meets_box_interior(segment, bounds):
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
        low, high = max(low, a), min(high, b)
    epsilon = Fraction(1, 10**12)
    return max(low, epsilon) < min(high, 1 - epsilon)


def expected_cycles(all_owner):
    result = {}
    for owner in ("m_2", "r_xy"):
        base = all_owner["primitive_geometry"][owner]["reduced_events"]
        for copy_sign in ("negative", "positive"):
            order = list(range(len(base))) if copy_sign == "positive" else list(reversed(range(len(base))))
            result[f"{owner}:{copy_sign}"] = (base, order)
    return result


def validate(data, all_owner, check_route_pairs=True):
    if data["schema"] != "t73_selected_source_exterior/v1":
        raise AssertionError("unexpected source-exterior schema")
    if data["all_owner_primitives_sha256"] != all_owner["sha256"]:
        raise AssertionError("source exterior is stale relative to reduced events")
    if data["canonical_representative_only"] is not True:
        raise AssertionError("source exterior overclaims canonicality")
    if data["actual_ar_relative_isotopy_proved"] is not False:
        raise AssertionError("source exterior improperly claims the AR relative isotopy")
    if data["contains_braid_word"] is not False:
        raise AssertionError("source exterior contains auxiliary braid data")
    clearance = data.get("ribbon_clearance", {})
    if (
        clearance.get("strict_clearance") is not True
        or clearance.get("method")
        != "exact centre-segment distance and L1 tubular-width bound"
    ):
        raise AssertionError("source exterior has no ruled-ribbon clearance certificate")
    expected = expected_cycles(all_owner)
    cycles = {cycle["cycle_id"]: cycle for cycle in data["cycles"]}
    if set(cycles) != set(expected):
        raise AssertionError("the four cable component cycles changed")
    occurrence_lookup = {}
    handle_counts = Counter()
    for cycle_id, (base, order) in expected.items():
        cycle = cycles[cycle_id]
        if cycle["event_count"] != len(order) or len(cycle["occurrences"]) != len(order):
            raise AssertionError("cycle event count changed")
        copy_sign = cycle["copy_sign"]
        multiplier = 1 if copy_sign == "positive" else -1
        for traversal_index, (occurrence, base_index) in enumerate(zip(cycle["occurrences"], order)):
            event = base[base_index]
            orientation = multiplier * int(event["orientation"])
            if (
                occurrence["traversal_index"] != traversal_index
                or occurrence["base_event_index"] != base_index
                or occurrence["source_id"] != event["source_id"]
                or occurrence["handle"] != event["label"].upper()
                or occurrence["base_orientation"] != int(event["orientation"])
                or occurrence["effective_orientation"] != orientation
            ):
                raise AssertionError("occurrence provenance or orientation changed")
            expected_sides = ("minus", "plus") if orientation > 0 else ("plus", "minus")
            if (
                occurrence["entry_sphere"] != f"{occurrence['handle']}_{expected_sides[0]}"
                or occurrence["exit_sphere"] != f"{occurrence['handle']}_{expected_sides[1]}"
            ):
                raise AssertionError("entry/exit side disagrees with effective orientation")
            if occurrence["occurrence_id"] in occurrence_lookup:
                raise AssertionError("duplicate occurrence ID")
            occurrence_lookup[occurrence["occurrence_id"]] = occurrence
            handle_counts[occurrence["handle"]] += 1
    if handle_counts != {"Y": 88, "Z": 542}:
        raise AssertionError("cabled y/z passage counts changed")

    sphere_lookup = {}
    endpoint_lookup = {}
    endpoint_roles = Counter()
    expected_sphere_counts = {"Y_minus": 88, "Y_plus": 88, "Z_minus": 542, "Z_plus": 542}
    for sphere in data["insertion_spheres"]:
        name = sphere["name"]
        if name in sphere_lookup:
            raise AssertionError("duplicate insertion sphere")
        sphere_lookup[name] = sphere
        lower, upper = point(sphere["box_lower"]), point(sphere["box_upper"])
        face = Fraction(sphere["designated_face_value"])
        if sphere["endpoint_count"] != len(sphere["endpoints"]):
            raise AssertionError("sphere endpoint count is stale")
        seen_points = set()
        for index, endpoint in enumerate(sphere["endpoints"]):
            value = point(endpoint["point"])
            pushed = point(endpoint["positive_push_off_point"])
            if endpoint["sphere_index"] != index or value[0] != face:
                raise AssertionError("endpoint index or designated face changed")
            if not (lower[1] < value[1] < upper[1] and lower[2] < value[2] < upper[2]):
                raise AssertionError("endpoint is outside the insertion face")
            if value in seen_points or pushed in seen_points:
                raise AssertionError("endpoint or push-off collision on insertion sphere")
            seen_points.add(value)
            if endpoint["endpoint_id"] in endpoint_lookup:
                raise AssertionError("duplicate endpoint ID")
            endpoint_lookup[endpoint["endpoint_id"]] = value
            endpoint_roles[endpoint["role"]] += 1
            occurrence = occurrence_lookup[endpoint["occurrence_id"]]
            expected_id = occurrence[f"{endpoint['role']}_endpoint_id"]
            expected_sphere = occurrence[f"{endpoint['role']}_sphere"]
            if endpoint["endpoint_id"] != expected_id or name != expected_sphere:
                raise AssertionError("endpoint is not bound to the occurrence side")
    if {name: item["endpoint_count"] for name, item in sphere_lookup.items()} != expected_sphere_counts:
        raise AssertionError("per-sphere endpoint counts changed")
    if endpoint_roles != {"entry": 630, "exit": 630} or len(endpoint_lookup) != 1260:
        raise AssertionError("endpoint incidence is not complete")
    if data["total_boundary_endpoint_count"] != 1260:
        raise AssertionError("total boundary endpoint count changed")

    intervals = data["exterior_intervals"]
    if len(intervals) != 630 or data["exterior_interval_count"] != 630:
        raise AssertionError("exterior interval count changed")
    from_counts, to_counts = Counter(), Counter()
    center_segments, push_segments = [], []
    inner_boxes = [
        (point(sphere["box_lower"]), point(sphere["box_upper"]))
        for sphere in data["insertion_spheres"]
    ]
    outer = data["ambient"]["outer_ball"]
    outer_bounds = (point(outer["lower"]), point(outer["upper"]))
    cycle_interval_counts = Counter()
    for route_index, interval in enumerate(intervals):
        if interval["route_index"] != route_index:
            raise AssertionError("route indices changed")
        cycle = cycles[interval["cycle_id"]]
        occurrences = cycle["occurrences"]
        index = int(interval["interval_id"].rsplit(":", 1)[1])
        current = occurrences[index]
        following = occurrences[(index + 1) % len(occurrences)]
        if (
            interval["from_occurrence_id"] != current["occurrence_id"]
            or interval["to_occurrence_id"] != following["occurrence_id"]
            or interval["from_endpoint_id"] != current["exit_endpoint_id"]
            or interval["to_endpoint_id"] != following["entry_endpoint_id"]
            or interval["cyclic_seam"] != (index == len(occurrences) - 1)
        ):
            raise AssertionError("exterior interval does not match consecutive cyclic events")
        expected_type = (
            "active_y_z"
            if current["handle"] != following["handle"]
            else "residual_z_z"
        )
        if interval["interval_type"] != expected_type:
            raise AssertionError("exterior interval type changed")
        vertices = [point(value) for value in interval["vertices"]]
        pushed = [point(value) for value in interval["positive_push_off_vertices"]]
        boundary_normal = point(interval["boundary_product_normal"])
        normal_vertices = [point(value) for value in interval["framing_normal_vertices"]]
        if (
            len(vertices) != 3
            or len(pushed) != 3
            or len(normal_vertices) != 3
            or boundary_normal == (0, 0, 0)
            or normal_vertices[0] != boundary_normal
            or normal_vertices[2] != boundary_normal
            or any(value == (0, 0, 0) for value in normal_vertices)
        ):
            raise AssertionError("route or product normal is incomplete")
        if vertices[0] != endpoint_lookup[interval["from_endpoint_id"]] or vertices[-1] != endpoint_lookup[interval["to_endpoint_id"]]:
            raise AssertionError("route endpoints disagree with the matching")
        if any(pushed[i] != add(vertices[i], normal_vertices[i]) for i in range(3)):
            raise AssertionError("route push-off does not extend the recorded normal field")
        expected_ribbon = [
            [vertices[index], vertices[index + 1], pushed[index + 1]]
            for index in range(2)
        ] + [
            [vertices[index], pushed[index + 1], pushed[index]]
            for index in range(2)
        ]
        ribbon = [
            [point(vertex) for vertex in triangle]
            for triangle in interval.get("ruled_ribbon_triangles", [])
        ]
        if ribbon != expected_ribbon or any(
            cross(sub(triangle[1], triangle[0]), sub(triangle[2], triangle[0]))
            == (0, 0, 0)
            for triangle in ribbon
        ):
            raise AssertionError("ruled framing ribbon is absent or degenerate")
        expected_boundary = {
            "core_vertices": interval["vertices"],
            "push_off_vertices": interval["positive_push_off_vertices"],
            "initial_transverse_edge": [
                interval["vertices"][0],
                interval["positive_push_off_vertices"][0],
            ],
            "terminal_transverse_edge": [
                interval["vertices"][-1],
                interval["positive_push_off_vertices"][-1],
            ],
        }
        if interval.get("ruled_ribbon_boundary") != expected_boundary:
            raise AssertionError("ruled framing ribbon boundary is incomplete")
        if interval["relative_twist"] != 0:
            raise AssertionError("route relative twist changed")
        if any(not inside_box(value, *outer_bounds, strict=True) for value in vertices + pushed):
            raise AssertionError("route leaves the outer ball")
        segments = list(zip(vertices, vertices[1:]))
        psegments = list(zip(pushed, pushed[1:]))
        if any(segment_meets_box_interior(segment, bounds) for segment in segments + psegments for bounds in inner_boxes):
            raise AssertionError("route enters an insertion-ball interior")
        center_segments.extend((route_index, segment) for segment in segments)
        push_segments.extend((route_index, segment) for segment in psegments)
        from_counts[interval["from_endpoint_id"]] += 1
        to_counts[interval["to_endpoint_id"]] += 1
        cycle_interval_counts[interval["cycle_id"]] += 1
    exit_ids = {occ["exit_endpoint_id"] for cycle in cycles.values() for occ in cycle["occurrences"]}
    entry_ids = {occ["entry_endpoint_id"] for cycle in cycles.values() for occ in cycle["occurrences"]}
    if set(from_counts) != exit_ids or set(from_counts.values()) != {1}:
        raise AssertionError("not every exit endpoint is used exactly once")
    if set(to_counts) != entry_ids or set(to_counts.values()) != {1}:
        raise AssertionError("not every entry endpoint is used exactly once")
    if cycle_interval_counts != {cycle_id: cycle["event_count"] for cycle_id, cycle in cycles.items()}:
        raise AssertionError("cycle interval counts changed")
    expected_by_copy = {
        copy_sign: {"active_y_z": 88, "residual_z_z": 227}
        for copy_sign in ("negative", "positive")
    }
    actual_by_copy = {
        copy_sign: {
            interval_type: sum(
                interval["copy_sign"] == copy_sign
                and interval["interval_type"] == interval_type
                for interval in intervals
            )
            for interval_type in ("active_y_z", "residual_z_z")
        }
        for copy_sign in ("negative", "positive")
    }
    if data["interval_counts_by_copy"] != expected_by_copy or actual_by_copy != expected_by_copy:
        raise AssertionError("each closure must contain 88 active and 227 residual intervals")
    seams = [item for item in intervals if item["cyclic_seam"]]
    if len(seams) != 4 or data["cyclic_seam_count"] != 4:
        raise AssertionError("there is not one cyclic seam per cable component")
    positive_m2 = next(item for item in seams if item["cycle_id"] == "m_2:positive")
    negative_m2 = next(item for item in seams if item["cycle_id"] == "m_2:negative")
    if [positive_m2["from_source_id"], positive_m2["to_source_id"]] != ["m_2:C_i", "c1:letter:0"]:
        raise AssertionError("positive m2 cyclic connector changed")
    if [negative_m2["from_source_id"], negative_m2["to_source_id"]] != ["c1:letter:0", "m_2:C_i"]:
        raise AssertionError("negative m2 cyclic connector changed")
    if check_route_pairs:
        for (first_route, first), (second_route, second) in itertools.combinations(center_segments, 2):
            if first_route != second_route and segment_intersects(first, second):
                raise AssertionError("two canonical centre routes intersect")
        for (first_route, first), (second_route, second) in itertools.combinations(push_segments, 2):
            if first_route != second_route and segment_intersects(first, second):
                raise AssertionError("two canonical push-off routes intersect")
        for _, first in center_segments:
            for _, second in push_segments:
                if segment_intersects(first, second):
                    raise AssertionError("canonical route meets a framing push-off")
        if data.get("ribbon_clearance") != clearance_certificate(intervals):
            raise AssertionError("stored ruled-ribbon clearance certificate is stale")
    return {
        "CYCLES": 4,
        "CABLED_PASSAGES": {"y": 88, "z": 542},
        "SPHERE_ENDPOINTS": expected_sphere_counts,
        "TOTAL_ENDPOINTS": 1260,
        "EXTERIOR_INTERVALS": 630,
        "INTERVAL_COUNTS_BY_COPY": expected_by_copy,
        "CYCLIC_SEAMS": 4,
        "FULL_MATCHING": "PASS",
        "RATIONAL_ROUTES": "PASS",
        "PRODUCT_NORMALS": "PASS",
        "RULED_RIBBON_TRIANGLES": 2520,
        "DISTINCT_RULED_RIBBONS": "PASS",
        "ACTUAL_AR_RELATIVE_ISOTOPY": "OPEN",
    }


def mutations(data, all_owner):
    cases = {}
    mutant = copy.deepcopy(data)
    mutant["insertion_spheres"][0]["endpoints"][1]["point"] = mutant["insertion_spheres"][0]["endpoints"][0]["point"]
    cases["endpoint_collision"] = mutant
    mutant = copy.deepcopy(data)
    mutant["cycles"][0]["occurrences"][0]["effective_orientation"] *= -1
    cases["orientation"] = mutant
    mutant = copy.deepcopy(data)
    mutant["exterior_intervals"][0]["to_endpoint_id"] = mutant["exterior_intervals"][1]["to_endpoint_id"]
    cases["matching"] = mutant
    mutant = copy.deepcopy(data)
    seam = next(item for item in mutant["exterior_intervals"] if item["cycle_id"] == "m_2:positive" and item["cyclic_seam"])
    seam["to_source_id"] = "wrong:cyclic:target"
    cases["cyclic_seam"] = mutant
    mutant = copy.deepcopy(data)
    mutant["exterior_intervals"][1]["vertices"] = copy.deepcopy(mutant["exterior_intervals"][0]["vertices"])
    cases["route_collision"] = mutant
    mutant = copy.deepcopy(data)
    mutant["exterior_intervals"][0]["boundary_product_normal"] = ["0", "0", "0"]
    cases["normal"] = mutant
    mutant = copy.deepcopy(data)
    mutant["ribbon_clearance"]["strict_clearance"] = False
    cases["ribbon_clearance"] = mutant
    mutant = copy.deepcopy(data)
    mutant["exterior_intervals"][0]["ruled_ribbon_triangles"][0][2] = copy.deepcopy(
        mutant["exterior_intervals"][0]["ruled_ribbon_triangles"][0][1]
    )
    cases["ribbon_triangle"] = mutant
    mutant = copy.deepcopy(data)
    mutant["actual_ar_relative_isotopy_proved"] = True
    cases["scope_promotion"] = mutant
    results = {}
    for name, candidate in cases.items():
        try:
            validate(candidate, all_owner, check_route_pairs=name == "route_collision")
        except AssertionError:
            results[name] = "FAIL"
        else:
            results[name] = "UNDETECTED"
    return results


def verify():
    builder = load_builder()
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    all_owner = json.loads(PRIMITIVES.read_text(encoding="utf-8"))
    if stored != builder.build():
        raise AssertionError("committed source exterior differs from live reconstruction")
    checks = validate(stored, all_owner, check_route_pairs=True)
    mutation_results = mutations(stored, all_owner)
    if set(mutation_results.values()) != {"FAIL"}:
        raise AssertionError(f"a source-exterior mutation survived: {mutation_results}")
    return {
        "T73_SELECTED_SOURCE_EXTERIOR": "PASS_CANONICAL_REPRESENTATIVE",
        **checks,
        "MUTATIONS": mutation_results,
        "SHA256": stored["sha256"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.check:
        for key, value in result.items():
            print(f"{key}={value}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
