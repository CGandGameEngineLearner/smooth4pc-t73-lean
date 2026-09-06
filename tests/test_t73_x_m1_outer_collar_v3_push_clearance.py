import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX_SCRIPT = ROOT / "scripts/build_t73_x_m1_outer_collar_v3_push_candidate_matrix.py"
CLEARANCE_SCRIPT = ROOT / "scripts/build_t73_x_m1_outer_collar_v3_push_clearance.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OuterCollarV3PushClearanceTest(unittest.TestCase):
    def test_complete_push_matrix(self):
        module = load(MATRIX_SCRIPT, "push_matrix")
        result = module.build()
        self.assertEqual(result, json.loads(module.OUTPUT.read_text()))
        self.assertEqual(result["segment_count"], 18156)
        self.assertEqual(result["expanded_3d_aabb_candidate_count"], 14_254_960)
        self.assertEqual(result["push_functional_endpoint_union_distinct_count"], 9078)

    def test_push_clearance(self):
        module = load(CLEARANCE_SCRIPT, "push_clearance")
        result = module.build()
        self.assertEqual(result, json.loads(module.OUTPUT.read_text()))
        self.assertEqual(result["covered_type_pair_count"], 11)
        self.assertEqual(result["exact_segment_check_count"], 75_618)
        self.assertEqual(result["permitted_incidence_count"], 15_134)
        self.assertEqual(result["intersection_count"], 0)
        self.assertTrue(result["global_push_clearance"])


if __name__ == "__main__":
    unittest.main()
