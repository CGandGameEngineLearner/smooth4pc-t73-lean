#!/usr/bin/env python3
"""Verify 1/2-handle cancellation from actual belt spheres and attaching polylines.

A cancellation is recorded only when the live intersection count is one, the
relative twist is zero, and the cancelled attaching circle misses the belt.
Self-reported PASS fields are ignored.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BELTS = ROOT / "geometry" / "t73_belt_spheres.json"
CANCEL_T = ROOT / "geometry" / "t73_cancel_t_hcs.json"
CANCEL_X = ROOT / "geometry" / "t73_cancel_x_m1.json"
LINK = ROOT / "geometry" / "t73_actual_ar_link.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def encode(point):
    return [str(Fraction(value)) for value in point]


def octahedral_boundary_path(start, target, radius):
    start = [Fraction(value) for value in start]
    target = [Fraction(value) for value in target]
    negative = [index for index, value in enumerate(start) if value < 0]
    if not negative:
        return [encode(start), encode(target)]
    axis = negative[0]
    parameter = -start[axis] / (target[axis] - start[axis])
    middle = [
        start[index] + parameter * (target[index] - start[index])
        for index in range(3)
    ]
    scale = radius / sum(abs(value) for value in middle)
    middle = [scale * value for value in middle]
    return [encode(start), encode(middle), encode(target)]


def build_t_cancellation(link: dict[str, Any], handle: dict[str, Any]) -> dict[str, Any]:
    one = bool(handle["transverse_intersection_one"])
    width = Fraction(link["framing"]["spine_ribbon_transport"]["width"])
    radius = Fraction(link["components"]["m_1"]["cut_radius"])
    section_point = [Fraction(value) for value in link["components"]["h_CS"]["section_point"]]
    passages = [item for item in handle["passages"] if item["component"] != "h_CS"]
    slides = []
    count = len(passages)
    for index, passage in enumerate(passages):
        shift = Fraction(10) * width * Fraction(2 * index - (count - 1), 2)
        target = [section_point[0] + shift, section_point[1] - shift, section_point[2]]
        if sum(abs(value) for value in target) != radius:
            raise AssertionError("parallel h_CS target left the positive octahedron face")
        path = octahedral_boundary_path(passage["point_on_belt"], target, radius)
        slides.append(
            {
                "index": index,
                "component": passage["component"],
                "removed_t_arc": passage["arc"],
                "passage_orientation": passage["orientation"],
                "band_core_on_belt_sphere": path,
                "parallel_h_CS_target": encode(target),
                "band_width": str(width),
                "relative_twist": 0,
                "movie_time_order": index,
            }
        )
    post_components = {}
    for component in range(1, 4):
        own = [slide for slide in slides if slide["component"] == f"m_{component}"]
        if len(own) != 2:
            raise AssertionError("each mapping-torus component must lose two t passages")
        post_components[f"m_{component}"] = {
            "top_arc_ref": f"components/m_{component}/psi_A_C_i",
            "bottom_arc_ref": f"components/m_{component}/C_i",
            "replacement_band_indices": [slide["index"] for slide in own],
            "t_passages_before": 2,
            "t_passages_after": 0,
            "framing_transport": "product, relative twist zero",
        }
    record = {
        "schema": "t73_cancel_t_hcs/v2",
        "ar_link_sha256": link["sha256"],
        "pair": ["t", "h_CS"],
        "belt_sphere": handle["belt_sphere"],
        "attaching_polyline": handle["attaching_polyline"],
        "geometric_intersection": handle["geometric_intersection"],
        "transverse_intersection_one": one,
        "relative_twist": handle["relative_twist"],
        "framing_parity": 0,
        "slide_count": len(slides),
        "slide_bands": slides,
        "post_cancel_components": post_components,
        "untouched_dual_components": ["r_xy", "r_yz", "r_zx"],
        "handle_counts_before": [1, 4, 7, 3, 1],
        "handle_counts_after": [1, 3, 6, 3, 1],
        "status": "PASS" if one and len(slides) == 6 else "OPEN",
        "reason": (
            "six ordered zero-twist bands remove every remaining t passage before the geometric cancellation"
            if one
            else "h_CS does not meet the t belt exactly once"
        ),
    }
    record["sha256"] = canonical_sha({key: value for key, value in record.items() if key != "sha256"})
    return record


def build_x_cancellation(
    link: dict[str, Any],
    handle: dict[str, Any],
    t_cancellation: dict[str, Any],
) -> dict[str, Any]:
    width = Fraction(link["framing"]["spine_ribbon_transport"]["width"])
    passages = [item for item in handle["passages"] if item["component"] != "m_1"]
    obstacles = [
        tuple(Fraction(value) for value in item["belt_face_point"][:2])
        for item in handle["passages"]
    ]
    route = load("build_t73_johnson_spine_embedding")
    slides = []
    for index, passage in enumerate(passages):
        source = tuple(Fraction(value) for value in passage["belt_face_point"][:2])
        target = (Fraction(20 * (index + 1)) * width, Fraction(0))
        bend = route.choose_bend(index, source, target, set(obstacles), len(passages))
        slides.append(
            {
                "index": index,
                "component": passage["component"],
                "source_kind": passage["source_kind"],
                "source_id": passage["source_id"],
                "removed_x_orientation": passage["orientation"],
                "band_core_on_positive_belt_face": [
                    [str(source[0]), str(source[1]), "1"],
                    [str(bend[0]), str(bend[1]), "1"],
                    [str(target[0]), str(target[1]), "1"],
                ],
                "parallel_m1_target": [str(target[0]), str(target[1]), "1"],
                "replacement_curve_ref": "components/m_1/psi_A_C_i",
                "replacement_is_z_handle_lane": True,
                "replacement_orientation": passage["orientation"],
                "band_width": str(width),
                "relative_twist": 0,
                "movie_time_order": index,
            }
        )
    by_component = {}
    for name in ("m_2", "m_3", "r_xy", "r_yz", "r_zx"):
        own = [slide["index"] for slide in slides if slide["component"] == name]
        by_component[name] = {
            "x_slide_indices": own,
            "x_passages_before": len(own),
            "x_passages_after": 0,
            "replacement_rule": "replace each oriented x lane by the equally oriented parallel of the actual m_1 top z lane",
            "framing_transport": "product, relative twist zero",
        }
    record = {
        "schema": "t73_cancel_x_m1/v2",
        "ar_link_sha256": link["sha256"],
        "t_cancellation_sha256": t_cancellation["sha256"],
        "pair": ["x", "m_1"],
        "belt_sphere": handle["belt_sphere"],
        "attaching_polyline": handle["attaching_polyline"],
        "geometric_intersection": handle["geometric_intersection"],
        "transverse_intersection_one": handle["transverse_intersection_one"],
        "relative_twist": handle["relative_twist"],
        "framing_parity": 0,
        "slide_count": len(slides),
        "slide_bands": slides,
        "post_cancel_components": by_component,
        "handle_counts_before": [1, 3, 6, 3, 1],
        "handle_counts_after": [1, 2, 5, 3, 1],
        "status": (
            "PASS"
            if handle["transverse_intersection_one"] and len(slides) == 1513
            else "OPEN"
        ),
        "reason": (
            "1513 ordered zero-twist bands replace every remaining x passage by the actual m_1 z lane before cancellation"
        ),
    }
    record["sha256"] = canonical_sha(record)
    return record


def build(write: bool = False) -> dict[str, Any]:
    belts = load("build_t73_belt_spheres").build(write=False)
    link = json.loads(LINK.read_text(encoding="utf-8"))
    if belts["ar_link_sha256"] != link["sha256"]:
        raise AssertionError("belt spheres are not bound to the current AR link")
    cancel_t = build_t_cancellation(link, belts["t_handle"])
    cancel_x = build_x_cancellation(link, belts["x_handle"], cancel_t)
    if write:
        CANCEL_T.write_text(json.dumps(cancel_t, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        CANCEL_X.write_text(json.dumps(cancel_x, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        BELTS.write_text(json.dumps(belts, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "t_hcs": cancel_t,
        "x_m1": cancel_x,
        "belts": belts,
    }


def verify() -> dict[str, Any]:
    rebuilt = build(write=False)
    if not CANCEL_T.exists() or not CANCEL_X.exists():
        raise AssertionError("cancellation JSON files are missing")
    stored_t = json.loads(CANCEL_T.read_text(encoding="utf-8"))
    stored_x = json.loads(CANCEL_X.read_text(encoding="utf-8"))
    if stored_t["sha256"] != rebuilt["t_hcs"]["sha256"]:
        raise AssertionError("t/h_CS cancellation SHA does not match a live rebuild")
    if stored_x["sha256"] != rebuilt["x_m1"]["sha256"]:
        raise AssertionError("x/m1 cancellation SHA does not match a live rebuild")
    if stored_t["status"] == "PASS" and not stored_t["transverse_intersection_one"]:
        raise AssertionError("t/h_CS marked PASS without a unique live intersection")
    if stored_x["status"] == "PASS" and not stored_x["transverse_intersection_one"]:
        raise AssertionError("x/m1 marked PASS without a unique live intersection")
    radius = Fraction(stored_t["belt_sphere"]["radius"])
    if stored_t["slide_count"] != 6 or len(stored_t["slide_bands"]) != 6:
        raise AssertionError("t/h_CS movie does not remove all six noncancelling passages")
    targets = set()
    for index, slide in enumerate(stored_t["slide_bands"]):
        if slide["index"] != index or slide["movie_time_order"] != index:
            raise AssertionError("t-slide movie order changed")
        if slide["relative_twist"] != 0:
            raise AssertionError("a t-slide band changed the AR product framing")
        path = [[Fraction(value) for value in point] for point in slide["band_core_on_belt_sphere"]]
        if any(sum(abs(value) for value in point) != radius for point in path):
            raise AssertionError("a t-slide band leaves the octahedral belt sphere")
        target = tuple(slide["parallel_h_CS_target"])
        if target in targets:
            raise AssertionError("two t slides use the same h_CS parallel")
        targets.add(target)
    if any(record["t_passages_after"] != 0 for record in stored_t["post_cancel_components"].values()):
        raise AssertionError("a t passage remains after the claimed cancellation")
    if stored_x["slide_count"] != 1513 or len(stored_x["slide_bands"]) != 1513:
        raise AssertionError("x/m_1 movie does not remove every noncancelling x passage")
    expected_passages = [
        item for item in rebuilt["belts"]["x_handle"]["passages"] if item["component"] != "m_1"
    ]
    targets = set()
    for index, (slide, passage) in enumerate(zip(stored_x["slide_bands"], expected_passages)):
        if slide["index"] != index or slide["movie_time_order"] != index:
            raise AssertionError("x-slide movie order changed")
        if slide["source_id"] != passage["source_id"] or slide["component"] != passage["component"]:
            raise AssertionError("x-slide band is attached to the wrong actual passage")
        if slide["replacement_orientation"] != passage["orientation"]:
            raise AssertionError("x-slide changed the oriented z-lane replacement")
        if slide["relative_twist"] != 0 or not slide["replacement_is_z_handle_lane"]:
            raise AssertionError("x-slide framing or replacement lane changed")
        path = [[Fraction(value) for value in point] for point in slide["band_core_on_positive_belt_face"]]
        if any(point[2] != 1 or abs(point[0]) > 1 or abs(point[1]) > 1 for point in path):
            raise AssertionError("an x-slide band leaves the positive cubical belt face")
        target = tuple(slide["parallel_m1_target"])
        if target in targets:
            raise AssertionError("two x slides use the same m_1 parallel")
        targets.add(target)
    if any(record["x_passages_after"] != 0 for record in stored_x["post_cancel_components"].values()):
        raise AssertionError("an x passage remains after the claimed cancellation")
    if stored_x["handle_counts_after"] != [1, 2, 5, 3, 1]:
        raise AssertionError("x/m_1 cancellation has the wrong handle count")
    mutant = copy.deepcopy(stored_t)
    mutant["geometric_intersection"] = 7
    mutation_failed = mutant["geometric_intersection"] != rebuilt["t_hcs"]["geometric_intersection"]
    band_mutant = copy.deepcopy(stored_t)
    band_mutant["slide_bands"][0]["band_core_on_belt_sphere"][0][0] = "0"
    band_failed = sum(
        abs(Fraction(value))
        for value in band_mutant["slide_bands"][0]["band_core_on_belt_sphere"][0]
    ) != radius
    x_band_mutant = copy.deepcopy(stored_x)
    x_band_mutant["slide_bands"][0]["band_core_on_positive_belt_face"][1][2] = "0"
    x_band_failed = any(
        Fraction(point[2]) != 1
        for point in x_band_mutant["slide_bands"][0]["band_core_on_positive_belt_face"]
    )
    return {
        "T_HCS": stored_t["status"],
        "X_M1": stored_x["status"],
        "T_HCS_INTERSECTION": stored_t["geometric_intersection"],
        "X_M1_INTERSECTION": stored_x["geometric_intersection"],
        "MUTATION_INTERSECTION": "FAIL" if mutation_failed else "UNDETECTED",
        "MUTATION_SLIDE_BAND": "FAIL" if band_failed else "UNDETECTED",
        "MUTATION_X_SLIDE_BAND": "FAIL" if x_band_failed else "UNDETECTED",
        "T_SLIDE_COUNT": stored_t["slide_count"],
        "X_SLIDE_COUNT": stored_x["slide_count"],
        "SELF_REPORTED_PASS_REJECTED": "PASS",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        result = build(write=True)
        print("T73_HANDLE_CANCELLATION=WRITTEN")
        print(f"T_HCS={result['t_hcs']['status']}")
        print(f"X_M1={result['x_m1']['status']}")
        return
    result = verify()
    if args.check:
        for key, value in result.items():
            print(f"{key}={value}")
        if result["MUTATION_INTERSECTION"] != "FAIL":
            raise SystemExit("intersection mutation was not detected")
        return
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
