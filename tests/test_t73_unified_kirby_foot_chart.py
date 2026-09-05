from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_unified_kirby_foot_chart.py"


class UnifiedKirbyFootChartTest(unittest.TestCase):
    def test_all_four_foot_pairs_and_final_yz_state(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_unified_feet", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_ALL_FOUR_T73_FOOT_BINDINGS_FINAL_YZ_STATE"
        )
        self.assertEqual(result["surviving_dotted_handles"], ["y", "z"])


if __name__ == "__main__":
    unittest.main()
