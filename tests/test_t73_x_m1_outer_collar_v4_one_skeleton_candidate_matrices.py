import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "scripts/build_t73_x_m1_outer_collar_v4_one_skeleton_candidate_matrices.py"
)


class OuterCollarV4OneSkeletonMatricesTest(unittest.TestCase):
    def test_all_three_matrices(self):
        spec = importlib.util.spec_from_file_location("matrices", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.build()
        self.assertEqual(result, json.loads(module.OUTPUT.read_text()))
        self.assertEqual(result["core_candidate_count"], 14_254_960)
        self.assertEqual(result["push_candidate_count"], 14_254_960)
        self.assertEqual(result["directed_core_push_candidate_count"], 28_528_020)
        self.assertEqual(result["core_nonempty_type_pair_count"], 11)
        self.assertEqual(result["push_nonempty_type_pair_count"], 11)
        self.assertEqual(result["directed_core_push_nonempty_type_pair_count"], 22)
        self.assertEqual(
            result["clearance_status"],
            "OPEN_APPLY_V4_EXACT_HASH_INTERVAL_AND_GMP_REDUCTIONS",
        )


if __name__ == "__main__":
    unittest.main()
