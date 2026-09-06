import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "scripts/verify_t73_x_m1_outer_collar_v7_reverse_static_ribbon_clearance.py"
)


class OuterCollarV7ReverseStaticRibbonClearanceTest(unittest.TestCase):
    def test_saved_reverse_ribbon_clearance(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["outward_float_aabb_candidates"], 8)
        self.assertEqual(result["permitted_coplanar_opposite_stars"], 4)
        self.assertEqual(result["nonincident_rectangle_candidates"], 4)
        self.assertEqual(result["exact_triangle_pair_checks"], 16)
        self.assertEqual(result["nonpermitted_intersections"], 0)
        self.assertTrue(result["reverse_mixed_static_ribbon_clearance"])
        self.assertEqual(result["reverse_dynamic_status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
