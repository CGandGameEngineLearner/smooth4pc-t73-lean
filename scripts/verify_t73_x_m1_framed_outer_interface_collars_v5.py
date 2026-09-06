#!/usr/bin/env python3
"""Independently replay V5 dual lifts and all local ribbon stars."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_t73_x_m1_framed_outer_interface_collars import (
    add,
    affine_vector_hits_zero,
    cross,
    point,
    subtract,
)
from build_t73_x_m1_outer_collar_v2_ribbon_self_clearance import star_relation

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v5_receipt.json"
V4 = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v4_receipt.json"
OBSTRUCTION = ROOT / "audit/t73_x_m1_outer_collar_v4_ribbon_candidate_matrix.json"
SLOPE = 1_000_033
FUNCTIONAL_Z = 2
DUAL_LIFT = (Fraction(1, 499_900), Fraction(233, 499_900), Fraction(1))
END_OFFSET = Fraction(1, 2)


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


def scale(factor, value):
    return tuple(factor * coordinate for coordinate in value)


def functional(value):
    return value[1] - SLOPE * value[0] + FUNCTIONAL_Z * value[2]


def expected_dual_core(old):
    core = [point(value) for value in old["final_core_vertices"]]
    height = Fraction(old["routing_base_height"])
    for index, endpoint in ((2, core[1]), (5, core[6])):
        core[index] = add(endpoint, scale(height - endpoint[2], DUAL_LIFT))
    core[3] = (
        core[3][0],
        functional(core[1]) + SLOPE * core[3][0] - FUNCTIONAL_Z * height,
        height,
    )
    end_height = height + END_OFFSET
    core[4] = (
        core[4][0],
        functional(core[6]) + SLOPE * core[4][0] - FUNCTIONAL_Z * end_height,
        end_height,
    )
    return core


def rectangles(record):
    core = [point(value) for value in record["final_core_vertices"]]
    push = [point(value) for value in record["final_push_vertices"]]
    vertices = core + push
    size = len(core)
    output = []
    for local in range(size - 1):
        output.append(
            {
                "interface": record["interface_index"],
                "neighbor_id": record["neighbor_id"],
                "type": local,
                "inner_edge": (core[local], push[local]),
                "target_edge": (core[local + 1], push[local + 1]),
                "quad": (core[local], core[local + 1], push[local + 1], push[local]),
                "triangles": tuple(
                    tuple(vertices[index] for index in ids)
                    for ids in record["final_ribbon_triangles"][
                        2 * local : 2 * local + 2
                    ]
                ),
            }
        )
    return output


def verify_full():
    data = json.loads(DATA.read_text())
    v4 = json.loads(V4.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    if (
        data["refuted_v4_receipt_sha256"] != v4["sha256"]
        or data["v4_ribbon_obstruction_sha256"] != obstruction["sha256"]
    ):
        raise AssertionError("v5 source binding changed")
    path = resolve(data["cache_path"])
    if (
        path.stat().st_size != data["cache_size"]
        or file_sha(path) != data["cache_sha256"]
    ):
        raise AssertionError("v5 cache bytes changed")
    digest = hashlib.sha256()
    records = changed = unchanged = transversality = 0
    star_counts = Counter()
    germ_groups = defaultdict(list)
    with (
        gzip.open(resolve(v4["cache_path"]), "rt", encoding="utf-8") as old_source,
        gzip.open(path, "rt", encoding="utf-8") as new_source,
    ):
        old_source.readline()
        header_line = new_source.readline()
        digest.update(header_line.encode())
        for old_line, new_line in zip(old_source, new_source, strict=True):
            digest.update(new_line.encode())
            old, new = json.loads(old_line), json.loads(new_line)
            normals = [point(value) for value in new["final_normal_field"]]
            new_core = [point(value) for value in new["final_core_vertices"]]
            if old["neighbor_kind"] == "actual_johnson_central_connector":
                if (
                    new["final_core_vertices"] != old["final_core_vertices"]
                    or new["final_push_vertices"] != old["final_push_vertices"]
                ):
                    raise AssertionError("v5 changed a Johnson collar")
                unchanged += 1
            else:
                if new_core != expected_dual_core(old):
                    raise AssertionError("v5 dual lift coordinates changed")
                expected_push = [
                    add(vertex, normal) for vertex, normal in zip(new_core, normals)
                ]
                if [
                    point(value) for value in new["final_push_vertices"]
                ] != expected_push:
                    raise AssertionError("v5 dual push is not its normal graph")
                changed += 1
            for index in range(len(new_core) - 1):
                tangent = subtract(new_core[index + 1], new_core[index])
                if affine_vector_hits_zero(
                    cross(tangent, normals[index]), cross(tangent, normals[index + 1])
                ):
                    raise AssertionError("v5 normal loses transversality")
                transversality += 1
            local_rectangles = rectangles(new)
            for first, second in pairwise(local_rectangles):
                edge = tuple(set(first["quad"]) & set(second["quad"]))
                relation = star_relation(first, second, edge)
                if relation == "COPLANAR_SAME_SIDE_OVERLAP":
                    raise AssertionError("v5 same-interface ribbon star folds")
                star_counts[f"same_interface/{relation}"] += 1
            germ_groups[(new["neighbor_id"], local_rectangles[0]["inner_edge"])].append(
                local_rectangles[0]
            )
            records += 1
    shared_dual = 0
    for values in germ_groups.values():
        if len(values) == 1:
            continue
        edge = tuple(set(values[0]["quad"]) & set(values[1]["quad"]))
        relation = star_relation(values[0], values[1], edge)
        if relation == "COPLANAR_SAME_SIDE_OVERLAP":
            raise AssertionError("v5 shared-dual germ star folds")
        star_counts[f"shared_dual_germ/{relation}"] += 1
        shared_dual += 1
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("v5 decompressed stream changed")
    if (records, changed, unchanged, transversality, shared_dual) != (
        3026,
        8,
        3018,
        18156,
        4,
    ):
        raise AssertionError("v5 replay totals changed")
    if sum(star_counts.values()) != 15134:
        raise AssertionError("v5 local ribbon star count changed")
    return {
        "verdict": "PASS_X_M1_FRAMED_OUTER_INTERFACE_COLLARS_V5_FULL_LOCAL_CANDIDATE",
        "cache_sha_checked": True,
        "collars_reconstructed": records,
        "changed_dual_collars": changed,
        "unchanged_johnson_collars": unchanged,
        "normal_transversality_checks": transversality,
        "local_ribbon_star_checks": sum(star_counts.values()),
        "local_ribbon_star_relation_counts": dict(sorted(star_counts.items())),
        "relative_twist_sum": 0,
        "classification": "CANDIDATE_UNVERIFIED",
        "global_clearance": "OPEN",
        "ambient_support": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
