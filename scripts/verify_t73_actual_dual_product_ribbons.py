#!/usr/bin/env python3
"""Independently verify the three actual pre-cancellation dual ribbons."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict, deque
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_actual_dual_product_ribbons.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
NAMES = ("r_xy", "r_yz", "r_zx")


def canonical_sha(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def cross(left, right):
    return (left[1] * right[2] - left[2] * right[1],
            left[2] * right[0] - left[0] * right[2],
            left[0] * right[1] - left[1] * right[0])


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    source = json.loads(AR_LINK.read_text(encoding="utf-8"))
    payload = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha(payload) or data["actual_ar_link_sha256"] != source["sha256"]:
        raise AssertionError("dual-ribbon hash/source binding changed")
    if [item["name"] for item in data["components"]] != list(NAMES):
        raise AssertionError("dual-ribbon component order changed")
    triangle_count = boundary_edges = 0
    for item in data["components"]:
        name = item["name"]
        source_item = source["components"][name]
        axis = source_item["disk"]["plane_axis"]
        plane = Fraction(source_item["disk"]["plane_value"])
        core = [point(value) for value in source_item["polyline"][:-1]]
        push = [point(value) for value in item["push_vertices"]]
        normal = point(item["product_normal"])
        if point(source_item["polyline"][0]) != point(source_item["polyline"][-1]):
            raise AssertionError("source dual boundary opened")
        if item["core_vertices"] != source_item["polyline"][:-1] or len(core) != 8:
            raise AssertionError("dual core vertices changed")
        if any(normal[index] != 0 for index in range(3) if index != axis) or normal[axis] <= 0:
            raise AssertionError("product normal is not the positive plane normal")
        if any(value[axis] != plane for value in core):
            raise AssertionError("core left source disk plane")
        if any(push[index] != tuple(core[index][coordinate] + normal[coordinate] for coordinate in range(3)) for index in range(8)):
            raise AssertionError("push-off is not the stated translation")
        if any(value[axis] != plane + normal[axis] for value in push):
            raise AssertionError("push-off left its translated disk plane")
        vertices = [point(value) for value in item["ribbon_vertices"]]
        triangles = [tuple(value) for value in item["ribbon_triangles"]]
        if vertices != core + push or len(triangles) != 16:
            raise AssertionError("ribbon cell count changed")
        edges = Counter()
        graph = defaultdict(set)
        for triangle in triangles:
            first, second, third = [vertices[index] for index in triangle]
            vectors = (tuple(second[i] - first[i] for i in range(3)),
                       tuple(third[i] - first[i] for i in range(3)))
            if cross(*vectors) == (0, 0, 0):
                raise AssertionError("degenerate dual-ribbon triangle")
            for edge in combinations(triangle, 2):
                edge = tuple(sorted(edge))
                edges[edge] += 1
                graph[edge[0]].add(edge[1]); graph[edge[1]].add(edge[0])
        boundary = [edge for edge, count in edges.items() if count == 1]
        if len(vertices) - len(edges) + len(triangles) != 0 or len(boundary) != 16 or max(edges.values()) != 2:
            raise AssertionError("ribbon is not a triangulated annulus")
        seen, queue = set(), deque([0])
        while queue:
            vertex = queue.popleft()
            if vertex not in seen:
                seen.add(vertex); queue.extend(graph[vertex] - seen)
        if len(seen) != 16:
            raise AssertionError("ribbon is disconnected")
        # The translated spanning disk lies in a plane disjoint from every
        # core point, so the core/push intersection number and linking are 0.
        if item["relative_twist"] != 0 or item["self_linking"] != 0:
            raise AssertionError("dual product framing changed")
        triangle_count += len(triangles)
        boundary_edges += len(boundary)
    if data["component_count"] != 3 or data["triangle_count"] != triangle_count:
        raise AssertionError("dual-ribbon totals changed")
    return {
        "verdict": "PASS_ACTUAL_PRE_CANCELLATION_DUAL_PRODUCT_RIBBONS",
        "components": 3,
        "triangles": triangle_count,
        "boundary_edges": boundary_edges,
        "self_linking": {name: 0 for name in NAMES},
        "post_cancellation_transport_status": data["post_cancellation_transport_status"],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
