#!/usr/bin/env python3
"""Replay V6 opposite exterior half-spaces and local ribbon stars."""

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
from verify_t73_x_m1_framed_outer_interface_collars_v5 import rectangles
from verify_t73_x_m1_transition_transition_ribbon_clearance_gmp import (
    triangles_intersect,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v6_receipt.json"
V5 = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v5_receipt.json"
OBSTRUCTION = ROOT / "audit/t73_x_m1_outer_collar_v5_ribbon_clearance.json"
SLOPE = 1_000_033
FUNCTIONAL_Z = 2
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


def functional(value):
    return value[1] - SLOPE * value[0] + FUNCTIONAL_Z * value[2]


def expected_changed_core(old):
    core = [point(value) for value in old["final_core_vertices"]]
    height = Fraction(old["routing_base_height"])
    core[3] = (-abs(core[3][0]), core[3][1], core[3][2])
    core[3] = (
        core[3][0],
        functional(core[1]) + SLOPE * core[3][0] - FUNCTIONAL_Z * height,
        height,
    )
    end_height = height + END_OFFSET
    core[4] = (-abs(core[4][0]), core[4][1], core[4][2])
    core[4] = (
        core[4][0],
        functional(core[6]) + SLOPE * core[4][0] - FUNCTIONAL_Z * end_height,
        end_height,
    )
    return core


def verify_full():
    data = json.loads(DATA.read_text())
    v5 = json.loads(V5.read_text())
    obstruction = json.loads(OBSTRUCTION.read_text())
    if (
        data["refuted_v5_receipt_sha256"] != v5["sha256"]
        or data["v5_ribbon_obstruction_sha256"] != obstruction["sha256"]
    ):
        raise AssertionError("v6 source binding changed")
    path = resolve(data["cache_path"])
    if (
        path.stat().st_size != data["cache_size"]
        or file_sha(path) != data["cache_sha256"]
    ):
        raise AssertionError("v6 cache bytes changed")
    digest = hashlib.sha256()
    records_count = changed = unchanged = transversality = former_collision_checks = 0
    stars = Counter()
    germs = defaultdict(list)
    with (
        gzip.open(resolve(v5["cache_path"]), "rt", encoding="utf-8") as old_source,
        gzip.open(path, "rt", encoding="utf-8") as new_source,
    ):
        old_source.readline()
        header_line = new_source.readline()
        digest.update(header_line.encode())
        for old_line, new_line in zip(old_source, new_source, strict=True):
            digest.update(new_line.encode())
            old, new = json.loads(old_line), json.loads(new_line)
            is_changed = (
                old["neighbor_kind"] != "actual_johnson_central_connector"
                and old["side"] == "after"
            )
            new_core = [point(value) for value in new["final_core_vertices"]]
            normals = [point(value) for value in new["final_normal_field"]]
            if is_changed:
                if new_core != expected_changed_core(old):
                    raise AssertionError("v6 changed dual coordinates differ from rule")
                changed += 1
            else:
                if (
                    new["final_core_vertices"] != old["final_core_vertices"]
                    or new["final_push_vertices"] != old["final_push_vertices"]
                ):
                    raise AssertionError("v6 changed an unselected collar")
                unchanged += 1
            expected_push = [
                add(vertex, normal) for vertex, normal in zip(new_core, normals)
            ]
            if [point(value) for value in new["final_push_vertices"]] != expected_push:
                raise AssertionError("v6 push is not its normal graph")
            for index in range(len(new_core) - 1):
                tangent = subtract(new_core[index + 1], new_core[index])
                if affine_vector_hits_zero(
                    cross(tangent, normals[index]), cross(tangent, normals[index + 1])
                ):
                    raise AssertionError("v6 normal loses transversality")
                transversality += 1
            local = rectangles(new)
            for first, second in pairwise(local):
                edge = tuple(set(first["quad"]) & set(second["quad"]))
                relation = star_relation(first, second, edge)
                if relation == "COPLANAR_SAME_SIDE_OVERLAP":
                    raise AssertionError("v6 same-interface local star folds")
                stars[f"same_interface/{relation}"] += 1
            germs[(new["neighbor_id"], local[0]["inner_edge"])].append(local[0])
            if new["interface_index"] == 3024:
                other = obstruction["collision"]
                if other["first"][0] != 3024 or other["second"][0] != 3023:
                    raise AssertionError("v5 obstruction identity changed")
                former_collision_checks += 1
            records_count += 1
    shared = 0
    for values in germs.values():
        if len(values) == 1:
            continue
        edge = tuple(set(values[0]["quad"]) & set(values[1]["quad"]))
        relation = star_relation(values[0], values[1], edge)
        if relation == "COPLANAR_SAME_SIDE_OVERLAP":
            raise AssertionError("v6 shared dual germ star folds")
        stars[f"shared_dual_germ/{relation}"] += 1
        shared += 1
    # Rebuild the exact V5 colliding pair from V6 and verify it is gone.
    with gzip.open(path, "rt", encoding="utf-8") as source:
        source.readline()
        selected = {}
        for line in source:
            record = json.loads(line)
            if record["interface_index"] in (3023, 3024):
                selected[record["interface_index"]] = rectangles(record)
    first_triangle = selected[3024][1]["triangles"][0]
    second_triangle = selected[3023][2]["triangles"][0]
    if triangles_intersect(first_triangle, second_triangle):
        raise AssertionError("v6 did not remove the V5 triangle collision")
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("v6 decompressed stream changed")
    if (
        records_count,
        changed,
        unchanged,
        transversality,
        shared,
        former_collision_checks,
    ) != (3026, 4, 3022, 18156, 4, 1):
        raise AssertionError("v6 replay totals changed")
    return {
        "verdict": "PASS_X_M1_FRAMED_OUTER_INTERFACE_COLLARS_V6_FULL_LOCAL_CANDIDATE",
        "cache_sha_checked": True,
        "collars_reconstructed": records_count,
        "changed_after_dual_collars": changed,
        "unchanged_collars": unchanged,
        "normal_transversality_checks": transversality,
        "local_ribbon_star_checks": sum(stars.values()),
        "local_ribbon_star_relation_counts": dict(sorted(stars.items())),
        "former_v5_collision_exact_rechecks": former_collision_checks,
        "relative_twist_sum": 0,
        "classification": "CANDIDATE_UNVERIFIED",
        "global_clearance": "OPEN",
        "ambient_support": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
