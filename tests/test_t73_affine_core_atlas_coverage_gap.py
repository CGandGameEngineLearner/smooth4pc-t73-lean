import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_affine_core_atlas_coverage_gap.py"


class AffineCoreAtlasCoverageGapTest(unittest.TestCase):
    def test_missing_post_x_cells_fail_closed(self):
        spec = importlib.util.spec_from_file_location("verifier", SCRIPT)
        assert spec and spec.loader
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify()
        self.assertEqual(result["verdict"], "PASS_AFFINE_CORE_ATLAS_COVERAGE_GAP")
        self.assertEqual(result["omitted_post_x_replacement_core_segments"], 60520)
        self.assertEqual(result["affine_post_x_replacement_roles"], 0)
        self.assertFalse(result["actual_t73_affine_input"])


if __name__ == "__main__":
    unittest.main()
