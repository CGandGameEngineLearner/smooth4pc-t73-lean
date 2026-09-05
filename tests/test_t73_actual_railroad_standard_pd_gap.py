from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_actual_railroad_standard_pd_gap.py"


class ActualRailroadStandardPDGapTest(unittest.TestCase):
    def test_odd_mixed_parity_blocks_standard_pd(self):
        spec = importlib.util.spec_from_file_location("verify_pd_gap", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_FAIL_CLOSED_ACTUAL_RAILROAD_PD_GAP"
        )
        self.assertEqual(
            result["odd_mixed_pairs"], {"m_2/m_3": -3, "m_3/r_yz": 1}
        )
        self.assertFalse(result["standard_pd_emitted"])


if __name__ == "__main__":
    unittest.main()
