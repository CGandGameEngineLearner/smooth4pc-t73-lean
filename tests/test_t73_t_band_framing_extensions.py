from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_t73_t_band_framing_extensions.py"


class TBandFramingExtensionTest(unittest.TestCase):
    def test_saved_extensions_match_actual_boundary_framings(self):
        spec = importlib.util.spec_from_file_location("verify_t_framing", SCRIPT)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.verify()["verdict"], "PASS_CANDIDATE_T_FRAMING_BOUNDARY_ONLY")


if __name__ == "__main__":
    unittest.main()
