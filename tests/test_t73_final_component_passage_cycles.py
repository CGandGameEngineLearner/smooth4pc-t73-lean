from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_final_component_passage_cycles.py"


class FinalComponentPassageCyclesTest(unittest.TestCase):
    def test_five_cycles_partition_all_final_passages(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_final_cycles", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_FIVE_FINAL_COMPONENT_PASSAGE_CYCLES"
        )
        self.assertEqual(result["used_passages"], 1785)
        self.assertEqual(result["cycles"], 5)


if __name__ == "__main__":
    unittest.main()
