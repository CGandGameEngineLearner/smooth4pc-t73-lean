import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_outer_collar_v7_relative_ribbon_volume_3017.py"


class OuterCollarV7RelativeRibbonVolume3017Test(unittest.TestCase):
    def test_saved_relative_ribbon_volume(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["states_replayed"], 23)
        self.assertEqual(result["transitions_replayed"], 22)
        self.assertEqual(result["repair_midpoints_replayed"], 1)
        self.assertTrue(result["fixed_germ_boundary_all_states"])
        self.assertEqual(result["trace_triangle_rank_checks"], 440)
        self.assertEqual(result["core_push_trace_checks"], 2200)
        self.assertEqual(result["moving_core_static_checks"], 718)
        self.assertEqual(result["moving_push_static_checks"], 550)
        self.assertEqual(result["r4_tetrahedra"], 660)
        self.assertEqual(result["r4_nonincident_tetrahedron_checks"], 5896)
        self.assertEqual(result["forbidden_intersections"], 0)
        self.assertEqual(result["external_ribbon_volume_clearance"], "OPEN")


if __name__ == "__main__":
    unittest.main()
