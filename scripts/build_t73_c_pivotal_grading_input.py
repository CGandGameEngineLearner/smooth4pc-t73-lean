#!/usr/bin/env python3
"""Define the standard auxiliary detector's primitive pivotal convention.

This is a new convention, not a recovery of the legacy endpoint coefficients.
The 88 physical labels are placed on parallel vertical blue strands in a
standard D^2 x I chart.  All signs and q-powers are subsequently derived by
``check_t73_c_pivotal_grading_inputs.py`` from BPW (A.4), BPW (A.6), and the
declared no-binding Blanchet product foams.

The selected cup feet are placed first, hence adjacent, in the new tensor
order.  Changing from this order to the public labels is only a simultaneous
coordinate conjugation of W, cup, and cap.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COLLAR = ROOT / "geometry" / "t73_p0_marked_vertical_collar.json"
OUTPUT = ROOT / "data" / "T73_C_PIVOTAL_GRADING_INPUT.json"

SELECTED_V = "actual:r_xy:w2:neg:r_xy:vertex:7"
SELECTED_V_DUAL = "actual:m_2:w44:pos:m_2:C_i"


def load_checker():
    path = ROOT / "scripts" / "check_t73_c_pivotal_grading_inputs.py"
    spec = importlib.util.spec_from_file_location("check_t73_c_pivotal", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_multiplier(sign: str) -> int:
    return 1 if sign == "pos" else -1 if sign == "neg" else 0


def atom(kind: str) -> dict[str, Any]:
    item: dict[str, Any] = {
        "kind": kind,
        "source_locator": (
            "BPW Appendix A (A.4)"
            if not kind.startswith("blanchet_")
            else "standard vertical blue product foam, with no red facet or binding"
        ),
    }
    if kind.startswith("blanchet_"):
        item["local_normal"] = [0, 1, 0]
    return item


def boundary(face: str, orientation: int) -> dict[str, Any]:
    return {
        "face": face,
        "oriented_tangent": [0, 0, orientation],
        "outward_coorientation": [0, 0, -1 if face == "source" else 1],
        "bpw_word_symbol": "up" if orientation == 1 else "down",
    }


def build(write: bool = False) -> dict[str, Any]:
    collar = json.loads(COLLAR.read_text(encoding="utf-8"))
    if collar.get("contains_braid_word") or collar.get("doubled_endpoint_count") != 88:
        raise AssertionError("standard P0 collar is missing or contains detector-braid data")
    endpoints = []
    for item in collar["doubled_endpoint_order"]:
        endpoint = {
            "physical_endpoint_id": (
                f"actual:{item['owner']}:w{item['wicket']}:{item['side']}:{item['source_id']}"
            ),
            "owner": item["owner"],
            "wicket": int(item["wicket"]),
            "sign": item["side"],
            "orientation": int(item["orientation"]),
            "geometric_order": int(item["index"]),
        }
        endpoints.append(endpoint)
    endpoints.sort(key=lambda item: int(item["geometric_order"]))
    by_id = {item["physical_endpoint_id"]: item for item in endpoints}
    if SELECTED_V not in by_id or SELECTED_V_DUAL not in by_id:
        raise AssertionError("selected cup feet are absent from actual endpoint labels")
    standard_order = [by_id[SELECTED_V], by_id[SELECTED_V_DUAL]] + [
        item
        for item in endpoints
        if item["physical_endpoint_id"] not in {SELECTED_V, SELECTED_V_DUAL}
    ]
    charts = []
    for position, endpoint in enumerate(standard_order):
        multiplier = copy_multiplier(endpoint["sign"])
        if multiplier == 0:
            raise AssertionError("unknown cable-copy sign")
        orientation = int(endpoint["orientation"]) * multiplier
        variance = "V" if orientation == 1 else "V_dual"
        x = Fraction(-1) + Fraction(2 * (position + 1), 89)
        if variance == "V":
            highest_atom = "V_v1_to_v_plus"
            defect_atom = "V_vminus1_to_v_minus"
        else:
            highest_atom = "Vdual_vminus1dual_to_qminus1_v_plus"
            defect_atom = "Vdual_v1dual_to_v_minus"
        charts.append(
            {
                "physical_endpoint_id": endpoint["physical_endpoint_id"],
                "owner": endpoint["owner"],
                "wicket": int(endpoint["wicket"]),
                "copy_sign": endpoint["sign"],
                "base_passage_orientation": int(endpoint["orientation"]),
                "copy_orientation_multiplier": multiplier,
                "orientation": orientation,
                "tensor_position": position,
                "standard_vertical_arc": {
                    "source": [str(x), "0", "0"],
                    "target": [str(x), "0", "1"],
                    "oriented_tangent": [0, 0, orientation],
                    "product_normal": [0, 1, 0],
                },
                "boundary_face": "source",
                "oriented_tangent_vector_at_boundary": [0, 0, orientation],
                "boundary_face_coorientation": [0, 0, -1],
                "source_boundary": boundary("source", orientation),
                "target_boundary": boundary("target", orientation),
                "bpw_boundary_word_symbol": "up" if orientation == 1 else "down",
                "variance": variance,
                "variance_derivation": (
                    "oriented_copy=base_passage_orientation*copy_orientation_multiplier; "
                    "standard upward blue point maps to V and downward blue point maps to V_dual"
                ),
                "nesting_parent_locator": "none: pairwise parallel vertical blue strands",
                "nesting_depth": 0,
                "defect_basis_state": "defect",
                "highest_duality_atoms": [
                    atom(highest_atom),
                    atom("blanchet_blue_product_no_binding"),
                ],
                "duality_atoms": [
                    atom(defect_atom),
                    atom("blanchet_blue_product_no_binding"),
                ],
            }
        )

    selected_cup_cap = {
        "cup": {
            "ordered_feet": [SELECTED_V, SELECTED_V_DUAL],
            "bpw_A6_term": (
                "coev(1)=v_plus tensor v_minus + q^-1 v_minus tensor v_plus"
            ),
            "movie_or_web_locator": (
                "standard adjacent blue cup at tensor positions 0,1 with product normal +y and no red binding"
            ),
            "terms": [
                {
                    "defect_endpoint_id": SELECTED_V_DUAL,
                    "atom": "coev_vplus_vminus_coeff_1",
                },
                {
                    "defect_endpoint_id": SELECTED_V,
                    "atom": "coev_vminus_vplus_coeff_qminus1",
                },
            ],
        },
        "cap": {
            "ordered_feet": [SELECTED_V, SELECTED_V_DUAL],
            "bpw_A6_term": (
                "ev(v_plus tensor v_minus)=q; ev(v_minus tensor v_plus)=1"
            ),
            "movie_or_web_locator": (
                "standard adjacent blue cap at tensor positions 0,1 with product normal +y and no red binding"
            ),
            "terms": [
                {
                    "defect_endpoint_id": SELECTED_V_DUAL,
                    "atom": "ev_vplus_vminus_coeff_q",
                },
                {
                    "defect_endpoint_id": SELECTED_V,
                    "atom": "ev_vminus_vplus_coeff_1",
                },
            ],
        },
    }
    grading_diagrams = [
        {
            "name": "leftover_unlink_227",
            "diagram_or_family_locator": "standard 227 disjoint zero-framed blue circles",
            "theory": "intrinsic framed KhR2",
            "framing_convention": "product framing, blackboard writhe zero",
        },
        {
            "name": "endpoint_cup_U",
            "diagram_or_family_locator": selected_cup_cap["cup"]["movie_or_web_locator"],
            "theory": "strict BHPW blue foam",
            "framing_convention": "product normal +y, writhe zero",
        },
        {
            "name": "endpoint_cap_C",
            "diagram_or_family_locator": selected_cup_cap["cap"]["movie_or_web_locator"],
            "theory": "strict BHPW blue foam",
            "framing_convention": "product normal +y, writhe zero",
        },
        {
            "name": "endpoint_braid_W",
            "diagram_or_family_locator": "data/T73_DELTA3_PUBLIC_INPUT.json point_push",
            "theory": "strict BHPW oriented tangle endpoint action",
            "framing_convention": "returned product normals; computed writhe zero",
            "conversion": {
                "blackboard_writhe": 0,
                "formula": "-(N-1)*w",
                "applied_shift": 0,
            },
        },
    ]
    payload = {
        "schema": "t73_c_pivotal_grading_input/v1",
        "scope": (
            "freely chosen standard auxiliary detector convention; not a recovery of legacy endpoint coefficients"
        ),
        "standard_collar": {
            "p0_marked_vertical_collar_sha256": collar["sha256"],
            "manifold": "D2 x I",
            "source_face": "D2 x {0}",
            "target_face": "D2 x {1}",
            "product_orientation": ["+x", "+y", "+I"],
            "blue_product_normal": [0, 1, 0],
            "strand_count": 88,
            "selected_cup_feet_are_adjacent": True,
            "tensor_order_rule": "selected V foot, selected V_dual foot, then old geometric order",
        },
        "endpoint_duality_charts": charts,
        "selected_cup_cap": selected_cup_cap,
        "highest_tensor_normalization_rule": (
            "multiply the mixed-to-all-V chart by q^(number of V_dual factors) so the highest tensor has coefficient 1"
        ),
        "grading_diagrams": grading_diagrams,
        "grading_scope": (
            "only standard endpoint/unlink diagrams are supplied; full MWW coefficient/Hattori/cabled comparison remains open"
        ),
    }
    if write:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build(write=args.write)
    if args.check:
        committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if committed != payload:
            raise AssertionError("committed pivotal input differs from standard reconstruction")
    print("T73_STANDARD_PIVOTAL_INPUT=DEFINED")
    print(f"ENDPOINTS={len(payload['endpoint_duality_charts'])}")
    print(
        "V_COUNT="
        + str(sum(item["variance"] == "V" for item in payload["endpoint_duality_charts"]))
    )
    print(
        "V_DUAL_COUNT="
        + str(sum(item["variance"] == "V_dual" for item in payload["endpoint_duality_charts"]))
    )


if __name__ == "__main__":
    main()
