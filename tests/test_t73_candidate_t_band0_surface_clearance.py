from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_candidate_t_band0_surface_clearance.py"


class CandidateTBand0SurfaceClearanceTest(unittest.TestCase):
    def test_band_and_push_disks_miss_other_cores(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_t_band0_surface_clearance", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_CANDIDATE_BAND_SURFACE_OTHER_CORE_CLEARANCE_ONLY")
        self.assertGreater(result["broad_phase_pairs"], 0)
        self.assertEqual(result["broad_phase_pairs"], result["broad_phase_rejections"])


if __name__ == "__main__":
    unittest.main()
