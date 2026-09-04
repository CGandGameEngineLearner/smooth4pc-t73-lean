#!/usr/bin/env python3
"""Verify the complete selected target canopolis template exactly."""

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
ARTIFACT = ROOT / "geometry" / "t73_selected_canopolis_normal_form.json"
PRIMITIVES = ROOT / "geometry" / "t73_all_owner_product_primitives.json"


def load_builder():
    path = ROOT / "scripts" / "build_t73_selected_canopolis_normal_form.py"
    spec = importlib.util.spec_from_file_location("canopolis_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def point(raw):
    return tuple(Fraction(value) for value in raw)


def add(a, b):
    return tuple(a[index] + b[index] for index in range(3))


def sub(a, b):
    return tuple(a[index] - b[index] for index in range(3))


def scale(value, scalar):
    return tuple(scalar * item for item in value)


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def inside(value, lower, upper, strict=False):
    if strict:
        return all(lower[index] < value[index] < upper[index] for index in range(3))
    return all(lower[index] <= value[index] <= upper[index] for index in range(3))


def disjoint_boxes(left, right):
    return any(
        left[1][index] < right[0][index] or right[1][index] < left[0][index]
        for index in range(3)
    )


def segment_intersects(first, second):
    """Exact closed-segment intersection in Q^3."""
    p, p2 = first
    q, q2 = second
    r, s, d = sub(p2, p), sub(q2, q), sub(q, p)
    if r == (0, 0, 0) or s == (0, 0, 0):
        raise AssertionError("zero-length target segment")
    if cross(r, s) != (0, 0, 0):
        for a, b in ((0, 1), (0, 2), (1, 2)):
            determinant = r[b] * s[a] - r[a] * s[b]
            if determinant == 0:
                continue
            t = (-d[a] * s[b] + d[b] * s[a]) / determinant
            u = (r[a] * d[b] - r[b] * d[a]) / determinant
            return 0 <= t <= 1 and 0 <= u <= 1 and add(p, scale(r, t)) == add(q, scale(s, u))
        raise AssertionError("nonparallel segments had no nonsingular coordinate minor")
    if cross(d, r) != (0, 0, 0):
        return False
    axis = next(index for index, value in enumerate(r) if value != 0)
    first_t = (q[axis] - p[axis]) / r[axis]
    second_t = (q2[axis] - p[axis]) / r[axis]
    low, high = sorted((first_t, second_t))
    return max(Fraction(0), low) <= min(Fraction(1), high)


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
        first = (lower[axis] - start[axis]) / direction[axis]
        second = (upper[axis] - start[axis]) / direction[axis]
        if first > second:
            first, second = second, first
        low, high = max(low, first), min(high, second)
    epsilon = Fraction(1, 10**12)
    return max(low, epsilon) < min(high, 1 - epsilon)


def validate(data, all_owner, check_pairwise=True):
    if data["schema"] != "t73_selected_canopolis_normal_form/v2":
        raise AssertionError("unexpected canopolis normal-form schema")
    if data["dependencies"]["all_owner_primitives_sha256"] != all_owner["sha256"]:
        raise AssertionError("normal form is stale relative to all-owner primitives")
    if data["contains_braid_word"] is not False or any(
        key in data for key in ("B44", "braid", "braid_word", "crossings")
    ):
        raise AssertionError("target template contains detector braid data")
    if (
        data["primitive_count"],
        data["active_corridor_count_per_closure"],
        data["added_z_arc_count_per_closure"],
        data["target_strand_count"],
    ) != (315, 88, 227, 630):
        raise AssertionError("selected target counts changed")

    primitives = data["primitives"]
    if len(primitives) != 315 or len({item["primitive_id"] for item in primitives}) != 315:
        raise AssertionError("primitive IDs are incomplete or duplicated")
    if Counter(item["role"] for item in primitives) != {
        "active_yz_corridor": 88,
        "added_z_arc": 227,
    }:
        raise AssertionError("primitive roles changed")
    cyclic = [item for item in primitives if item["is_cyclic_m2_connector"]]
    if len(cyclic) != 2 or any(
        item["source_ids"] != ["m_2:C_i", "c1:letter:0"] for item in cyclic
    ):
        raise AssertionError("the two cyclic m2 ribbon sides are absent")
    if any(
        item["connector_kind"]
        != "cyclic_bottom_top_connector_after_t_cancellation"
        for item in cyclic
    ):
        raise AssertionError("cyclic m2 connector lost its collar type")
    if any(item["relative_twist"] != 0 for item in primitives):
        raise AssertionError("a primitive is not product framed")

    closure_boxes = {
        item["name"]: (point(item["lower"]), point(item["upper"]))
        for item in data["closure_balls"]
    }
    if set(closure_boxes) != {"left_closure", "right_closure"} or not disjoint_boxes(
        closure_boxes["left_closure"], closure_boxes["right_closure"]
    ):
        raise AssertionError("the two target closure balls are not disjoint")
    if not (
        closure_boxes["left_closure"][1][0]
        < 0
        < closure_boxes["right_closure"][0][0]
    ):
        raise AssertionError("x=0 does not separate the target closure balls")

    expected_endpoint_counts = {
        "Y_source": 88,
        "Z_target": 542,
        "Z_source": 542,
        "Y_target": 88,
    }
    balls = {}
    endpoints = {}
    endpoint_ball = {}
    for ball in data["insertion_balls"]:
        name = ball["name"]
        if name in balls:
            raise AssertionError("duplicate insertion ball")
        bounds = (point(ball["lower"]), point(ball["upper"]))
        balls[name] = bounds
        closure = closure_boxes[ball["closure"]]
        if not inside(bounds[0], *closure, strict=True) or not inside(
            bounds[1], *closure, strict=True
        ):
            raise AssertionError("an insertion ball is not inside its closure")
        records = ball["endpoints"]
        if ball["endpoint_count"] != len(records):
            raise AssertionError("an insertion-ball endpoint count is stale")
        face = Fraction(ball["designated_face_value"])
        seen_points = set()
        for index, record in enumerate(records):
            value = point(record["point"])
            pushed = point(record["positive_push_off_point"])
            if record["index"] != index or value[0] != face:
                raise AssertionError("endpoint order or designated face changed")
            if not (
                bounds[0][1] < value[1] < bounds[1][1]
                and bounds[0][2] < value[2] < bounds[1][2]
            ):
                raise AssertionError("endpoint lies outside its insertion face")
            if value in seen_points or record["endpoint_id"] in endpoints:
                raise AssertionError("target endpoint collision or duplicate ID")
            seen_points.add(value)
            endpoints[record["endpoint_id"]] = record
            endpoint_ball[record["endpoint_id"]] = name
            if pushed != add(value, point(data["product_normal"])):
                raise AssertionError("endpoint push-off is not the product normal")
    if set(balls) != set(expected_endpoint_counts):
        raise AssertionError("the four parametrized insertion balls are absent")
    for first, second in itertools.combinations(balls, 2):
        if not disjoint_boxes(balls[first], balls[second]):
            raise AssertionError("two insertion balls overlap")
    actual_endpoint_counts = {
        item["name"]: len(item["endpoints"]) for item in data["insertion_balls"]
    }
    if (
        actual_endpoint_counts != expected_endpoint_counts
        or data["endpoint_counts_per_insertion_ball"] != expected_endpoint_counts
        or data["total_boundary_endpoint_count"] != 1260
        or len(endpoints) != 1260
    ):
        raise AssertionError("the complete 88/542/542/88 incidence is absent")

    normal = point(data["product_normal"])
    if normal != (0, 0, Fraction(1, 10**7)):
        raise AssertionError("target product normal changed")
    all_center_segments = []
    all_push_segments = []
    endpoint_usage = Counter()
    for side, records in (
        ("left", data["left_closure_strands"]),
        ("right", data["right_closure_strands"]),
    ):
        if len(records) != 315:
            raise AssertionError(f"{side} closure does not have 315 arcs")
        closure = closure_boxes[f"{side}_closure"]
        allowed_active = (
            {"Y_source", "Z_target"}
            if side == "left"
            else {"Z_source", "Y_target"}
        )
        residual_ball = "Z_target" if side == "left" else "Z_source"
        for index, record in enumerate(records):
            primitive = primitives[index]
            if record["index"] != index or record["side"] != side:
                raise AssertionError("target arc index or side changed")
            for field in (
                "role",
                "primitive_id",
                "owner",
                "source_ids",
                "is_cyclic_m2_connector",
            ):
                if record[field] != primitive[field]:
                    raise AssertionError(f"target arc lost primitive field {field}")
            ids = record["endpoint_ids"]
            if len(ids) != 2 or any(endpoint_id not in endpoints for endpoint_id in ids):
                raise AssertionError("target arc has incomplete endpoint incidence")
            if record.get("orientation") != {
                "direction": "listed_vertex_order",
                "from_endpoint_id": ids[0],
                "to_endpoint_id": ids[1],
                "ribbon_side": primitive["ribbon_side"],
            }:
                raise AssertionError("target arc orientation is absent or inconsistent")
            if [endpoints[endpoint_id].get("oriented_incidence") for endpoint_id in ids] != [
                "initial",
                "terminal",
            ]:
                raise AssertionError("target endpoint oriented incidence changed")
            if primitive["role"] == "active_yz_corridor":
                if {endpoint_ball[endpoint_id] for endpoint_id in ids} != allowed_active:
                    raise AssertionError("active target arc is not Y--Z")
                expected_vertices = 2
            else:
                if {endpoint_ball[endpoint_id] for endpoint_id in ids} != {residual_ball}:
                    raise AssertionError("added target arc is not Z--Z")
                expected_vertices = 4
            vertices = [point(value) for value in record["centerline"]]
            pushed = [point(value) for value in record["positive_push_off"]]
            if len(vertices) != expected_vertices or len(pushed) != expected_vertices:
                raise AssertionError("target arc has the wrong PL shape")
            if vertices[0] != point(endpoints[ids[0]]["point"]) or vertices[-1] != point(
                endpoints[ids[1]]["point"]
            ):
                raise AssertionError("target arc endpoints disagree with incidence")
            if any(pushed[position] != add(vertex, normal) for position, vertex in enumerate(vertices)):
                raise AssertionError("target push-off does not extend the product normal")
            if record["relative_twist"] != 0 or point(record["product_normal"]) != normal:
                raise AssertionError("target framing is not the product framing")
            if any(not inside(vertex, *closure, strict=True) for vertex in vertices + pushed):
                raise AssertionError("target arc leaves its closure ball")
            segments = list(zip(vertices, vertices[1:]))
            push_segments = list(zip(pushed, pushed[1:]))
            for first, second in itertools.combinations(segments, 2):
                if first[1] != second[0] and segment_intersects(first, second):
                    raise AssertionError("a target arc self-intersects")
            for segment in segments + push_segments:
                for ball_name, bounds in balls.items():
                    if ball_name not in {endpoint_ball[ids[0]], endpoint_ball[ids[1]]}:
                        if segment_meets_box_interior(segment, bounds):
                            raise AssertionError("target arc enters an unrelated insertion ball")
            all_center_segments.extend((f"{side}:{index}", segment) for segment in segments)
            all_push_segments.extend((f"{side}:{index}", segment) for segment in push_segments)
            endpoint_usage.update(ids)
    if set(endpoint_usage) != set(endpoints) or set(endpoint_usage.values()) != {1}:
        raise AssertionError("not every target endpoint is used exactly once")

    if check_pairwise:
        for (first_id, first), (second_id, second) in itertools.combinations(
            all_center_segments, 2
        ):
            if first_id != second_id and segment_intersects(first, second):
                raise AssertionError("two target centre arcs intersect")
        for (first_id, first), (second_id, second) in itertools.combinations(
            all_push_segments, 2
        ):
            if first_id != second_id and segment_intersects(first, second):
                raise AssertionError("two target push-offs intersect")
        for _, first in all_center_segments:
            for _, second in all_push_segments:
                if segment_intersects(first, second):
                    raise AssertionError("a target centre arc meets a framing push-off")

    pattern = data["two_representable_pattern"]
    if not pattern["split_union_as_abstract_target_template"]:
        raise AssertionError("abstract target template is not split")
    if pattern["relative_source_isotopy_claimed"] is not False:
        raise AssertionError("target template overclaims a source isotopy")
    cyclic_indices = data["cyclic_connector"]["primitive_indices"]
    if len(cyclic_indices) != 2 or any(
        not 0 <= index < 88 or not primitives[index]["is_cyclic_m2_connector"]
        for index in cyclic_indices
    ):
        raise AssertionError("cyclic connector primitive indices are wrong")
    return {
        "FOUR_INSERTION_BALLS": "PASS",
        "TWO_DISJOINT_TARGET_CLOSURE_BALLS": "PASS",
        "TARGET_SEPARATING_SPHERE": "PASS",
        "ENDPOINT_COUNTS": expected_endpoint_counts,
        "TOTAL_ENDPOINTS": 1260,
        "TARGET_ARCS": 630,
        "ACTIVE_YZ_PER_CLOSURE": 88,
        "RESIDUAL_ZZ_PER_CLOSURE": 227,
        "CYCLIC_CONNECTOR": "PASS",
        "PAIRWISE_DISJOINT_ARCS": "PASS",
        "PRODUCT_FRAMINGS": "PASS",
        "BRAID_DATA": "ABSENT",
    }


def mutation_results(data, all_owner):
    cases = {}
    mutant = copy.deepcopy(data)
    mutant["primitives"][data["cyclic_connector"]["primitive_indices"][0]][
        "is_cyclic_m2_connector"
    ] = False
    cases["cyclic_connector"] = mutant
    mutant = copy.deepcopy(data)
    mutant["added_z_arc_count_per_closure"] = 226
    cases["added_count"] = mutant
    mutant = copy.deepcopy(data)
    mutant["insertion_balls"][0]["upper"][0] = "2"
    cases["box_separator"] = mutant
    mutant = copy.deepcopy(data)
    mutant["insertion_balls"][0]["endpoints"].pop()
    cases["endpoint_count"] = mutant
    mutant = copy.deepcopy(data)
    mutant["left_closure_strands"][88]["endpoint_ids"][0] = mutant[
        "left_closure_strands"
    ][0]["endpoint_ids"][0]
    cases["z_z_incidence"] = mutant
    mutant = copy.deepcopy(data)
    mutant["left_closure_strands"][1]["centerline"] = copy.deepcopy(
        mutant["left_closure_strands"][0]["centerline"]
    )
    cases["arc_collision"] = mutant
    mutant = copy.deepcopy(data)
    mutant["right_closure_strands"][0]["relative_twist"] = 1
    cases["framing"] = mutant
    mutant = copy.deepcopy(data)
    mutant["left_closure_strands"][0]["orientation"]["to_endpoint_id"] = mutant[
        "left_closure_strands"
    ][1]["endpoint_ids"][1]
    cases["orientation"] = mutant
    mutant = copy.deepcopy(data)
    mutant["two_representable_pattern"]["relative_source_isotopy_claimed"] = True
    cases["scope_promotion"] = mutant
    results = {}
    for name, candidate in cases.items():
        try:
            validate(candidate, all_owner, check_pairwise=name == "arc_collision")
        except (AssertionError, KeyError):
            results[name] = "FAIL"
        else:
            results[name] = "UNDETECTED"
    return results


def verify():
    builder = load_builder()
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    all_owner = json.loads(PRIMITIVES.read_text(encoding="utf-8"))
    if stored != builder.build():
        raise AssertionError("committed canopolis target differs from rebuild")
    checks = validate(stored, all_owner, check_pairwise=True)
    mutations = mutation_results(stored, all_owner)
    if set(mutations.values()) != {"FAIL"}:
        raise AssertionError(f"a canopolis mutation survived: {mutations}")
    return {
        "T73_SELECTED_CANOPOLIS_NORMAL_FORM": "PASS_COMPLETE_TARGET_TEMPLATE",
        **checks,
        "SOURCE_RELATIVE_ISOTOPY": "REFUTED_LITERAL_SPLIT",
        "DEFECT_AWARE_CURRYING": "OPEN",
        "GRADING_CORRECTION": "UNDETERMINED_UNTIL_CURRYING_CELLS",
        "MUTATIONS": mutations,
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
