from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_candidate_t_band0_surface.py"


class CandidateTBand0SurfaceTest(unittest.TestCase):
    def test_saved_surface_is_a_framed_candidate_disk(self):
        spec = importlib.util.spec_from_file_location("verify_t_band0_surface", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.verify()
        self.assertEqual(result["verdict"], "PASS_CANDIDATE_FRAMED_BAND_DISK_AND_PUSH_LOCAL_EMBEDDEDNESS_ONLY")
        self.assertEqual(result["euler_characteristic"], 1)


if __name__ == "__main__":
    unittest.main()
