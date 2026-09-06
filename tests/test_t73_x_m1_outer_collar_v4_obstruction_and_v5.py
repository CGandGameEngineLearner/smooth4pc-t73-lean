import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V4_OBSTRUCTION = ROOT / "audit/t73_x_m1_outer_collar_v4_ribbon_candidate_matrix.json"
V5_SCRIPT = (
    ROOT / "scripts/build_t73_x_m1_framed_outer_interface_collars_v5_verification.py"
)


class OuterCollarV4ObstructionAndV5Test(unittest.TestCase):
    def test_v4_exact_local_star_obstruction(self):
        saved = json.loads(V4_OBSTRUCTION.read_text())
        self.assertEqual(
            saved["verdict"], "REFUTED_X_M1_OUTER_COLLAR_V4_RIBBON_LOCAL_STAR"
        )
        self.assertEqual(saved["collision"]["interface"], 3018)
        self.assertTrue(saved["collision"]["certificate"]["normal_cross_is_zero"])
        self.assertTrue(saved["collision"]["certificate"]["normal_dot_is_positive"])

    def test_v5_saved_full_local_replay(self):
        spec = importlib.util.spec_from_file_location("v5_receipt", V5_SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.check_files(json.loads(module.OUTPUT.read_text()))
        result = receipt["full_result"]
        self.assertEqual(result["changed_dual_collars"], 8)
        self.assertEqual(result["unchanged_johnson_collars"], 3018)
        self.assertEqual(result["local_ribbon_star_checks"], 15134)
        self.assertEqual(result["classification"], "CANDIDATE_UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
