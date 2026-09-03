from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class JohnsonGeometricBraidTest(unittest.TestCase):
    def test_actual_johnson_lanes_recover_public_word(self):
        path = ROOT / "scripts" / "generate_t73_johnson_geometric_braid.py"
        spec = importlib.util.spec_from_file_location("johnson_braid", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.generate()
        self.assertEqual(result["strand_count"], 44)
        self.assertEqual(result["elementary_crossing_count"], 11340)
        self.assertEqual(result["endpoint_return_status"], "PASS")
        self.assertEqual(result["relative_endpoint_word_status"], "PASS")
        self.assertEqual(result["historical_pd_status"], "NOT_USED_OR_CLAIMED")
        self.assertEqual(result["independent_ar_derivation_status"], "PASS_CODE_DEPENDENCY_SEPARATION")
        self.assertEqual(result["replacement_presentation_status"], "PENDING_GLOBAL_P0_AUDIT")


if __name__ == "__main__":
    unittest.main()
