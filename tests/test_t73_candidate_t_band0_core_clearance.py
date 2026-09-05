from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_candidate_t_band0_core_clearance.py"


class CandidateTBand0CoreClearanceTest(unittest.TestCase):
    def test_candidate_core_misses_actual_m2_m3_lifts(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_t_band0_clearance", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_CANDIDATE_ALL_CORE_CLEARANCE_ONLY")
        self.assertGreater(result["exact_deck_checks"], 0)


if __name__ == "__main__":
    unittest.main()
