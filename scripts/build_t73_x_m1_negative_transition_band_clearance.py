#!/usr/bin/env python3
"""Prove v3 negative transitions are disjoint from all global band lanes."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
from fractions import Fraction
from pathlib import Path

from shapely.geometry import box
from shapely.strtree import STRtree


ROOT = Path(__file__).resolve().parents[1]
TRANSITIONS = ROOT / "audit/t73_x_m1_negative_global_r3_middle_transition_cores_v3_receipt.json"
BANDS = ROOT / "audit/t73_x_band_global_r3_port_strips_receipt.json"
BAND_CLEARANCE = ROOT / "audit/t73_x_band_global_r3_port_strip_clearance.json"
OUTPUT = ROOT / "audit/t73_x_m1_negative_transition_band_clearance.json"


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


def outward_xy_box(segment):
    low_x = math.nextafter(float(min(segment[0][0], segment[1][0])), -math.inf)
    low_y = math.nextafter(float(min(segment[0][1], segment[1][1])), -math.inf)
    high_x = math.nextafter(float(max(segment[0][0], segment[1][0])), math.inf)
    high_y = math.nextafter(float(max(segment[0][1], segment[1][1])), math.inf)
    return box(low_x, low_y, high_x, high_y)


def build():
    transitions = json.loads(TRANSITIONS.read_text())
    bands = json.loads(BANDS.read_text())
    band_clearance = json.loads(BAND_CLEARANCE.read_text())
    band_columns = []
    band_horizontal = []
    with gzip.open(resolve(bands["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            for raw in (
                record["negative_lane_vertices"],
                list(reversed(record["positive_lane_vertices_reverse_orientation"])),
            ):
                vertices = [point(value) for value in raw]
                band_columns.extend(((vertices[0], vertices[1]), (vertices[4], vertices[5])))
                band_horizontal.extend(
                    (vertices[index], vertices[index + 1]) for index in (1, 2, 3)
                )
    transition_shell = []
    transition_non_shell = []
    with gzip.open(resolve(transitions["cache_path"]), "rt", encoding="utf-8") as source:
        source.readline()
        for line in source:
            record = json.loads(line)
            vertices = [point(value) for value in record["core_vertices"]]
            if record["side"] == "first":
                transition_shell.extend(((vertices[0], vertices[1]), (vertices[1], vertices[2])))
                transition_non_shell.extend(
                    (vertices[index], vertices[index + 1]) for index in (2, 3, 4, 5)
                )
            else:
                transition_non_shell.extend(
                    (vertices[index], vertices[index + 1]) for index in (0, 1, 2, 3)
                )
                transition_shell.extend(((vertices[4], vertices[5]), (vertices[5], vertices[6])))
    column_tree = STRtree([outward_xy_box(segment) for segment in band_columns])
    pairs = column_tree.query([outward_xy_box(segment) for segment in transition_shell])
    if pairs.shape[1] != 0:
        raise AssertionError("v3 transition shell segments overlap band-column xy boxes")
    minimum_band_horizontal_z = min(
        min(segment[0][2], segment[1][2]) for segment in band_horizontal
    )
    maximum_transition_non_shell_z = max(
        max(segment[0][2], segment[1][2]) for segment in transition_non_shell
    )
    if maximum_transition_non_shell_z >= minimum_band_horizontal_z:
        raise AssertionError("v3 non-shell and band horizontal z intervals overlap")
    result = {
        "schema": "t73_x_m1_negative_transition_band_clearance/v1",
        "negative_transition_cores_v3_receipt_sha256": transitions["sha256"],
        "global_band_port_strips_receipt_sha256": bands["sha256"],
        "global_band_port_strip_clearance_sha256": band_clearance["sha256"],
        "band_shell_column_count": len(band_columns),
        "transition_shell_escape_skew_segment_count": len(transition_shell),
        "outward_rounded_xy_box_candidate_count": int(pairs.shape[1]),
        "band_horizontal_segment_count": len(band_horizontal),
        "transition_non_shell_segment_count": len(transition_non_shell),
        "minimum_band_horizontal_z": str(minimum_band_horizontal_z),
        "maximum_transition_non_shell_z": str(maximum_transition_non_shell_z),
        "xy_separation_argument": (
            "each rational xy bound is converted to nearest float and expanded "
            "one nextafter step outward; zero intersecting conservative boxes "
            "implies zero exact xy intersections"
        ),
        "z_separation_argument": (
            "all transition non-shell segments have z<=0, while all band "
            "horizontal segments have z>=100 up to infinitesimal strip width"
        ),
        "extra_transition_band_core_intersections": 0,
        "verdict": "PASS_X_M1_NEGATIVE_TRANSITION_BAND_CORE_CLEARANCE",
    }
    result["sha256"] = canonical_sha256(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.check and json.loads(OUTPUT.read_text()) != result:
        raise AssertionError("negative transition/band clearance is stale")
    print(json.dumps({
        "verdict": result["verdict"],
        "shell_segments": result["transition_shell_escape_skew_segment_count"],
        "column_candidates": result["outward_rounded_xy_box_candidate_count"],
        "non_shell_max_z": result["maximum_transition_non_shell_z"],
        "band_horizontal_min_z": result["minimum_band_horizontal_z"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
