import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_x_m1_outer_collar_v4_core_clearance.py"


class OuterCollarV4CoreClearanceTest(unittest.TestCase):
    def test_complete_v4_core_clearance(self):
        spec = importlib.util.spec_from_file_location("clearance", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.build()
        self.assertEqual(result, json.loads(module.OUTPUT.read_text()))
        self.assertEqual(result["covered_type_pair_count"], 11)
        self.assertEqual(result["broad_aabb_candidate_count"], 14_254_960)
        self.assertEqual(result["reduced_candidate_count"], 24_208)
        self.assertEqual(result["exact_segment_check_count"], 9_074)
        self.assertEqual(result["intersection_count"], 0)
        self.assertTrue(result["global_core_clearance"])


if __name__ == "__main__":
    unittest.main()
