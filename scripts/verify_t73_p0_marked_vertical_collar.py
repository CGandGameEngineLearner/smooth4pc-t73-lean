#!/usr/bin/env python3
"""Verify the static marked P0 product collar independently of any braid."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "geometry" / "t73_p0_marked_vertical_collar.json"
CUT = ROOT / "geometry" / "t73_actual_cut_tangle.json"


def load_builder():
    path = ROOT / "scripts" / "build_t73_p0_marked_vertical_collar.py"
    spec = importlib.util.spec_from_file_location("marked_collar_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def point(value: Any, where: str) -> tuple[Fraction, Fraction, Fraction]:
    if not isinstance(value, list) or len(value) != 3:
        raise AssertionError(f"{where} is not a three-coordinate point")
    return tuple(Fraction(entry) for entry in value)  # type: ignore[return-value]


def validate(data: dict[str, Any], cut: dict[str, Any]) -> dict[str, Any]:
    if data.get("schema") != "t73_p0_marked_vertical_collar/v1":
        raise AssertionError("unexpected marked-collar schema")
    if data.get("actual_cut_tangle_sha256") != cut["sha256"]:
        raise AssertionError("marked collar is not bound to the actual cut source IDs")
    if data.get("contains_braid_word") is not False:
        raise AssertionError("P0 marked collar must not contain B44 or another braid word")
    forbidden = {"braid", "braid_word", "B44", "crossings", "six_sweeps"}
    if forbidden & set(data):
        raise AssertionError("P0 collar contains forbidden auxiliary C data")
    arcs = data.get("arcs")
    if not isinstance(arcs, list) or len(arcs) != 44 or data.get("arc_count") != 44:
        raise AssertionError("marked collar does not contain exactly 44 arcs")
    source = {
        int(item["wicket"]): (
            item["owner"],
            int(item["orientation"]),
            item["source_id"],
            item["paired_z_source_id"],
            int(item["word_event_index"]),
        )
        for item in cut["passages"]
    }
    centers = set()
    positive_pushes = set()
    by_wicket = {}
    delta = Fraction(data["normal_delta"])
    if delta <= 0:
        raise AssertionError("product normal has nonpositive width")
    for expected_wicket, arc in enumerate(arcs, start=1):
        if arc["wicket"] != expected_wicket:
            raise AssertionError("wicket order is not 1 through 44")
        expected = source[expected_wicket]
        actual = (
            arc["owner"],
            int(arc["orientation"]),
            arc["source_id"],
            arc["paired_z_source_id"],
            int(arc["actual_word_event_index"]),
        )
        if actual != expected:
            raise AssertionError(f"wicket {expected_wicket} source binding changed")
        if arc["orientation"] not in (-1, 1):
            raise AssertionError("arc orientation is not signed")
        x, y = (Fraction(value) for value in arc["standard_point"])
        if x * x + y * y >= 1:
            raise AssertionError("standard point is outside D2")
        if (x, y) in centers:
            raise AssertionError("two center arcs coincide")
        centers.add((x, y))
        bottom, top = (
            point(value, f"arc {expected_wicket}")
            for value in arc["center_arc"]
        )
        if bottom != (x, y, -1) or top != (x, y, 1):
            raise AssertionError("center arc is not vertical from bottom to top disk")
        normal = point(arc["product_normal"], "product_normal")
        if normal != (0, delta, 0):
            raise AssertionError("normal is not the constant selected product normal")
        pushed_bottom, pushed_top = (
            point(value, "positive_push_off_arc")
            for value in arc["positive_push_off_arc"]
        )
        if pushed_bottom != (x, y + delta, -1) or pushed_top != (x, y + delta, 1):
            raise AssertionError("positive push-off does not follow the normal")
        if x * x + (y + delta) * (y + delta) >= 1:
            raise AssertionError("positive push-off leaves D2")
        if (x, y + delta) in positive_pushes:
            raise AssertionError("two positive push-offs coincide")
        positive_pushes.add((x, y + delta))
        rectangle = arc["framing_rectangle"]
        vertices = [point(value, "framing_rectangle") for value in rectangle["vertices"]]
        if vertices != [bottom, top, pushed_top, pushed_bottom]:
            raise AssertionError("framing rectangle vertices do not span center and push-off")
        if rectangle["triangles"] != [[0, 1, 2], [0, 2, 3]]:
            raise AssertionError("framing rectangle triangulation changed")
        by_wicket[expected_wicket] = arc
    if centers & positive_pushes:
        raise AssertionError("a framing push-off meets a center arc")
    if data["owner_counts"] != {"m_2": 42, "r_xy": 2}:
        raise AssertionError("owner counts are not 42 plus 2")
    if data["orientation_counts"] != {
        "positive": sum(item["orientation"] == 1 for item in arcs),
        "negative": sum(item["orientation"] == -1 for item in arcs),
    }:
        raise AssertionError("orientation counts are stale")

    endpoints = data.get("doubled_endpoint_order")
    if not isinstance(endpoints, list) or len(endpoints) != 88:
        raise AssertionError("doubled endpoint marking does not have 88 entries")
    expected_wickets = [w for w in [1, 2] + list(reversed(range(3, 45))) for _ in range(2)]
    expected_sides = ["neg", "pos"] * 44
    endpoint_points = set()
    for index, endpoint in enumerate(endpoints):
        if endpoint["index"] != index:
            raise AssertionError("endpoint indices are not consecutive")
        if endpoint["wicket"] != expected_wickets[index] or endpoint["side"] != expected_sides[index]:
            raise AssertionError("doubled endpoint order changed")
        arc = by_wicket[endpoint["wicket"]]
        if endpoint["owner"] != arc["owner"] or endpoint["orientation"] != arc["orientation"]:
            raise AssertionError("endpoint owner or orientation changed")
        expected_source = (
            arc["paired_z_source_id"] if endpoint["side"] == "neg" else arc["source_id"]
        )
        expected_coefficient = -1 if endpoint["side"] == "neg" else 1
        if endpoint["source_id"] != expected_source or endpoint["normal_coefficient"] != expected_coefficient:
            raise AssertionError("endpoint side is not bound to the correct physical source")
        x, y = (Fraction(value) for value in arc["standard_point"])
        expected_point = (x, y + expected_coefficient * delta, Fraction(0))
        actual_point = point(endpoint["point"], "doubled endpoint")
        if actual_point != expected_point or actual_point[0] ** 2 + actual_point[1] ** 2 >= 1:
            raise AssertionError("doubled endpoint has the wrong product-normal coordinate")
        if actual_point in endpoint_points:
            raise AssertionError("two doubled endpoints coincide")
        endpoint_points.add(actual_point)
    if data.get("doubled_endpoint_count") != 88:
        raise AssertionError("doubled endpoint count is stale")
    return {
        "ARCS": 44,
        "ENDPOINTS": 88,
        "OWNER_COUNTS": data["owner_counts"],
        "PAIRWISE_DISJOINT_CENTER_ARCS": "PASS",
        "PAIRWISE_DISJOINT_PUSH_OFFS": "PASS",
        "BOUNDARY_ENDPOINTS": "PASS",
        "PRODUCT_FRAMING_RECTANGLES": "PASS",
        "SOURCE_BINDING": "PASS",
        "BRAID_IN_P0": "ABSENT",
    }


def mutations(data, cut):
    cases = {}
    mutant = copy.deepcopy(data)
    mutant["arcs"][1]["standard_point"] = mutant["arcs"][0]["standard_point"]
    cases["duplicate_center"] = mutant
    mutant = copy.deepcopy(data)
    mutant["arcs"][0]["orientation"] *= -1
    cases["orientation"] = mutant
    mutant = copy.deepcopy(data)
    mutant["arcs"][0]["owner"] = "m_2"
    cases["owner"] = mutant
    mutant = copy.deepcopy(data)
    mutant["arcs"][0]["product_normal"] = ["0", "0", "0"]
    cases["zero_normal"] = mutant
    mutant = copy.deepcopy(data)
    mutant["braid_word"] = [1, -1]
    cases["braid_in_p0"] = mutant
    mutant = copy.deepcopy(data)
    mutant["doubled_endpoint_order"][0], mutant["doubled_endpoint_order"][1] = (
        mutant["doubled_endpoint_order"][1],
        mutant["doubled_endpoint_order"][0],
    )
    cases["endpoint_order"] = mutant
    results = {}
    for name, candidate in cases.items():
        try:
            validate(candidate, cut)
        except AssertionError:
            results[name] = "FAIL"
        else:
            results[name] = "UNDETECTED"
    return results


def verify() -> dict[str, Any]:
    builder = load_builder()
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    cut = json.loads(CUT.read_text(encoding="utf-8"))
    if stored != builder.build():
        raise AssertionError("committed marked collar differs from live reconstruction")
    checks = validate(stored, cut)
    mutation_results = mutations(stored, cut)
    if set(mutation_results.values()) != {"FAIL"}:
        raise AssertionError(f"a marked-collar mutation survived: {mutation_results}")
    return {
        "T73_P0_MARKED_VERTICAL_COLLAR": "PASS",
        **checks,
        "MUTATIONS": mutation_results,
        "SHA256": stored["sha256"],
    }


def main() -> None:
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
