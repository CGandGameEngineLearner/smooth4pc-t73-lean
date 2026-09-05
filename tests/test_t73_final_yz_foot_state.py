from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_final_yz_foot_state.py"


class FinalYZFootStateTest(unittest.TestCase):
    def test_all_final_passages_bind_to_two_foot_pairs(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_final_yz", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_FINAL_YZ_FOOT_AND_PASSAGE_STATE")
        self.assertEqual(result["y_passages"], 234)
        self.assertEqual(result["z_passages"], 1549)
        self.assertEqual(result["unique_passage_ids"], 1783)


if __name__ == "__main__":
    unittest.main()
