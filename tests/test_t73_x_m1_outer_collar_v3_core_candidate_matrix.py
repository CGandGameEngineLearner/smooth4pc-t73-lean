import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_t73_x_m1_outer_collar_v3_core_candidate_matrix.py"


class OuterCollarV3CoreCandidateMatrixTest(unittest.TestCase):
    def test_saved_complete_matrix(self):
        spec = importlib.util.spec_from_file_location("matrix", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.build()
        self.assertEqual(result, json.loads(module.OUTPUT.read_text()))
        self.assertEqual(result["segment_count"], 18156)
        self.assertEqual(result["expanded_3d_aabb_candidate_count"], 14_254_960)
        self.assertEqual(
            result["clearance_status"],
            "OPEN_APPLY_EXACT_HASH_REDUCTIONS_AND_GMP_SURVIVORS",
        )


if __name__ == "__main__":
    unittest.main()
