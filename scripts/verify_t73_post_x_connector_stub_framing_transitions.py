#!/usr/bin/env python3
"""Verify the 3026 source-relative connector/stub framing collars."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_post_x_connector_stub_framing_transitions_receipt.json"
GAP = ROOT / "audit/t73_post_x_connector_stub_framing_gap.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    return path


def point(values):
    return tuple(Fraction(value) for value in values)


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def verify(check_cache_sha=True):
    data = json.loads(DATA.read_text())
    gap = json.loads(GAP.read_text())
    unsigned = {key: value for key, value in data.items() if key != "sha256"}
    if data["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("framing transition receipt SHA mismatch")
    if data["framing_gap_sha256"] != gap["sha256"]:
        raise AssertionError("framing transitions are not bound to the current gap")
    cache = resolve(data["cache_path"])
    if not cache.is_file() or cache.stat().st_size != data["cache_size"]:
        raise AssertionError("framing transition cache missing or resized")
    if check_cache_sha and file_sha256(cache) != data["cache_sha256"]:
        raise AssertionError("framing transition cache SHA mismatch")

    digest = hashlib.sha256()
    records = triangles = endpoint_matches = transverse = relative_twist = 0
    types = Counter()
    last_identity = None
    with gzip.open(cache, "rt", encoding="utf-8") as source:
        for line_number, line in enumerate(source):
            digest.update(line.encode())
            record = json.loads(line)
            if line_number == 0:
                if record["schema"] != "t73_post_x_connector_stub_framing_transitions/v1":
                    raise AssertionError("framing transition stream header changed")
                continue
            identity = (record["band_index"], record["side"])
            if record["side"] not in ("before", "after"):
                raise AssertionError("invalid transition side")
            if last_identity is not None:
                if record["side"] == "before" and record["band_index"] <= last_identity[0]:
                    raise AssertionError("transition stream band order changed")
                if record["side"] == "after" and last_identity != (record["band_index"], "before"):
                    raise AssertionError("transition before/after pairing changed")
            last_identity = identity
            core = [point(value) for value in record["core_vertices"]]
            normals = [point(value) for value in record["normal_field"]]
            push = [point(value) for value in record["push_vertices"]]
            if len(core) != 3 or len(normals) != 3 or len(push) != 3:
                raise AssertionError("transition path size changed")
            if any(tuple(core[i][axis] + normals[i][axis] for axis in range(3)) != push[i] for i in range(3)):
                raise AssertionError("transition push is not its normal graph")
            if record["side"] == "before":
                if normals[0] != normals[1] or normals[1] == normals[2]:
                    raise AssertionError("before normal homotopy pattern changed")
            else:
                if normals[1] != normals[2] or normals[0] == normals[1]:
                    raise AssertionError("after normal homotopy pattern changed")
            for segment in range(2):
                tangent = subtract(core[segment + 1], core[segment])
                for normal in normals[segment:segment + 2]:
                    if normal == (0, 0, 0) or cross(tangent, normal) == (0, 0, 0):
                        raise AssertionError("transition normal vanishes or becomes tangent")
                    transverse += 1
            if record["ribbon_triangles"] != [[0, 1, 4], [0, 4, 3], [1, 2, 5], [1, 5, 4]]:
                raise AssertionError("transition ribbon triangulation changed")
            if record["relative_twist"] != 0:
                raise AssertionError("unexpected connector-stub relative twist")
            records += 1
            triangles += 4
            endpoint_matches += 2
            relative_twist += record["relative_twist"]
            types[f"{record['component']}/{record['neighbor_kind']}"] += 1

    if digest.hexdigest().upper() != data["record_stream_sha256"]:
        raise AssertionError("framing transition record stream SHA mismatch")
    totals = (records, triangles, endpoint_matches, transverse, relative_twist)
    if totals != (3026, 12104, 6052, 12104, 0):
        raise AssertionError(f"framing transition totals changed: {totals}")
    if dict(sorted(types.items())) != data["transition_type_counts"]:
        raise AssertionError("framing transition type inventory changed")
    if data["global_transition_clearance_status"] != "OPEN":
        raise AssertionError("local transitions were overstated as globally clear")
    return {
        "verdict": "PASS_POST_X_CONNECTOR_STUB_FRAMING_TRANSITIONS_FULL_LOCAL",
        "transitions": records,
        "ribbon_triangles": triangles,
        "endpoint_normal_matches": endpoint_matches,
        "normal_transversality_checks": transverse,
        "relative_twist_sum": relative_twist,
        "cache_sha_checked": check_cache_sha,
        "global_clearance": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
