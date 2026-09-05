#!/usr/bin/env python3
"""Independently verify the four framed marked-strip mapping cylinders."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict, deque
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_dotted_s3_foot_collars.json"
FOOT_MODEL = ROOT / "geometry/t73_ar_foot_pairing_model.json"
FINAL_FEET = ROOT / "geometry/t73_final_yz_foot_state.json"
AMBIENT = ROOT / "geometry/t73_dotted_disk_ambient_extensions.json"
DOTTED = ROOT / "geometry/t73_actual_dotted_s3_passage_cells.json"


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def apply_matrix(matrix, value):
    return tuple(sum(Fraction(entry) * coordinate for entry, coordinate in zip(row, value)) for row in matrix)


def cross(left, right):
    return (left[1] * right[2] - left[2] * right[1], left[2] * right[0] - left[0] * right[2], left[0] * right[1] - left[1] * right[0])


def disk_point(center, basis, lane_scale, uv):
    return tuple(center[axis] + lane_scale * uv[0] * basis[0][axis] + lane_scale * uv[1] * basis[1][axis] for axis in range(3))


def target_point(handle, physical_foot, uv):
    center = Fraction(-4 if handle == "y" else 4)
    if physical_foot == "positive":
        return (center - 2, uv[1], -Fraction(1, 2) + uv[0] / 10)
    return (center + 2, uv[1], Fraction(1, 2) + uv[0] / 10)


def verify():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    foot_model = json.loads(FOOT_MODEL.read_text(encoding="utf-8"))
    final_feet = json.loads(FINAL_FEET.read_text(encoding="utf-8"))
    ambient = json.loads(AMBIENT.read_text(encoding="utf-8"))
    dotted = json.loads(DOTTED.read_text(encoding="utf-8"))
    if data["sha256"] != canonical_sha({key: value for key, value in data.items() if key != "sha256"}):
        raise AssertionError("foot-collar payload SHA changed")
    expected_bindings = {
        "ar_foot_pairing_model_sha256": foot_model["sha256"],
        "final_yz_foot_state_sha256": final_feet["sha256"],
        "dotted_disk_ambient_extensions_sha256": ambient["sha256"],
        "actual_dotted_s3_passage_cells_sha256": dotted["sha256"],
    }
    if any(data[key] != value for key, value in expected_bindings.items()):
        raise AssertionError("foot-collar source binding changed")
    expected_tetrahedra = []
    for triangle in ((0, 1, 2), (0, 2, 3)):
        a, b, c = sorted(triangle)
        expected_tetrahedra.extend(((a, b, c, c + 4), (a, b, b + 4, c + 4), (a, a + 4, b + 4, c + 4)))
    faces = Counter(tuple(sorted(face)) for tetrahedron in expected_tetrahedra for face in combinations(tetrahedron, 3))
    boundary_faces = [face for face, count in faces.items() if count == 1]
    boundary_edges = {tuple(sorted(edge)) for face in boundary_faces for edge in combinations(face, 2)}
    boundary_vertices = {vertex for face in boundary_faces for vertex in face}
    if len(boundary_vertices) - len(boundary_edges) + len(boundary_faces) != 2 or max(faces.values()) != 2:
        raise AssertionError("collar template is not a tetrahedral 3-ball")
    adjacency = defaultdict(set)
    for first, second in boundary_edges:
        adjacency[first].add(second); adjacency[second].add(first)
    seen, queue = set(), deque([next(iter(boundary_vertices))])
    while queue:
        vertex = queue.popleft()
        if vertex not in seen:
            seen.add(vertex); queue.extend(adjacency[vertex] - seen)
    if seen != boundary_vertices:
        raise AssertionError("collar template boundary is disconnected")
    feet_by_index = {item["handle_index"]: item for item in foot_model["feet"]}
    final_by_handle = {item["name"]: item for item in final_feet["handles"]}
    dotted_by_handle = {item["handle"]: item for item in dotted["charts"]}
    collars = {(item["handle"], item["physical_foot"]): item for item in data["collars"]}
    if len(collars) != 4:
        raise AssertionError("foot-collar inventory changed")
    triangle_checks = reflection_checks = endpoint_checks = push_checks = 0
    for handle, final in final_by_handle.items():
        foot = feet_by_index[final["foot_handle_index"]]
        matrix = foot["reflection_matrix"]
        basis = tuple(point(value) for value in final["tangent_basis"])
        lane_scale = Fraction(foot["radius"]) / 10
        final_entries = {item["passage_id"]: item for item in final["passages"]}
        positive = collars[(handle, "positive")]
        negative = collars[(handle, "negative")]
        normalized = [point(value) for value in positive["normalized_strip_vertices"]]
        if negative["normalized_strip_vertices"] != positive["normalized_strip_vertices"]:
            raise AssertionError("paired collar domains changed")
        for collar in (positive, negative):
            if collar["slice_triangles"] != [[0, 1, 2], [0, 2, 3]] or collar["mapping_cylinder_tetrahedra"] != [list(value) for value in expected_tetrahedra]:
                raise AssertionError("collar triangulation changed")
            for embedding in ("source_disk_vertices", "target_chart_vertices"):
                values = [point(value) for value in collar[embedding]]
                for ids in collar["slice_triangles"]:
                    first, second, third = [values[index] for index in ids]
                    if cross(tuple(second[i] - first[i] for i in range(3)), tuple(third[i] - first[i] for i in range(3))) == (0, 0, 0):
                        raise AssertionError("collar boundary triangle degenerated")
                    triangle_checks += 1
        for p, n in zip(positive["source_disk_vertices"], negative["source_disk_vertices"]):
            if apply_matrix(matrix, point(p)) != point(n):
                raise AssertionError("source collar strips are not reflection paired")
            reflection_checks += 1
        v_low, v_high = normalized[0][1], normalized[2][1]
        delta = Fraction(dotted_by_handle[handle]["passage_push_delta"])
        passages = {item["passage_id"]: item for item in dotted_by_handle[handle]["passages"]}
        records = [item for item in data["endpoint_records"] if item["handle"] == handle]
        if len(records) != final["passage_count"]:
            raise AssertionError("foot-collar endpoint count changed")
        for record in records:
            passage = passages[record["passage_id"]]
            entry = final_entries[record["passage_id"]]
            uv, push_uv = point(record["normalized_slot"]), point(record["normalized_push_slot"])
            if record["owner"] != entry["component"] or record["orientation"] != entry["orientation"]:
                raise AssertionError("foot-collar passage provenance changed")
            if not (v_low < uv[1] < push_uv[1] < v_high) or push_uv != (uv[0], uv[1] + delta):
                raise AssertionError("marked point/push left the collar strip")
            passage_push = [point(value) for value in passage["push_vertices"]]
            if passage["orientation"] == 1:
                target_push = {"positive": passage_push[0], "negative": passage_push[1]}
            else:
                target_push = {"negative": passage_push[0], "positive": passage_push[1]}
            for physical_foot in ("positive", "negative"):
                values = record["feet"][physical_foot]
                source_endpoint = point(values["source_endpoint"])
                source_push = point(values["source_push_endpoint"])
                target_endpoint = point(values["target_endpoint"])
                target_push_endpoint = point(values["target_push_endpoint"])
                center = point(foot[f"{physical_foot}_center"])
                if source_endpoint != disk_point(center, basis, lane_scale, uv) or source_push != disk_point(center, basis, lane_scale, push_uv):
                    raise AssertionError("collar source embedding formula changed")
                if target_endpoint != target_point(handle, physical_foot, uv) or target_push_endpoint != target_point(handle, physical_foot, push_uv):
                    raise AssertionError("collar target embedding formula changed")
                if target_endpoint != point(passage["foot_to_chart_endpoint_map"][physical_foot]) or target_push_endpoint != target_push[physical_foot]:
                    raise AssertionError("collar target does not meet dotted passage ribbon")
                if source_push == source_endpoint or target_push_endpoint == target_endpoint:
                    raise AssertionError("collar framing vector vanished")
                endpoint_checks += 1; push_checks += 1
            if apply_matrix(matrix, point(record["feet"]["positive"]["source_endpoint"])) != point(record["feet"]["negative"]["source_endpoint"]):
                raise AssertionError("marked endpoints lost foot reflection")
            if apply_matrix(matrix, point(record["feet"]["positive"]["source_push_endpoint"])) != point(record["feet"]["negative"]["source_push_endpoint"]):
                raise AssertionError("pushed endpoints lost foot reflection")
            reflection_checks += 2
    if (len(data["endpoint_records"]), endpoint_checks, push_checks) != (1785, 3570, 3570):
        raise AssertionError("foot-collar endpoint totals changed")
    if data["collar_count"] != 4 or data["mapping_cylinder_tetrahedron_count"] != 24 or data["endpoint_pair_count"] != 3570:
        raise AssertionError("foot-collar aggregate counts changed")
    return {
        "verdict": "PASS_REFLECTION_PAIRED_FRAMED_MARKED_STRIP_COLLARS_TO_DOTTED_S3",
        "collars": 4,
        "mapping_cylinder_tetrahedra": 24,
        "passages": 1785,
        "endpoint_checks": endpoint_checks,
        "push_endpoint_checks": push_checks,
        "reflection_checks": reflection_checks,
        "boundary_triangle_checks": triangle_checks,
        "scope_boundary": data["scope_boundary"],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
