#!/usr/bin/env python3
"""Independently verify v3 transition/band separation with NumPy intervals."""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import os
from fractions import Fraction
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit/t73_x_m1_negative_transition_band_clearance.json"
TRANSITIONS = ROOT / "audit/t73_x_m1_negative_global_r3_middle_transition_cores_v3_receipt.json"
BANDS = ROOT / "audit/t73_x_band_global_r3_port_strips_receipt.json"


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def resolve(value):
    path = Path(value)
    if path.exists():
        return path
    if value.startswith("/mnt/") and os.name == "nt":
        return Path(f"{value[5].upper()}:/{value[7:]}")
    return path


def point(values):
    return tuple(Fraction(value) for value in values)


def expanded_bounds(segments):
    low = np.array([
        [math.nextafter(float(min(segment[0][axis], segment[1][axis])), -math.inf) for axis in range(2)]
        for segment in segments
    ])
    high = np.array([
        [math.nextafter(float(max(segment[0][axis], segment[1][axis])), math.inf) for axis in range(2)]
        for segment in segments
    ])
    return low, high


def verify():
    saved = json.loads(DATA.read_text())
    unsigned = {key: value for key, value in saved.items() if key != "sha256"}
    if saved["sha256"] != canonical_sha256(unsigned):
        raise AssertionError("negative transition/band payload SHA mismatch")
    transitions = json.loads(TRANSITIONS.read_text())
    bands = json.loads(BANDS.read_text())
    if saved["negative_transition_cores_v3_receipt_sha256"] != transitions["sha256"]:
        raise AssertionError("negative transition/band transition binding changed")
    if saved["global_band_port_strips_receipt_sha256"] != bands["sha256"]:
        raise AssertionError("negative transition/band strip binding changed")
    columns = []
    band_horizontal = []
    with gzip.open(resolve(bands["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            for raw in (record["negative_lane_vertices"], list(reversed(record["positive_lane_vertices_reverse_orientation"]))):
                vertices = [point(value) for value in raw]
                columns.extend(((vertices[0], vertices[1]), (vertices[4], vertices[5])))
                band_horizontal.extend((vertices[index], vertices[index + 1]) for index in (1, 2, 3))
    shell = []
    non_shell = []
    with gzip.open(resolve(transitions["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            vertices = [point(value) for value in record["core_vertices"]]
            if record["side"] == "first":
                shell.extend(((vertices[0], vertices[1]), (vertices[1], vertices[2])))
                non_shell.extend((vertices[index], vertices[index + 1]) for index in (2, 3, 4, 5))
            else:
                non_shell.extend((vertices[index], vertices[index + 1]) for index in (0, 1, 2, 3))
                shell.extend(((vertices[4], vertices[5]), (vertices[5], vertices[6])))
    column_low, column_high = expanded_bounds(columns)
    shell_low, shell_high = expanded_bounds(shell)
    candidates = 0
    for low, high in zip(shell_low, shell_high):
        candidates += int(np.sum(np.all(column_high >= low, axis=1) & np.all(high >= column_low, axis=1)))
    if candidates != 0:
        raise AssertionError("independent NumPy interval check found a shell/column candidate")
    min_band_z = min(min(segment[0][2], segment[1][2]) for segment in band_horizontal)
    max_transition_z = max(max(segment[0][2], segment[1][2]) for segment in non_shell)
    if max_transition_z >= min_band_z:
        raise AssertionError("independent z interval separation failed")
    if (len(columns), len(shell), len(band_horizontal), len(non_shell)) != (6052, 6052, 9078, 12104):
        raise AssertionError("negative transition/band segment inventory changed")
    return {
        "verdict": "PASS_X_M1_NEGATIVE_TRANSITION_BAND_CORE_CLEARANCE",
        "band_columns": len(columns),
        "transition_shell_segments": len(shell),
        "conservative_xy_candidates": candidates,
        "band_horizontal_segments": len(band_horizontal),
        "transition_non_shell_segments": len(non_shell),
        "extra_intersections": 0,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
