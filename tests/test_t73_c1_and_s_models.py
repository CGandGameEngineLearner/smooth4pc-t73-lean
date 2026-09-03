from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class C1CutLinkTest(unittest.TestCase):
    def test_product_ribbons_are_the_p0_reconstruction_strands(self) -> None:
        c1 = load("certify_t73_c1_cut_link")
        result = c1.generate()
        self.assertEqual(result["geometric_status"], "PASS")
        self.assertEqual(result["C1_status"], "PASS")
        self.assertEqual(result["schema"], "t73_c1_cut_link/v3")
        self.assertEqual(result["counts"]["rectangles"], 44)
        self.assertEqual(result["counts"]["leftover_z_circles"], 227)
        self.assertEqual(result["counts"]["min_strand_vertices"], 34021)
        self.assertFalse(result["uniqueness_of_regular_neighborhoods_used"])
        self.assertEqual(len({item["strand_id"] for item in result["rectangles"]}), 44)
        self.assertEqual(result["rectangles"][0]["y_side_ends"][0][2], 0)
        self.assertEqual(result["rectangles"][0]["y_side_ends"][1][2], 4 * 11340)
        self.assertEqual(
            result["reconstruct_t73_p0_checks"],
            ["verify_ball", "verify_strands", "strand_points_in_ball"],
        )


class C2ComparisonTest(unittest.TestCase):
    def test_action_supports_miss_the_p0_ball_and_h_uses_c1_movies(self) -> None:
        c1 = load("certify_t73_c1_cut_link").generate()
        c2 = load("certify_t73_c2_comparison").generate()
        self.assertEqual(c2["C2_status"], "PASS")
        self.assertEqual(c2["c1_certificate_sha256"], c1["certificate_sha256"])
        self.assertEqual(len(c2["H"]["movies"]), 44)
        self.assertEqual(
            c2["H"]["movies"][0]["frames"][0]["arc_sha256"],
            c1["rectangles"][0]["y_side_sha256"],
        )
        left = c2["action_squares"]["left"]["support"]["bounds"]
        right = c2["action_squares"]["right"]["support"]["bounds"]
        ball = c1["p0_ball_bounds"]
        disjoint = load("certify_t73_c2_comparison").bounds_disjoint
        self.assertTrue(disjoint(left, ball))
        self.assertTrue(disjoint(right, ball))
        self.assertTrue(disjoint(left, right))


class SStandardSpheresTest(unittest.TestCase):
    def test_reversed_picture_belt_spheres_miss_the_p0_ball(self) -> None:
        module = load("certify_t73_s_standard_spheres")
        result = module.generate()
        self.assertEqual(result["schema"], "t73_s_standard_spheres/v6")
        self.assertEqual(result["verdict"], "PASS")
        self.assertTrue(result["checks"]["three_spheres"])
        self.assertTrue(result["checks"]["disjoint_from_model_ball"])
        self.assertTrue(result["checks"]["five_spotted_ball_tubings"])
        self.assertTrue(result["checks"]["detector_fixed"])
        self.assertTrue(result["checks"]["actual_standard_sphere_endpoint_foam_computed"])
        self.assertTrue(result["checks"]["replacement_standard_sphere_endpoint_foam_computed"])
        self.assertTrue(result["checks"]["three_one_handles"])
        self.assertTrue(result["checks"]["sphere_euler_characteristic_2"])
        self.assertEqual(result["ambient_3_manifold"]["homeomorphism_type"], "#^3(S^1 x S^2)")
        self.assertFalse(result["ambient_3_manifold"]["identified_with_partial_W2"])
        self.assertTrue(result["ambient_3_manifold"]["johnson_replacement_reversed_picture"])
        self.assertFalse(result["algebraic_nielsen_slides"]["fixes_B"])
        self.assertFalse(result["closed_hj_53_used_to_fix_B"])
        self.assertTrue(result["hj_53_used_for_kernel_invariance"])
        self.assertFalse(result["hj_lemmas_55_57_invoked"])
        for sphere in result["spheres"]:
            self.assertEqual(sphere["endpoint_foam"]["b"], 0)
            self.assertEqual(sphere["endpoint_foam"]["evaluation"]["epsilon_1"], 0)
            self.assertEqual(sphere["endpoint_foam"]["evaluation"]["epsilon_X"], 1)
            self.assertFalse(sphere["endpoint_foam"]["actual_w2_lasagna_map"])
            self.assertIn(sphere["kernel_attaching"]["owner"], {"r_xy", "r_yz", "r_zx"})
            self.assertTrue(sphere["kernel_attaching"]["misses_detector_ball"])
            self.assertTrue(sphere["kernel_attaching"]["to_standard_movie"]["fixes_model_ball"])
        self.assertTrue(result["checks"]["replacement_kernel_attaching_unknots_realized"])
        self.assertTrue(result["checks"]["replacement_nielsen_generator_movies_fix_model_ball"])
        self.assertTrue(result["checks"]["actual_attaching_system_identified"])
        self.assertTrue(result["checks"]["dual_loop_pairing_identity"])
        self.assertTrue(result["checks"]["chart_return_misses_belt_cubes"])
        self.assertTrue(result["checks"]["misses_c1_leftover_circles"])
        self.assertTrue(result["checks"]["misses_c2_supports"])
        self.assertFalse(result["closed_hj_53_used_to_fix_B"])
        for sphere in result["spheres"]:
            for box in sphere["dual_loop"]["chart_arc_boxes"]:
                for other in result["spheres"]:
                    self.assertTrue(
                        module.boxes_interior_disjoint(box, other["box"]),
                        f"{sphere['name']} chart return meets {other['name']}",
                    )
        self.assertEqual(result["spheres"][0]["kernel_attaching"]["attaching_word"], ["z", "y", "Z", "Y"])
        self.assertEqual(result["spheres"][1]["kernel_attaching"]["attaching_word"], ["y", "z", "Y", "Z"])
        self.assertEqual(result["spheres"][2]["kernel_attaching"]["attaching_word"], [])
        self.assertEqual(
            len(result["nielsen_pl_movies"]),
            result["algebraic_nielsen_slides"]["operation_count"],
        )
        self.assertTrue(result["attaching_homology"]["identified_with_actual_attaching_system"])
        self.assertFalse(result["attaching_homology"]["geometric_parallel_copies_instantiated"])
        for movie in result["nielsen_pl_movies"]:
            self.assertTrue(movie["misses_detector_ball"])
            self.assertTrue(movie["fixes_model_ball"])
            self.assertFalse(movie["actual_attaching_system_movie"])
        c1 = load("certify_t73_c1_cut_link").generate()
        self.assertEqual(result["model_ball"]["bounds"], c1["p0_ball_bounds"])
        self.assertEqual(len(result["spotted_ball_tubings"]), 5)


if __name__ == "__main__":
    unittest.main()
