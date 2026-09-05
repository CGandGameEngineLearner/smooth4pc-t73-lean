from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_band0_hybrid_state.py"


class XBandZeroHybridStateTest(unittest.TestCase):
    def test_first_x_slide_closes_across_both_chart_germs(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_x_hybrid", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_X_BAND0_HYBRID_FRAMED_STATE_0_TO_1"
        )
        self.assertEqual(result["hybrid_pieces"], 4)
        self.assertEqual(result["chart_gluings"], 4)
        self.assertEqual(result["x_intersection_after"], 0)


if __name__ == "__main__":
    unittest.main()
