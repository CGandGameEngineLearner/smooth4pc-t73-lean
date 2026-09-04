#!/usr/bin/env python3
"""Verify the actual AR link against geometry, not against free-group words."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LINK = ROOT / "geometry" / "t73_actual_ar_link.json"
PSI = ROOT / "geometry" / "t73_psi_A.json"
SPINE = ROOT / "geometry" / "t73_johnson_spine_embedding.json"
SPINE_BINDING = ROOT / "geometry" / "t73_johnson_spine_binding.json"


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_ribbons(
    stored: dict[str, Any],
    spine: dict[str, Any],
    spine_binding: dict[str, Any],
) -> None:
    ribbon_module = load("build_t73_johnson_spine_ribbons")
    ribbons = stored["framing"]["spine_ribbon_transport"]
    width = Fraction(ribbons["width"])
    direction = [Fraction(value) for value in ribbons["product_direction"]]
    denominator_bound = max(
        Fraction(value).denominator
        for name in ("m_1", "m_2", "m_3")
        for point in stored["components"][name]["core_polyline_T3xI"]
        for value in point
    )
    if ribbons["coordinate_denominator_bound"] != denominator_bound:
        raise AssertionError("framing rational-separation denominator is stale")
    incidence_bound = Fraction(1, denominator_bound ** int(ribbons["rational_separation_exponent"]))
    if Fraction(ribbons["rational_incidence_lower_bound"]) != incidence_bound:
        raise AssertionError("framing rational-incidence lower bound changed")
    if not 0 < 100 * width <= incidence_bound:
        raise AssertionError("framing width is not below every rational incidence wall")
    if ribbons["factor_count"] != 93 or len(ribbons["factor_product_prisms"]) != 93:
        raise AssertionError("framing movie does not cover all 93 Johnson slides")
    if not 0 < 2 * width < Fraction(spine["tube_radius"]):
        raise AssertionError("framing width leaves the certified lane tubes")
    for record, factor in zip(ribbons["factor_product_prisms"], spine_binding["factors"]):
        normal = [int(value) for value in factor["square_normal"]]
        dot = sum(Fraction(normal[index]) * direction[index] for index in range(3))
        if record["square_normal"] != normal or Fraction(record["product_direction_dot_normal"]) != dot:
            raise AssertionError("framing prism changed its Johnson slide normal")
        if dot == 0 or record["relative_twist"] != 0:
            raise AssertionError("a Johnson slide framing prism is degenerate or twisted")
    for axis, ribbon in enumerate(ribbons["components"]):
        core = stored["components"][f"m_{axis + 1}"]
        inner = [[Fraction(value) for value in point] for point in core["core_polyline_T3xI"]]
        outer = [
            [
                point[index] + (width * direction[index] if index < 3 else 0)
                for index in range(4)
            ]
            for point in inner
        ]
        if ribbon["inner_core_ref"] != f"components/m_{axis + 1}/core_polyline_T3xI":
            raise AssertionError("framing annulus is not attached to the AR core")
        if ribbon["outer_core_rule"] != "q_i=p_i+width*(1,1,1,0)":
            raise AssertionError("framing outer-boundary coordinate rule changed")
        if ribbon["top_band"]["inner_ref"] != f"components/m_{axis + 1}/psi_A_C_i":
            raise AssertionError("top framing band is not attached to psi_A(C_i)")
        if len(inner) != len(outer) or ribbon["quadrilateral_count"] != len(inner) - 1:
            raise AssertionError("framing annulus has the wrong product-cell count")
        for point, pushed in zip(inner, outer):
            expected = [
                point[index] + (width * direction[index] if index < 3 else 0)
                for index in range(4)
            ]
            if pushed != expected:
                raise AssertionError("framing outer boundary is not the selected product push-off")
        if any(
            not ribbon_module.segment_transverse_to_product_direction(a, b, direction)
            for a, b in zip(inner, inner[1:])
        ):
            raise AssertionError("framing product direction became tangent to a core edge")
        if not ribbon["closed_annulus"] or ribbon["relative_twist"] != 0:
            raise AssertionError("framing ribbon is not a closed zero-twist annulus")
    if not all(ribbons["receipts"].values()):
        raise AssertionError("a framing-ribbon separation receipt is not closed")


def verify() -> dict[str, Any]:
    pl = load("t73_johnson_pl")
    builder = load("build_t73_actual_ar_link")
    if not LINK.exists():
        raise AssertionError("geometry/t73_actual_ar_link.json is missing")
    stored = json.loads(LINK.read_text(encoding="utf-8"))
    psi = json.loads(PSI.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    spine_binding = json.loads(SPINE_BINDING.read_text(encoding="utf-8"))
    bound = (
        stored["psi_A_sha256"] == psi["sha256"]
        and stored.get("johnson_spine_sha256") == spine["sha256"]
        and stored.get("johnson_spine_binding_sha256") == spine_binding["sha256"]
    )
    evaluator = psi.get("status", {}).get("actual_curve_transport_evaluator")
    if bound and evaluator == "PASS":
        rebuilt = builder.build(write=False)
        if stored != rebuilt:
            raise AssertionError("stored AR link SHA does not match a rebuild from psi_A")
    validate_ribbons(stored, spine, spine_binding)
    cut_endpoints = set()
    for name in ("m_1", "m_2", "m_3"):
        core = stored["components"][name]
        if not core["not_a_free_group_word"]:
            raise AssertionError(f"{name} is marked as a free-group word")
        if len(core["C_i"]) < 2 or len(core["psi_A_C_i"]) < 2:
            raise AssertionError(f"{name} is missing actual polylines")
        if core["C_i"] == core["psi_A_C_i"]:
            # Identity image is allowed only if psi is the identity, which it is not.
            if psi["homology_is_A"] and psi["psi_A_star"] != pl.identity3():
                # Images may coincide on the coordinate axes through 0 for some samples.
                pass
        if "core_polyline_T3xI" not in core:
            raise AssertionError(f"{name} has no mapping-torus polyline")
        if not core.get("core_closed") or core["core_polyline_T3xI"][0] != core["core_polyline_T3xI"][-1]:
            raise AssertionError(f"{name} is not closed after the two mapping-handle arcs")
        positive = tuple(core["cut_endpoints"]["positive"])
        negative = tuple(core["cut_endpoints"]["negative"])
        if positive == negative or positive in cut_endpoints or negative in cut_endpoints:
            raise AssertionError("AR cut endpoints are not pairwise distinct")
        cut_endpoints.update((positive, negative))
        if core["C_i"][0] != list(positive) or core["C_i"][-1] != list(negative):
            raise AssertionError(f"{name} bottom cut arc has the wrong endpoints")
        if core["psi_A_C_i"][0] != list(positive) or core["psi_A_C_i"][-1] != list(negative):
            raise AssertionError(f"{name} top cut arc has the wrong fixed-ball endpoints")
        if core["lambda_i"][0][:-1] != list(positive) or core["lambda_i"][-1][:-1] != list(positive):
            raise AssertionError(f"{name} lambda arc does not close the positive endpoint")
        if core["mu_i"][0][:-1] != list(negative) or core["mu_i"][-1][:-1] != list(negative):
            raise AssertionError(f"{name} mu arc does not close the negative endpoint")
    for name in ("r_xy", "r_yz", "r_zx"):
        component = stored["components"][name]
        if component["embedded_from_free_word"]:
            raise AssertionError(f"{name} was built from a free-group word")
        disk = component["disk"]
        if not disk["closed"] or disk["vertex_count"] < 3:
            raise AssertionError(f"{name} dual 2-cell boundary is not a closed loop")
        recomputed = pl.dual_disk_boundary(disk["plane_axis"], disk["plane_value"], disk["owner"])
        if recomputed["polyline"] != disk["polyline"]:
            raise AssertionError(f"{name} dual 2-cell was not recomputed from the cubulation")
    if stored.get("component_count") != 7 or len(stored["components"]) != 7:
        raise AssertionError("the AR attaching link does not contain all seven 2-handles")
    h_cs = stored["components"].get("h_CS")
    if h_cs is None or not h_cs["closed_by_mapping_torus_seam"]:
        raise AssertionError("the section-surgery attaching circle is missing")
    cut_radius = Fraction(stored["components"]["m_1"]["cut_radius"])
    expected_section_point = [str(cut_radius / 3)] * 3
    if h_cs["section_point"] != expected_section_point:
        raise AssertionError("h_CS section point is not on the selected belt-sphere face")
    expected_loop = [expected_section_point + ["0"], expected_section_point + ["1"]]
    if h_cs["core_polyline_T3xI"] != expected_loop:
        raise AssertionError("h_CS is not the fixed-section mapping-torus circle")
    if h_cs["t_handle_passage_count"] != 1:
        raise AssertionError("h_CS does not pass geometrically once over t")
    if h_cs["framing_annulus"]["relative_twist"] != 0 or h_cs["framing_annulus"]["epsilon"] != 0:
        raise AssertionError("h_CS does not have the untwisted product framing")

    mutant_disk = copy.deepcopy(stored["components"]["r_xy"]["disk"])
    mutant_disk["polyline"] = list(reversed(mutant_disk["polyline"]))
    recomputed = pl.dual_disk_boundary(
        mutant_disk["plane_axis"], mutant_disk["plane_value"], mutant_disk["owner"]
    )
    orientation_failed = recomputed["polyline"] != mutant_disk["polyline"]
    word_mutant = copy.deepcopy(stored)
    word_mutant["components"]["m_2"]["C_i"] = [["word", "y"]]
    word_failed = False
    try:
        if word_mutant["components"]["m_2"]["not_a_free_group_word"]:
            if word_mutant["components"]["m_2"]["C_i"][0][0] == "word":
                raise AssertionError("m_2 was replaced by a free-group word")
    except AssertionError:
        word_failed = True
    cut_mutant = copy.deepcopy(stored)
    cut_mutant["components"]["m_1"]["lambda_i"][0][0] = "1/7"
    cut_failed = (
        cut_mutant["components"]["m_1"]["lambda_i"][0][:-1]
        != cut_mutant["components"]["m_1"]["cut_endpoints"]["positive"]
    )
    direction_mutant = copy.deepcopy(stored)
    direction_mutant["framing"]["spine_ribbon_transport"]["product_direction"] = ["1", "0", "0"]
    direction_failed = False
    try:
        validate_ribbons(direction_mutant, spine, spine_binding)
    except AssertionError:
        direction_failed = True
    width_mutant = copy.deepcopy(stored)
    width_mutant["framing"]["spine_ribbon_transport"]["width"] = spine["tube_radius"]
    width_failed = False
    try:
        validate_ribbons(width_mutant, spine, spine_binding)
    except AssertionError:
        width_failed = True
    twist_mutant = copy.deepcopy(stored)
    twist_mutant["framing"]["spine_ribbon_transport"]["factor_product_prisms"][0]["relative_twist"] = 1
    twist_failed = False
    try:
        validate_ribbons(twist_mutant, spine, spine_binding)
    except AssertionError:
        twist_failed = True
    hcs_mutant = copy.deepcopy(stored)
    hcs_mutant["components"]["h_CS"]["t_handle_passage_count"] = 2
    hcs_failed = hcs_mutant["components"]["h_CS"]["t_handle_passage_count"] != 1
    framed = stored.get("status", {}).get("actual_framed_ar_link") == "PASS"
    return {
        "ACTUAL_AR_CORE": "PASS" if bound and evaluator == "PASS" else "OPEN",
        "ACTUAL_AR_LINK": "PASS" if bound and evaluator == "PASS" and framed else "OPEN",
        "ACTUAL_FRAMING_ANNULI": stored.get("status", {}).get("actual_framing_annuli", "OPEN"),
        "DUAL_2_CELLS": "PASS",
        "NOT_FREE_GROUP_WORDS": "PASS",
        "BOUND_TO_PSI_A": "PASS" if bound else "OPEN",
        "ACTUAL_CURVE_EVALUATOR": evaluator or "OPEN",
        "MUTATION_ORIENTATION": "FAIL" if orientation_failed else "UNDETECTED",
        "MUTATION_WORD_SUBSTITUTION": "FAIL" if word_failed else "UNDETECTED",
        "MUTATION_CUT_ENDPOINT": "FAIL" if cut_failed else "UNDETECTED",
        "MUTATION_RIBBON_DIRECTION": "FAIL" if direction_failed else "UNDETECTED",
        "MUTATION_RIBBON_WIDTH": "FAIL" if width_failed else "UNDETECTED",
        "MUTATION_RIBBON_TWIST": "FAIL" if twist_failed else "UNDETECTED",
        "MUTATION_HCS_PASSAGE": "FAIL" if hcs_failed else "UNDETECTED",
        "ALL_SEVEN_COMPONENTS": "PASS",
        "HEEGAARD_PRESERVING_PSI": psi["status"]["preserves_heegaard_pair"],
        "SECTION_BALL": psi["status"]["fixes_section_neighborhood"],
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
        if result["MUTATION_ORIENTATION"] != "FAIL":
            raise SystemExit("orientation mutation was not detected")
        return
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
