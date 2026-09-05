from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_band0_m1_parallel.py"


class XBandZeroM1ParallelTest(unittest.TestCase):
    def test_complete_twentieth_parallel_is_framed_and_disjoint(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_x_band0_parallel", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_X_BAND0_COMPLETE_FRAMED_M1_PARALLEL"
        )
        self.assertEqual(result["parallel_coefficient"], 20)


if __name__ == "__main__":
    unittest.main()
