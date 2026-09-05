#!/usr/bin/env python3
"""Thicken marked-point tracks to explicit reflection-paired PL isotopies.

An exact denominator bound replaces millions of costly rational projections.
The artifact stores one reusable 36-tetrahedron spacetime template and an
exact affine chart for every track segment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKS = ROOT / "geometry/t73_foot_to_dotted_disk_tracks.json"
SLOTS = ROOT / "geometry/t73_foot_to_dotted_slot_map.json"
FOOT_CHART = ROOT / "geometry/t73_unified_kirby_foot_chart.json"
OUTPUT = ROOT / "geometry/t73_dotted_disk_ambient_extensions.json"

# Exact Johnson/AR coordinates legitimately exceed Python's defensive decimal
# conversion threshold; these integers are generated locally, not user input.
sys.set_int_max_str_digits(0)


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def payload_sha(value: dict) -> str:
    return canonical_sha({key: item for key, item in value.items() if key != "sha256"})


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(values):
    return [str(value) for value in values]


def template_triangles():
    # C=0, I_0,...,I_3=1,...,4 and O_0,...,O_3=5,...,8.
    inner = [(0, 1 + index, 1 + (index + 1) % 4) for index in range(4)]
    annulus = []
    for index in range(4):
        inner_0, inner_1 = 1 + index, 1 + (index + 1) % 4
        outer_0, outer_1 = 5 + index, 5 + (index + 1) % 4
        annulus.extend(((inner_0, outer_0, outer_1), (inner_0, outer_1, inner_1)))
    return inner + annulus


def prism_tetrahedra(triangles):
    tetrahedra = []
    for a, b, c in triangles:
        # Global vertex order chooses the same diagonal on every shared edge
        # prism, independently of the adjacent triangle's cyclic ordering.
        a, b, c = sorted((a, b, c))
        tetrahedra.extend(
            ((a, b, c, c + 9), (a, b, b + 9, c + 9), (a, a + 9, b + 9, c + 9))
        )
    return tetrahedra


def coefficient_vertices():
    """Vertices in (s,u,time), with s/u stored as constant + scale*r."""
    result = []
    for time in (0, 1):
        center = time
        vertices = [{"name": "C", "s_constant": center, "s_scale": 0, "u_scale": 0}]
        for name, s_scale, u_scale in (
            ("I0", -1, -1), ("I1", 1, -1), ("I2", 1, 1), ("I3", -1, 1)
        ):
            vertices.append({"name": name, "s_constant": center, "s_scale": s_scale, "u_scale": u_scale})
        for name, s_constant, s_scale, u_scale in (
            ("O0", 0, -4, -4), ("O1", 1, 4, -4),
            ("O2", 1, 4, 4), ("O3", 0, -4, 4),
        ):
            vertices.append({"name": name, "s_constant": s_constant, "s_scale": s_scale, "u_scale": u_scale})
        for vertex in vertices:
            vertex["time"] = time
        result.extend(vertices)
    return result


def source_bounds(tracks: dict):
    denominator_bound = 1
    radial_margin = None
    for handle in tracks["handles"]:
        for track in handle["tracks"]:
            for field in ("normalized_start", "normalized_waypoint", "normalized_target"):
                value = point(track[field])
                denominator_bound = max(denominator_bound, *(x.denominator for x in value))
                margin = 1 - value[0] ** 2 - value[1] ** 2
                if margin <= 0:
                    raise AssertionError("track vertex is not in the open normalized disk")
                radial_margin = margin if radial_margin is None else min(radial_margin, margin)
    return denominator_bound, radial_margin


def build() -> dict:
    tracks = json.loads(TRACKS.read_text(encoding="utf-8"))
    slots = json.loads(SLOTS.read_text(encoding="utf-8"))
    foot_chart = json.loads(FOOT_CHART.read_text(encoding="utf-8"))
    denominator_bound, radial_margin = source_bounds(tracks)
    separation_bound = Fraction(1, 8 * denominator_bound**16)
    support_scale = min(Fraction(1, 100 * denominator_bound**8), radial_margin / 100)
    if (12 * support_scale) ** 2 >= separation_bound:
        raise AssertionError("support scale does not clear fixed marks")
    if 16 * support_scale >= radial_margin / 2:
        raise AssertionError("support scale does not stay in the foot disk")

    slot_handles = {item["handle"]: item for item in slots["handles"]}
    chart_handles = {item["name"]: item for item in foot_chart["handles"]}
    handles = []
    segment_count = 0
    for handle in tracks["handles"]:
        slot_entries = {item["passage_id"]: item for item in slot_handles[handle["handle"]]["entries"]}
        foot_pair = chart_handles[handle["handle"]]["foot_pair"]
        moves = []
        for track in handle["tracks"]:
            path = [point(track[field]) for field in ("normalized_start", "normalized_waypoint", "normalized_target")]
            segments = []
            for segment_index, (start, end) in enumerate(zip(path, path[1:])):
                direction = (end[0] - start[0], end[1] - start[1])
                if direction == (0, 0):
                    raise AssertionError("zero-length track segment")
                segments.append({
                    "segment_index": segment_index,
                    "start": encode(start),
                    "end": encode(end),
                    "affine_chart": "direction=end-start; positive_normal=(-direction_y,direction_x); x=start+s*direction+u*positive_normal",
                    "support_scale_reference": "#/clearance_certificate/support_scale",
                    "spacetime_template": "corridor_36_tetrahedra/v1",
                })
                segment_count += 1
            entry = slot_entries[track["passage_id"]]
            moves.append({
                "move_index": track["move_index"],
                "passage_id": track["passage_id"],
                "owner": entry["component"],
                "orientation": entry["orientation"],
                "segments": segments,
                "physical_foot_embeddings": {
                    "positive_endpoint": track["positive_foot_endpoint"],
                    "negative_endpoint": track["negative_foot_endpoint"],
                    "pairing_matrix": foot_pair["reflection_matrix"],
                    "rule": "the negative cell is the reflection image of the positive cell",
                },
                "inverse": "reverse segments, exchange start/end, and set time to 1-time",
            })
        handles.append({"handle": handle["handle"], "move_count": len(moves), "moves": moves})

    triangles = template_triangles()
    tetrahedra = prism_tetrahedra(triangles)
    result = {
        "schema": "t73_dotted_disk_ambient_extensions/v2",
        "sources": {
            "foot_to_dotted_disk_tracks": TRACKS.relative_to(ROOT).as_posix(),
            "foot_to_dotted_disk_tracks_payload_sha256": payload_sha(tracks),
            "foot_to_dotted_slot_map": SLOTS.relative_to(ROOT).as_posix(),
            "foot_to_dotted_slot_map_payload_sha256": payload_sha(slots),
            "unified_foot_chart": FOOT_CHART.relative_to(ROOT).as_posix(),
            "unified_foot_chart_payload_sha256": payload_sha(foot_chart),
        },
        "clearance_certificate": {
            "coordinate_denominator_bound": str(denominator_bound),
            "minimum_track_vertex_radial_margin_squared": str(radial_margin),
            "fixed_mark_distance_squared_lower_bound": str(separation_bound),
            "support_scale": str(support_scale),
            "proof_rule": "nonincident rational point/segment distance^2 >= 1/(8*D^16); corridor width <= 12*r and radial displacement <= 16*r",
        },
        "template": {
            "name": "corridor_36_tetrahedra/v1",
            "coordinate_rule": "x = start + s*direction + u*positive_normal",
            "coefficient_vertices": coefficient_vertices(),
            "slice_triangles": [list(item) for item in triangles],
            "spacetime_tetrahedra": [list(item) for item in tetrahedra],
            "outer_boundary_rule": "O0,...,O3 have identical spatial coordinates at time 0 and 1",
            "marked_core_rule": "C moves from s=0 to s=1",
        },
        "handles": handles,
        "move_count": sum(handle["move_count"] for handle in handles),
        "track_segment_count": segment_count,
        "normalized_tetrahedron_instance_count": segment_count * len(tetrahedra),
        "reflection_paired_physical_tetrahedron_count": segment_count * len(tetrahedra) * 2,
        "completion_status": "REFLECTION_PAIRED_AMBIENT_DOTTED_DISK_EXTENSIONS_CONSTRUCTED",
        "scope_boundary": "closes local foot-disk ambient extensions only; does not prove source connector tangle isotopic to railroad target",
    }
    result["sha256"] = canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check and json.loads(OUTPUT.read_text(encoding="utf-8")) != result:
        raise AssertionError("dotted-disk ambient extensions are stale")
    print("T73_DOTTED_DISK_AMBIENT=REFLECTION_PAIRED_AMBIENT_DOTTED_DISK_EXTENSIONS_CONSTRUCTED")


if __name__ == "__main__":
    main()
