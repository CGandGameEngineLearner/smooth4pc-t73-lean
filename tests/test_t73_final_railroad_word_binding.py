from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_final_railroad_word_binding.py"


class FinalRailroadWordBindingTest(unittest.TestCase):
    def test_actual_railroad_rejects_old_m3_order(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_railroad", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_ACTUAL_1878_RAILROAD_LEDGER_OLD_M3_REJECTED",
        )
        self.assertEqual(result["actual_crossings"], 1878)
        self.assertFalse(result["old_word_direct_matches"]["m_3"])
        self.assertTrue(result["old_word_inverse_matches"]["r_xy"])
        self.assertEqual(result["standard_pd_status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
