#!/usr/bin/env python3
"""Independently replay the minimal two-record V7 sign assignment."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
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
from verify_t73_x_m1_framed_outer_interface_collars_v6 import expected_changed_core
from verify_t73_x_m1_transition_transition_ribbon_clearance_gmp import (
    triangles_intersect,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v7_receipt.json"
V5 = ROOT / "audit/t73_x_m1_framed_outer_interface_collars_v5_receipt.json"
V5_OBSTRUCTION = ROOT / "audit/t73_x_m1_outer_collar_v5_ribbon_clearance.json"
V6_OBSTRUCTION = ROOT / "audit/t73_x_m1_outer_collar_v6_ribbon_clearance.json"
SELECTED = {3022, 3023}


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


def verify_full():
    data = json.loads(DATA.read_text())
    v5 = json.loads(V5.read_text())
    v5_obstruction = json.loads(V5_OBSTRUCTION.read_text())
    v6_obstruction = json.loads(V6_OBSTRUCTION.read_text())
    if (
        data["source_v5_receipt_sha256"] != v5["sha256"]
        or data["v5_ribbon_obstruction_sha256"] != v5_obstruction["sha256"]
        or data["v6_ribbon_obstruction_sha256"] != v6_obstruction["sha256"]
    ):
        raise AssertionError("v7 source binding changed")
    path = resolve(data["cache_path"])
    if (
        path.stat().st_size != data["cache_size"]
        or file_sha(path) != data["cache_sha256"]
    ):
        raise AssertionError("v7 cache bytes changed")
    digest = hashlib.sha256()
    records_count = changed = unchanged = transversality = 0
    stars = Counter()
    germs = defaultdict(list)
    selected_records = {}
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
            index = new["interface_index"]
            new_core = [point(value) for value in new["final_core_vertices"]]
            normals = [point(value) for value in new["final_normal_field"]]
            if index in SELECTED:
                if new_core != expected_changed_core(old):
                    raise AssertionError("v7 selected exterior transform changed")
                changed += 1
            else:
                if (
                    new["final_core_vertices"] != old["final_core_vertices"]
                    or new["final_push_vertices"] != old["final_push_vertices"]
                ):
                    raise AssertionError("v7 changed an unselected V5 collar")
                unchanged += 1
            expected_push = [
                add(vertex, normal) for vertex, normal in zip(new_core, normals)
            ]
            if [point(value) for value in new["final_push_vertices"]] != expected_push:
                raise AssertionError("v7 push is not its normal graph")
            for segment in range(len(new_core) - 1):
                tangent = subtract(new_core[segment + 1], new_core[segment])
                if affine_vector_hits_zero(
                    cross(tangent, normals[segment]),
                    cross(tangent, normals[segment + 1]),
                ):
                    raise AssertionError("v7 normal loses transversality")
                transversality += 1
            local = rectangles(new)
            for first, second in pairwise(local):
                edge = tuple(set(first["quad"]) & set(second["quad"]))
                relation = star_relation(first, second, edge)
                if relation == "COPLANAR_SAME_SIDE_OVERLAP":
                    raise AssertionError("v7 same-interface local star folds")
                stars[f"same_interface/{relation}"] += 1
            germs[(new["neighbor_id"], local[0]["inner_edge"])].append(local[0])
            if index in (3019, 3020, 3023, 3024):
                selected_records[index] = local
            records_count += 1
    shared = 0
    for values in germs.values():
        if len(values) == 1:
            continue
        edge = tuple(set(values[0]["quad"]) & set(values[1]["quad"]))
        relation = star_relation(values[0], values[1], edge)
        if relation == "COPLANAR_SAME_SIDE_OVERLAP":
            raise AssertionError("v7 shared dual germ star folds")
        stars[f"shared_dual_germ/{relation}"] += 1
        shared += 1
    historical = (
        (3024, 1, 3023, 2),
        (3020, 1, 3019, 2),
    )
    for first_interface, first_type, second_interface, second_type in historical:
        if triangles_intersect(
            selected_records[first_interface][first_type]["triangles"][0],
            selected_records[second_interface][second_type]["triangles"][0],
        ):
            raise AssertionError("v7 retains a historical V5/V6 triangle collision")
    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("v7 decompressed stream changed")
    if (
        records_count,
        changed,
        unchanged,
        transversality,
        shared,
        sum(stars.values()),
    ) != (3026, 2, 3024, 18156, 4, 15134):
        raise AssertionError("v7 replay totals changed")
    return {
        "verdict": "PASS_X_M1_FRAMED_OUTER_INTERFACE_COLLARS_V7_FULL_LOCAL_CANDIDATE",
        "cache_sha_checked": True,
        "collars_reconstructed": records_count,
        "changed_collars": changed,
        "unchanged_collars": unchanged,
        "negative_exterior_interfaces": sorted(SELECTED),
        "normal_transversality_checks": transversality,
        "local_ribbon_star_checks": sum(stars.values()),
        "local_ribbon_star_relation_counts": dict(sorted(stars.items())),
        "historical_collision_exact_rechecks": len(historical),
        "relative_twist_sum": 0,
        "classification": "CANDIDATE_UNVERIFIED",
        "global_clearance": "OPEN",
        "ambient_support": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify_full(), sort_keys=True))
