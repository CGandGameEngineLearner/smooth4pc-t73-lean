from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_x_m1_framing_exteriorization.py"


class XM1FramingExteriorizationTest(unittest.TestCase):
    def test_uniform_outward_push_clears_all_remaining_cores(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_x_m1_framing", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_X_FINAL_LINK_UNIFORM_OUTWARD_FRAMING"
        )
        self.assertEqual(result["remaining_core_segments"], 12104)
        self.assertEqual(result["pure_nu_core_segments"], 0)


if __name__ == "__main__":
    unittest.main()
