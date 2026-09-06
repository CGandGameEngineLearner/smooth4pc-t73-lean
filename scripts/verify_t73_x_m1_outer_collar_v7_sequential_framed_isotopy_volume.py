#!/usr/bin/env python3
"""Independently replay the complete sequential ribbon world-volume."""

from __future__ import annotations

import gzip
import hashlib
import itertools
import json
import os
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = (
    ROOT
    / "audit/t73_x_m1_outer_collar_v7_sequential_framed_isotopy_volume_receipt.json"
)
V1 = ROOT / "audit/t73_x_m1_outer_collar_v7_isotopy_trace_receipt.json"
SEQUENTIAL = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_isotopy_trace_receipt.json"
)
SEQUENTIAL_VERIFY = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_isotopy_trace_verification.json"
)
STATIC_RIBBON = (
    ROOT / "audit/t73_x_m1_outer_collar_v7_sequential_static_ribbon_clearance.json"
)
TRACE_COUNT = 3026
PRISM_TETRAHEDRA = ((0, 1, 2, 5), (0, 1, 4, 5), (0, 3, 4, 5))


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    if os.name != "nt" and len(value) > 3 and value[1:3] in (":\\", ":/"):
        return Path("/mnt") / value[0].lower() / value[3:].replace("\\", "/")
    return path


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def point(value):
    return tuple(Fraction(coordinate) for coordinate in value)


def encode(values):
    return [[str(coordinate) for coordinate in value] for value in values]


def ribbon_triangles(core, push):
    result = []
    for index in range(len(core) - 1):
        quad = (core[index], core[index + 1], push[index + 1], push[index])
        result.extend(((quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3])))
    return result


def determinant3(matrix):
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def rank_three(vertices, tetrahedron):
    origin = vertices[tetrahedron[0]]
    directions = [
        tuple(vertices[tetrahedron[row]][axis] - origin[axis] for axis in range(4))
        for row in (1, 2, 3)
    ]
    return any(
        determinant3([[directions[row][axis] for axis in columns] for row in range(3)])
        for columns in itertools.combinations(range(4), 3)
    )


def verify_prism_template():
    faces = Counter()
    for tetrahedron in PRISM_TETRAHEDRA:
        for omitted in range(4):
            faces[
                tuple(sorted(tetrahedron[:omitted] + tetrahedron[omitted + 1 :]))
            ] += 1
    boundary = {face for face, count in faces.items() if count == 1}
    expected = {
        (0, 1, 2),
        (3, 4, 5),
        (0, 1, 4),
        (0, 3, 4),
        (1, 2, 5),
        (1, 4, 5),
        (0, 2, 5),
        (0, 3, 5),
    }
    if boundary != expected or any(
        count != 2 for face, count in faces.items() if face not in boundary
    ):
        raise AssertionError("canonical triangular-prism boundary changed")


def volume(bottom, top, start, end):
    vertices = []
    tetrahedra = []
    for first, second in zip(bottom, top, strict=True):
        offset = len(vertices)
        vertices.extend([(*value, start) for value in first])
        vertices.extend([(*value, end) for value in second])
        tetrahedra.extend(
            [offset + index for index in tetrahedron]
            for tetrahedron in PRISM_TETRAHEDRA
        )
    if not all(rank_three(vertices, tetrahedron) for tetrahedron in tetrahedra):
        raise AssertionError("independent volume rank check failed")
    return vertices, tetrahedra


def verify_full():
    verify_prism_template()
    data = json.loads(DATA.read_text())
    v1 = json.loads(V1.read_text())
    sequential = json.loads(SEQUENTIAL.read_text())
    sequential_verification = json.loads(SEQUENTIAL_VERIFY.read_text())
    static_ribbon = json.loads(STATIC_RIBBON.read_text())
    if (
        data["sequential_trace_receipt_sha256"] != sequential["sha256"]
        or data["sequential_trace_verification_sha256"]
        != sequential_verification["sha256"]
        or data["static_ribbon_clearance_sha256"] != static_ribbon["sha256"]
        or sequential["local_trace_receipt_sha256"] != v1["sha256"]
    ):
        raise AssertionError("framed volume bindings changed")
    path = resolve(data["cache_path"])
    if (
        path.stat().st_size != data["cache_size"]
        or file_sha(path) != data["cache_sha256"]
    ):
        raise AssertionError("framed volume cache bytes changed")
    digest = hashlib.sha256()
    counts = Counter()
    previous_end = Fraction(0)
    with (
        gzip.open(resolve(v1["cache_path"]), "rt", encoding="utf-8") as source,
        gzip.open(path, "rt", encoding="utf-8") as candidate,
    ):
        source.readline()
        header_line = candidate.readline()
        digest.update(header_line.encode())
        header = json.loads(header_line)
        if (
            header["schema"]
            != "t73_x_m1_outer_collar_v7_sequential_framed_isotopy_volume/v1"
            or header["triangular_prism_tetrahedra"]
            != [list(value) for value in PRISM_TETRAHEDRA]
            or not header["classification"].startswith("CANDIDATE_UNVERIFIED")
        ):
            raise AssertionError("framed volume header changed")
        for position, (old_line, new_line) in enumerate(
            zip(source, candidate, strict=True)
        ):
            digest.update(new_line.encode())
            old, new = json.loads(old_line), json.loads(new_line)
            start = Fraction(position, TRACE_COUNT)
            middle = Fraction(2 * position + 1, 2 * TRACE_COUNT)
            end = Fraction(position + 1, TRACE_COUNT)
            if start != previous_end:
                raise AssertionError("framed-volume time slots overlap or leave a gap")
            previous_end = end
            initial_core = [point(value) for value in old["initial_core_subdivision"]]
            initial_push = [
                point(value) for value in old["phase_one_push_initial_subdivision"]
            ]
            final_core = [point(value) for value in old["final_core_route"]]
            constant_push = [
                point(value)
                for value in old["phase_one_push_final_constant_normal_route"]
            ]
            local_terminal = [
                point(value) for value in old["phase_two_push_spacetime_vertices"]
            ]
            final_push = constant_push[:-1] + [local_terminal[2][:3]]
            initial = ribbon_triangles(initial_core, initial_push)
            constant = ribbon_triangles(final_core, constant_push)
            final = ribbon_triangles(final_core, final_push)
            families = {
                "source_stationary": (
                    volume(initial, initial, Fraction(0), start) if start else ([], [])
                ),
                "phase_one_moving": volume(initial, constant, start, middle),
                "phase_two_stationary_prefix": volume(
                    constant[:-2], constant[:-2], middle, end
                ),
                "phase_two_moving_terminal": volume(
                    constant[-2:], final[-2:], middle, end
                ),
                "final_stationary": (
                    volume(final, final, end, Fraction(1)) if end < 1 else ([], [])
                ),
            }
            expected = {
                "interface_index": position,
                "band_index": old["band_index"],
                "component": old["component"],
                "side": old["side"],
                "neighbor_kind": old["neighbor_kind"],
                "neighbor_id": old["neighbor_id"],
                "time_interval": [str(start), str(end)],
                "phase_one_interval": [str(start), str(middle)],
                "phase_two_interval": [str(middle), str(end)],
                "boundary_match_count": 5,
                "moving_volume_interiors_pairwise_time_disjoint": True,
                "moving_static_volume_clearance_status": "OPEN",
                "ambient_support_status": "OPEN_BUILD_TETRAHEDRAL_EXTENSION",
                "classification": "CANDIDATE_UNVERIFIED",
            }
            prism_counts = {
                "source_stationary": len(initial) if start else 0,
                "phase_one_moving": len(initial),
                "phase_two_stationary_prefix": len(constant) - 2,
                "phase_two_moving_terminal": 2,
                "final_stationary": len(final) if end < 1 else 0,
            }
            for name, (vertices, tetrahedra) in families.items():
                expected[f"{name}_spacetime_vertices"] = encode(vertices)
                expected[f"{name}_tetrahedra"] = tetrahedra
                expected[f"{name}_prism_count"] = prism_counts[name]
                counts[name] += len(tetrahedra)
                counts["rank"] += len(tetrahedra)
            if any(new.get(key) != value for key, value in expected.items()):
                raise AssertionError(
                    "framed volume differs from independent reconstruction"
                )
            counts["records"] += 1
            counts["boundary_matches"] += 5
    if previous_end != 1:
        raise AssertionError("framed-volume schedule does not cover global time")
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("framed-volume decompressed stream changed")
    expected_counts = Counter(
        {
            "records": 3026,
            "source_stationary": 90750,
            "phase_one_moving": 90780,
            "phase_two_stationary_prefix": 72624,
            "phase_two_moving_terminal": 18156,
            "final_stationary": 90750,
            "rank": 363060,
            "boundary_matches": 15130,
        }
    )
    if counts != expected_counts:
        raise AssertionError(f"framed-volume totals changed: {counts}")
    return {
        "verdict": "PASS_X_M1_OUTER_COLLAR_V7_SEQUENTIAL_FRAMED_ISOTOPY_VOLUME_FULL_LOCAL_CANDIDATE",
        "cache_sha_checked": True,
        "traces_reconstructed": counts["records"],
        "triangular_prisms_reconstructed": counts["rank"] // 3,
        "r4_tetrahedra": counts["rank"],
        "r4_rank_checks": counts["rank"],
        "boundary_matches": counts["boundary_matches"],
        "moving_volume_interiors_pairwise_time_disjoint": True,
        "moving_static_volume_clearance": "OPEN",
        "ambient_support": "OPEN",
        "classification": "CANDIDATE_UNVERIFIED",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
