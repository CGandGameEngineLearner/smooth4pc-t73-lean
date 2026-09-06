import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts/build_t73_x_m1_outer_collar_v7_replacement_ribbon_clearance_verification.py"
)


class OuterCollarV7ReplacementRibbonClearanceTest(unittest.TestCase):
    def test_saved_full_exact_cross_clearance(self):
        spec = importlib.util.spec_from_file_location("receipt", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        result = receipt["full_result"]
        self.assertEqual(result["aabb_and_float_outward_f_candidates"], 4_809_221)
        self.assertEqual(result["exact_bounds_rejects"], 1342)
        self.assertEqual(result["exact_skew_axis_rejects"], 4_807_879)
        self.assertEqual(result["intersection_count"], 0)
        self.assertTrue(result["global_replacement_cross_clearance"])


if __name__ == "__main__":
    unittest.main()
