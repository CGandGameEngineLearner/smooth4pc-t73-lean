from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_band0_current_link_clearance.py"


class XBandZeroCurrentLinkClearanceTest(unittest.TestCase):
    def test_disk_and_push_clear_all_current_passages(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_x_band0_clearance", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_X_BAND0_CURRENT_LINK_AND_PUSH_CLEARANCE"
        )
        self.assertEqual(result["current_passage_arcs"], 1514)


if __name__ == "__main__":
    unittest.main()
