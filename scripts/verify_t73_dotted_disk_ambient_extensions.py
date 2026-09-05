#!/usr/bin/env python3
"""Independently verify the reflection-paired dotted-disk PL extensions."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict, deque
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_dotted_disk_ambient_extensions.json"
TRACKS = ROOT / "geometry/t73_foot_to_dotted_disk_tracks.json"
SLOTS = ROOT / "geometry/t73_foot_to_dotted_slot_map.json"
FOOT_CHART = ROOT / "geometry/t73_unified_kirby_foot_chart.json"

sys.set_int_max_str_digits(0)


def canonical_sha(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest().upper()


def payload_sha(value: dict) -> str:
    return canonical_sha({key: item for key, item in value.items() if key != "sha256"})


def point(values):
    return tuple(Fraction(value) for value in values)


def lies_on_segment(value, start, end):
    direction = (end[0] - start[0], end[1] - start[1])
    delta = (value[0] - start[0], value[1] - start[1])
    axis = next((index for index, coordinate in enumerate(direction) if coordinate), None)
    if axis is None:
        return value == start
    parameter = delta[axis] / direction[axis]
    return 0 <= parameter <= 1 and all(
        delta[index] == parameter * direction[index] for index in range(2)
    )


def apply_matrix(matrix, value):
    return tuple(
        sum(Fraction(entry) * coordinate for entry, coordinate in zip(row, value))
        for row in matrix
    )


def determinant(vectors):
    a, b, c = vectors
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def verify_template(template: dict, radius: Fraction):
    expected_triangles = [(0, 1 + i, 1 + (i + 1) % 4) for i in range(4)]
    for i in range(4):
        expected_triangles.extend(((1 + i, 5 + i, 5 + (i + 1) % 4),
                                   (1 + i, 5 + (i + 1) % 4, 1 + (i + 1) % 4)))
    expected_tetrahedra = []
    for triangle in expected_triangles:
        a, b, c = sorted(triangle)
        expected_tetrahedra.extend(((a, b, c, c + 9),
                                    (a, b, b + 9, c + 9),
                                    (a, a + 9, b + 9, c + 9)))
    if template["slice_triangles"] != [list(item) for item in expected_triangles]:
        raise AssertionError("disk slice triangulation changed")
    if template["spacetime_tetrahedra"] != [list(item) for item in expected_tetrahedra]:
        raise AssertionError("prism triangulation changed")

    vertices = []
    for index, record in enumerate(template["coefficient_vertices"]):
        if record["time"] != index // 9:
            raise AssertionError("template time slice changed")
        vertices.append((
            Fraction(record["s_constant"]) + Fraction(record["s_scale"]) * radius,
            Fraction(record["u_scale"]) * radius,
            Fraction(record["time"]),
        ))
    if len(vertices) != 18 or vertices[0] != (0, 0, 0) or vertices[9] != (1, 0, 1):
        raise AssertionError("marked core endpoints changed")
    if any(vertices[index][:2] != vertices[index + 9][:2] for index in range(5, 9)):
        raise AssertionError("outer support boundary is not pointwise fixed")

    for offset in (0, 9):
        for a, b, c in expected_triangles:
            va, vb, vc = vertices[a + offset], vertices[b + offset], vertices[c + offset]
            area = (vb[0] - va[0]) * (vc[1] - va[1]) - (vb[1] - va[1]) * (vc[0] - va[0])
            if area <= 0:
                raise AssertionError("a disk slice triangle changed orientation")

    face_counts = Counter()
    for tetrahedron in expected_tetrahedra:
        base = vertices[tetrahedron[0]]
        vectors = [tuple(vertices[index][axis] - base[axis] for axis in range(3))
                   for index in tetrahedron[1:]]
        if determinant(vectors) == 0:
            raise AssertionError("degenerate spacetime tetrahedron")
        for face in combinations(tetrahedron, 3):
            face_counts[tuple(sorted(face))] += 1
    if max(face_counts.values()) != 2 or any(count not in (1, 2) for count in face_counts.values()):
        raise AssertionError("tetrahedra do not form a pseudomanifold")
    boundary_faces = [face for face, count in face_counts.items() if count == 1]
    boundary_edges = {edge for face in boundary_faces for edge in combinations(face, 2)}
    boundary_vertices = {vertex for face in boundary_faces for vertex in face}
    if len(boundary_vertices) - len(boundary_edges) + len(boundary_faces) != 2:
        raise AssertionError("template boundary is not an Euler-characteristic two sphere")
    adjacency = defaultdict(set)
    for edge in boundary_edges:
        adjacency[edge[0]].add(edge[1])
        adjacency[edge[1]].add(edge[0])
    seen, queue = set(), deque([next(iter(boundary_vertices))])
    while queue:
        vertex = queue.popleft()
        if vertex not in seen:
            seen.add(vertex)
            queue.extend(adjacency[vertex] - seen)
    if seen != boundary_vertices:
        raise AssertionError("template boundary is disconnected")
    return len(expected_tetrahedra), len(boundary_faces)


def verify() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    tracks = json.loads(TRACKS.read_text(encoding="utf-8"))
    slots = json.loads(SLOTS.read_text(encoding="utf-8"))
    foot_chart = json.loads(FOOT_CHART.read_text(encoding="utf-8"))
    if data["sha256"] != payload_sha(data):
        raise AssertionError("ambient-extension payload SHA changed")
    expected_sources = {
        "foot_to_dotted_disk_tracks": TRACKS.relative_to(ROOT).as_posix(),
        "foot_to_dotted_disk_tracks_payload_sha256": payload_sha(tracks),
        "foot_to_dotted_slot_map": SLOTS.relative_to(ROOT).as_posix(),
        "foot_to_dotted_slot_map_payload_sha256": payload_sha(slots),
        "unified_foot_chart": FOOT_CHART.relative_to(ROOT).as_posix(),
        "unified_foot_chart_payload_sha256": payload_sha(foot_chart),
    }
    if data["sources"] != expected_sources:
        raise AssertionError("ambient-extension sources changed")
    if data["completion_status"] != "REFLECTION_PAIRED_AMBIENT_DOTTED_DISK_EXTENSIONS_CONSTRUCTED":
        raise AssertionError("ambient-extension scope changed")

    denominator_bound = 1
    radial_margin = None
    for handle in tracks["handles"]:
        for track in handle["tracks"]:
            for field in ("normalized_start", "normalized_waypoint", "normalized_target"):
                value = point(track[field])
                denominator_bound = max(denominator_bound, *(x.denominator for x in value))
                margin = 1 - value[0] ** 2 - value[1] ** 2
                if margin <= 0:
                    raise AssertionError("track leaves normalized disk")
                radial_margin = margin if radial_margin is None else min(radial_margin, margin)
    lower_bound = Fraction(1, 8 * denominator_bound**16)
    radius = min(Fraction(1, 100 * denominator_bound**8), radial_margin / 100)
    certificate = data["clearance_certificate"]
    if (Fraction(certificate["coordinate_denominator_bound"]) != denominator_bound
            or Fraction(certificate["minimum_track_vertex_radial_margin_squared"]) != radial_margin
            or Fraction(certificate["fixed_mark_distance_squared_lower_bound"]) != lower_bound
            or Fraction(certificate["support_scale"]) != radius):
        raise AssertionError("clearance certificate changed")
    if (12 * radius) ** 2 >= lower_bound or 16 * radius >= radial_margin / 2:
        raise AssertionError("support inequalities fail")
    tetrahedra_per_segment, boundary_faces = verify_template(data["template"], radius)

    slot_handles = {item["handle"]: item for item in slots["handles"]}
    chart_handles = {item["name"]: item for item in foot_chart["handles"]}
    artifact_handles = {item["handle"]: item for item in data["handles"]}
    moves = segments = collision_checks = reflection_checks = 0
    for source_handle in tracks["handles"]:
        name = source_handle["handle"]
        entries = slot_handles[name]["entries"]
        entry_by_id = {entry["passage_id"]: entry for entry in entries}
        current = {entry["passage_id"]: (point(entry["belt_point"])[0] / 4,
                                            point(entry["belt_point"])[1] / 4)
                   for entry in entries}
        target = {entry["passage_id"]: point(entry["target_disk_slot"]) for entry in entries}
        artifact_moves = artifact_handles[name]["moves"]
        if len(artifact_moves) != len(source_handle["tracks"]):
            raise AssertionError("move list length changed")
        matrix = chart_handles[name]["foot_pair"]["reflection_matrix"]
        for source_track, move in zip(source_handle["tracks"], artifact_moves):
            passage_id = source_track["passage_id"]
            entry = entry_by_id[passage_id]
            path = [point(source_track[field]) for field in ("normalized_start", "normalized_waypoint", "normalized_target")]
            if (move["move_index"] != source_track["move_index"] or move["passage_id"] != passage_id
                    or move["owner"] != entry["component"] or move["orientation"] != entry["orientation"]):
                raise AssertionError("move provenance changed")
            if path[0] != current[passage_id] or path[-1] != target[passage_id]:
                raise AssertionError("move state endpoints changed")
            obstacles = [value for other_id, value in current.items() if other_id != passage_id]
            for segment_index, (start, end) in enumerate(zip(path, path[1:])):
                record = move["segments"][segment_index]
                if (record["segment_index"] != segment_index or point(record["start"]) != start
                        or point(record["end"]) != end or start == end):
                    raise AssertionError("affine segment chart changed")
                for obstacle in obstacles:
                    collision_checks += 1
                    if lies_on_segment(obstacle, start, end):
                        raise AssertionError("support core meets a fixed marked point")
                segments += 1
            embedding = move["physical_foot_embeddings"]
            positive = point(embedding["positive_endpoint"])
            negative = point(embedding["negative_endpoint"])
            if embedding["pairing_matrix"] != matrix or apply_matrix(matrix, positive) != negative:
                raise AssertionError("physical-foot reflection changed")
            reflection_checks += 1
            current[passage_id] = target[passage_id]
            moves += 1
        if current != target:
            raise AssertionError("final marked configuration changed")

    if (moves, segments, collision_checks, reflection_checks) != (1785, 3570, 4911880, 1785):
        raise AssertionError("ambient-extension verification counts changed")
    if (data["move_count"] != moves or data["track_segment_count"] != segments
            or data["normalized_tetrahedron_instance_count"] != segments * tetrahedra_per_segment
            or data["reflection_paired_physical_tetrahedron_count"] != segments * tetrahedra_per_segment * 2):
        raise AssertionError("ambient-extension aggregate counts changed")
    return {
        "verdict": "PASS_REFLECTION_PAIRED_AMBIENT_DOTTED_DISK_EXTENSIONS",
        "moves": moves,
        "track_segments": segments,
        "collision_checks": collision_checks,
        "reflection_checks": reflection_checks,
        "template_tetrahedra": tetrahedra_per_segment,
        "template_boundary_faces": boundary_faces,
        "physical_tetrahedron_instances": data["reflection_paired_physical_tetrahedron_count"],
        "scope_boundary": data["scope_boundary"],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
