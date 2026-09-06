import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_outer_collar_v7_relative_framed_movie_3017.py"


class OuterCollarV7RelativeFramedMovie3017Test(unittest.TestCase):
    def test_saved_relative_framed_movie(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["states_replayed"], 22)
        self.assertEqual(result["transitions_replayed"], 21)
        self.assertTrue(result["fixed_germ_boundary_all_states"])
        self.assertEqual(result["trace_triangle_rank_checks"], 420)
        self.assertEqual(result["core_trace_self_checks"], 504)
        self.assertEqual(result["push_trace_self_checks"], 504)
        self.assertEqual(result["core_push_trace_checks"], 2100)
        self.assertEqual(result["moving_core_static_checks"], 776)
        self.assertEqual(result["moving_push_static_checks"], 784)
        self.assertEqual(result["forbidden_intersections"], 0)
        self.assertEqual(result["ribbon_volume"], "OPEN_REBUILD_WITH_NEW_CORE_MODES")


if __name__ == "__main__":
    unittest.main()
