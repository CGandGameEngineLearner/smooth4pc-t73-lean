#!/usr/bin/env python3
"""Independently verify the standard handle-pair boundary shelling."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "geometry/t73_x_m1_standard_pair_boundary_s3.json"
HANDLE_PAIR = ROOT / "geometry/t73_x_m1_handle_pair_deletion.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def faces(simplex, size):
    return {tuple(face) for face in itertools.combinations(simplex, size)}


def verify():
    data = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("standard-pair S3 payload SHA mismatch")
    handle_pair = json.loads(HANDLE_PAIR.read_text())
    if data["x_m1_handle_pair_deletion_sha256"] != handle_pair["sha256"]:
        raise AssertionError("standard-pair S3 source binding changed")
    four = [tuple(value) for value in handle_pair["standard_pair"]["union_four_simplices"]]
    facet_counts = Counter(
        tuple(sorted(face)) for simplex in four for face in itertools.combinations(simplex, 4)
    )
    boundary = sorted(face for face, count in facet_counts.items() if count == 1)
    if [list(value) for value in boundary] != data["boundary_tetrahedra"]:
        raise AssertionError("standard-pair boundary tetrahedra changed")
    triangle_degree = Counter(
        triangle for tetrahedron in boundary for triangle in faces(tetrahedron, 3)
    )
    if set(triangle_degree.values()) != {2}:
        raise AssertionError("standard-pair boundary is not closed")

    removed_index = data["removed_tetrahedron_index"]
    removed = boundary[removed_index]
    order = data["ball_shelling_order"]
    if sorted(order) != sorted(set(range(len(boundary))) - {removed_index}):
        raise AssertionError("shelling does not use each complement tetrahedron once")
    chosen = []
    boundary_faces = set()
    pure_intersection_checks = disk_attachment_checks = 0
    for step_index, tetrahedron_index in enumerate(order):
        tetrahedron = boundary[tetrahedron_index]
        tetrahedron_faces = faces(tetrahedron, 3)
        if not chosen:
            shared = set()
            boundary_faces = set(tetrahedron_faces)
        else:
            shared = tetrahedron_faces & boundary_faces
            if len(shared) not in (1, 2, 3):
                raise AssertionError("shelling attachment is not a triangular disk")
            disk_attachment_checks += 1
            # Reject stray shared vertices/edges outside the shared triangles.
            chosen_tetrahedra = [boundary[index] for index in chosen]
            for size in (1, 2):
                for face in faces(tetrahedron, size):
                    already_present = any(set(face) <= set(old) for old in chosen_tetrahedra)
                    covered = any(set(face) <= set(triangle) for triangle in shared)
                    if already_present != covered:
                        raise AssertionError("shelling intersection is not pure two-dimensional")
                    pure_intersection_checks += 1
            boundary_faces = (boundary_faces - shared) | (tetrahedron_faces - shared)
        saved_step = data["ball_shelling_steps"][step_index]
        if saved_step["tetrahedron_index"] != tetrahedron_index:
            raise AssertionError("saved shelling step index changed")
        if saved_step["shared_boundary_triangles"] != [list(face) for face in sorted(shared)]:
            raise AssertionError("saved shelling intersection changed")
        chosen.append(tetrahedron_index)

    removed_boundary = faces(removed, 3)
    if boundary_faces != removed_boundary:
        raise AssertionError("shelled complement boundary is not the removed tetrahedron sphere")
    if data["recognized_boundary_type"] != "S3":
        raise AssertionError("verified shelling was not recorded as S3")
    return {
        "verdict": "PASS_STANDARD_X_M1_HANDLE_PAIR_BOUNDARY_S3_SHELLING",
        "boundary_tetrahedra": len(boundary),
        "complement_ball_tetrahedra": len(order),
        "disk_attachment_checks": disk_attachment_checks,
        "pure_intersection_checks": pure_intersection_checks,
        "final_boundary_triangles": len(boundary_faces),
        "recognized_boundary_type": "S3",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
