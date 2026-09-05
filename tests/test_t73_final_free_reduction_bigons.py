from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_final_free_reduction_bigons.py"


class FinalFreeReductionBigonsTest(unittest.TestCase):
    def test_three_local_bigons_reach_railroad_survivors(self):
        spec = importlib.util.spec_from_file_location("verify_bigons", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_THREE_FINAL_FREE_REDUCTION_BIGON_TUBES"
        )
        self.assertEqual(result["moves"], 3)
        self.assertTrue(result["all_inverse_moves"])


if __name__ == "__main__":
    unittest.main()
