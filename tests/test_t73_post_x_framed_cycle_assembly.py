from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_post_x_framed_cycle_assembly.py"


class PostXFramedCycleAssemblyTest(unittest.TestCase):
    def test_five_complete_charted_cycles(self):
        spec = importlib.util.spec_from_file_location("verify_charted_cycles", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_FIVE_COMPLETE_FRAMED_CYCLES_IN_GRAPH_OF_CHARTS")
        self.assertEqual(result["core_segments"], 68154)
        self.assertEqual(result["unified_s3_embedding_status"], "OPEN_CANCELLATION_COMPLEMENT_MAP")


if __name__ == "__main__":
    unittest.main()
