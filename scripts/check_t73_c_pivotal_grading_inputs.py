#!/usr/bin/env python3
"""Fail-closed audit of the C pivotal and absolute-grading inputs.

This checker deliberately does *not* infer a pivotal chart from an endpoint's
orientation.  In the BPW conventions an oriented point can carry V or V^*,
and the identification V^* -> V is basis dependent (BPW (A.4)); cups and caps
then use the ordered evaluation/coevaluation formulas (BPW (A.6)).  Blanchet
foam charts may add further signs.  Those choices must therefore be supplied
as primitive geometric data rather than as already-derived coefficients.

Likewise, the Manolescu--Neithalath erratum requires a writhe entry whenever
one converts between framed KhR_2 and a rational/unframed convention.  A zero
writhe for the detector braid alone is not a complete grading ledger.

The current repository intentionally has no
``data/T73_C_PIVOTAL_GRADING_INPUT.json``.  Consequently this command reports
OPEN and exits 2.  ``--allow-open`` is for audit tests which verify that this
failure mode remains closed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "T73_C_PIVOTAL_GRADING_INPUT.json"
SCHEMA = ROOT / "data" / "T73_C_PIVOTAL_GRADING_INPUT.schema.json"
ENDPOINTS = ROOT / "geometry" / "t73_actual_cut_tangle.json"
PUBLIC = ROOT / "data" / "T73_DELTA3_PUBLIC_INPUT.json"
REPORT = ROOT / "audit" / "t73_c_pivotal_grading_report.json"
ENDPOINT_BUILDER = ROOT / "scripts" / "build_t73_endpoint_transport.py"
LEGACY_CONVENTION = ROOT / "data" / "T73_ENDPOINT_CONVENTION.json"

SELECTED_CUP_IDS = {
    "actual:r_xy:w2:neg:r_xy:vertex:7",
    "actual:m_2:w44:pos:m_2:C_i",
}

REQUIRED_DIAGRAMS = {
    "mww_selected_coefficient_closure",
    "hattori_target_closure",
    "leftover_unlink_227",
    "endpoint_cup_U",
    "endpoint_cap_C",
    "endpoint_braid_W",
    "cabled_state_s0",
    "mww_to_bhpw_selected_comparison",
}

REQUIRED_ENDPOINT_FIELDS = {
    "physical_endpoint_id",
    "tensor_position",
    "orientation",
    "boundary_face",
    "oriented_tangent_vector_at_boundary",
    "boundary_face_coorientation",
    "bpw_boundary_word_symbol",
    "variance",
    "variance_derivation",
    "nesting_parent_locator",
    "nesting_depth",
    "defect_basis_state",
    "duality_atoms",
}

ALLOWED_VARIANCE = {"V", "V_dual"}
ALLOWED_DEFECT_STATE = {"highest", "defect"}
ALLOWED_ATOMS = {
    # BPW (A.4).
    "V_v1_to_v_plus",
    "V_vminus1_to_v_minus",
    "Vdual_v1dual_to_v_minus",
    "Vdual_vminus1dual_to_qminus1_v_plus",
    # BPW (A.6), with the tensor order part of the atom name.
    "coev_vplus_vminus_coeff_1",
    "coev_vminus_vplus_coeff_qminus1",
    "ev_vplus_vminus_coeff_q",
    "ev_vminus_vplus_coeff_1",
    # BHPW sign-producing local charts.  The input must cite a local normal
    # and a source locator before one of these is accepted.
    "blanchet_detachment_positive",
    "blanchet_detachment_negative",
}


def detector_writhe() -> int:
    data = json.loads(PUBLIC.read_text(encoding="utf-8"))
    columns = data["point_push"]["crossing_row_columns"]
    sign_index = columns.index("sign")
    # Each primitive row contributes a signed square in B44.  Cabling a
    # crossing contributes four crossings with the same total sign.
    return 8 * sum(int(row[sign_index]) for row in data["point_push"]["crossing_rows"])


def _copy_orientation_multiplier(copy_sign: str) -> int:
    if copy_sign == "pos":
        return 1
    if copy_sign == "neg":
        return -1
    raise ValueError(f"unknown cable-copy sign {copy_sign!r}")


def endpoint_diagnostics(actual_endpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Explain, endpoint by endpoint, why orientation does not fix a pivot.

    The product of the stored passage orientation and the cable-copy sign is
    derivable.  It is recorded as a necessary oriented-intersection datum, but
    it is not promoted to a BPW ``V``/``V_dual`` variance: that also requires
    the missing source/target boundary face and its coorientation.
    """

    legacy_by_id: dict[str, dict[str, Any]] = {}
    if LEGACY_CONVENTION.is_file():
        legacy = json.loads(LEGACY_CONVENTION.read_text(encoding="utf-8"))
        legacy_by_id = {
            item["physical_endpoint_id"]: item for item in legacy.get("endpoints", [])
        }

    diagnostics: list[dict[str, Any]] = []
    for endpoint in sorted(actual_endpoints, key=lambda item: int(item["geometric_order"])):
        endpoint_id = endpoint["physical_endpoint_id"]
        passage_orientation = int(endpoint["orientation"])
        copy_multiplier = _copy_orientation_multiplier(endpoint["sign"])
        oriented_copy_passage_sign = passage_orientation * copy_multiplier
        legacy = legacy_by_id.get(endpoint_id)
        legacy_orientation = legacy.get("orientation") if legacy else None
        legacy_pivotal = legacy.get("pivotal_coefficient") if legacy else None
        absent = [
            # Needed to turn the oriented intersection sign into an arrow in
            # the BPW boundary word, hence into V or V^*.
            "boundary_face_source_or_target",
            "oriented_tangent_vector_at_boundary",
            "boundary_face_coorientation",
            "bpw_boundary_word_symbol_derived_from_those_vectors",
            # Needed for the position-dependent V^* -> V chart in BPW (A.4).
            "cup_web_or_platform_nesting_parent",
            "cup_web_or_platform_nesting_depth",
            "ordered_BPW_A4_duality_atom_path",
            # Needed to determine any signs in the strict Blanchet lift.
            "blanchet_binding_or_detachment_local_normal",
            "strict_foam_movie_locator_for_the_chart",
        ]
        if endpoint_id in SELECTED_CUP_IDS:
            absent.extend(
                [
                    "selected_cup_ordered_BPW_A6_term",
                    "selected_cap_ordered_BPW_A6_term",
                    "selected_cup_and_cap_strict_movie_locators",
                ]
            )
        diagnostics.append(
            {
                "physical_endpoint_id": endpoint_id,
                "owner": endpoint["owner"],
                "wicket": int(endpoint["wicket"]),
                "tensor_position_from_boundary_order": int(endpoint["geometric_order"]),
                "actual_endpoint_locator": (
                    "geometry/t73_actual_cut_tangle.json#/framed_endpoints/"
                    f"{int(endpoint['geometric_order'])}"
                ),
                "present_primitives": {
                    "copy_sign": endpoint["sign"],
                    "copy_orientation_multiplier": copy_multiplier,
                    "base_passage_orientation": passage_orientation,
                    "oriented_copy_passage_sign": oriented_copy_passage_sign,
                    "transported_normal_coefficient": endpoint[
                        "transported_normal_coefficient"
                    ],
                },
                "legacy_assignment": {
                    "orientation": legacy_orientation,
                    "pivotal_coefficient": legacy_pivotal,
                    "orientation_ignores_base_passage": (
                        legacy_orientation is not None
                        and int(legacy_orientation) != oriented_copy_passage_sign
                    ),
                    "accepted_as_primitive_derivation": False,
                },
                "exact_absent_primitives": absent,
                "variance": "UNDETERMINED",
                "pivotal_sign": "UNDETERMINED",
                "q_power": "UNDETERMINED",
            }
        )
    return diagnostics


def legacy_assessment(diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
    assigned = [
        item["legacy_assignment"]["pivotal_coefficient"]
        for item in diagnostics
        if item["legacy_assignment"]["pivotal_coefficient"] is not None
    ]
    return {
        "endpoint_count": len(assigned),
        "all_coefficients_plus_q0": bool(assigned)
        and all(
            int(coefficient.get("sign", 0)) == 1
            and int(coefficient.get("q_power", 1)) == 0
            for coefficient in assigned
        ),
        "orientation_disagreement_endpoint_ids": [
            item["physical_endpoint_id"]
            for item in diagnostics
            if item["legacy_assignment"]["orientation_ignores_base_passage"]
        ],
        "primitive_derivation_count": 0,
        "accepted_for_pivotal_certification": False,
        "reason": (
            "The legacy table serializes derived sign/q-power literals but "
            "contains no boundary-face, BPW A.4/A.6, nesting, or Blanchet-normal proof."
        ),
    }


def base_report() -> dict[str, Any]:
    actual = json.loads(ENDPOINTS.read_text(encoding="utf-8"))
    endpoints = actual.get("framed_endpoints", [])
    builder_source = ENDPOINT_BUILDER.read_text(encoding="utf-8")
    diagnostics = endpoint_diagnostics(endpoints)
    return {
        "schema": "t73_c_pivotal_grading_report/v1",
        "status": "OPEN",
        "actual_endpoint_count": len(endpoints),
        "actual_endpoint_orientations_present": all(
            endpoint.get("sign") in {"neg", "pos"} for endpoint in endpoints
        ),
        "actual_passage_orientations_present": all(
            endpoint.get("orientation") in {-1, 1} for endpoint in endpoints
        ),
        "detector_braid_writhe": detector_writhe(),
        "hard_coded_builder_assignments_present": (
            "pivotal_sign = 1" in builder_source and "q_power = 0" in builder_source
        ),
        "endpoint_diagnostics": diagnostics,
        "legacy_endpoint_coefficients": legacy_assessment(diagnostics),
        "missing": [],
        "derived": {
            "hom_normalization": -44,
            "X_labels": 227,
            "one_handle_gluing_shift": 315,
            "cabled_s0_shift": -4,
            "formal_sum": 494,
        },
        "degree_494_certified": False,
        "pivotal_coefficients_certified": False,
    }


def validate_input(payload: dict[str, Any], report: dict[str, Any]) -> None:
    if payload.get("schema") != "t73_c_pivotal_grading_input/v1":
        report["missing"].append("root.schema=t73_c_pivotal_grading_input/v1")

    charts = payload.get("endpoint_duality_charts")
    if not isinstance(charts, list) or len(charts) != 88:
        report["missing"].append("88 endpoint_duality_charts")
        charts = []

    seen_ids: set[str] = set()
    seen_positions: set[int] = set()
    for index, chart in enumerate(charts):
        if not isinstance(chart, dict):
            report["missing"].append(f"endpoint_duality_charts[{index}] object")
            continue
        absent = sorted(REQUIRED_ENDPOINT_FIELDS - set(chart))
        for field in absent:
            report["missing"].append(f"endpoint_duality_charts[{index}].{field}")
        endpoint_id = chart.get("physical_endpoint_id")
        position = chart.get("tensor_position")
        if isinstance(endpoint_id, str):
            if endpoint_id in seen_ids:
                report["missing"].append(f"duplicate physical_endpoint_id {endpoint_id}")
            seen_ids.add(endpoint_id)
        if isinstance(position, int):
            if position in seen_positions:
                report["missing"].append(f"duplicate tensor_position {position}")
            seen_positions.add(position)
        if chart.get("orientation") not in {-1, 1}:
            report["missing"].append(f"endpoint_duality_charts[{index}].orientation=+-1")
        if chart.get("boundary_face") not in {"source", "target"}:
            report["missing"].append(
                f"endpoint_duality_charts[{index}].boundary_face=source|target"
            )
        for vector_field in (
            "oriented_tangent_vector_at_boundary",
            "boundary_face_coorientation",
        ):
            vector = chart.get(vector_field)
            if not isinstance(vector, list) or len(vector) != 3:
                report["missing"].append(
                    f"endpoint_duality_charts[{index}].{vector_field}=3-vector"
                )
        if chart.get("bpw_boundary_word_symbol") not in {"up", "down"}:
            report["missing"].append(
                f"endpoint_duality_charts[{index}].bpw_boundary_word_symbol=up|down"
            )
        if chart.get("variance") not in ALLOWED_VARIANCE:
            report["missing"].append(f"endpoint_duality_charts[{index}].variance=V|V_dual")
        if not chart.get("variance_derivation"):
            report["missing"].append(
                f"endpoint_duality_charts[{index}].variance_derivation"
            )
        if not chart.get("nesting_parent_locator"):
            report["missing"].append(
                f"endpoint_duality_charts[{index}].nesting_parent_locator"
            )
        if chart.get("defect_basis_state") not in ALLOWED_DEFECT_STATE:
            report["missing"].append(
                f"endpoint_duality_charts[{index}].defect_basis_state=highest|defect"
            )
        atoms = chart.get("duality_atoms")
        if not isinstance(atoms, list) or not atoms:
            report["missing"].append(f"endpoint_duality_charts[{index}].duality_atoms")
        else:
            for atom_index, atom in enumerate(atoms):
                if not isinstance(atom, dict) or atom.get("kind") not in ALLOWED_ATOMS:
                    report["missing"].append(
                        f"endpoint_duality_charts[{index}].duality_atoms[{atom_index}].kind"
                    )
                    continue
                if not atom.get("source_locator"):
                    report["missing"].append(
                        f"endpoint_duality_charts[{index}].duality_atoms[{atom_index}].source_locator"
                    )
                if atom["kind"].startswith("blanchet_") and not atom.get("local_normal"):
                    report["missing"].append(
                        f"endpoint_duality_charts[{index}].duality_atoms[{atom_index}].local_normal"
                    )

    if charts and seen_positions != set(range(88)):
        report["missing"].append("tensor_position permutation 0..87")

    cup_cap = payload.get("selected_cup_cap")
    if not isinstance(cup_cap, dict):
        report["missing"].append("selected_cup_cap")
    else:
        for name in ("cup", "cap"):
            item = cup_cap.get(name)
            if not isinstance(item, dict):
                report["missing"].append(f"selected_cup_cap.{name}")
                continue
            for field in ("ordered_feet", "bpw_A6_term", "movie_or_web_locator"):
                if not item.get(field):
                    report["missing"].append(f"selected_cup_cap.{name}.{field}")

    diagrams = payload.get("grading_diagrams")
    if not isinstance(diagrams, list):
        report["missing"].append("grading_diagrams")
        diagrams = []
    by_name = {
        item.get("name"): item for item in diagrams if isinstance(item, dict) and item.get("name")
    }
    for name in sorted(REQUIRED_DIAGRAMS - set(by_name)):
        report["missing"].append(f"grading_diagrams[{name}]")
    for name, item in by_name.items():
        for field in ("diagram_or_family_locator", "theory", "framing_convention"):
            if not item.get(field):
                report["missing"].append(f"grading_diagrams[{name}].{field}")
        conversion = item.get("conversion")
        if conversion:
            for field in ("blackboard_writhe", "formula", "applied_shift"):
                if field not in conversion:
                    report["missing"].append(f"grading_diagrams[{name}].conversion.{field}")
            if conversion.get("formula") != "-(N-1)*w":
                report["missing"].append(
                    f"grading_diagrams[{name}].conversion.formula=-(N-1)*w"
                )
            if all(field in conversion for field in ("blackboard_writhe", "applied_shift")):
                expected = -int(conversion["blackboard_writhe"])  # N=2
                if int(conversion["applied_shift"]) != expected:
                    report["missing"].append(
                        f"grading_diagrams[{name}].conversion.applied_shift={expected}"
                    )

    report["pivotal_coefficients_certified"] = not any(
        item.startswith("endpoint_duality_charts")
        or item.startswith("selected_cup_cap")
        or item.startswith("tensor_position")
        for item in report["missing"]
    )
    report["degree_494_certified"] = (
        report["pivotal_coefficients_certified"]
        and not any(item.startswith("grading_diagrams") for item in report["missing"])
        and report["derived"]["formal_sum"] == 494
    )
    report["status"] = (
        "CERTIFIED" if report["pivotal_coefficients_certified"] and report["degree_494_certified"]
        else "OPEN"
    )


def generate() -> dict[str, Any]:
    report = base_report()
    if not SCHEMA.is_file():
        report["missing"].append(str(SCHEMA.relative_to(ROOT)))
    if not INPUT.is_file():
        report["missing"].extend(
            [
                str(INPUT.relative_to(ROOT)),
                "88 ordered V/V_dual endpoint charts with BPW (A.4) atoms",
                "ordered cup/cap BPW (A.6) terms and geometric movie locators",
                "Blanchet sign normals for every sign-producing chart",
                "complete framed-KhR2/BHPW/MN-erratum writhe ledger",
            ]
        )
    else:
        validate_input(json.loads(INPUT.read_text(encoding="utf-8")), report)
    # Deduplicate while retaining a deterministic order.
    report["missing"] = list(dict.fromkeys(report["missing"]))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--allow-open", action="store_true")
    args = parser.parse_args()
    report = generate()
    if args.write:
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "CERTIFIED" and not args.allow_open:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
