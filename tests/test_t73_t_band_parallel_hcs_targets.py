from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_t_band_parallel_hcs_targets.py"


class TBandParallelHcsTargetTest(unittest.TestCase):
    def test_six_targets_are_ordered_framed_hcs_copies(self):
        spec = importlib.util.spec_from_file_location("verify_hcs_targets", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_ACTUAL_HCS_PARALLEL_TARGET_BINDING")
        self.assertEqual(result["lane_coefficients"], [-25, -15, -5, 5, 15, 25])


if __name__ == "__main__":
    unittest.main()
