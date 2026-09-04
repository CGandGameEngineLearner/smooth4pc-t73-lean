from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SRelativeMovesTest(unittest.TestCase):
    def test_committed_certificate_replays(self) -> None:
        path = ROOT / "scripts" / "certify_t73_s_relative_moves.py"
        spec = importlib.util.spec_from_file_location("s_relative", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        generated = module.generate()
        self.assertEqual(generated["verdict"], "PASS")
        self.assertTrue(generated["checks"]["detector_fixed"])
        self.assertEqual(generated["relative_geometry"]["spotted_ball_boundary_count"], 7)
        self.assertEqual(generated["relative_geometry"]["maximum_spotted_ball_tubings"], 5)
        self.assertEqual(
            generated["mww_hemisphere_table"]["coequalizer_difference"],
            {"1": 0, "X": 0},
        )
        self.assertFalse(
            generated["candidate_binding"]["actual_standard_sphere_endpoint_foam_computed"]
        )
        self.assertEqual(len(generated["relative_geometry"]["relative_sphere_movies"]), 3)
        self.assertEqual(len(generated["relative_geometry"]["spotted_ball_tubing_movies"]), 5)
        self.assertTrue(generated["relative_geometry"]["identity_on_p0_ball"])
        self.assertEqual(generated["relative_geometry"]["ambient_homeomorphism_type"], "#^3(S^1 x S^2)")
        self.assertEqual(generated["relative_geometry"]["identified_with_partial_W2"], False)
        self.assertTrue(generated["checks"]["replacement_standard_sphere_endpoint_foam_computed"])
        self.assertTrue(generated["checks"]["replacement_nielsen_generator_movies_fix_model_ball"])
        self.assertTrue(generated["checks"]["actual_attaching_system_identified"])
        self.assertIn("PASS", generated["relative_geometry"]["collar_motion"])
        self.assertGreater(generated["relative_geometry"]["nielsen_pl_movie_count"], 0)
        self.assertFalse(generated["relative_geometry"]["nielsen_parallel_copies_instantiated"])
        self.assertFalse(generated["actual_w2_lasagna_map"])
        self.assertFalse(generated["checks"]["D_vA0_equals_D_v"])
        self.assertFalse(generated["checks"]["D_vA1_equals_zero"])


if __name__ == "__main__":
    unittest.main()
