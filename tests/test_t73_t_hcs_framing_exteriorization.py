from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_t_hcs_framing_exteriorization.py"


class THcsFramingExteriorizationTest(unittest.TestCase):
    def test_state_six_framing_is_pushed_out_of_t_ball(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_t_hcs_framing", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_STATE6_FRAMING_EXTERIORIZATION")
        self.assertEqual(result["normal_replacements"], 63)


if __name__ == "__main__":
    unittest.main()
