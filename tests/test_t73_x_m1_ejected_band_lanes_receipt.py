from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_ejected_band_lanes.py"


class XM1EjectedBandLanesReceiptTest(unittest.TestCase):
    def test_receipt_and_counts(self):
        spec = importlib.util.spec_from_file_location("verify_ejected_lanes", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        receipt, checks = module.check_receipt()
        self.assertTrue(all(checks.values()))
        self.assertEqual(receipt["source_core_and_push_segment_count"], 12104)
        self.assertEqual(receipt["piecewise_affine_image_segment_count"], 30144)


if __name__ == "__main__":
    unittest.main()
