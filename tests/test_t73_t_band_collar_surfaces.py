from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_t_band_collar_surfaces.py"


class TBandCollarSurfaceTest(unittest.TestCase):
    def test_six_collar_disks_are_individually_embedded_and_sequential(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        spec = importlib.util.spec_from_file_location("verify_t_collar", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(
            result["verdict"],
            "PASS_T_BAND_COLLAR_DISKS_SEQUENTIAL_CANDIDATE_FRAMING_ONLY",
        )
        self.assertEqual(result["surfaces"], 6)
        self.assertEqual(result["movie_time_levels"], [0, 1, 2, 3, 4, 5])


if __name__ == "__main__":
    unittest.main()
