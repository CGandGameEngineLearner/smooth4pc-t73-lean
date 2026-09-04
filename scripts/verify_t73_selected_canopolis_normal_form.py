#!/usr/bin/env python3
"""Verify the selected four-box canopolis normal form with exact arithmetic."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "geometry" / "t73_selected_canopolis_normal_form.json"
PRIMITIVES = ROOT / "geometry" / "t73_all_owner_product_primitives.json"


def load_builder():
    path = ROOT / "scripts" / "build_t73_selected_canopolis_normal_form.py"
    spec = importlib.util.spec_from_file_location("canopolis_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def point(raw):
    return tuple(Fraction(value) for value in raw)


def inside(point_value, lower, upper, strict=False):
    if strict:
        return all(lower[i] < point_value[i] < upper[i] for i in range(3))
    return all(lower[i] <= point_value[i] <= upper[i] for i in range(3))


def disjoint_boxes(left, right):
    return any(left[1][i] < right[0][i] or right[1][i] < left[0][i] for i in range(3))


def validate(data, all_owner):
    if data["schema"] != "t73_selected_canopolis_normal_form/v1":
        raise AssertionError("unexpected canopolis normal-form schema")
    if data["dependencies"]["all_owner_primitives_sha256"] != all_owner["sha256"]:
        raise AssertionError("normal form is stale relative to all-owner primitives")
    if data["contains_braid_word"] is not False or any(
        key in data for key in ("B44", "braid", "braid_word", "crossings")
    ):
        raise AssertionError("canopolis normal form contains detector braid data")
    if (
        data["primitive_count"],
        data["active_corridor_count"],
        data["added_z_arc_count"],
    ) != (271, 44, 227):
        raise AssertionError("selected primitive counts changed")
    primitives = data["primitives"]
    if len(primitives) != 271 or len({item["primitive_id"] for item in primitives}) != 271:
        raise AssertionError("primitive IDs are incomplete or duplicated")
    if sum(item["role"] == "active_yz_corridor" for item in primitives) != 44:
        raise AssertionError("active corridor count does not follow the primitives")
    if sum(item["role"] == "added_z_arc" for item in primitives) != 227:
        raise AssertionError("added z count does not follow the primitives")
    cyclic = [item for item in primitives if item["is_cyclic_m2_connector"]]
    if len(cyclic) != 1 or cyclic[0]["source_ids"] != ["m_2:C_i", "c1:letter:0"]:
        raise AssertionError("cyclic m2 connector is absent or not unique")
    if cyclic[0]["connector_kind"] != "cyclic_bottom_top_connector_after_t_cancellation":
        raise AssertionError("cyclic m2 connector lost its cancellation-collar type")
    if any(item["relative_twist"] != 0 for item in primitives):
        raise AssertionError("a primitive is not product framed")

    closure_boxes = [
        (point(item["lower"]), point(item["upper"]))
        for item in data["closure_balls"]
    ]
    if len(closure_boxes) != 2 or not disjoint_boxes(*closure_boxes):
        raise AssertionError("the two closure balls are not disjoint")
    if not (closure_boxes[0][1][0] < 0 < closure_boxes[1][0][0]):
        raise AssertionError("x=0 does not separate the closure balls")
    boxes = {}
    closure_by_name = {
        item["name"]: bounds
        for item, bounds in zip(data["closure_balls"], closure_boxes)
    }
    for item in data["insertion_balls"]:
        bounds = (point(item["lower"]), point(item["upper"]))
        if item["name"] in boxes:
            raise AssertionError("duplicate insertion ball")
        boxes[item["name"]] = bounds
        closure = closure_by_name[item["closure"]]
        if not inside(bounds[0], closure[0], closure[1], strict=True) or not inside(
            bounds[1], closure[0], closure[1], strict=True
        ):
            raise AssertionError("an insertion ball is not strictly inside its closure ball")
    if set(boxes) != {"Y_source", "Z_target", "Z_source", "Y_target"}:
        raise AssertionError("the four insertion balls are not parametrized")
    for first in boxes:
        for second in boxes:
            if first < second and not disjoint_boxes(boxes[first], boxes[second]):
                raise AssertionError("two insertion balls overlap")

    delta = Fraction(data["product_normal"][1])
    if point(data["product_normal"]) != (0, delta, 0) or delta <= 0:
        raise AssertionError("product normal is invalid")
    expected_ends = {
        "left": (Fraction(-7), Fraction(-3)),
        "right": (Fraction(3), Fraction(7)),
    }
    for side, records in (
        ("left", data["left_closure_strands"]),
        ("right", data["right_closure_strands"]),
    ):
        if len(records) != 271:
            raise AssertionError(f"{side} closure does not have 271 strands")
        lane_points = set()
        pushed_points = set()
        for index, record in enumerate(records):
            primitive = primitives[index]
            if record["index"] != index or record["side"] != side:
                raise AssertionError("strand index or side changed")
            for field in ("role", "primitive_id", "owner", "source_ids", "is_cyclic_m2_connector"):
                if record[field] != primitive[field]:
                    raise AssertionError(f"strand lost primitive field {field}")
            start, end = (point(value) for value in record["centerline"])
            source_x, target_x = expected_ends[side]
            if start[0] != source_x or end[0] != target_x or start[1:] != end[1:]:
                raise AssertionError("normal-form strand is not a straight product corridor")
            if side == "left" and not (start[0] < 0 and end[0] < 0):
                raise AssertionError("left strand crosses the separating plane")
            if side == "right" and not (start[0] > 0 and end[0] > 0):
                raise AssertionError("right strand crosses the separating plane")
            lane = start[1:]
            if lane in lane_points:
                raise AssertionError("two strands occupy the same private lane")
            lane_points.add(lane)
            if record["relative_twist"] != 0 or point(record["product_normal"]) != (0, delta, 0):
                raise AssertionError("strand framing is not the common product framing")
            push_start, push_end = (point(value) for value in record["positive_push_off"])
            if push_start != (start[0], start[1] + delta, start[2]) or push_end != (
                end[0],
                end[1] + delta,
                end[2],
            ):
                raise AssertionError("strand push-off does not extend the product normal")
            pushed_lane = push_start[1:]
            if pushed_lane in lane_points or pushed_lane in pushed_points:
                raise AssertionError("a push-off meets a centre or another push-off")
            pushed_points.add(pushed_lane)
        if lane_points & pushed_points:
            raise AssertionError("product push-offs meet centre strands")
    if not data["two_representable_pattern"]["split_union"]:
        raise AssertionError("two representable closures are not split")
    if not data["two_representable_pattern"]["relative_to_all_four_insertion_balls"]:
        raise AssertionError("normal form is not relative to all insertion balls")
    cyclic_lane = data["cyclic_connector"]["private_lane"]
    if not 0 <= cyclic_lane < 44 or not primitives[cyclic_lane]["is_cyclic_m2_connector"]:
        raise AssertionError("cyclic connector private lane is wrong")
    return {
        "FOUR_INSERTION_BALLS": "PASS",
        "TWO_DISJOINT_CLOSURE_BALLS": "PASS",
        "SEPARATING_SPHERE": "PASS",
        "ACTIVE_CORRIDORS": 44,
        "ADDED_Z_ARCS": 227,
        "CYCLIC_CONNECTOR": "PASS",
        "PAIRWISE_DISJOINT_STRANDS": "PASS",
        "PRODUCT_FRAMINGS": "PASS",
        "BRAID_DATA": "ABSENT",
    }


def mutation_results(data, all_owner):
    cases = {}
    mutant = copy.deepcopy(data)
    mutant["primitives"][data["cyclic_connector"]["private_lane"]]["is_cyclic_m2_connector"] = False
    cases["cyclic_connector"] = mutant
    mutant = copy.deepcopy(data)
    mutant["added_z_arc_count"] = 226
    cases["added_count"] = mutant
    mutant = copy.deepcopy(data)
    mutant["insertion_balls"][0]["upper"][0] = "2"
    cases["box_separator"] = mutant
    mutant = copy.deepcopy(data)
    mutant["left_closure_strands"][0]["centerline"][1][0] = "1"
    cases["strand_separator"] = mutant
    mutant = copy.deepcopy(data)
    mutant["left_closure_strands"][1]["centerline"] = copy.deepcopy(
        mutant["left_closure_strands"][0]["centerline"]
    )
    cases["private_lane"] = mutant
    mutant = copy.deepcopy(data)
    mutant["right_closure_strands"][0]["relative_twist"] = 1
    cases["framing"] = mutant
    results = {}
    for name, candidate in cases.items():
        try:
            validate(candidate, all_owner)
        except AssertionError:
            results[name] = "FAIL"
        else:
            results[name] = "UNDETECTED"
    return results


def verify():
    builder = load_builder()
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    all_owner = json.loads(PRIMITIVES.read_text(encoding="utf-8"))
    if stored != builder.build():
        raise AssertionError("committed canopolis normal form differs from rebuild")
    checks = validate(stored, all_owner)
    mutations = mutation_results(stored, all_owner)
    if set(mutations.values()) != {"FAIL"}:
        raise AssertionError(f"a canopolis mutation survived: {mutations}")
    return {
        "T73_SELECTED_CANOPOLIS_NORMAL_FORM": "PASS_TARGET_ONLY",
        **{f"TARGET_{key}": value for key, value in checks.items()},
        "SOURCE_RELATIVE_ISOTOPY": "OPEN",
        "BOUNDARY_ENDPOINT_INCIDENCE": "OPEN",
        "GRADING_CORRECTION": "UNDETERMINED_UNTIL_ISOTOPY_VS_COBORDISM",
        "MUTATIONS": mutations,
        "SHA256": stored["sha256"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.check:
        for key, value in result.items():
            print(f"{key}={value}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
