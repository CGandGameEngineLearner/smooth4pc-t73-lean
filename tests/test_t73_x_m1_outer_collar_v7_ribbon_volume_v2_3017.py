import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_outer_collar_v7_ribbon_volume_v2_3017.py"


class OuterCollarV7RibbonVolumeV23017Test(unittest.TestCase):
    def test_saved_refined_ribbon_volume(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["states_reconstructed"], 26)
        self.assertEqual(result["transitions_reconstructed"], 25)
        self.assertEqual(result["repair_midpoints_reconstructed"], 4)
        self.assertEqual(result["core_push_trace_checks"], 2500)
        self.assertEqual(result["moving_core_static_checks"], 774)
        self.assertEqual(result["moving_push_static_checks"], 982)
        self.assertEqual(result["r4_tetrahedra"], 750)
        self.assertEqual(result["r4_nonincident_tetrahedron_checks"], 6700)
        self.assertTrue(result["internal_ribbon_volume_self_clearance"])
        self.assertTrue(result["static_one_skeleton_clearance"])
        self.assertEqual(result["static_ribbon_volume_clearance"], "OPEN")


if __name__ == "__main__":
    unittest.main()
