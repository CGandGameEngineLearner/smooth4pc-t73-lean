#!/usr/bin/env python3
"""Build all 1513 global/local hybrid x-band replacement states."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from verify_t73_x_band_local_movie import expand_band

ROOT = Path(__file__).resolve().parents[1]
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
SOURCE_GERMS = ROOT / "geometry/t73_x_source_chart_germs.json"
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
POST_CANCEL = ROOT / "geometry/t73_t_hcs_handle_pair_deletion.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
BAND0_HYBRID = ROOT / "geometry/t73_x_band_hybrid_state_0000_0001.json"
OUTPUT = ROOT / "geometry/t73_x_band_hybrid_movie.json"
PERIOD = Fraction(4)


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def point(values):
    return tuple(Fraction(value) for value in values)


def encode(value):
    return [str(coordinate) for coordinate in value]


def encode_points(values):
    return [encode(value) for value in values]


def translate(value, deck):
    return tuple(value[axis] + PERIOD * deck[axis] for axis in range(3)) + tuple(
        value[3:]
    )


def merkle_state_sha(leaves):
    digest = hashlib.sha256()
    for key in sorted(leaves):
        digest.update(bytes.fromhex(leaves[key]))
    return digest.hexdigest().upper()


def cut_complement(points, normals, center_index, before, after, deck):
    def interpolate(value, start, end, start_value, end_value):
        parameter = (value[0] - start[0]) / (end[0] - start[0])
        return tuple(
            start_value[axis]
            + parameter * (end_value[axis] - start_value[axis])
            for axis in range(4)
        )

    before_normal = interpolate(
        before,
        points[center_index - 1],
        points[center_index],
        normals[center_index - 1],
        normals[center_index],
    )
    after_normal = interpolate(
        after,
        points[center_index],
        points[center_index + 1],
        normals[center_index],
        normals[center_index + 1],
    )
    complement = [
        after,
        *points[center_index + 1 :],
        *[translate(points[index], deck) for index in range(1, center_index)],
        translate(before, deck),
    ]
    complement_normals = [
        after_normal,
        *normals[center_index + 1 :],
        *normals[1:center_index],
        before_normal,
    ]
    return complement, complement_normals


def source_interval_global(local_interval, germ):
    deck = tuple(germ["global_deck"])
    if germ["chart"] == "mapping_torus_top_global":
        return [translate(value, deck) for value in local_interval]
    return [
        tuple(value[axis] + PERIOD * deck[axis] for axis in range(3))
        for value in local_interval
    ]


def component_base_hashes(post_cancel, ar_link):
    hashes = {}
    for component in ("m_2", "m_3"):
        hashes[component] = post_cancel["deletion"]["remaining_components"][component][
            "state6_core_sha256"
        ]
    for component in ("r_xy", "r_zx"):
        hashes[component] = canonical_sha(ar_link["components"][component]["polyline"])
    return hashes


def build() -> dict:
    local_movie = json.loads(LOCAL_MOVIE.read_text(encoding="utf-8"))
    germs_data = json.loads(SOURCE_GERMS.read_text(encoding="utf-8"))
    foliation = json.loads(FOLIATION.read_text(encoding="utf-8"))
    cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    post_cancel = json.loads(POST_CANCEL.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    band0_hybrid = json.loads(BAND0_HYBRID.read_text(encoding="utf-8"))
    germs = {item["band_index"]: item for item in germs_data["germs"]}
    base = [point(value) for value in foliation["base_vertices"]]
    unit_normals = [point(value) for value in foliation["unit_normal_field"]]
    base_deck = (-1, 0, 1)
    base_hashes = component_base_hashes(post_cancel, ar_link)
    component_leaves = {
        component: {
            "base": canonical_sha(
                {"component": component, "base_geometry_sha256": geometry_hash}
            )
        }
        for component, geometry_hash in base_hashes.items()
    }
    transitions = []
    for band, local_record in zip(cancellation["slide_bands"], local_movie["bands"]):
        index = band["index"]
        germ = germs[index]
        vertices, _, normals, _, _, _, _, _, _, _ = expand_band(band)
        orientation = band["replacement_orientation"]
        width = Fraction(band["band_width"])
        source_center = vertices[0]
        source_interval_local = [vertices[0], vertices[1]]
        source_interval = source_interval_global(source_interval_local, germ)
        target_center = tuple((left + right) / 2 for left, right in zip(vertices[4], vertices[5]))
        target_before_local = (
            Fraction(2) - orientation * width,
            *target_center[1:],
        )
        target_after_local = (
            Fraction(2) + orientation * width,
            *target_center[1:],
        )
        level = local_record["target_parallel_coefficient"]
        level_points = [
            tuple(value[axis] + level * normal[axis] for axis in range(4))
            for value, normal in zip(base, unit_normals)
        ]
        level_normals = list(unit_normals)
        if orientation == 1:
            oriented_points = level_points
            oriented_normals = level_normals
            oriented_deck = base_deck
            center_index = 3
        else:
            oriented_points = list(reversed(level_points))
            oriented_normals = list(reversed(level_normals))
            oriented_deck = tuple(-value for value in base_deck)
            center_index = len(level_points) - 1 - 3
        target_before_global = (
            -target_before_local[0],
            target_before_local[1],
            target_before_local[2] + 4,
            Fraction(0),
        )
        target_after_global = (
            -target_after_local[0],
            target_after_local[1],
            target_after_local[2] + 4,
            Fraction(0),
        )
        target_complement, target_complement_normals = cut_complement(
            oriented_points,
            oriented_normals,
            center_index,
            target_before_global,
            target_after_global,
            oriented_deck,
        )
        negative_lane = [vertices[value] for value in (0, 2, 4)]
        positive_lane = [vertices[value] for value in (5, 3, 1)]
        negative_normals = [normals[value] for value in (0, 2, 4)]
        positive_normals = [normals[value] for value in (5, 3, 1)]
        component = band["component"]
        before_state = merkle_state_sha(component_leaves[component])
        replacement_descriptor = {
            "band_index": index,
            "source_id": band["source_id"],
            "source_chart": germ["chart"],
            "source_interval_global_sha256": canonical_sha(
                encode_points(source_interval)
            ),
            "negative_lane_sha256": canonical_sha(encode_points(negative_lane)),
            "target_level": level,
            "target_complement_sha256": canonical_sha(
                encode_points(target_complement)
            ),
            "positive_lane_sha256": canonical_sha(encode_points(positive_lane)),
        }
        replacement_sha = canonical_sha(replacement_descriptor)
        component_leaves[component][f"band:{index}"] = replacement_sha
        after_state = merkle_state_sha(component_leaves[component])
        transitions.append({
            "band_index": index,
            "state_before": index,
            "state_after": index + 1,
            "component": component,
            "source_id": band["source_id"],
            "source_germ_sha256": canonical_sha(germ),
            "source_interval_local_sha256": canonical_sha(
                encode_points(source_interval_local)
            ),
            "source_interval_global_sha256": replacement_descriptor[
                "source_interval_global_sha256"
            ],
            "negative_lane_sha256": replacement_descriptor["negative_lane_sha256"],
            "negative_lane_normal_sha256": canonical_sha(
                encode_points(negative_normals)
            ),
            "target_parallel_level": level,
            "target_orientation": orientation,
            "target_oriented_closing_deck": list(oriented_deck),
            "target_interval_local_oriented_sha256": canonical_sha(
                encode_points([target_before_local, target_after_local])
            ),
            "target_interval_global_oriented_sha256": canonical_sha(
                encode_points([target_before_global, target_after_global])
            ),
            "target_parallel_complement_vertex_count": len(target_complement),
            "target_parallel_complement_sha256": replacement_descriptor[
                "target_complement_sha256"
            ],
            "target_parallel_complement_normal_sha256": canonical_sha(
                encode_points(target_complement_normals)
            ),
            "positive_lane_sha256": replacement_descriptor["positive_lane_sha256"],
            "positive_lane_normal_sha256": canonical_sha(
                encode_points(positive_normals)
            ),
            "chart_gluing_count": 4,
            "intersection_orientation_sum": (
                band["removed_x_orientation"] - band["replacement_orientation"]
            ),
            "replacement_cell_sha256": replacement_sha,
            "component_state_before_sha256": before_state,
            "component_state_after_sha256": after_state,
            "inverse_restores_component_state_sha256": before_state,
            "status": "HYBRID_REPLACEMENT_CELL_CONSTRUCTED",
        })
    band0_pieces = {item["name"]: item for item in band0_hybrid["pieces"]}
    first = transitions[0]
    if (
        first["negative_lane_sha256"]
        != canonical_sha(band0_pieces["negative_band_lane"]["vertices"])
        or first["positive_lane_sha256"]
        != canonical_sha(band0_pieces["positive_band_lane"]["vertices"])
        or first["target_parallel_complement_sha256"]
        != band0_pieces["oriented_m1_parallel_complement"]["vertices_sha256"]
    ):
        raise AssertionError("generic hybrid movie does not reproduce verified band 0")
    result = {
        "schema": "t73_x_band_hybrid_movie/v1",
        "x_local_movie_sha256": local_movie["sha256"],
        "x_source_chart_germs_sha256": germs_data["sha256"],
        "m1_parallel_foliation_sha256": foliation["sha256"],
        "post_t_hcs_deletion_sha256": post_cancel["sha256"],
        "verified_band0_hybrid_sha256": band0_hybrid["sha256"],
        "transitions": transitions,
        "final_component_states": {
            component: {
                "replacement_count": len(leaves) - 1,
                "state_sha256": merkle_state_sha(leaves),
            }
            for component, leaves in component_leaves.items()
        },
        "completion_status": "ALL_1513_X_HYBRID_REPLACEMENT_CELLS_CONSTRUCTED",
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
        raise AssertionError("x hybrid movie is stale")
    print("T73_X_HYBRID_MOVIE=ALL_1513_X_HYBRID_REPLACEMENT_CELLS_CONSTRUCTED")


if __name__ == "__main__":
    main()
