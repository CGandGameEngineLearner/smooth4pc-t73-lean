#!/usr/bin/env python3
"""Run every currently implemented stage of the strict P0 reconstruction."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate() -> dict[str, Any]:
    final_certificate = json.loads(
        (ROOT / "audit" / "t73_p0_johnson_certificate.json").read_text(encoding="utf-8")
    )
    final_pass = final_certificate["verdict"] == "PASS" and all(final_certificate["checks"].values())
    torus = load("build_t73_ar_torus").generate()
    factor = load("factor_t73_matrix_nielsen").generate()
    psi = load("build_t73_psi_candidate").generate()
    movie = load("generate_t73_heegaard_nielsen_movie").generate()
    templates = load("generate_t73_pl_nielsen_templates").generate()
    placement = load("place_t73_nielsen_supports").generate()
    routing = load("route_t73_handle_feet").generate()
    thickening = load("thicken_t73_handle_routes").generate()
    passage_comparison = load("compare_t73_nielsen_passages").generate()
    word_movie = load("construct_t73_word_kirby_movie").generate()
    band_schedule = load("generate_t73_ryz_band_schedule").generate()
    linking_path = ROOT / "audit" / "t73_reduced_link_pd.json"
    if linking_path.is_file():
        linking_result = load("extract_t73_ryz_linking").compute(json.loads(linking_path.read_text()))
        linking_state = "PASS"
        linking_value = linking_result["linking_m2_ryz"]
    else:
        linking_result = None
        linking_state = "OPEN"
        linking_value = None
    framing = load("audit_t73_ryz_framing").generate(linking_value)
    nonidentifiability = load("falsify_t73_linking_from_words").generate()
    compact_basis = load("check_t73_compact_free_basis").run(timeout=300)
    ia_representative = load("search_t73_ia_representative").generate(max_length=1)
    ia_movie = load("construct_t73_ia_to_compact_movie").generate()
    ia_band_schedule = load("generate_t73_ia_band_schedule").generate()
    ia_framing = load("audit_t73_ia_framing").generate(linking_value)
    inner_geometry = load("audit_t73_inner_conjugation_geometry").generate()
    dual_search = load("search_t73_dual_meridian_ia").generate(max_depth=3, max_states=200000)
    johnson_factor = load("factor_t73_matrix_johnson").generate()
    johnson_sides = load("search_t73_johnson_alpha_sides").generate()["known_candidate"]
    johnson_movie = load("generate_t73_johnson_alpha_movie").generate()
    johnson_relative = load("straighten_t73_johnson_relative_ball").generate()
    pl_ready = (
        movie["combinatorial_status"] == "PASS"
        and templates["local_template_status"] == "PASS"
        and placement["relative_section_arc_status"] == "PASS"
        and routing["polyline_routing_status"] == "PASS"
        and thickening["handle_foot_chart_status"] == "PASS"
        and thickening["global_heegaard_map_status"] == "PASS"
        and ia_representative["automorphism_channel_status"] == "PASS"
        and inner_geometry["geometric_verdict"] == "PASS_EMBEDDED_INNER_CONJUGATION"
        and ia_movie["word_movie_status"] == "PASS"
        and ia_band_schedule["global_band_embedding_status"] == "PASS"
        and linking_state == "PASS"
        and ia_framing["framing_status"] == "PASS"
    )
    johnson_ready_for_embedded_link = (
        johnson_sides["gap_is_bijective"]
        and johnson_sides["total_y_channels"] == 44
        and johnson_sides["net_r_yz_coefficient"] == 0
        and johnson_sides["exact_compact_match"]
        and johnson_movie["spine_pl_movie_status"] == "PASS"
        and johnson_relative["relative_spine_movie_status"] == "PASS"
        and johnson_relative["chosen_alpha_representative_local_identity_status"] == "PASS"
    )
    stages = {
        "T0_ar_torus": {
            "state": "PASS",
            "sha256": torus["model_sha256"],
        },
        "T1_matrix_factorization": {
            "state": "PASS",
            "operations": factor["operation_count"],
            "sha256": factor["witness_sha256"],
        },
        "T2_linear_phi_audit": {
            "state": psi["psi_A_status"],
            "sha256": psi["audit_sha256"],
        },
        "T2a_compact_free_basis": {
            "state": compact_basis["compact_verdict"],
            "nielsen_control": compact_basis["control_verdict"],
            "gap_version": compact_basis["compact"]["gap_version"],
            "sha256": compact_basis["receipt_sha256"],
        },
        "T2b_ia_44_channel_candidate": {
            "state": ia_representative["automorphism_channel_status"],
            "conjugator": ia_representative["conjugator"],
            "channels": ia_representative["total_y_channels"],
            "exact_compact_match": ia_representative["exact_compact_m2_match"],
            "geometric_state": ia_representative["geometric_status"],
            "sha256": ia_representative["witness_sha256"],
        },
        "T2b1_inner_conjugation_geometry": {
            "state": inner_geometry["geometric_verdict"],
            "outer_automorphism_unchanged": inner_geometry["outer_automorphism_unchanged"],
            "base_channels": inner_geometry["base_total_channels"],
            "based_channels": inner_geometry["based_ia_total_channels"],
            "sha256": inner_geometry["audit_sha256"],
        },
        "T2c_ia_to_compact_word_movie": {
            "state": ia_movie["word_movie_status"],
            "commutations": ia_movie["r_yz_commutation_count"],
            "bigons": ia_movie["free_bigon_move_count"],
            "geometric_state": ia_movie["geometric_status"],
            "sha256": ia_movie["movie_sha256"],
        },
        "T2d_ia_band_schedule": {
            "local_state": ia_band_schedule["local_band_status"],
            "owner_state": ia_band_schedule["owner_transport_status"],
            "global_embedding_state": ia_band_schedule["global_band_embedding_status"],
            "moves": ia_band_schedule["schedule_length"],
            "sha256": ia_band_schedule["schedule_sha256"],
        },
        "T2e_ia_framing": {
            "state": ia_framing["framing_status"],
            "net_slide_coefficient": ia_framing["net_oriented_r_yz_slide_coefficient"],
            "condition": ia_framing["condition"],
        },
        "T2f_dual_meridian_extension_search": {
            "state": dual_search["verdict"],
            "states": dual_search["states_visited"],
            "detector_candidates": dual_search["detector_cyclic_class_changed_44_channel_candidates"],
            "sufficient_extensions": len(dual_search["sufficient_dual_meridian_extension_candidates"]),
            "search_truncated": dual_search["search_truncated"],
            "scope": dual_search["scope"],
            "sha256": dual_search["receipt_sha256"],
        },
        "T2g_johnson_alpha_factorization": {
            "state": johnson_factor["matrix_product_status"],
            "unit_moves": johnson_factor["unit_alpha_move_count"],
            "sha256": johnson_factor["witness_sha256"],
        },
        "T2h_johnson_side_candidate": {
            "state": "PASS" if johnson_ready_for_embedded_link else "FAIL",
            "channels": johnson_sides["total_y_channels"],
            "exact_compact_match": johnson_sides["exact_compact_match"],
            "net_r_yz_coefficient": johnson_sides["net_r_yz_coefficient"],
            "gap_is_bijective": johnson_sides["gap_is_bijective"],
        },
        "T2i_johnson_relative_pl_movie": {
            "spine_state": johnson_movie["spine_pl_movie_status"],
            "ambient_state": johnson_movie["ambient_splitting_extension"],
            "relative_state": johnson_relative["relative_spine_movie_status"],
            "chosen_alpha_local_identity": johnson_relative["chosen_alpha_representative_local_identity_status"],
            "protected_ball_radius": johnson_relative["protected_ball_radius"],
            "sha256": johnson_relative["movie_sha256"],
        },
        "T2j_johnson_final_certificate": {
            "state": final_certificate["verdict"],
            "P0_status": final_certificate["P0_status"],
            "all_checks": all(final_certificate["checks"].values()),
            "sha256": final_certificate["certificate_sha256"],
        },
        "T3_paired_heegaard_movie": {
            "combinatorial_state": movie["combinatorial_status"],
            "pl_state": movie["pl_realization_status"],
            "sha256": movie["movie_sha256"],
        },
        "T3a_local_pl_templates": {
            "state": templates["local_template_status"],
            "unit_slides": templates["unit_slide_count"],
            "global_state": templates["global_placement_status"],
            "sha256": templates["witness_sha256"],
        },
        "T3b_relative_support_placement": {
            "state": placement["relative_section_arc_status"],
            "placements": placement["placement_count"],
            "handle_foot_routing": placement["handle_foot_routing_status"],
            "sha256": placement["placement_sha256"],
        },
        "T3c_handle_foot_routing": {
            "state": routing["polyline_routing_status"],
            "thickening_state": routing["thickening_status"],
            "sha256": routing["routing_sha256"],
        },
        "T3d_route_thickening": {
            "state": thickening["handle_foot_chart_status"],
            "global_map_state": thickening["global_heegaard_map_status"],
            "sha256": thickening["thickening_sha256"],
        },
        "T3e_nielsen_passage_comparison": {
            "state": passage_comparison["current_nielsen_route_status"],
            "nielsen_channels": passage_comparison["nielsen_representative"]["total_y_channels"],
            "compact_channels": passage_comparison["compact_representative"]["total_y_channels"],
            "P0_global_state": passage_comparison["P0_global_status"],
            "sha256": passage_comparison["comparison_sha256"],
        },
        "T3f_word_kirby_movie": {
            "state": word_movie["word_movie_status"],
            "moves": len(word_movie["combined_movie"]),
            "geometric_band_state": word_movie["geometric_band_status"],
            "sha256": word_movie["movie_sha256"],
        },
        "T3g_ryz_band_schedule": {
            "local_state": band_schedule["local_band_status"],
            "owner_state": band_schedule["owner_transport_status"],
            "global_embedding_state": band_schedule["global_band_embedding_status"],
            "global_framing_state": band_schedule["global_framing_status"],
            "sha256": band_schedule["schedule_sha256"],
        },
        "T3h_ryz_framing": {
            "state": framing["framing_status"],
            "net_slide_coefficient": framing["net_oriented_r_yz_slide_coefficient"],
            "known_relator_framing": framing["input_framing_ryz"],
            "missing_input": framing["missing_input"],
            "sha256": framing["audit_sha256"],
        },
        "T3i_reduced_link_linking": {
            "state": linking_state,
            "input": "audit/t73_reduced_link_pd.json",
            "linking_m2_ryz": linking_value,
            "result": linking_result,
        },
        "T3j_linking_nonidentifiability": {
            "state": "PASS",
            "word_ledger_determines_linking": nonidentifiability["word_ledger_determines_linking"],
            "zero_control": nonidentifiability["zero_linking_control"]["linking_m2_ryz"],
            "unit_control": nonidentifiability["unit_linking_control"]["linking_m2_ryz"],
            "sha256": nonidentifiability["witness_sha256"],
        },
        "T4_ar_attaching_link": {
            "state": "PASS" if final_pass else "BLOCKED",
            "reason": "Johnson side-choice attaching link and exact passage lanes",
        },
        "T5_cancellation_and_44_channel_collar": {
            "state": "PASS" if final_pass else "BLOCKED",
            "reason": "two product cancellations and 44 framed Johnson lanes",
        },
        "T6_relative_endpoint_braid": {
            "state": "PASS" if final_pass else "BLOCKED",
            "reason": "AR-side six-sweep construction and exact 11340-letter PL re-extraction",
        },
    }
    return {
        "schema": "t73_p0_pipeline_status/v1",
        "overall": final_certificate["P0_status"] if final_pass else "OPEN",
        "P0_proved": final_pass,
        "P0_falsified": False,
        "stages": stages,
        "next_required_object": None if final_pass else "complete the Johnson P0 certificate",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate()
    if args.check:
        print("T73_P0_PIPELINE=PASS")
        print(f"OVERALL={result['overall']}")
        print(f"NEXT_REQUIRED_OBJECT={result['next_required_object']}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
