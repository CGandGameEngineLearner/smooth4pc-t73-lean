from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_source_chart_germs.py"


class XSourceChartGermsTest(unittest.TestCase):
    def test_all_global_source_germs_are_unique(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_x_sources", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_ALL_1513_X_SOURCE_CHART_GERMS")
        self.assertEqual(result["johnson_top_germs"], 1509)
        self.assertEqual(result["dual_boundary_germs"], 4)
        self.assertFalse(result["nu_equals_u_assumed"])


if __name__ == "__main__":
    unittest.main()
