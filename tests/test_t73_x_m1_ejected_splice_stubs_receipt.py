from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_ejected_splice_stubs.py"


class XM1EjectedSpliceStubsReceiptTest(unittest.TestCase):
    def test_receipt_and_counts(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_ejected_stubs", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        receipt, checks = module.check_receipt()
        self.assertTrue(all(checks.values()))
        self.assertEqual(receipt["piecewise_affine_stub_image_segment_count"], 25712)
        self.assertEqual(receipt["unmapped_middle_core_segment_count"], 48416)


if __name__ == "__main__":
    unittest.main()
