from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_t_band0_sequential_state.py"


class TBandZeroSequentialStateTest(unittest.TestCase):
    def test_first_slide_is_framed_embedded_and_invertible(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_t_state_01", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_T_BAND0_SEQUENTIAL_FRAMED_KIRBY_SLIDE"
        )
        self.assertEqual(result["state_transition"], [0, 1])
        self.assertGreater(result["inverse_recovered_source_segments"], 0)


if __name__ == "__main__":
    unittest.main()
