import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts/verify_t73_x_m1_outer_collar_v7_ribbon_volume_v2_static_clearance_3017.py"
)


class OuterCollarV7RibbonVolumeV2StaticClearance3017Test(unittest.TestCase):
    def test_saved_static_ribbon_volume_clearance(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["moving_tetrahedra"], 750)
        self.assertEqual(result["static_tetrahedra"], 18390)
        self.assertEqual(result["semantic_matrices_replayed"], 4)
        self.assertEqual(result["exact_tetrahedron_checks"], 5048)
        self.assertEqual(result["source_candidates"], 0)
        self.assertEqual(result["final_candidates"], 5048)
        self.assertEqual(result["forbidden_intersections"], 0)
        self.assertTrue(result["scheduled_static_collar_ribbon_volume_clearance"])
        self.assertEqual(result["retained_replacement_ribbon_volume"], "OPEN")


if __name__ == "__main__":
    unittest.main()
