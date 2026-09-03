from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ARGeometryPipelineTest(unittest.TestCase):
    def test_torus_model_has_exact_periodic_pairing(self) -> None:
        model = load("build_t73_ar_torus").generate()
        self.assertEqual(model["checks"]["cover_tetrahedra"], 384)
        self.assertTrue(model["checks"]["all_boundary_faces_paired_by_period_translation"])
        self.assertEqual(model["psi_A_status"].split(":", 1)[0], "OPEN")

    def test_nielsen_factorization_reconstructs_A(self) -> None:
        module = load("factor_t73_matrix_nielsen")
        witness = module.generate()
        self.assertEqual(witness["construction_states"][-1], module.A)
        self.assertEqual(witness["product_check"], "PASS")

    def test_linear_data_do_not_fake_relative_psi(self) -> None:
        audit = load("build_t73_psi_candidate").generate()
        self.assertEqual(audit["psi_A_status"], "OPEN")
        self.assertFalse(audit["linear_phi_A"]["fixes_section_arc_endpoints"])
        self.assertGreater(len(audit["missing_geometric_data"]), 0)

    def test_paired_nielsen_movie_preserves_dual_pairing(self) -> None:
        movie = load("generate_t73_heegaard_nielsen_movie").generate()
        self.assertEqual(movie["combinatorial_status"], "PASS")
        self.assertTrue(movie["all_intersection_pairings_identity"])
        self.assertTrue(movie["pl_realization_status"].startswith("OPEN"))

    @unittest.skipUnless(shutil.which("gap"), "GAP is not installed")
    def test_pipeline_blocks_link_generation_until_pl_psi_exists(self) -> None:
        pipeline = load("check_t73_p0_pipeline").generate()
        self.assertEqual(
            pipeline["overall"],
            "PROVED_FOR_EXPLICIT_JOHNSON_REPLACEMENT_PRESENTATION",
        )
        self.assertTrue(pipeline["P0_proved"])
        self.assertEqual(pipeline["stages"]["T3d_route_thickening"]["state"], "PASS")
        self.assertEqual(
            pipeline["stages"]["T3e_nielsen_passage_comparison"]["state"],
            "FALSIFIED_FOR_PUBLIC_44_CHANNEL_COLLAR",
        )
        self.assertEqual(pipeline["stages"]["T3f_word_kirby_movie"]["state"], "PASS")
        self.assertEqual(pipeline["stages"]["T3g_ryz_band_schedule"]["local_state"], "PASS")
        self.assertEqual(pipeline["stages"]["T3h_ryz_framing"]["state"], "OPEN")
        self.assertEqual(pipeline["stages"]["T3i_reduced_link_linking"]["state"], "OPEN")
        self.assertFalse(
            pipeline["stages"]["T3j_linking_nonidentifiability"]["word_ledger_determines_linking"]
        )
        self.assertIn(
            pipeline["stages"]["T2a_compact_free_basis"]["state"],
            ("FAIL_NOT_FREE_BASIS", "GAP_NOT_INSTALLED"),
        )
        self.assertEqual(pipeline["stages"]["T2b_ia_44_channel_candidate"]["channels"], 44)
        self.assertFalse(pipeline["stages"]["T2b_ia_44_channel_candidate"]["exact_compact_match"])
        self.assertEqual(
            pipeline["stages"]["T2b1_inner_conjugation_geometry"]["state"],
            "BASEPOINT_CHANGE_ONLY_NOT_AN_EMBEDDED_44_CHANNEL_WITNESS",
        )
        self.assertEqual(pipeline["stages"]["T2d_ia_band_schedule"]["moves"], 11756)
        self.assertEqual(pipeline["stages"]["T2e_ia_framing"]["net_slide_coefficient"], -40)
        self.assertEqual(pipeline["stages"]["T2f_dual_meridian_extension_search"]["state"], "NONE_WITHIN_SEARCH")
        self.assertEqual(pipeline["stages"]["T2f_dual_meridian_extension_search"]["detector_candidates"], 751)
        self.assertEqual(pipeline["stages"]["T2h_johnson_side_candidate"]["state"], "PASS")
        self.assertEqual(pipeline["stages"]["T2h_johnson_side_candidate"]["channels"], 44)
        self.assertTrue(pipeline["stages"]["T2h_johnson_side_candidate"]["exact_compact_match"])
        self.assertEqual(pipeline["stages"]["T2i_johnson_relative_pl_movie"]["relative_state"], "PASS")
        self.assertEqual(pipeline["stages"]["T2i_johnson_relative_pl_movie"]["chosen_alpha_local_identity"], "PASS")
        self.assertTrue(pipeline["P0_proved"])
        self.assertFalse(pipeline["P0_falsified"])

    def test_unit_slide_templates_are_exact_and_local(self) -> None:
        templates = load("generate_t73_pl_nielsen_templates").generate()
        self.assertEqual(templates["local_template_status"], "PASS")
        self.assertEqual(templates["unit_slide_count"], 52)
        self.assertTrue(templates["global_placement_status"].startswith("OPEN"))

    def test_supports_are_placed_sequentially_away_from_section_arc(self) -> None:
        placement = load("place_t73_nielsen_supports").generate()
        self.assertEqual(placement["relative_section_arc_status"], "PASS")
        self.assertTrue(placement["time_interiors_pairwise_disjoint"])
        self.assertTrue(placement["handle_foot_routing_status"].startswith("OPEN"))

    def test_handle_foot_routes_avoid_protected_section_tube(self) -> None:
        routing = load("route_t73_handle_feet").generate()
        self.assertEqual(routing["polyline_routing_status"], "PASS")
        self.assertEqual(len(routing["pair_routes"]), 6)
        self.assertTrue(routing["thickening_status"].startswith("OPEN"))

    def test_handle_foot_routes_have_disjoint_tubes(self) -> None:
        thickening = load("thicken_t73_handle_routes").generate()
        self.assertEqual(thickening["target_source_tube_disjointness"], "PASS")
        self.assertEqual(thickening["handle_foot_chart_status"], "PASS")
        self.assertTrue(thickening["global_heegaard_map_status"].startswith("OPEN"))

    def test_nielsen_moves_compose_to_an_F3_automorphism(self) -> None:
        free_map = load("compose_t73_free_group_psi").generate()
        self.assertEqual(free_map["free_group_automorphism_status"], "PASS")
        self.assertEqual(free_map["left_inverse_check"], [[1], [2], [3]])
        self.assertEqual(free_map["right_inverse_check"], [[1], [2], [3]])
        self.assertTrue(free_map["spine_thickening_status"].startswith("OPEN"))

    def test_explicit_nielsen_route_does_not_have_44_channels(self) -> None:
        comparison = load("compare_t73_nielsen_passages").generate()
        self.assertEqual(comparison["nielsen_representative"]["total_y_channels"], 42)
        self.assertEqual(comparison["compact_representative"]["total_y_channels"], 44)
        self.assertEqual(comparison["current_nielsen_route_status"], "FALSIFIED_FOR_PUBLIC_44_CHANNEL_COLLAR")
        self.assertEqual(comparison["P0_global_status"], "OPEN")

    def test_word_kirby_movie_connects_309_and_311_representatives(self) -> None:
        movie = load("construct_t73_word_kirby_movie").generate()
        self.assertEqual(movie["nielsen_length"], 309)
        self.assertEqual(movie["compact_length"], 311)
        self.assertEqual(movie["word_movie_status"], "PASS")
        self.assertTrue(movie["geometric_band_status"].startswith("OPEN"))

    def test_word_movie_has_a_complete_local_band_schedule(self) -> None:
        schedule = load("generate_t73_ryz_band_schedule").generate()
        self.assertEqual(schedule["owner_transport_status"], "PASS")
        self.assertEqual(schedule["local_band_status"], "PASS")
        self.assertEqual(schedule["schedule_length"], 11258)
        self.assertTrue(schedule["global_band_embedding_status"].startswith("OPEN"))

    def test_net_ryz_slide_leaves_one_global_framing_condition(self) -> None:
        audit = load("audit_t73_ryz_framing").generate()
        self.assertEqual(audit["net_oriented_r_yz_slide_coefficient"], 1)
        self.assertEqual(audit["framing_status"], "OPEN")
        self.assertEqual(load("audit_t73_ryz_framing").generate(0)["framing_status"], "PASS")
        self.assertEqual(load("audit_t73_ryz_framing").generate(1)["framing_status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
