#!/usr/bin/env python3
"""Verify the one-cup target while refusing the absent source currying map."""

from __future__ import annotations

import argparse
import importlib.util
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "geometry" / "t73_single_hom_defect_target.json"


def load_builder():
    path = ROOT / "scripts" / "build_t73_single_hom_defect_target.py"
    spec = importlib.util.spec_from_file_location("single_hom_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def point(raw):
    return tuple(Fraction(value) for value in raw)


def verify():
    builder = load_builder()
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if stored != builder.build():
        raise AssertionError("single-Hom target differs from live reconstruction")
    if stored["morphism_type"] != {"source": "P86", "target": "P88"}:
        raise AssertionError("single-Hom boundary type changed")
    if len(stored["bottom_endpoints"]) != 86 or len(stored["top_endpoints"]) != 88:
        raise AssertionError("P86/P88 endpoint count changed")
    if [item["bottom_index"] for item in stored["bottom_endpoints"]] != list(range(86)):
        raise AssertionError("bottom endpoint order changed")
    if [item["top_index"] for item in stored["top_endpoints"]] != list(range(88)):
        raise AssertionError("top endpoint order changed")
    through = [cell for cell in stored["cells"] if cell["kind"] == "through_strand"]
    cups = [cell for cell in stored["cells"] if cell["kind"] == "one_cup"]
    if len(through) != 86 or len(cups) != 1:
        raise AssertionError("target is not 86 through strands plus one cup")
    if cups[0]["top_indices"] != [0, 1] or len(cups[0]["bpw_A6_terms"]) != 2:
        raise AssertionError("selected pivotal cup changed")
    for cell in through:
        start, end = (point(value) for value in cell["vertices"])
        if start[:2] != end[:2] or start[2] != 0 or end[2] != 1:
            raise AssertionError("a through cell is not vertical")
        if point(cell["product_normal"]) != (0, 1, 0):
            raise AssertionError("through product normal changed")
    cup_vertices = [point(value) for value in cups[0]["vertices"]]
    if cup_vertices[0] != point(stored["top_endpoints"][0]["point"]) or cup_vertices[-1] != point(stored["top_endpoints"][1]["point"]):
        raise AssertionError("cup feet are not target positions 0 and 1")
    if stored["source_exterior_interval_count"] != 630:
        raise AssertionError("source interval count changed")
    if stored["source_to_target_interval_map"] or stored["z_coend_gluing_cells"]:
        raise AssertionError("unverified source/gluing cells were inserted")
    if stored["source_to_target_status"] != "OPEN":
        raise AssertionError("single-Hom target improperly claims the source map")
    if stored["grading"]["gluing_cobordism_euler"] != "UNDETERMINED":
        raise AssertionError("gluing Euler degree was asserted without cells")
    return {
        "T73_SINGLE_HOM_DEFECT_TARGET": "PASS_TARGET_ONLY",
        "MORPHISM": "P86_TO_P88",
        "THROUGH": 86,
        "CUP": 1,
        "SOURCE_INTERVALS": 630,
        "Z_COEND_GLUING": "OPEN",
        "SOURCE_TO_TARGET_MAP": "OPEN",
        "GRADING": "UNDETERMINED",
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
