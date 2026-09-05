from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_actual_dual_product_ribbons.py"


class ActualDualProductRibbonsTest(unittest.TestCase):
    def test_three_actual_source_ribbons(self):
        spec = importlib.util.spec_from_file_location("verify_dual_ribbons", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_ACTUAL_PRE_CANCELLATION_DUAL_PRODUCT_RIBBONS")
        self.assertEqual(result["triangles"], 48)
        self.assertEqual(result["self_linking"], {"r_xy": 0, "r_yz": 0, "r_zx": 0})


if __name__ == "__main__":
    unittest.main()
