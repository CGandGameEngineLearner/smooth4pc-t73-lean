from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class JohnsonAlphaSideTest(unittest.TestCase):
    def test_known_side_choice_has_44_channels_and_zero_area(self):
        path = ROOT / "scripts" / "search_t73_johnson_alpha_sides.py"
        spec = importlib.util.spec_from_file_location("side_search", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate()
        candidate = result["known_candidate"]
        self.assertTrue(candidate["gap_is_bijective"])
        self.assertEqual(candidate["m2_length"], 311)
        self.assertEqual(candidate["total_y_channels"], 44)
        self.assertEqual(candidate["net_r_yz_coefficient"], 0)
        self.assertTrue(candidate["exact_compact_match"])

    def test_selected_sides_have_exact_square_diagonal_movie(self):
        path = ROOT / "scripts" / "generate_t73_johnson_alpha_movie.py"
        spec = importlib.util.spec_from_file_location("alpha_movie", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate()
        self.assertEqual(result["move_count"], 93)
        self.assertTrue(result["all_squares_nondegenerate"])
        self.assertTrue(result["all_endpoints_match"])
        self.assertEqual(result["ambient_splitting_extension"], "PASS_BY_JOHNSON_ALPHA_CONSTRUCTION")
        self.assertTrue(result["relative_section_ball_status"].startswith("OPEN"))

    def test_square_movies_can_be_made_relative_to_radius_one_eighth_ball(self):
        path = ROOT / "scripts" / "straighten_t73_johnson_relative_ball.py"
        spec = importlib.util.spec_from_file_location("relative_movie", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate()
        self.assertEqual(result["move_count"], 93)
        self.assertEqual(result["relative_spine_movie_status"], "PASS")
        self.assertGreater(module.Fraction(result["protected_ball_radius"]), 0)
        self.assertLessEqual(module.Fraction(result["protected_ball_radius"]), module.Fraction(1, 8))
        self.assertEqual(result["square_isotopy_support_status"], "PASS_OUTSIDE_PROTECTED_BALL")
        self.assertEqual(result["chosen_alpha_representative_local_identity_status"], "PASS")
        self.assertTrue(result["relative_ambient_extension"].startswith("PASS"))


if __name__ == "__main__":
    unittest.main()
