from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_candidate_t_band0_relative_boundary.py"


class CandidateTBand0RelativeBoundaryTest(unittest.TestCase):
    def test_band_disk_boundary_matches_actual_records(self):
        spec = importlib.util.spec_from_file_location("verify_t_band0_boundary", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.verify()["verdict"], "PASS_CANDIDATE_BAND0_RELATIVE_BOUNDARY_ONLY")


if __name__ == "__main__":
    unittest.main()
