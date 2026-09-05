from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_collar_product_extension.py"


class XM1CollarProductExtensionTest(unittest.TestCase):
    def test_product_extension_covers_all_local_lanes(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_x_product", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_X_M1_COLLAR_PRODUCT_EXTENSION_AND_OUTWARD_FRAMING_DOMAIN")
        self.assertEqual(result["four_simplices"], 144)
        self.assertEqual(result["band_lane_segments"], 6052)
        self.assertGreater(result["original_push_lane_segments_outside_domain"], 0)


if __name__ == "__main__":
    unittest.main()
