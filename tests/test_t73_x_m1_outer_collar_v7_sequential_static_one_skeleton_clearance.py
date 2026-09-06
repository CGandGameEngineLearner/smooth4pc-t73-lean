import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts/verify_t73_x_m1_outer_collar_v7_sequential_static_one_skeleton_clearance.py"
)


class OuterCollarV7SequentialStaticOneSkeletonClearanceTest(unittest.TestCase):
    def test_saved_ordered_mixed_one_skeleton_clearance(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify_full()
        self.assertEqual(result["directed_matrices_replayed"], 3)
        self.assertEqual(result["outward_float_aabb_candidates"], 9058)
        self.assertEqual(result["exact_separated_pairs"], 9054)
        self.assertEqual(result["permitted_opposite_germ_incidences"], 4)
        self.assertEqual(result["nonpermitted_intersections"], 0)
        self.assertTrue(result["ordered_mixed_static_one_skeleton_clearance"])
        self.assertEqual(result["ribbon_status"], "OPEN")
        self.assertEqual(result["moving_static_status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
