import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts/verify_t73_x_m1_outer_collar_v7_normal_field_static_clearance_3017.py"
)


class OuterCollarV7NormalFieldStaticClearance3017Test(unittest.TestCase):
    def test_saved_static_clearance(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["static_vertical_triangles"], 12260)
        self.assertEqual(result["semantic_matrices_replayed"], 4)
        self.assertEqual(result["exact_triangle_checks"], 1560)
        self.assertEqual(result["source_static_candidates"], 0)
        self.assertEqual(result["final_static_candidates"], 1560)
        self.assertEqual(result["forbidden_intersections"], 0)
        self.assertTrue(result["global_framed_one_skeleton_clearance"])
        self.assertEqual(result["ribbon_world_volume"], "OPEN")


if __name__ == "__main__":
    unittest.main()
