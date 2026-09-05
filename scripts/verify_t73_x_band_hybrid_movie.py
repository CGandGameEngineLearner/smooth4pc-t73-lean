#!/usr/bin/env python3
"""Independently replay all 1513 chart-typed hybrid replacement states."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from verify_t73_x_band0_hybrid_state import verify as verify_band0
from build_t73_x_band_local_movie_receipt import check_receipt
from verify_t73_x_band_local_movie import expand_band
from verify_t73_x_m1_parallel_foliation import verify as verify_foliation
from verify_t73_x_source_chart_germs import verify as verify_sources

ROOT = Path(__file__).resolve().parents[1]
MOVIE = ROOT / "geometry/t73_x_band_hybrid_movie.json"
LOCAL_MOVIE = ROOT / "geometry/t73_x_band_local_movie.json"
SOURCE_GERMS = ROOT / "geometry/t73_x_source_chart_germs.json"
FOLIATION = ROOT / "geometry/t73_x_m1_parallel_foliation.json"
X_CANCELLATION = ROOT / "geometry/t73_cancel_x_m1.json"
POST_CANCEL = ROOT / "geometry/t73_t_hcs_handle_pair_deletion.json"
AR_LINK = ROOT / "geometry/t73_actual_ar_link.json"
BAND0 = ROOT / "geometry/t73_x_band_hybrid_state_0000_0001.json"
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
        before, points[center_index - 1], points[center_index], normals[center_index - 1], normals[center_index]
    )
    after_normal = interpolate(
        after, points[center_index], points[center_index + 1], normals[center_index], normals[center_index + 1]
    )
    values = [
        after,
        *points[center_index + 1 :],
        *[translate(points[index], deck) for index in range(1, center_index)],
        translate(before, deck),
    ]
    value_normals = [
        after_normal,
        *normals[center_index + 1 :],
        *normals[1:center_index],
        before_normal,
    ]
    return values, value_normals


def source_interval_global(local_interval, germ):
    deck = tuple(germ["global_deck"])
    if germ["chart"] == "mapping_torus_top_global":
        return [translate(value, deck) for value in local_interval]
    return [
        tuple(value[axis] + PERIOD * deck[axis] for axis in range(3))
        for value in local_interval
    ]


def base_hashes(post_cancel, ar_link):
    output = {
        component: post_cancel["deletion"]["remaining_components"][component][
            "state6_core_sha256"
        ]
        for component in ("m_2", "m_3")
    }
    for component in ("r_xy", "r_zx"):
        output[component] = canonical_sha(ar_link["components"][component]["polyline"])
    return output


def verify() -> dict:
    prerequisite_verdicts = {
        "local_movie": check_receipt()["full_verifier_verdict"],
        "source_germs": verify_sources()["verdict"],
        "target_foliation": verify_foliation()["verdict"],
        "band0_hybrid": verify_band0()["verdict"],
    }
    movie = json.loads(MOVIE.read_text(encoding="utf-8"))
    local_movie = json.loads(LOCAL_MOVIE.read_text(encoding="utf-8"))
    germs_data = json.loads(SOURCE_GERMS.read_text(encoding="utf-8"))
    foliation = json.loads(FOLIATION.read_text(encoding="utf-8"))
    cancellation = json.loads(X_CANCELLATION.read_text(encoding="utf-8"))
    post_cancel = json.loads(POST_CANCEL.read_text(encoding="utf-8"))
    ar_link = json.loads(AR_LINK.read_text(encoding="utf-8"))
    band0 = json.loads(BAND0.read_text(encoding="utf-8"))
    if movie["completion_status"] != "ALL_1513_X_HYBRID_REPLACEMENT_CELLS_CONSTRUCTED":
        raise AssertionError("x hybrid movie scope changed")
    expected_hashes = {
        "x_local_movie_sha256": local_movie["sha256"],
        "x_source_chart_germs_sha256": germs_data["sha256"],
        "m1_parallel_foliation_sha256": foliation["sha256"],
        "post_t_hcs_deletion_sha256": post_cancel["sha256"],
        "verified_band0_hybrid_sha256": band0["sha256"],
    }
    if any(movie[field] != value for field, value in expected_hashes.items()):
        raise AssertionError("x hybrid movie has stale prerequisites")
    germs = {item["band_index"]: item for item in germs_data["germs"]}
    base = [point(value) for value in foliation["base_vertices"]]
    normals = [point(value) for value in foliation["unit_normal_field"]]
    bases = base_hashes(post_cancel, ar_link)
    leaves = {
        component: {
            "base": canonical_sha(
                {"component": component, "base_geometry_sha256": geometry_hash}
            )
        }
        for component, geometry_hash in bases.items()
    }
    gluing_checks = inverse_checks = 0
    seen_source_ranges = set()
    for record, local_record, band in zip(
        movie["transitions"], local_movie["bands"], cancellation["slide_bands"]
    ):
        index = band["index"]
        germ = germs[index]
        component = band["component"]
        if record["band_index"] != index or record["source_germ_sha256"] != canonical_sha(germ):
            raise AssertionError("hybrid transition order or source germ changed")
        vertices, _, band_normals, _, _, _, _, _, _, _ = expand_band(band)
        source_local = [vertices[0], vertices[1]]
        source_global = source_interval_global(source_local, germ)
        if record["source_interval_local_sha256"] != canonical_sha(encode_points(source_local)) or record["source_interval_global_sha256"] != canonical_sha(encode_points(source_global)):
            raise AssertionError("hybrid source interval changed")
        range_key = (component, tuple(germ["global_vertex_range"]))
        if range_key in seen_source_ranges:
            raise AssertionError("hybrid source intervals are not globally distinct")
        seen_source_ranges.add(range_key)

        orientation = band["replacement_orientation"]
        width = Fraction(band["band_width"])
        target_center = tuple((left + right) / 2 for left, right in zip(vertices[4], vertices[5]))
        target_before_local = (Fraction(2) - orientation * width, *target_center[1:])
        target_after_local = (Fraction(2) + orientation * width, *target_center[1:])
        target_before_global = (-target_before_local[0], target_before_local[1], target_before_local[2] + 4, Fraction(0))
        target_after_global = (-target_after_local[0], target_after_local[1], target_after_local[2] + 4, Fraction(0))
        if record["target_interval_local_oriented_sha256"] != canonical_sha(encode_points([target_before_local, target_after_local])) or record["target_interval_global_oriented_sha256"] != canonical_sha(encode_points([target_before_global, target_after_global])):
            raise AssertionError("hybrid target interval changed")
        level = local_record["target_parallel_coefficient"]
        level_points = [
            tuple(value[axis] + level * normal[axis] for axis in range(4))
            for value, normal in zip(base, normals)
        ]
        if orientation == 1:
            oriented_points = level_points
            oriented_normals = normals
            deck = (-1, 0, 1)
            center_index = 3
        else:
            oriented_points = list(reversed(level_points))
            oriented_normals = list(reversed(normals))
            deck = (1, 0, -1)
            center_index = len(level_points) - 4
        complement, complement_normals = cut_complement(
            oriented_points,
            oriented_normals,
            center_index,
            target_before_global,
            target_after_global,
            deck,
        )
        negative = [vertices[value] for value in (0, 2, 4)]
        positive = [vertices[value] for value in (5, 3, 1)]
        negative_normals = [band_normals[value] for value in (0, 2, 4)]
        positive_normals = [band_normals[value] for value in (5, 3, 1)]
        expected_geometry = {
            "negative_lane_sha256": canonical_sha(encode_points(negative)),
            "negative_lane_normal_sha256": canonical_sha(encode_points(negative_normals)),
            "target_parallel_complement_sha256": canonical_sha(encode_points(complement)),
            "target_parallel_complement_normal_sha256": canonical_sha(encode_points(complement_normals)),
            "positive_lane_sha256": canonical_sha(encode_points(positive)),
            "positive_lane_normal_sha256": canonical_sha(encode_points(positive_normals)),
            "target_oriented_closing_deck": list(deck),
        }
        if any(record[field] != value for field, value in expected_geometry.items()):
            raise AssertionError("hybrid replacement piece geometry changed")
        if negative[0] != source_local[0] or positive[-1] != source_local[1] or negative[-1] != target_after_local or positive[0] != target_before_local:
            raise AssertionError("hybrid local band boundary does not glue")
        if complement[0] != target_after_global or complement[-1] != translate(target_before_global, deck):
            raise AssertionError("hybrid target complement endpoints do not glue")
        gluing_checks += 4
        if record["intersection_orientation_sum"] != 0:
            raise AssertionError("hybrid replacement does not cancel its x intersection")
        before_state = merkle_state_sha(leaves[component])
        descriptor = {
            "band_index": index,
            "source_id": band["source_id"],
            "source_chart": germ["chart"],
            "source_interval_global_sha256": canonical_sha(encode_points(source_global)),
            "negative_lane_sha256": expected_geometry["negative_lane_sha256"],
            "target_level": level,
            "target_complement_sha256": expected_geometry["target_parallel_complement_sha256"],
            "positive_lane_sha256": expected_geometry["positive_lane_sha256"],
        }
        replacement_sha = canonical_sha(descriptor)
        if record["replacement_cell_sha256"] != replacement_sha or record["component_state_before_sha256"] != before_state:
            raise AssertionError("hybrid component state-before changed")
        leaves[component][f"band:{index}"] = replacement_sha
        after_state = merkle_state_sha(leaves[component])
        if record["component_state_after_sha256"] != after_state or record["inverse_restores_component_state_sha256"] != before_state:
            raise AssertionError("hybrid component state-after or inverse changed")
        inverse_checks += 1
    expected_final = {
        component: {
            "replacement_count": len(component_leaves) - 1,
            "state_sha256": merkle_state_sha(component_leaves),
        }
        for component, component_leaves in leaves.items()
    }
    if movie["final_component_states"] != expected_final:
        raise AssertionError("hybrid final component states changed")
    return {
        "verdict": "PASS_ALL_1513_X_HYBRID_PIECE_WORD_STATES",
        "transitions": len(movie["transitions"]),
        "chart_gluing_checks": gluing_checks,
        "inverse_state_checks": inverse_checks,
        "unique_source_ranges": len(seen_source_ranges),
        "component_replacement_counts": {
            component: value["replacement_count"]
            for component, value in expected_final.items()
        },
        "prerequisite_verdicts": prerequisite_verdicts,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
