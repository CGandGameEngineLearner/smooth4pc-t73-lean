import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUSH_SCRIPT = ROOT / "scripts/build_t73_x_m1_outer_collar_v4_push_clearance.py"
MUTUAL_SCRIPT = ROOT / "scripts/build_t73_x_m1_outer_collar_v4_core_push_clearance.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OuterCollarV4PushMutualClearanceTest(unittest.TestCase):
    def test_push_clearance(self):
        module = load(PUSH_SCRIPT, "push_clearance")
        result = module.build()
        self.assertEqual(result, json.loads(module.OUTPUT.read_text()))
        self.assertEqual(result["covered_type_pair_count"], 11)
        self.assertEqual(result["exact_segment_check_count"], 75_618)
        self.assertEqual(result["intersection_count"], 0)
        self.assertTrue(result["global_push_clearance"])

    def test_directed_mutual_clearance(self):
        module = load(MUTUAL_SCRIPT, "mutual_clearance")
        result = module.build()
        self.assertEqual(result, json.loads(module.OUTPUT.read_text()))
        self.assertEqual(result["covered_directed_type_pair_count"], 22)
        self.assertEqual(result["broad_aabb_candidate_count"], 28_528_020)
        self.assertEqual(result["exact_segment_check_count"], 93_818)
        self.assertEqual(result["intersection_count"], 0)
        self.assertTrue(
            result["former_v3_collision_pair_covered_by_same_interface_gmp"]
        )
        self.assertTrue(result["global_core_push_clearance"])


if __name__ == "__main__":
    unittest.main()
