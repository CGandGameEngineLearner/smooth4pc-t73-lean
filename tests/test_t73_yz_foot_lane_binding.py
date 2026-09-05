from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_yz_foot_lane_binding.py"


class YZFootLaneBindingTest(unittest.TestCase):
    def test_johnson_base_lanes_bind_to_both_foot_pairs(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_yz_feet", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"], "PASS_YZ_JOHNSON_BASE_LANE_FOOT_BINDINGS"
        )
        self.assertEqual(result["total_passages"], 263)
        self.assertEqual(
            result["scope"], "BASE_JOHNSON_LANES_ONLY_HYBRID_Z_REPLACEMENTS_OPEN"
        )


if __name__ == "__main__":
    unittest.main()
