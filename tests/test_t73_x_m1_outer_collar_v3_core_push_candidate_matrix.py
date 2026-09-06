import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_x_m1_outer_collar_v3_core_push_candidate_matrix.py"


class OuterCollarV3CorePushCandidateMatrixTest(unittest.TestCase):
    def test_complete_directed_matrix(self):
        spec = importlib.util.spec_from_file_location("matrix", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.build()
        self.assertEqual(result, json.loads(module.OUTPUT.read_text()))
        self.assertEqual(result["core_segment_count"], 18156)
        self.assertEqual(result["push_segment_count"], 18156)
        self.assertEqual(result["directed_nonempty_type_pair_count"], 22)
        self.assertEqual(result["expanded_3d_aabb_candidate_count"], 28_527_996)
        self.assertEqual(
            result["clearance_status"],
            "OPEN_APPLY_DIRECTED_EXACT_HASH_INTERVAL_AND_GMP_REDUCTIONS",
        )


if __name__ == "__main__":
    unittest.main()
