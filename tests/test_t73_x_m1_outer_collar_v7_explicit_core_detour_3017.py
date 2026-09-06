import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_outer_collar_v7_explicit_core_detour_3017.py"


class OuterCollarV7ExplicitCoreDetour3017Test(unittest.TestCase):
    def test_saved_explicit_core_detour(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["states_replayed"], 22)
        self.assertEqual(result["transitions_replayed"], 21)
        self.assertEqual(result["trace_triangles_replayed"], 210)
        self.assertEqual(result["state_self_segment_checks"], 132)
        self.assertEqual(result["transition_self_triangle_checks"], 504)
        self.assertEqual(result["static_core_exact_triangle_checks"], 332)
        self.assertEqual(result["forbidden_intersections"], 0)
        self.assertEqual(result["fixed_vertices"], [0])
        self.assertEqual(result["moving_vertices"], [1, 2, 3, 4, 5])
        self.assertEqual(result["push_and_ribbon_status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
