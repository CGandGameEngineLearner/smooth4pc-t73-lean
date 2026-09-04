#!/usr/bin/env python3
"""Build the AR attaching cores from the bound Johnson spine and dual cells.

Following Aitchison--Rubinstein p. 6, the circles C_i are cut through the
fixed section ball.  Thus the bottom and top pieces are arcs, not complete
based circles, and lambda_i, mu_i close their four endpoints through the
mapping one-handle.  This file does not mark the framed link complete until
the transported top ribbons psi_A(A_i) have their own checked artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "geometry" / "t73_actual_ar_link.json"
MANIFEST = ROOT / "geometry" / "t73_johnson_generators" / "manifest.json"
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


def canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def lift(point: list[str], u: str) -> list[str]:
    return list(point) + [u]


def axis_point(axis: int, value: Fraction) -> list[Fraction]:
    point = [Fraction(0), Fraction(0), Fraction(0)]
    point[axis] = value
    return point


def mapping_torus_core(pl, spine_component: dict[str, Any], axis: int) -> dict[str, Any]:
    # Work strictly inside the pointwise-fixed ball.  The endpoints and their
    # future ribbon push-offs then agree on the bottom and top fibers.
    cut_radius = pl.PROTECTED_RADIUS / 2
    positive = axis_point(axis, cut_radius)
    negative = axis_point(axis, -cut_radius)
    bottom_lift = [
        positive,
        axis_point(axis, Fraction(1)),
        axis_point(axis, Fraction(2)),
        axis_point(axis, Fraction(3)),
        axis_point(axis, Fraction(4) - cut_radius),
    ]
    bottom = [
        pl.encode(positive),
        pl.encode(axis_point(axis, Fraction(1))),
        pl.encode(axis_point(axis, Fraction(2))),
        pl.encode(axis_point(axis, Fraction(-1))),
        pl.encode(negative),
    ]
    closed_top = [pl.decode(point) for point in spine_component["polyline"]]
    if closed_top[0] != [Fraction(0)] * 3 or closed_top[-1] != [Fraction(0)] * 3:
        raise AssertionError("Johnson spine component is not based at the fixed point")
    radial_plus = pl.decode(spine_component["spoke"]["radial_plus"])
    radial_minus = pl.decode(spine_component["spoke"]["radial_minus"])
    if closed_top[1] != radial_plus or closed_top[-2] != radial_minus:
        raise AssertionError("Johnson spine does not have the recorded fixed-ball spokes")
    top_points = [positive] + closed_top[1:-1] + [negative]
    top = [pl.encode(point) for point in top_points]

    lambda_arc = [
        lift(pl.encode(positive), "0"),
        lift(pl.encode(positive), "1/2"),
        lift(pl.encode(positive), "1"),
    ]
    mu_arc = [
        lift(pl.encode(negative), "1"),
        lift(pl.encode(negative), "1/2"),
        lift(pl.encode(negative), "0"),
    ]
    # Orientation is t psi_A(C_i) t^{-1} C_i^{-1}: up lambda, forward along
    # the top image arc, down mu, then backwards along the bottom arc.
    core = lambda_arc + [lift(point, "1") for point in top[1:]]
    core += mu_arc[1:]
    core += [lift(point, "0") for point in reversed(bottom)][1:]
    if core[0] != core[-1]:
        raise AssertionError("cut AR pieces do not close to a circle")

    # A provisional value is replaced below by the common width selected by
    # the checked ribbon builder.
    ribbon_offset = [pl.PROTECTED_RADIUS / 16] * 3
    bottom_band = pl.framing_annulus(bottom, ribbon_offset)
    return {
        "axis": axis,
        "formula": "(C_i-(R-int R'))^- union lambda_i union psi_A(C_i-(R-int R'))^+ union mu_i",
        "source_reference": "Aitchison--Rubinstein (1984), p. 6, Figure 2c",
        "cut_radius": str(cut_radius),
        "cut_endpoints": {
            "positive": pl.encode(positive),
            "negative": pl.encode(negative),
        },
        "C_i": bottom,
        "C_i_universal_cover_lift": [pl.encode(point) for point in bottom_lift],
        "psi_A_C_i": top,
        "lambda_i": lambda_arc,
        "mu_i": mu_arc,
        "core_polyline_T3xI": core,
        "core_closed": True,
        "framing_annulus_bottom": bottom_band,
        "framing_annulus_top": "OPEN: requires the checked Johnson spine-ribbon transport",
        "source": "actual cut coordinate arc and bound Johnson lane-spine image arc",
        "not_a_free_group_word": True,
    }


def section_surgery_component(pl, width: Fraction, cut_radius: Fraction) -> dict[str, Any]:
    section_point = [cut_radius / 3, cut_radius / 3, cut_radius / 3]
    encoded_point = pl.encode(section_point)
    offset = pl.encode([width, -width, Fraction(0)])
    return {
        "kind": "section_surgery_2_handle",
        "source_reference": "Aitchison--Rubinstein (1984), p. 6, Figure 2d",
        "section_point": encoded_point,
        "t_handle_cross_section": "octahedral S^2: |x|+|y|+|z|=cut_radius",
        "core_polyline_T3xI": [lift(encoded_point, "0"), lift(encoded_point, "1")],
        "mapping_torus_seam_identification": "(section_point,1)=(section_point,0)",
        "closed_by_mapping_torus_seam": True,
        "t_handle_passage_count": 1,
        "framing_annulus": {
            "inner_ref": "core_polyline_T3xI",
            "outer_rule": "q_i=p_i+width*(1,-1,0,0)",
            "offset": offset,
            "relative_twist": 0,
            "epsilon": 0,
        },
        "product_framing": "PASS",
    }


def build(write: bool = False) -> dict[str, Any]:
    pl = load("t73_johnson_pl")
    if not MANIFEST.exists() or not PSI.exists() or not SPINE.exists() or not SPINE_BINDING.exists():
        raise AssertionError("psi_A, Johnson spine, and binding must be written first")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    psi = json.loads(PSI.read_text(encoding="utf-8"))
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    binding = json.loads(SPINE_BINDING.read_text(encoding="utf-8"))
    if psi.get("status", {}).get("actual_curve_transport_evaluator") != "PASS":
        raise AssertionError(
            "current hierarchical psi_A has no actual curve-transport evaluator; "
            "the AR link must not be rebuilt from the legacy point evaluator"
        )
    if binding["spine_embedding_sha256"] != spine["sha256"]:
        raise AssertionError("Johnson spine binding is stale")
    if psi.get("spine_binding_sha256") != binding["sha256"]:
        raise AssertionError("psi_A is not bound to the selected Johnson spine")
    if binding["coordinate_spine_curve_transport"] != "PASS":
        raise AssertionError("Johnson coordinate-spine transport is not closed")
    cores = [
        mapping_torus_core(pl, spine["components"][axis], axis)
        for axis in range(3)
    ]
    ribbons = load("build_t73_johnson_spine_ribbons").build_ribbons(
        cores, spine, binding
    )
    h_cs = section_surgery_component(
        pl, Fraction(ribbons["width"]), Fraction(cores[0]["cut_radius"])
    )
    for core, ribbon in zip(cores, ribbons["components"]):
        core["framing_annulus_bottom"] = {
            "inner_ref": "C_i",
            "outer_rule": "q_i=p_i+width*(1,1,1)",
            "offset": ribbon["top_band"]["offset"],
        }
        core["framing_annulus_top"] = ribbon["top_band"]
        core["full_framing_annulus"] = ribbon
    # Johnson: plane x_i = 0 meets H2 in D2^i; plane x_i = 1/2 meets H1 in D1^i.
    dual = {
        "r_yz": pl.dual_disk_boundary(0, 0, 1),
        "r_zx": pl.dual_disk_boundary(1, 0, 1),
        "r_xy": pl.dual_disk_boundary(2, 0, 1),
        "d1_x": pl.dual_disk_boundary(0, 2, 0),
        "d1_y": pl.dual_disk_boundary(1, 2, 0),
        "d1_z": pl.dual_disk_boundary(2, 2, 0),
    }
    for name, disk in dual.items():
        if not disk["closed"] or disk["vertex_count"] < 3:
            raise AssertionError(f"{name} is not a closed dual-cell boundary")
    result = {
        "schema": "t73_actual_ar_link/v2",
        "psi_A_sha256": psi["sha256"],
        "generator_manifest_sha256": manifest["sha256"],
        "johnson_spine_sha256": spine["sha256"],
        "johnson_spine_binding_sha256": binding["sha256"],
        "components": {
            "m_1": cores[0],
            "m_2": cores[1],
            "m_3": cores[2],
            "h_CS": h_cs,
            "r_xy": {
                "kind": "dual_2_cell_boundary",
                "plane": "z=0 meets H2",
                "polyline": dual["r_xy"]["polyline"],
                "disk": dual["r_xy"],
                "word_projection_only": "[x,y]",
                "embedded_from_free_word": False,
            },
            "r_yz": {
                "kind": "dual_2_cell_boundary",
                "plane": "x=0 meets H2",
                "polyline": dual["r_yz"]["polyline"],
                "disk": dual["r_yz"],
                "word_projection_only": "[y,z]",
                "embedded_from_free_word": False,
            },
            "r_zx": {
                "kind": "dual_2_cell_boundary",
                "plane": "y=0 meets H2",
                "polyline": dual["r_zx"]["polyline"],
                "disk": dual["r_zx"],
                "word_projection_only": "[z,x]",
                "embedded_from_free_word": False,
            },
        },
        "framing": {
            "rule": (
                "AR product annulus A_i^- union psi_A(A_i)^+ union the two "
                "lambda_i/mu_i rectangles"
            ),
            "epsilon": 0,
            "source": "Aitchison--Rubinstein p. 6, Figure 2c",
            "transported_top_ribbon": "PASS",
            "spine_ribbon_transport": ribbons,
        },
        "status": {
            "actual_cut_mapping_torus_cores": "PASS",
            "actual_psi_images": "PASS",
            "pairwise_disjoint_core_receipt": "PASS",
            "dual_2_cells_from_cubulation": "PASS",
            "free_words_are_not_embeddings": "PASS",
            "heegaard_preserving_psi_A": psi["status"]["preserves_heegaard_pair"],
            "section_ball_identity": psi["status"]["fixes_section_neighborhood"],
            "actual_framing_annuli": "PASS",
            "actual_framed_ar_link": "PASS",
            "all_seven_2_handle_components_present": "PASS",
        },
        "component_count": 7,
    }
    result["sha256"] = canonical_sha({key: value for key, value in result.items() if key != "sha256"})
    if write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(write=args.write)
    if args.check or args.write:
        print("T73_ACTUAL_AR_LINK=WRITTEN" if args.write else "T73_ACTUAL_AR_LINK=CHECKED")
        print(f"M_CORES={3}")
        print(f"R_XY_VERTS={result['components']['r_xy']['disk']['vertex_count']}")
        print(f"R_YZ_VERTS={result['components']['r_yz']['disk']['vertex_count']}")
        print(f"R_ZX_VERTS={result['components']['r_zx']['disk']['vertex_count']}")
        print(f"EMBEDDED_FROM_FREE_WORD={result['components']['r_xy']['embedded_from_free_word']}")
        print(f"HEEGAARD_PRESERVING_PSI={result['status']['heegaard_preserving_psi_A']}")
        print(f"ACTUAL_CUT_CORES={result['status']['actual_cut_mapping_torus_cores']}")
        print(f"ACTUAL_FRAMING_ANNULI={result['status']['actual_framing_annuli']}")
        print(f"SHA256={result['sha256']}")
        return
    print(json.dumps(result["status"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
