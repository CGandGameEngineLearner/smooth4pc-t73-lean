from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_railroad_product_framings.py"


class RailroadProductFramingsTest(unittest.TestCase):
    def test_five_target_push_offs_have_zero_linking(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_railroad_framing", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_RAILROAD_TARGET_FIVE_ZERO_PRODUCT_FRAMINGS"
        )
        self.assertEqual(result["integer_surgery_framings"], {
            "m_2": 0,
            "m_3": 0,
            "r_xy": 0,
            "r_yz": 0,
            "r_zx": 0,
        })
        self.assertEqual(result["source_framed_isotopy"], "OPEN")


if __name__ == "__main__":
    unittest.main()
