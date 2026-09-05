from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_actual_source_standard_pd_sqlite.py"


class ActualSourceStandardPDReceiptTest(unittest.TestCase):
    def test_source_native_pd_receipt(self):
        spec = importlib.util.spec_from_file_location("verify_source_pd", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt, checks = module.check_receipt()
        self.assertTrue(all(checks.values()))
        self.assertEqual(receipt["crossing_count"], 1761630)
        self.assertEqual(receipt["framing_status"], "OPEN_SOURCE_PRODUCT_PUSH_OFFS_REQUIRED")
        self.assertTrue(checks["post_x_coverage"])


if __name__ == "__main__":
    unittest.main()
