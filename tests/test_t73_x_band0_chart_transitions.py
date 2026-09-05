from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_band0_chart_transitions.py"


class XBandZeroChartTransitionTest(unittest.TestCase):
    def test_source_target_germs_and_framing_transport(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_x_band0_charts", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_X_BAND0_ACTUAL_CHART_GERMS_AND_FRAMING_TRANSPORT",
        )
        self.assertEqual(result["source_global_range"], [20, 22])
        self.assertEqual(result["target_global_range"], [2, 4])


if __name__ == "__main__":
    unittest.main()
