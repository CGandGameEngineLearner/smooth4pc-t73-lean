#!/usr/bin/env python3
"""GMP exact verifier for transition/transition framing ribbons."""

from __future__ import annotations

import gzip
import json
import os
import sys
from pathlib import Path

from gmpy2 import mpq


ROOT = Path(__file__).resolve().parents[1]
PUSH = ROOT / "audit/t73_x_m1_negative_transition_push_paths_v3_receipt.json"
PARTITION = ROOT / "audit/t73_x_m1_transition_ribbon_exact_candidate_partition.json"


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def point(value):
    return tuple(mpq(coordinate) for coordinate in value)


def subtract(first, second):
    return tuple(a - b for a, b in zip(first, second))


def cross3(first, second):
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def dot(first, second):
    return sum(a * b for a, b in zip(first, second))


def det(first, second, third):
    return dot(first, cross3(second, third))


def quotient(value):
    return value[0] - value[1], 2 * value[0] - value[2]


def cross2(first, second):
    return first[0] * second[1] - first[1] * second[0]


def interpolate_x(first, second, parameter):
    return first[0] + parameter * (second[0] - first[0])


def constant_intersection(first, second, delta):
    a, b = first
    c, d = second
    qa, qb, qc, qd = quotient(a), quotient(b), quotient(c), quotient(d)
    u = (qb[0] - qa[0], qb[1] - qa[1])
    v = (qd[0] - qc[0], qd[1] - qc[1])
    w = (qc[0] - qa[0], qc[1] - qa[1])
    denominator = cross2(u, v)
    if denominator:
        first_parameter = cross2(w, v) / denominator
        second_parameter = cross2(w, u) / denominator
        if not (0 <= first_parameter <= 1 and 0 <= second_parameter <= 1):
            return False
        gap = abs(
            interpolate_x(a, b, first_parameter)
            - interpolate_x(c, d, second_parameter)
        )
        return gap <= delta
    if cross2(w, u):
        return False
    axis = 0 if u[0] else 1
    low = max(min(qa[axis], qb[axis]), min(qc[axis], qd[axis]))
    high = min(max(qa[axis], qb[axis]), max(qc[axis], qd[axis]))
    if low > high:
        return False

    def lift(value, start, end, q_start, q_end):
        return start[0] + (value - q_start) * (end[0] - start[0]) / (q_end - q_start)

    differences = (
        lift(low, a, b, qa[axis], qb[axis]) - lift(low, c, d, qc[axis], qd[axis]),
        lift(high, a, b, qa[axis], qb[axis]) - lift(high, c, d, qc[axis], qd[axis]),
    )
    minimum = mpq(0) if differences[0] * differences[1] <= 0 else min(map(abs, differences))
    return minimum <= delta


def orient(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def segment2(first, second):
    a, b = first
    c, d = second
    values = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)

    def boxed(p, q, r):
        return min(p[0], q[0]) <= r[0] <= max(p[0], q[0]) and min(p[1], q[1]) <= r[1] <= max(p[1], q[1])

    return (
        (values[0] == 0 and boxed(a, b, c))
        or (values[1] == 0 and boxed(a, b, d))
        or (values[2] == 0 and boxed(c, d, a))
        or (values[3] == 0 and boxed(c, d, b))
        or ((values[0] < 0) != (values[1] < 0) and (values[2] < 0) != (values[3] < 0))
    )


def project2(value, drop):
    return tuple(value[axis] for axis in range(3) if axis != drop)


def point_in_triangle(value, triangle):
    signs = [orient(triangle[index], triangle[(index + 1) % 3], value) for index in range(3)]
    return all(item >= 0 for item in signs) or all(item <= 0 for item in signs)


def segment_triangle(segment, triangle):
    p, q = segment
    a, b, c = triangle
    direction, u, v, rhs = subtract(q, p), subtract(b, a), subtract(c, a), subtract(a, p)
    minus_u, minus_v = tuple(-value for value in u), tuple(-value for value in v)
    denominator = det(direction, minus_u, minus_v)
    if denominator:
        parameter = det(rhs, minus_u, minus_v) / denominator
        alpha = det(direction, rhs, minus_v) / denominator
        beta = det(direction, minus_u, rhs) / denominator
        return 0 <= parameter <= 1 and alpha >= 0 and beta >= 0 and alpha + beta <= 1
    normal = cross3(u, v)
    if dot(normal, subtract(p, a)) or dot(normal, subtract(q, a)):
        return False
    drop = max(range(3), key=lambda axis: abs(normal[axis]))
    segment2d = project2(p, drop), project2(q, drop)
    triangle2d = tuple(project2(value, drop) for value in triangle)
    return (
        point_in_triangle(segment2d[0], triangle2d)
        or point_in_triangle(segment2d[1], triangle2d)
        or any(segment2(segment2d, (triangle2d[index], triangle2d[(index + 1) % 3])) for index in range(3))
    )


def triangles_intersect(first, second):
    return any(segment_triangle((first[index], first[(index + 1) % 3]), second) for index in range(3)) or any(
        segment_triangle((second[index], second[(index + 1) % 3]), first) for index in range(3)
    )


def load_geometry(path):
    records = []
    with gzip.open(path, "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            records.append({
                "vertices": [point(value) for value in record["core_vertices"] + record["push_vertices"]],
                "triangles": record["ribbon_triangles"],
            })
    return records


def rectangle(records, index):
    record, segment = divmod(index, 6)
    vertices = records[record]["vertices"]
    size = len(vertices) // 2
    return (vertices[segment], vertices[segment + 1]), (vertices[size + segment], vertices[size + segment + 1])


def triangle(records, index):
    record, local = divmod(index, 12)
    values = records[record]
    return tuple(values["vertices"][vertex] for vertex in values["triangles"][local])


def verify():
    push = json.loads(PUSH.read_text())
    partition = json.loads(PARTITION.read_text())
    records = load_geometry(resolve(push["cache_path"]))
    first_core, first_push = rectangle(records, 0)
    displacement = subtract(first_push[0], first_core[0])
    delta = displacement[0]
    constant_checks = 0
    with gzip.open(resolve(partition["constant_candidate_path"]), "rt", encoding="utf-8") as source:
        if source.readline().strip() != "constant_rectangle_pairs/v1":
            raise AssertionError("constant rectangle candidate schema changed")
        for line in source:
            first_index, second_index = (int(value) for value in line.split(","))
            first_core, first_push = rectangle(records, first_index)
            second_core, second_push = rectangle(records, second_index)
            if any(subtract(pushed, core) != displacement for core, pushed in zip(first_core + second_core, first_push + second_push)):
                raise AssertionError("constant candidate contains a variable normal")
            constant_checks += 1
            if constant_checks % 100_000 == 0 and os.environ.get("T73_PROGRESS"):
                print(f"constant rectangles {constant_checks}/{partition['constant_rectangle_pair_count']}", file=sys.stderr, flush=True)
            if constant_intersection(first_core, second_core, delta):
                return {
                    "verdict": "REFUTED_TRANSITION_RIBBON_GLOBAL_CLEARANCE",
                    "kind": "constant_rectangle",
                    "first": first_index,
                    "second": second_index,
                    "constant_checks_before_collision": constant_checks,
                }
    variable_checks = 0
    with gzip.open(resolve(partition["variable_candidate_path"]), "rt", encoding="utf-8") as source:
        if source.readline().strip() != "variable_triangle_pairs/v1":
            raise AssertionError("variable triangle candidate schema changed")
        for line in source:
            first_index, second_index = (int(value) for value in line.split(","))
            variable_checks += 1
            if triangles_intersect(triangle(records, first_index), triangle(records, second_index)):
                return {
                    "verdict": "REFUTED_TRANSITION_RIBBON_GLOBAL_CLEARANCE",
                    "kind": "variable_triangle",
                    "first": first_index,
                    "second": second_index,
                    "constant_checks": constant_checks,
                    "variable_checks_before_collision": variable_checks,
                }
    return {
        "verdict": "PASS_TRANSITION_TRANSITION_RIBBON_EXACT_CLEARANCE",
        "constant_rectangle_checks": constant_checks,
        "variable_triangle_checks": variable_checks,
        "intersections": 0,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
